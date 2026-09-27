import unittest
from scripts.extract_near_exit_strategy_inputs import build_exit_lookups
import pandas as pd

class NearExitExtractorTests(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
