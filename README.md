TRACK_ID=PS06

## AnaRisk Sentinel — Transaction Risk Investigation Assistant

AnaRisk Sentinel is an investigation assistant for a bank's fraud desk. A single customer's
transaction history (CSV) goes in; an investigation report comes out. The report's first
finding is always whether anything needs attention at all — a routine history is reported as
routine, not padded with manufactured risk.

### How it works

The system deliberately keeps risk *detection* deterministic and rule-based, and uses the LLM
only to *explain* what the rules already found. Nothing is invented by the model; every
transaction the narrative cites comes from the evidence payload handed to it.

1. **Parse** (`analyzer/services/parser.py`) — validates the uploaded CSV: required columns
   (`transaction_id, customer_id, date, description, payee, amount, channel`), row-level
   type/format checks, empty-file and missing-header handling.
2. **Baseline** (`analyzer/services/baseline.py`) — builds a per-customer behavioural profile:
   typical amount range (quartile-based once enough history exists, min/max otherwise), payee
   frequency and recency, channel distribution, and transaction cadence. Also tracks
   *history strength* (sparse / moderate / strong) so thin histories aren't treated as
   confidently as established ones.
3. **Rule engine** (`analyzer/services/rules.py`) — four independent, explainable signals,
   each producing its own severity and cited transaction IDs:
   - Unusually large transactions relative to the customer's typical upper amount.
   - Bursts of payments to a payee that only recently appeared.
   - Behavioural breaks — a window of activity that diverges from baseline across multiple
     dimensions (amount, channel, payee familiarity, frequency) at once.
   - Activity bursts — an unusual spike in transaction volume in a short window.
4. **Evidence threading** (`analyzer/services/evidence_threads.py`) — clusters related signals
   (shared transactions or close temporal proximity) into investigation threads, so an
   investigator sees "these three things are probably one story," not a flat signal list.
5. **Classification** (`rules.py: classify_overall`) — combines signals and thread strength
   into an overall verdict and priority, including the explicit "nothing needs attention" case.
6. **AI narrative** (`analyzer/services/gemini.py`) — sends the deterministic evidence payload
   (signals, threads, baseline, capped transaction citations) to Gemini with a system prompt
   that restricts it to explaining and connecting the supplied evidence, not inventing new
   findings. Gemini calls are isolated behind `GeminiConfigError` / `GeminiRequestError` /
   `GeminiResponseError`, so a missing key, network failure, or malformed response degrades to
   a clear error rather than a crash or a fabricated report.
7. **PDF export** (`analyzer/services/pdf_report.py`) — a two-page investigator-facing report
   built from the same deterministic + AI output, via ReportLab.

### Known limitation

The current rule set does not include an "odd-hours activity" check. The transaction schema
used here carries a date but not a time, so time-of-day risk can't be evaluated from this data
model yet — flagged here rather than silently omitted. [Update this once you've decided
whether to add a `time` column + rule before submitting, or keep this as a stated scope call.]

### Tech stack

- Backend: Python, Django (single process, no database dependency — no persisted models)
- Frontend: server-rendered Django template, vanilla JS, vanilla CSS (`static/app.js`, `static/style.css`)
- AI: Google Gemini API (`google-genai` SDK) for narrative generation only
- No external services besides Gemini; no third-party vector DB

### Run it

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here   # or set it in your shell/CI environment
python app.py
```

Serves the full app (backend + frontend) at **http://localhost:8000** — no second terminal,
no build step, no manual setup. `GEMINI_API_KEY` is read from the environment only; nothing is
hardcoded or committed.

### Data

No external datasets are used. All CSV transaction histories under `data/` are synthetic,
generated to cover:
- [list your scenario files here, e.g. `activity_burst.csv`, `behavioural_burst.csv`,
  `channel_shift.csv`, `everything_abnormal.csv`, `final_test.csv`]
- a routine, nothing-to-flag history, to demonstrate the "no attention needed" path

### Demo video

[Link here — 2-3 minutes, showing one routine case (report says "nothing needs attention")
and one difficult case (multiple correlated signals, evidence thread, AI narrative, PDF export).]