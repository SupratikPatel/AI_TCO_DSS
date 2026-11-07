"""Pure currency helpers. Rates are USD per 1 EUR (Req 12.2)."""

import math


def _check_rate(rate: float) -> None:
    if not math.isfinite(rate) or rate <= 0:
        raise ValueError(f"FX rate must be a positive finite number, got {rate!r}")


def eur_to_usd(amount_eur: float, rate: float) -> float:
    _check_rate(rate)
    return amount_eur * rate


def usd_to_eur(amount_usd: float, rate: float) -> float:
    _check_rate(rate)
    return amount_usd / rate


def round_display(amount: float) -> float:
    """Round a display amount to 2 decimal places (Req 12.5)."""
    return round(amount, 2)
