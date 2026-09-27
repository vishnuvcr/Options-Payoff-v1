import unittest

from src.intraday_selection import first_positive_intraday_surface, max_positive_candidate


class IntradaySelectionTests(unittest.TestCase):
    def test_0920_negative_does_not_skip_day(self):
        surfaces = [
            ("2026-09-10T09:20", [
                {"shift_points": 0, "flatline_inr": -100.0},
                {"shift_points": 50, "flatline_inr": 0.0},
            ]),
            ("2026-09-10T09:21", [
                {"shift_points": -50, "flatline_inr": 125.0},
                {"shift_points": 50, "flatline_inr": 200.0},
            ]),
        ]
        result = first_positive_intraday_surface(surfaces)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "2026-09-10T09:21")
        self.assertEqual(result[1]["shift_points"], 50)

    def test_no_threshold_is_applied(self):
        surfaces = [
            ("2026-09-10T09:20", [
                {"shift_points": 0, "flatline_inr": 1.0},
            ]),
        ]
        result = first_positive_intraday_surface(surfaces)
        self.assertIsNotNone(result)
        self.assertEqual(result[1]["flatline_inr"], 1.0)

    def test_maximum_positive_candidate_wins(self):
        candidates = [
            {"shift_points": -50, "flatline_inr": 500.0},
            {"shift_points": 0, "flatline_inr": 900.0},
            {"shift_points": 50, "flatline_inr": 700.0},
        ]
        winner = max_positive_candidate(candidates)
        self.assertEqual(winner["shift_points"], 0)
        self.assertEqual(winner["flatline_inr"], 900.0)

    def test_zero_or_negative_surface_has_no_winner(self):
        self.assertIsNone(max_positive_candidate([
            {"shift_points": 0, "flatline_inr": 0.0},
            {"shift_points": 50, "flatline_inr": -1.0},
        ]))


if __name__ == "__main__":
    unittest.main()
