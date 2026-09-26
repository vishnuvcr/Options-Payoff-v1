import unittest

import pandas as pd

from scripts.run_backtest import parse_args, select_trades


class MaxEqualSelectionTests(unittest.TestCase):
    def test_selects_highest_flatline_value_within_minus_plus_400(self) -> None:
        candidates = pd.DataFrame(
            [
                {
                    "entry_timestamp": "2022-01-03 09:20:00+05:30",
                    "candidate_label": "SHIFT_MINUS_400",
                    "shift_points": -400,
                    "estimated_all_green_flatline": True,
                    "estimated_equal_max_profit_loss_inr": 1800.0,
                    "chart_return_pct": 3.0,
                    "net_pnl_inr": 100.0,
                    "total_costs_inr": 10.0,
                },
                {
                    "entry_timestamp": "2022-01-03 09:20:00+05:30",
                    "candidate_label": "ATM",
                    "shift_points": 0,
                    "estimated_all_green_flatline": True,
                    "estimated_equal_max_profit_loss_inr": 2400.0,
                    "chart_return_pct": 2.7,
                    "net_pnl_inr": 200.0,
                    "total_costs_inr": 10.0,
                },
                {
                    "entry_timestamp": "2022-01-03 09:20:00+05:30",
                    "candidate_label": "SHIFT_PLUS_400",
                    "shift_points": 400,
                    "estimated_all_green_flatline": True,
                    "estimated_equal_max_profit_loss_inr": 2200.0,
                    "chart_return_pct": 3.1,
                    "net_pnl_inr": -50.0,
                    "total_costs_inr": 10.0,
                },
                {
                    "entry_timestamp": "2022-01-03 09:20:00+05:30",
                    "candidate_label": "SHIFT_PLUS_450",
                    "shift_points": 450,
                    "estimated_all_green_flatline": True,
                    "estimated_equal_max_profit_loss_inr": 9000.0,
                    "chart_return_pct": 20.0,
                    "net_pnl_inr": 999.0,
                    "total_costs_inr": 10.0,
                },
            ]
        )

        class Args:
            selection_mode = "max_equal_flatline"
            selection_score = "equal_max_profit_loss_inr"
            selection_max_shift_points = 400
            selection_step_points = 50
            min_equal_max_profit_loss_inr = 0.0
            min_chart_return_pct = None
            threshold_pct = 2.5
            fallback_order = "ATM_MINUS_400,ATM_PLUS_400"

        selected = select_trades(candidates, Args())
        self.assertEqual(len(selected), 1)
        self.assertEqual(int(selected.iloc[0]["shift_points"]), 0)
        self.assertEqual(float(selected.iloc[0]["estimated_equal_max_profit_loss_inr"]), 2400.0)

    def test_optional_legacy_percentage_gate_can_be_applied(self) -> None:
        candidates = pd.DataFrame(
            [
                {
                    "entry_timestamp": "2022-01-03 09:20:00+05:30",
                    "candidate_label": "ATM",
                    "shift_points": 0,
                    "estimated_all_green_flatline": True,
                    "estimated_equal_max_profit_loss_inr": 2400.0,
                    "chart_return_pct": 2.4,
                    "net_pnl_inr": 100.0,
                    "total_costs_inr": 10.0,
                },
                {
                    "entry_timestamp": "2022-01-03 09:20:00+05:30",
                    "candidate_label": "SHIFT_PLUS_50",
                    "shift_points": 50,
                    "estimated_all_green_flatline": True,
                    "estimated_equal_max_profit_loss_inr": 2200.0,
                    "chart_return_pct": 2.6,
                    "net_pnl_inr": 150.0,
                    "total_costs_inr": 10.0,
                },
            ]
        )

        class Args:
            selection_mode = "max_equal_flatline"
            selection_score = "equal_max_profit_loss_inr"
            selection_max_shift_points = 400
            selection_step_points = 50
            min_equal_max_profit_loss_inr = 0.0
            min_chart_return_pct = 2.5
            threshold_pct = 2.5
            fallback_order = "ATM_MINUS_400,ATM_PLUS_400"

        selected = select_trades(candidates, Args())
        self.assertEqual(len(selected), 1)
        self.assertEqual(int(selected.iloc[0]["shift_points"]), 50)


if __name__ == "__main__":
    unittest.main()
