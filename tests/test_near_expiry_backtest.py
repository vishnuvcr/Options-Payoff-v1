import types
import unittest

from src.costs import CostModel
from scripts.run_near_expiry_exit_backtest import candidate_metrics


class NearExpiryBacktestTests(unittest.TestCase):
    def test_entry_slippage_is_reflected_in_gross_pnl(self):
        row = types.SimpleNamespace(
            entry_timestamp="2026-08-04 09:20:00+05:30",
            strike=100.0,
            near_expiry="2026-08-04",
            far_expiry="2026-08-11",
            near_call_close=8.0,
            near_put_close=8.0,
            far_call_close=10.0,
            far_put_close=10.0,
            near_settlement=100.0,
            near_exit_timestamp="2026-08-04 15:30:00+05:30",
            far_call_exit_close=12.0,
            far_put_exit_close=7.0,
            near_lot_size=50,
            far_lot_size=50,
        )
        out = candidate_metrics(row, CostModel(slippage_pct=0.01))
        self.assertIsNotNone(out)
        # Entry execution cashflow after 1% slippage = -0.36/unit.
        # Near pair payoff = 0; far exits after 1% slippage = 11.88 - 7.07.
        # Therefore gross = 4.45/unit, not the 5.00/unit raw-price result.
        self.assertAlmostEqual(out["gross_pnl_inr"], 4.45 * 50, places=8)


if __name__ == "__main__":
    unittest.main()
