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
