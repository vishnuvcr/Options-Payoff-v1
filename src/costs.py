from __future__ import annotations

from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class CostModel:
    brokerage_per_order_inr: float = 20.0
    exchange_turnover_rate: float = 0.0003553
    sebi_turnover_rate: float = 0.000001
    stamp_duty_buy_rate: float = 0.00003
    gst_rate: float = 0.18
    stt_before_2026_04_01: float = 0.001
    stt_from_2026_04_01: float = 0.0015
    slippage_pct: float = 0.0

def executed_premium(premium: float, side: int, slippage_pct: float) -> float:
    if premium < 0:
        raise ValueError('premium must be non-negative')
    if side == 1:
        return premium * (1.0 + slippage_pct)
    if side == -1:
        return premium * (1.0 - slippage_pct)
    raise ValueError('side must be +1 or -1')

def stt_rate_for_date(trade_date: date, model: CostModel) -> float:
    if trade_date >= date(2026, 4, 1):
        return model.stt_from_2026_04_01
    return model.stt_before_2026_04_01

def four_leg_entry_cashflow(
    near_call: float, near_put: float, next_call: float, next_put: float,
    slippage_pct: float = 0.0
) -> dict[str, float]:
    sell_call = executed_premium(near_call, -1, slippage_pct)
    buy_put = executed_premium(near_put, +1, slippage_pct)
    buy_call = executed_premium(next_call, +1, slippage_pct)
    sell_put = executed_premium(next_put, -1, slippage_pct)
    turnover = sell_call + buy_put + buy_call + sell_put
    sell_turnover = sell_call + sell_put
    buy_turnover = buy_put + buy_call
    cashflow = sell_call + sell_put - buy_put - buy_call
    return {
        'sell_call': sell_call,
        'buy_put': buy_put,
        'buy_call': buy_call,
        'sell_put': sell_put,
        'premium_turnover': turnover,
        'sell_premium_turnover': sell_turnover,
        'buy_premium_turnover': buy_turnover,
        'entry_cashflow_per_unit': cashflow,
    }

def transaction_costs(
    trade_date: date,
    turnover_per_unit: float,
    sell_turnover_per_unit: float,
    buy_turnover_per_unit: float,
    lot_size: int,
    model: CostModel,
) -> dict[str, float]:
    if lot_size <= 0:
        raise ValueError('lot_size must be positive')
    turnover = turnover_per_unit * lot_size
    sell_turnover = sell_turnover_per_unit * lot_size
    buy_turnover = buy_turnover_per_unit * lot_size
    brokerage = 4.0 * model.brokerage_per_order_inr
    exchange = turnover * model.exchange_turnover_rate
    sebi = turnover * model.sebi_turnover_rate
    stamp = buy_turnover * model.stamp_duty_buy_rate
    stt = sell_turnover * stt_rate_for_date(trade_date, model)
    gst = model.gst_rate * (brokerage + exchange + sebi)
    total = brokerage + exchange + sebi + stamp + stt + gst
    return {
        'brokerage': brokerage,
        'exchange_transaction': exchange,
        'sebi_fee': sebi,
        'stamp_duty': stamp,
        'stt': stt,
        'gst': gst,
        'total_costs': total,
    }

def trigger_base(
    mode: str,
    spot: float,
    lot_size: int,
    buy_premium_per_unit: float,
    configured_capital_per_lot: float | None = None,
) -> float:
    if lot_size <= 0:
        raise ValueError('lot_size must be positive')
    if mode == 'buy_premium':
        return buy_premium_per_unit * lot_size
    if mode == 'spot_notional':
        return spot * lot_size
    if mode == 'configured_capital':
        if configured_capital_per_lot is None or configured_capital_per_lot <= 0:
            raise ValueError('configured_capital_per_lot is required for configured_capital mode')
        return configured_capital_per_lot
    raise ValueError(f'unsupported trigger base mode: {mode}')