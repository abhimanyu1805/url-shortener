from __future__ import annotations

import random
import string


BASE62_ALPHABET = string.digits + string.ascii_letters


def generate_short_code(length: int = 7) -> str:
    return "".join(random.choice(BASE62_ALPHABET) for _ in range(length))
