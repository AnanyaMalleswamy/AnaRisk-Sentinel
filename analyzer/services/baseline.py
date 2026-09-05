import statistics
from collections import defaultdict
from datetime import datetime, date
from itertools import groupby

# we need a minimum number of these many days to see a pattern in the transaction historyand come to a conclusion
HISTORY_STRENGTH_RULES = {
    "strong": {"min_count": 15, "min_days": 30},
    "moderate": {"min_count": 5, "min_days": 7},
}

# Minimum transaction count required before we trust quartile-based
# (IQR) amount boundaries. Below this we go back to min/max.
MIN_COUNT_FOR_QUARTILES = 4

# How many top recurring payees to surface explicitly.
TOP_RECURRING_PAYEES_LIMIT = 5

