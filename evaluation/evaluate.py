"""
Evaluation harness for Financial Incident Intelligence.

Runs the pipeline once, compares the detector's output against the
hidden ground truth it never had access to, and reports:

- Detection precision / recall / F1
- Root-cause accuracy (primary hypothesis vs ground-truth scenario)
- Exposure accuracy (detected variance vs confirmed ground-truth
  exposure, in aggregate and per-incident)
- Blast-radius / correlation accuracy (does the systemic cluster
  actually contain every true systemic incident, and nothing else)

This does not call an LLM -- it evaluates the deterministic
detection, correlation, and hypothesis layers, which is what the
benchmark in the project plan is meant to measure. The AI
investigation narrative is validated separately (see
investigation/agent_validator.py), since its job is to explain
evidence that is already established here, not to establish it.

Usage:
    python -m evaluation.evaluate
"""

import json
from dataclasses import asdict, dataclass

from pipeline import PipelineResult, run_pipeline


@dataclass
class DetectionMetrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


@dataclass
class ExposureMetrics:
    ground_truth_total: int
    detected_total: int
    absolute_error: int
    percent_error: float


@dataclass
class RootCauseMetrics:
    evaluated: int
    correct: int
    accuracy: float


@dataclass
class ClusterMetrics:
    true_systemic_incident_ids: set
    detected_systemic_incident_ids: set
    correctly_included: int
    missed: int
    incorrectly_included: int


@dataclass
class EvaluationReport:
    total_settlements: int
    detection: DetectionMetrics
    exposure: ExposureMetrics
    root_cause: RootCauseMetrics
    cluster: ClusterMetrics


def evaluate_detection(result: PipelineResult) -> DetectionMetrics:
    """
    Compare detected incidents against ground truth by payment_id.
    """

    ground_truth_payment_ids = {
        record.payment_id for record in result.ground_truth
    }

    detected_payment_ids = {
        incident.payment_id for incident in result.detected_incidents
    }

    true_positives = len(
        ground_truth_payment_ids & detected_payment_ids
    )
    false_positives = len(
        detected_payment_ids - ground_truth_payment_ids
    )
    false_negatives = len(
        ground_truth_payment_ids - detected_payment_ids
    )

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0.0
    )

    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return DetectionMetrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
    )


def evaluate_exposure(result: PipelineResult) -> ExposureMetrics:
    """
    Compare aggregate detected variance against confirmed
    ground-truth exposure.
    """

    ground_truth_total = sum(
        record.exposure_amount for record in result.ground_truth
    )

    detected_total = result.financial_exposure.gross_variance

    absolute_error = abs(ground_truth_total - detected_total)

    percent_error = (
        absolute_error / ground_truth_total * 100
        if ground_truth_total > 0
        else 0.0
    )

    return ExposureMetrics(
        ground_truth_total=ground_truth_total,
        detected_total=detected_total,
        absolute_error=absolute_error,
        percent_error=round(percent_error, 2),
    )


def evaluate_root_cause(result: PipelineResult) -> RootCauseMetrics:
    """
    For every incident with matching ground truth, check whether the
    deterministic primary hypothesis names the correct scenario.
    """

    ground_truth_by_payment = {
        record.payment_id: record for record in result.ground_truth
    }

    evaluated = 0
    correct = 0

    for report in result.incident_reports:
        record = ground_truth_by_payment.get(report.payment_id)

        if record is None:
            continue

        evaluated += 1

        primary_hypothesis = report.primary_hypothesis

        if (
            primary_hypothesis is not None
            and primary_hypothesis.name == record.root_cause
        ):
            correct += 1

    accuracy = (correct / evaluated) if evaluated > 0 else 0.0

    return RootCauseMetrics(
        evaluated=evaluated,
        correct=correct,
        accuracy=round(accuracy, 4),
    )


def evaluate_cluster(result: PipelineResult) -> ClusterMetrics:
    """
    Check whether the correlation engine's systemic cluster matches
    the true set of systemically-injected incidents.
    """

    true_systemic_incident_ids = {
        incident.incident_id
        for incident in result.detected_incidents
        if incident.payment_id.startswith("PAY_SYS_")
    }

    detected_systemic_incident_ids = set()

    for cluster in result.clusters:
        if cluster.scope != "SYSTEMIC":
            continue

        for incident in cluster.incidents:
            if incident.payment_id.startswith("PAY_SYS_"):
                detected_systemic_incident_ids.add(incident.incident_id)

    correctly_included = len(
        true_systemic_incident_ids & detected_systemic_incident_ids
    )
    missed = len(
        true_systemic_incident_ids - detected_systemic_incident_ids
    )
    incorrectly_included = len(
        detected_systemic_incident_ids - true_systemic_incident_ids
    )

    return ClusterMetrics(
        true_systemic_incident_ids=true_systemic_incident_ids,
        detected_systemic_incident_ids=detected_systemic_incident_ids,
        correctly_included=correctly_included,
        missed=missed,
        incorrectly_included=incorrectly_included,
    )


def evaluate(result: PipelineResult) -> EvaluationReport:
    return EvaluationReport(
        total_settlements=len(result.state_graph.settlements),
        detection=evaluate_detection(result),
        exposure=evaluate_exposure(result),
        root_cause=evaluate_root_cause(result),
        cluster=evaluate_cluster(result),
    )


def print_report(report: EvaluationReport) -> None:
    print("Financial Incident Intelligence -- Evaluation Report")
    print("=====================================================")
    print()
    print(f"Settlements processed:  {report.total_settlements}")
    print()

    print("Detection")
    print("-----------------------------")
    print(f"True positives:   {report.detection.true_positives}")
    print(f"False positives:  {report.detection.false_positives}")
    print(f"False negatives:  {report.detection.false_negatives}")
    print(f"Precision:        {report.detection.precision}")
    print(f"Recall:           {report.detection.recall}")
    print(f"F1:               {report.detection.f1}")
    print()

    print("Exposure")
    print("-----------------------------")
    print(f"Ground-truth exposure:  ₹{report.exposure.ground_truth_total}")
    print(f"Detected exposure:      ₹{report.exposure.detected_total}")
    print(f"Absolute error:         ₹{report.exposure.absolute_error}")
    print(f"Percent error:          {report.exposure.percent_error}%")
    print()

    print("Root cause")
    print("-----------------------------")
    print(f"Evaluated:  {report.root_cause.evaluated}")
    print(f"Correct:    {report.root_cause.correct}")
    print(f"Accuracy:   {report.root_cause.accuracy}")
    print()

    print("Cluster / blast radius")
    print("-----------------------------")
    print(f"True systemic incidents:        {len(report.cluster.true_systemic_incident_ids)}")
    print(f"Correctly clustered:            {report.cluster.correctly_included}")
    print(f"Missed:                         {report.cluster.missed}")
    print(f"Incorrectly included:           {report.cluster.incorrectly_included}")


def report_to_dict(report: EvaluationReport) -> dict:
    payload = asdict(report)

    payload["cluster"]["true_systemic_incident_ids"] = sorted(
        report.cluster.true_systemic_incident_ids
    )
    payload["cluster"]["detected_systemic_incident_ids"] = sorted(
        report.cluster.detected_systemic_incident_ids
    )

    return payload


def main() -> None:
    result = run_pipeline()
    report = evaluate(result)

    print_report(report)

    output_path = "evaluation/report.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report_to_dict(report), file, indent=4)

    print()
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
