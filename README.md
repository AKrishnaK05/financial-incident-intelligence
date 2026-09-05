# Financial Incident Intelligence (FII)

> **A financial state graph + autonomous investigation agent for distributed payment operations.**

Financial systems can tell finance teams that two records do not match. FII goes one step further: it reconstructs the expected financial state, traces the event chain, tests competing explanations, measures the blast radius and exposure, and recommends a governed response.

## The incident

FII's hero scenario is deliberately synthetic and reproducible:

| Event | Amount |
|---|---:|
| Payment captured | ₹10,000 |
| Refund processed | -₹3,000 |
| Expected downstream settlement representation | ₹7,000 |
| Observed downstream settlement representation | ₹10,000 |
| Variance | ₹3,000 |

The refund is processed before the modeled settlement cutoff, but its `refund.processed` event is delivered after that cutoff. The downstream representation therefore misses the refund adjustment at the cutoff.

The system does **not** claim that a real Razorpay settlement engine depends on merchant webhook delivery. The simulator models a downstream finance representation whose inputs arrive asynchronously. This keeps the incident technically honest while preserving the distributed-systems failure mode we want to investigate.

## Why FII is different

**Reconciliation:**
> These records do not match.

**FII:**
> These records do not match → here is the causal event chain → these competing hypotheses were tested → this mechanism has the strongest evidence → these merchants/payments are affected → this is the quantified exposure → this is the governed action → here is what remains unknown.

The LLM is deliberately **not** the financial source of truth. Financial values, incident detection, hypothesis evidence, exposure, blast radius, and governance are deterministic and testable.

## Architecture

```text
Synthetic payment / refund / webhook events
                    │
                    ▼
          Deterministic settlement engine
                    │
                    ▼
             Incident detector
                    │
                    ▼
             Financial state graph
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Evidence + timeline   Incident correlation
          │                   │
          ▼                   ▼
   Hypothesis engine     Blast radius
          │                   │
          ▼                   ▼
      Reasoning          Financial exposure
          └─────────┬─────────┘
                    ▼
             Incident report
                    │
                    ▼
             Governance policy
                    │
                    ▼
       Curated AgentContext (facts only)
                    │
                    ▼
              Gemini / Mock / OpenAI
                    │
                    ▼
          Structured AI narrative
                    │
                    ▼
                Validator
                    │
                    ▼
       Human approval / escalation
```

`pipeline.py` is the reusable computation entry point. `simulator/main.py` is only a narrated CLI presentation of that pipeline. The API, UI, tests, and evaluation harness all consume the same pipeline.

## Core design principles

1. **Deterministic financial truth** — money and settlement state are calculated outside the LLM.
2. **Evidence before explanation** — the model receives curated evidence and deterministic hypothesis results.
3. **No hallucinated financial facts** — IDs, amounts, timestamps, exposure, and actions are validated outside the model.
4. **Mechanism vs. underlying cause** — the system can be highly confident that a delayed event caused the observed variance while honestly leaving the deeper infrastructure cause unresolved.
5. **Human control** — recommendations always require approval; the system never executes financial remediation automatically.
6. **Reproducibility** — a fixed seed produces the same synthetic world and deterministic investigation.
7. **Evaluation by ground truth** — the simulator records injected incidents separately from the detector and never feeds ground truth into the investigation.

## What is implemented

- Synthetic merchants, payments, refunds, and asynchronous webhook events
- Multi-refund payment support with refund-total invariant
- Controlled isolated and systemic `REFUND_EVENT_LATENCY` scenarios
- Deterministic expected vs. observed settlement representation
- Incident detection and severity classification
- Financial state graph and event traversal
- Evidence and timeline analysis
- Four competing root-cause hypotheses
- Deterministic hypothesis ranking with evidence margin
- Systemic incident correlation and blast-radius analysis
- Deterministic financial exposure calculation
- Governed action policy and human approval requests
- Provider interface with mock, Gemini, and optional OpenAI implementations
- Pydantic structured LLM output
- Evidence-bound AI prompt
- Post-generation validator that prevents the model from changing root cause, confidence, reasoning trace, or governed action
- FastAPI backend
- Streamlit investigation command center
- Deterministic evaluation harness
- Automated tests

## Current deterministic benchmark

Default run: **10 base payments + 1 hero payment + 20 systemic payments**.

Typical seed-42 result:

| Metric | Result |
|---|---:|
| Settlements processed | 31 |
| Detected incidents | 19 |
| Precision | 1.0000 |
| Recall | 1.0000 |
| F1 | 1.0000 |
| Ground-truth exposure | ₹21,000 |
| Exposure error | ₹0 |
| Root-cause accuracy | 1.0000 |
| Systemic incidents correctly clustered | 18/18 |

The detection metric is intentionally transparent about its current limitation: the simulator currently has one incident mechanism and defines a real exception as expected-vs-observed variance. The evaluation harness is therefore a strong reproducibility/regression benchmark, but detection precision/recall will become genuinely discriminative after adding independent noise and unrelated incident types.

## Run locally

Create an environment and install dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the deterministic CLI:

```bash
python -m simulator.main
```

Run tests:

```bash
pytest tests/ -v
```

Run evaluation:

```bash
python -m evaluation.evaluate
```

Run API:

```bash
uvicorn api.main:app --reload
```

Then use:

- `GET /health`
- `POST /run`
- `GET /evaluation`
- `GET /incidents/{incident_id}`
- `POST /incidents/{incident_id}/investigate`
- `POST /incidents/{incident_id}/approval`

Run UI:

```bash
streamlit run ui/app.py
```

## Gemini

The project defaults to the deterministic mock provider so the repository works without credentials. For the actual AI demo, set:

```text
AGENT_PROVIDER=gemini
AGENT_MODEL=gemini-2.5-flash
GEMINI_API_KEY=...
```

A `.env.example` file is included. Environment variables must be exported by the shell or loaded by the user's preferred environment manager; secrets are never stored in the repository.

## Repository structure

```text
financial-incident-intelligence/
├── api/                    # FastAPI interface
├── configs/                # Typed domain contracts and settings
├── data/ground_truth/      # Evaluation artifacts
├── docs/                   # Architecture notes
├── evaluation/             # Deterministic benchmark
├── financial_engine/       # Expected/observed settlement logic
├── governance/             # Bounded actions + human approval
├── incidents/              # Incident detection
├── investigation/          # Evidence, reasoning, AI and validation
├── simulator/              # Synthetic event generation + CLI
├── tests/                  # Automated tests
├── ui/                     # Streamlit command center
├── pipeline.py             # Single reusable deterministic pipeline
└── README.md
```

## Scope and roadmap

Only one failure mechanism is intentionally implemented deeply: `REFUND_EVENT_LATENCY`. This is a deliberate choice for a buildathon demo: one mechanism is investigated end-to-end rather than presenting shallow support for a large taxonomy.

The strongest next extensions would be:

1. independent noise and unrelated incident mechanisms for a non-tautological detector benchmark;
2. richer cross-merchant temporal correlation;
3. persistent incident case storage;
4. replayable investigation traces and audit history;
5. calibrated confidence/evidence scoring using held-out synthetic scenarios;
6. more provider-agnostic AI evaluation for unsupported-claim rate and governance compliance.
