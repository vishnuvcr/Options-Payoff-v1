from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Leg:
    option_type: str  # "CE" or "PE"
    side: int          # +1 buy, -1 sell
    strike: float
    expiry_label: str


def intrinsic_value(option_type: str, spot: float, strike: float) -> float:
    option_type = option_type.upper()
    if option_type == "CE":
        return max(spot - strike, 0.0)
    if option_type == "PE":
        return max(strike - spot, 0.0)
    raise ValueError(f"Unsupported option_type={option_type!r}")


def terminal_payoff(option_type: str, side: int, spot: float, strike: float) -> float:
    if side not in (-1, 1):
        raise ValueError("side must be +1 (buy) or -1 (sell)")
    return side * intrinsic_value(option_type, spot, strike)


def strategy_legs(common_strike: float, near_expiry: str, next_expiry: str) -> tuple[Leg, ...]:
    # User strategy:
    # near weekly:  sell call, buy put
    # next weekly:  buy call, sell put
    return (
        Leg("CE", -1, common_strike, near_expiry),
        Leg("PE", +1, common_strike, near_expiry),
        Leg("CE", +1, common_strike, next_expiry),
        Leg("PE", -1, common_strike, next_expiry),
    )


def static_chart_payoff(
    terminal_spot: float,
    legs: Iterable[Leg],
    entry_prices: Mapping[tuple[str, str], float],
) -> float:
    """
    Reconstructs the user's one-dimensional payoff chart by applying the
    same hypothetical terminal spot to every leg, even when expiries differ.

    entry_prices maps (expiry_label, option_type) -> executed entry premium.
    Positive P&L includes premium cash received at entry.
    """
    pnl = 0.0
    for leg in legs:
        key = (leg.expiry_label, leg.option_type)
        if key not in entry_prices:
            raise KeyError(f"Missing entry price for {key}")
        premium = entry_prices[key]
        # Buy: -premium; Sell: +premium
        pnl += -leg.side * premium
        pnl += terminal_payoff(leg.option_type, leg.side, terminal_spot, leg.strike)
    return pnl


def cross_expiry_terminal_pnl(
    near_spot: float,
    next_spot: float,
    common_strike: float,
    near_call: float,
    near_put: float,
    next_call: float,
    next_put: float,
) -> float:
    """
    Economically correct terminal P&L for the four-leg position when the
    near-expiry options settle at near_spot and the next-expiry options
    settle at next_spot.

    This excludes taxes/fees/slippage and is per underlying unit.

    Premium cashflow at entry:
        + near_call - near_put - next_call + next_put

    Expiry intrinsic payoff:
        (K - near_spot) + (next_spot - K)
        = next_spot - near_spot
    """
    entry_cashflow = near_call - near_put - next_call + next_put
    expiry_payoff = next_spot - near_spot
    return entry_cashflow + expiry_payoff


def synthetic_forward_pnl_components(
    near_spot: float,
    next_spot: float,
    common_strike: float,
    near_call: float,
    near_put: float,
    next_call: float,
    next_put: float,
) -> dict[str, float]:
    return {
        "entry_cashflow": near_call - near_put - next_call + next_put,
        "near_synthetic_forward_payoff": common_strike - near_spot,
        "next_synthetic_forward_payoff": next_spot - common_strike,
        "cross_expiry_terminal_pnl": cross_expiry_terminal_pnl(
            near_spot,
            next_spot,
            common_strike,
            near_call,
            near_put,
            next_call,
            next_put,
        ),
    }


def strike_candidates(
    spot: float,
    atm_step: float,
    shifts: tuple[float, ...] = (0.0, -400.0, 400.0),
) -> tuple[float, ...]:
    if atm_step <= 0:
        raise ValueError("atm_step must be positive")
    atm = round(spot / atm_step) * atm_step
    return tuple(atm + shift for shift in shifts)


def threshold_met(pnl: float, base_value: float, threshold_pct: float = 2.5) -> bool:
    if base_value <= 0:
        raise ValueError("base_value must be positive")
    return (pnl / base_value) * 100.0 > threshold_pct
