import unittest

from src.options_payoff import (
    cross_expiry_terminal_pnl,
    estimated_equal_max_profit_loss,
    static_chart_payoff,
    static_flatline_value,
    strategy_legs,
    strike_candidates,
    strike_grid,
    threshold_met,
)


class StrategyPayoffTests(unittest.TestCase):
    def test_static_chart_is_flat_across_terminal_spot(self) -> None:
        legs = strategy_legs(100.0, "near", "next")
        prices = {
            ("near", "CE"): 6.0,
            ("near", "PE"): 5.0,
            ("next", "CE"): 8.0,
            ("next", "PE"): 7.0,
        }

        values = [
            static_chart_payoff(x, legs, prices)
            for x in (50.0, 80.0, 100.0, 120.0, 150.0)
        ]
        self.assertTrue(all(abs(v - values[0]) < 1e-12 for v in values))
        # Entry credit = +6 -5 -8 +7 = 0
        self.assertAlmostEqual(values[0], 0.0)

    def test_cross_expiry_pnl_is_not_flat(self) -> None:
        gross = cross_expiry_terminal_pnl(
            near_spot=105.0,
            next_spot=95.0,
            common_strike=100.0,
            near_call=6.0,
            near_put=5.0,
            next_call=8.0,
            next_put=7.0,
        )
        self.assertAlmostEqual(gross, -10.0)

        gross_reverse = cross_expiry_terminal_pnl(
            near_spot=95.0,
            next_spot=105.0,
            common_strike=100.0,
            near_call=6.0,
            near_put=5.0,
            next_call=8.0,
            next_put=7.0,
        )
        self.assertAlmostEqual(gross_reverse, 10.0)

    def test_flat_chart_can_hide_real_cross_expiry_loss(self) -> None:
        legs = strategy_legs(100.0, "near", "next")
        prices = {
            ("near", "CE"): 7.0,
            ("near", "PE"): 6.0,
            ("next", "CE"): 8.0,
            ("next", "PE"): 7.0,
        }
        chart = static_chart_payoff(100.0, legs, prices)
        realized = cross_expiry_terminal_pnl(110, 95, 100, 7, 6, 8, 7)

        # The static chart looks positive by +0.00 only after this particular
        # input; the realized position is still directional across expiries.
        self.assertAlmostEqual(chart, 0.0)
        self.assertAlmostEqual(realized, -15.0)

    def test_candidate_strikes(self) -> None:
        self.assertEqual(strike_candidates(24175.0, 50.0), (24200.0, 23800.0, 24600.0))


    def test_phase7_strike_grid_is_exhaustive(self) -> None:
        grid = strike_grid(24175.0, 50.0, 400, 50)
        self.assertEqual(len(grid), 17)
        self.assertEqual(grid[0], 23775.0)
        self.assertEqual(grid[-1], 24575.0)
        self.assertIn(24175.0, grid)

    def test_equal_max_profit_loss_metric_for_green_flatline(self) -> None:
        legs = strategy_legs(100.0, "near", "next")
        prices = {
            ("near", "CE"): 8.0,
            ("near", "PE"): 5.0,
            ("next", "CE"): 7.0,
            ("next", "PE"): 10.0,
        }
        value = static_chart_payoff(100.0, legs, prices)
        value_direct = static_flatline_value(100.0, "near", "next", 8.0, 5.0, 7.0, 10.0)
        self.assertAlmostEqual(value, 6.0)
        self.assertAlmostEqual(value_direct, 6.0)
        summary = estimated_equal_max_profit_loss(value, 50)
        self.assertAlmostEqual(summary["estimated_max_profit_inr"], 300.0)
        self.assertAlmostEqual(summary["estimated_min_pnl_inr"], 300.0)
        self.assertTrue(summary["estimated_all_green_flatline"])
        self.assertTrue(summary["estimated_flatline_is_constant"])

    def test_threshold_is_strictly_greater_than(self) -> None:
        self.assertTrue(threshold_met(2.51, 100.0, 2.5))
        self.assertFalse(threshold_met(2.50, 100.0, 2.5))


if __name__ == "__main__":
    unittest.main()
