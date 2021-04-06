from typing import Any

import arrow

BANKING_ENDPOINT = "/banking/v2"


def arrow_or_none(value: Any):
    return arrow.get(value) if value else None
