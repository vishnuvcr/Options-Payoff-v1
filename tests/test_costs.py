import unittest
from datetime import date
from src.costs import CostModel, four_leg_entry_cashflow, transaction_costs, trigger_base

class CostModelTests(unittest.TestCase):
    def test_four_leg_cashflow_without_slippage(self):
        x=four_leg_entry_cashflow(6,5,8,7,0.0)
        self.assertAlmostEqual(x['entry_cashflow_per_unit'],0.0)
        self.assertAlmostEqual(x['premium_turnover'],26.0)

    def test_slippage_changes_entry_cashflow(self):
        x=four_leg_entry_cashflow(6,5,8,7,0.10)
        self.assertAlmostEqual(x['sell_call'],5.4)
        self.assertAlmostEqual(x['buy_put'],5.5)
        self.assertAlmostEqual(x['buy_call'],8.8)
        self.assertAlmostEqual(x['sell_put'],6.3)
        self.assertAlmostEqual(x['entry_cashflow_per_unit'],-2.6)

    def test_entry_stt_changes_on_2026_april_first(self):
        m=CostModel()
        old=transaction_costs(date(2026,3,31),26,13,13,0,0,65,m)
        new=transaction_costs(date(2026,4,1),26,13,13,0,0,65,m)
        self.assertGreater(new['stt_entry'],old['stt_entry'])

    def test_exercise_stt_is_charged_on_long_intrinsic_value(self):
        m=CostModel()
        c=transaction_costs(date(2026,4,1),26,13,13,100,0,65,m)
        self.assertAlmostEqual(c['stt_exercise'],100*65*0.0015)

    def test_trigger_base_buy_premium(self):
        self.assertAlmostEqual(trigger_base('buy_premium',24000,65,10),650.0)

if __name__=='__main__': unittest.main()

class HistoricalLotSizeTests(unittest.TestCase):
    def test_historical_nifty_lots(self):
        from scripts.extract_strategy_inputs import nifty_lot_size
        self.assertEqual(nifty_lot_size(date(2021,7,29)), 75)
        self.assertEqual(nifty_lot_size(date(2021,8,5)), 50)
        self.assertEqual(nifty_lot_size(date(2024,5,2)), 25)
        self.assertEqual(nifty_lot_size(date(2024,11,21)), 75)
        self.assertEqual(nifty_lot_size(date(2026,1,6)), 65)

