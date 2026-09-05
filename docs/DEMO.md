# Buildathon demo flow

## 1. Deterministic proof

The default run processes **51 settlement records** (30 base + 1 hero + 20 systemic) and reports the batch match rate plus the exceptions that remain unresolved without human approval.

```bash
python -m simulator.main
```

Use the hero incident to tell the story:

- ₹10,000 payment captured
- ₹3,000 refund processed before cutoff
- refund event delivered after cutoff
- expected representation ₹7,000
- observed representation ₹10,000
- FII identifies `REFUND_EVENT_LATENCY`
- correlated incidents expand the blast radius to multiple merchants
- governance recommends `ESCALATE_INCIDENT`
- the exception remains explicitly `UNRESOLVED` because financial remediation is not executed automatically
- the batch report shows the 51-record throughput, 62.75% match rate, and 19 unresolved exceptions
- approval remains pending for a human reviewer

## 2. Evaluation proof

```bash
python -m evaluation.evaluate
```

Show the independent metrics and explain the current benchmark limitation: one incident mechanism means detector precision/recall is primarily a regression/reproducibility metric. Root-cause, exposure, and clustering checks remain useful because they are evaluated against ground truth rather than copied from the detector.

## 3. AI proof

Export the Gemini credentials in the shell:

```powershell
$env:AGENT_PROVIDER="gemini"
$env:AGENT_MODEL="gemini-2.5-flash"
$env:GEMINI_API_KEY="..."
python -m simulator.main
```

The important demonstration is not that Gemini can summarize the incident. It is that:

1. Gemini receives a curated evidence boundary rather than the full financial graph.
2. Deterministic reasoning ranks `REFUND_EVENT_LATENCY`.
3. Gemini explains that mechanism in structured output.
4. The validator rejects a response that changes the root cause, confidence, reasoning trace, or governed action.
5. The deeper infrastructure cause of the delay remains explicitly unresolved.

## 4. UI proof

```bash
streamlit run ui/app.py
```

Recommended click path:

1. Run the pipeline.
2. Open `INC_CAND_000001`.
3. Show expected vs observed amount.
4. Show event timeline.
5. Expand competing hypotheses.
6. Show evidence score and margin.
7. Show systemic blast radius.
8. Show `ESCALATE_INCIDENT` and pending approval.
9. Click **Investigate with AI** when Gemini is configured.

## 5. API proof

```bash
uvicorn api.main:app --reload
```

Useful endpoints:

```text
GET  /health
POST /run
GET  /evaluation
GET  /incidents/{incident_id}
POST /incidents/{incident_id}/investigate
POST /incidents/{incident_id}/approval
```

The API keeps the latest run in memory. This is deliberate for the buildathon demo and should not be described as production persistence.
