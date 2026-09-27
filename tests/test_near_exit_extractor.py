import unittest
from scripts.extract_near_exit_horizon_inputs import build_exit_lookups, expiry_pair
import pandas as pd

class NearExitHorizonTests(unittest.TestCase):
    def test_same_contract_supports_multiple_exit_dates(self):
        df = pd.DataFrame([
            {'timestamp': pd.Timestamp('2026-08-25 15:29:00+05:30'), 'strike': 25000, 'close': 100.0, 'option_type': 'CE', 'trading_date': pd.Timestamp('2026-08-25').date()},
            {'timestamp': pd.Timestamp('2026-09-01 15:29:00+05:30'), 'strike': 25000, 'close': 140.0, 'option_type': 'CE', 'trading_date': pd.Timestamp('2026-09-01').date()},
            {'timestamp': pd.Timestamp('2026-08-25 15:29:00+05:30'), 'strike': 25000, 'close': 90.0, 'option_type': 'PE', 'trading_date': pd.Timestamp('2026-08-25').date()},
        ])
        exits = build_exit_lookups(df, [
            pd.Timestamp('2026-08-25 15:30:00+05:30'),
            pd.Timestamp('2026-09-01 15:30:00+05:30'),
        ])
        self.assertEqual(exits[pd.Timestamp('2026-08-25').date()][(25000.0,'CE')][0],100.0)
        self.assertEqual(exits[pd.Timestamp('2026-09-01').date()][(25000.0,'CE')][0],140.0)

    def test_horizon_pair_changes_far_expiry_only(self):
        expiries = [
            pd.Timestamp('2026-08-27').date(),
            pd.Timestamp('2026-09-03').date(),
            pd.Timestamp('2026-09-10').date(),
            pd.Timestamp('2026-09-17').date(),
        ]
        entry = pd.Timestamp('2026-08-20').date()
        self.assertEqual(expiry_pair(entry, expiries, 1)[1], expiries[1])
        self.assertEqual(expiry_pair(entry, expiries, 2)[1], expiries[2])
        self.assertEqual(expiry_pair(entry, expiries, 3)[1], expiries[3])

if __name__ == '__main__':
    unittest.main()
