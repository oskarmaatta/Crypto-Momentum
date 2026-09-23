import unittest

import pandas as pd

from helpers.backtest import backtest_sma


class BacktestTests(unittest.TestCase):
    def prices(self, last_open=12, last_high=13, last_low=11, last_close=12):
        return pd.DataFrame({
            'time': [0, 1, 2],
            'open': [10, 10, last_open],
            'high': [11, 13, last_high],
            'low': [9, 9, last_low],
            'close': [10, 12, last_close],
        })

    def run_exit(self, **kwargs):
        return backtest_sma(self.prices(**kwargs), 2, 1, 1, atr_window=2)

    def test_original_behavior(self):
        result = backtest_sma(self.prices(last_close=13), 2)
        self.assertEqual(result['position'].tolist(), [False, False, True])
        self.assertEqual(result['cumulative_pl'].iloc[-1], 1)

    def test_stop_wins_when_both_touched(self):
        result = self.run_exit(last_high=16, last_low=8)
        self.assertEqual(result['atr'].iloc[1], 3)
        self.assertEqual(result['pl'].iloc[-1], -3)
        self.assertEqual(result['exit_reason'].iloc[-1], 'stop_loss')

    def test_gap_stop(self):
        result = self.run_exit(last_open=8, last_low=7)
        self.assertEqual(result['pl'].iloc[-1], -4)

    def test_gap_target_precedes_intrabar_stop(self):
        result = self.run_exit(last_open=16, last_high=17, last_low=8)
        self.assertEqual(result['pl'].iloc[-1], 4)
        self.assertEqual(result['exit_reason'].iloc[-1], 'take_profit')

    def test_target_only(self):
        result = backtest_sma(self.prices(last_high=16, last_low=8), 2,
                              take_profit_atr=1, atr_window=2)
        self.assertEqual(result['pl'].iloc[-1], 3)

    def test_waits_for_atr(self):
        result = backtest_sma(self.prices(), 2, stop_loss_atr=1)
        self.assertFalse(result['position'].any())
        self.assertEqual(result['pl'].sum(), 0)

    def test_invalid_parameters(self):
        for value in (0, -1, float('inf'), float('nan')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                backtest_sma(self.prices(), 2, stop_loss_atr=value)


if __name__ == '__main__':
    unittest.main()
