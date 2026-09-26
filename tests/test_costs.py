import unittest
from datetime import date

from src.costs import CostModel, four_leg_entry_cashflow, transaction_costs, trigger_base

class CostModelTests(unittest.TestCase):
    def test_four_leg_cashflow_without_slippage(self):
        x=four_leg_entry_cashflow(6,5,8,7,0.0)
        self.assertAlmostEqual(x['entry_cashflow_per_unit'],0.0)
        self.assertAlmostEqual(x['premium_turnover'],26.0)

    def test_slippage_reduces_short_sale_proceeds_and_increases_buy_cost(self):
        x=four_leg_entry_cashflow(6,5,8,7,0.10)
        self.assertAlmostEqual(x['sell_call'],5.4)
        self.assertAlmostEqual(x['buy_put'],5.5)
        self.assertAlmostEqual(x['buy_call'],8.8)
        self.assertAlmostEqual(x['sell_put'],6.3)
        self.assertAlmostEqual(x['entry_cashflow_per_unit'],-2.6)

    def test_stt_changes_on_2026_april_first(self):
        m=CostModel()
        old=transaction_costs(date(2026,3,31),26,13,13,65,m)
        new=transaction_costs(date(2026,4,1),26,13,13,65,m)
        self.assertGreater(new['stt'],old['stt'])

    def test_trigger_base_buy_premium(self):
        self.assertAlmostEqual(trigger_base('buy_premium',24000,65,10),650.0)

if __name__=='__main__': unittest.main()