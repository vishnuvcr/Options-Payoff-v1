import unittest
import pandas as pd

from scripts.extract_near_exit_strategy_inputs import build_exit_lookups, build_entry_lookup, common_from_lookup

class NearExitExtractorTests(unittest.TestCase):
    def test_same_contract_supports_two_exit_dates(self):
        df = pd.DataFrame([
            {'timestamp': pd.Timestamp('2026-08-25 15:29:00+05:30'), 'strike': 25000, 'close': 100.0, 'option_type': 'CE', 'trading_date': pd.Timestamp('2026-08-25', tz='Asia/Kolkata').date()},
            {'timestamp': pd.Timestamp('2026-09-01 15:29:00+05:30'), 'strike': 25000, 'close': 140.0, 'option_type': 'CE', 'trading_date': pd.Timestamp('2026-09-01', tz='Asia/Kolkata').date()},
            {'timestamp': pd.Timestamp('2026-08-25 15:29:00+05:30'), 'strike': 25000, 'close': 90.0, 'option_type': 'PE', 'trading_date': pd.Timestamp('2026-08-25', tz='Asia/Kolkata').date()},
            {'timestamp': pd.Timestamp('2026-09-01 15:29:00+05:30'), 'strike': 25000, 'close': 80.0, 'option_type': 'PE', 'trading_date': pd.Timestamp('2026-09-01', tz='Asia/Kolkata').date()},
        ])
        exits = build_exit_lookups(
            df,
            [pd.Timestamp('2026-08-25 15:30:00+05:30'), pd.Timestamp('2026-09-01 15:30:00+05:30')],
        )
        self.assertEqual(exits[pd.Timestamp('2026-08-25').date()][(25000.0, 'CE')][0], 100.0)
        self.assertEqual(exits[pd.Timestamp('2026-09-01').date()][(25000.0, 'CE')][0], 140.0)
        self.assertEqual(exits[pd.Timestamp('2026-08-25').date()][(25000.0, 'PE')][0], 90.0)

    def test_common_lookup_requires_both_call_and_put_in_both_expiries(self):
        ts = pd.Timestamp('2026-08-20 09:20:00+05:30')
        near = {ts: {25000.0: {'CE': 100.0, 'PE': 110.0}, 25100.0: {'CE': 90.0}}}
        far = {ts: {25000.0: {'CE': 130.0, 'PE': 140.0}, 25100.0: {'CE': 100.0, 'PE': 120.0}}}
        self.assertEqual(common_from_lookup(near, far, ts), {25000.0})

if __name__ == '__main__':
    unittest.main()
