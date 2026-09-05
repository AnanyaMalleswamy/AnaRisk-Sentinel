import json
import os
import re

from google import genai
from google.genai import types

GEMINI_MODEL = "gemini-2.5-flash"  # cheap/fast model choice for quota reasons

MAX_SIGNALS_IN_PAYLOAD = 10
MAX_THREADS_IN_PAYLOAD = 5
MAX_CITED_TRANSACTIONS = 20

_ID_TOKEN_PATTERN = re.compile(r"\b[A-Za-z]{1,6}\d{2,8}\b")

class GeminiConfigError(Exception):
    """Raised when Gemini cannot be configured (e.g. missing API key)."""


class GeminiRequestError(Exception):
    """Raised when the Gemini API call itself fails (network/timeout/API error)."""


class GeminiResponseError(Exception):
    """Raised when Gemini's response is missing, malformed, or fails validation."""


#system prompt comes here


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "assessment": {"type": "string"},
        "key_findings": {"type": "array", "items": {"type": "string"}},
        "behavioral_change": {"type": "string"},
        "investigator_priority": {"type": "string"},
        "recommended_review": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["assessment", "key_findings", "behavioral_change", "investigator_priority", "recommended_review"],
}

def build_evidence_payload(customer_id, transactions, baseline, signals, threads, classification):
    """Compact, structured evidence -- never the raw CSV."""
    txn_by_id = {t["transaction_id"]: t for t in transactions}

    cited_ids = set()
    for s in signals[:MAX_SIGNALS_IN_PAYLOAD]:
        cited_ids.update(s["transaction_ids"])
    for t in threads[:MAX_THREADS_IN_PAYLOAD]:
        cited_ids.update(t["transaction_ids"])
    cited_ids = list(cited_ids)[:MAX_CITED_TRANSACTIONS]

    relevant_transactions = [
        {
            "transaction_id": tid,
            "date": txn_by_id[tid]["date"],
            "amount": txn_by_id[tid]["amount"],
            "payee": txn_by_id[tid]["payee"],
            "channel": txn_by_id[tid]["channel"],
        }
        for tid in cited_ids if tid in txn_by_id
    ]

    return {
        "customer_id": customer_id,
        "classification": classification,
        "baseline_summary": {
            "transaction_count": baseline["transaction_count"],
            "history_strength": baseline["history_strength"],
            "history_start": baseline["history_start"],
            "history_end": baseline["history_end"],
            "amount_profile": baseline["amount_profile"],
            "dominant_channel": baseline["channel_profile"]["dominant_channel"],
            "transactions_per_week": baseline["frequency_profile"]["transactions_per_week"],
        },
        "signals": [
            {
                "signal_type": s["signal_type"],
                "severity": s["severity"],
                "reason": s["reason"],
                "transaction_ids": s["transaction_ids"],
            }
            for s in signals[:MAX_SIGNALS_IN_PAYLOAD]
        ],
        "threads": [
            {
                "thread_id": t["thread_id"],
                "priority": t["priority"],
                "signal_types": t["signal_types"],
                "time_range": t["time_range"],
                "transaction_ids": t["transaction_ids"],
            }
            for t in threads[:MAX_THREADS_IN_PAYLOAD]
        ],
        "relevant_transactions": relevant_transactions,
    }


def _extract_referenced_ids(text):
    return set(_ID_TOKEN_PATTERN.findall(text or ""))


def validate_narrative_traceability(narrative, valid_transaction_ids):
    """Returns the set of any transaction-ID-shaped tokens Gemini mentioned
    that were NOT in the evidence it was given. Empty set = clean."""
    referenced = set()
    referenced |= _extract_referenced_ids(narrative.get("assessment", ""))
    for finding in narrative.get("key_findings", []):
        referenced |= _extract_referenced_ids(finding)
    referenced |= _extract_referenced_ids(narrative.get("behavioral_change", ""))
    referenced |= _extract_referenced_ids(narrative.get("investigator_priority", ""))
    for step in narrative.get("recommended_review", []):
        referenced |= _extract_referenced_ids(step)
    return referenced - set(valid_transaction_ids)


def _get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiConfigError(
            "GEMINI_API_KEY is not set. Add it to your .env file before generating a report."
        )
    return genai.Client(api_key=api_key)

