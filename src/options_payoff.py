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


def strike_grid(
    spot: float,
    atm_step: float = 50.0,
    max_shift_points: int = 400,
    step_points: int = 50,
) -> tuple[float, ...]:
    """Return every common-strike candidate from -max_shift to +max_shift."""
    if atm_step <= 0:
        raise ValueError("atm_step must be positive")
    if max_shift_points < 0:
        raise ValueError("max_shift_points must be >= 0")
    if step_points <= 0:
        raise ValueError("step_points must be positive")
    if max_shift_points % step_points != 0:
        raise ValueError("max_shift_points must be divisible by step_points")
    atm = round(spot / atm_step) * atm_step
    return tuple(
        atm + shift
        for shift in range(-max_shift_points, max_shift_points + 1, step_points)
    )


def static_flatline_value(
    common_strike: float,
    near_expiry: str,
    next_expiry: str,
    near_call: float,
    near_put: float,
    next_call: float,
    next_put: float,
) -> float:
    """Return the constant P&L of the one-dimensional same-spot payoff chart.

    For this four-leg structure the terminal intrinsic terms cancel when the
    *same hypothetical spot* is applied to both expiries. The result is the
    entry premium cashflow C1-P1-C2+P2, per unit of underlying.
    """
    legs = strategy_legs(common_strike, near_expiry, next_expiry)
    prices = {
        (near_expiry, "CE"): float(near_call),
        (near_expiry, "PE"): float(near_put),
        (next_expiry, "CE"): float(next_call),
        (next_expiry, "PE"): float(next_put),
    }
    return float(static_chart_payoff(common_strike, legs, prices))


def estimated_equal_max_profit_loss(
    flatline_value_per_unit: float,
    lot_size: int,
) -> dict[str, float | bool]:
    """Summarize the chart's estimated max-profit=max-loss flatline.

    This is deliberately labeled an *estimated chart metric*, not the
    economically correct max loss of the held cross-expiry position. For a
    positive flatline, the chart's maximum and minimum P&L are equal to the
    same positive value.
    """
    value = float(flatline_value_per_unit) * int(lot_size)
    return {
        "estimated_max_profit_inr": value,
        "estimated_min_pnl_inr": value,
        "estimated_equal_max_profit_loss_inr": value,
        "estimated_all_green_flatline": bool(value > 0.0),
        "estimated_flatline_is_constant": True,
    }


def threshold_met(pnl: float, base_value: float, threshold_pct: float = 2.5) -> bool:
    if base_value <= 0:
        raise ValueError("base_value must be positive")
    return (pnl / base_value) * 100.0 > threshold_pct



def near_expiry_manual_close_pnl(
    near_spot: float,
    common_strike: float,
    near_call: float,
    near_put: float,
    far_call_entry: float,
    far_put_entry: float,
    far_call_exit: float,
    far_put_exit: float,
) -> float:
    """Gross per-unit P&L when all four legs are closed at near expiry.

    The near-expiry short CE and long PE settle intrinsically at T1. The
    farther-expiry long CE and short PE are manually squared off at T1 using
    their observed executable exit prices. This is the user's actual exit
    convention and is distinct from holding the far options to their own
    expiry.
    """
    entry_cashflow = near_call - near_put - far_call_entry + far_put_entry
    near_pair_payoff = -intrinsic_value("CE", near_spot, common_strike) + intrinsic_value(
        "PE", near_spot, common_strike
    )
    far_close_value = far_call_exit - far_put_exit
    return entry_cashflow + near_pair_payoff + far_close_value
