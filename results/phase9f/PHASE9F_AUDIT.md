# Phase 9F — Cross-market and regime audit

Trades joined: **169**
NSE context source: **yfinance fallback**
India VIX source: **yfinance fallback**
FII/DII source: **Hareeshkesavan**

This phase is descriptive only. No regime-based entry filter was adopted.

## Regime coverage

| variable           | regime       |   trades |   net_pnl_inr |   mean_net_pnl_inr |   win_rate_pct |   win_rate_wilson_low_pct |   win_rate_wilson_high_pct |   profit_factor |   max_drawdown_inr |   iid_mean_ci_low |   iid_mean_ci_high |   block4_mean_ci_low |   block4_mean_ci_high |
|:-------------------|:-------------|---------:|--------------:|-------------------:|---------------:|--------------------------:|---------------------------:|----------------:|-------------------:|------------------:|-------------------:|---------------------:|----------------------:|
| india_vix_regime   | Q1           |       43 |     53977     |          1255.28   |        72.093  |                  57.309   |                    83.2534 |         8.48212 |           3477.12  |          755.577  |           1781.8   |             724.003  |              1784.66  |
| india_vix_regime   | Q2           |       42 |     31223.2   |           743.411  |        59.5238 |                  44.4943  |                    72.9571 |         3.0229  |           4296.04  |          208.964  |           1319.71  |             319.627  |              1215.03  |
| india_vix_regime   | Q3           |       42 |     37563.3   |           894.363  |        66.6667 |                  51.5525  |                    78.9875 |         3.93087 |           4738.17  |          363.062  |           1472.12  |             423.201  |              1395.88  |
| india_vix_regime   | Q4           |       42 |      2925.31  |            69.6503 |        57.1429 |                  42.2062  |                    70.8823 |         1.09991 |          10052.1   |         -654.746  |            719.802 |            -504.08   |               665.794 |
| nifty_gap_regime   | flat         |       66 |     46353.8   |           702.33   |        66.6667 |                  54.6563  |                    76.8436 |         2.59186 |          21683     |          152.187  |           1211.63  |             -16.1653 |              1311.74  |
| nifty_gap_regime   | negative     |       46 |     31681.9   |           688.737  |        60.8696 |                  46.4568  |                    73.6068 |         2.79657 |           6100.09  |          170.417  |           1243.85  |             182.374  |              1249.68  |
| nifty_gap_regime   | positive     |       57 |     47653.1   |           836.02   |        63.1579 |                  50.1778  |                    74.4764 |         3.64877 |           5006.8   |          373.5    |           1297.32  |             369.471  |              1308.6   |
| fii_regime         | FII_net_buy  |        2 |      -585.67  |          -292.835  |        50      |                   9.45312 |                    90.5469 |         0.16778 |            703.744 |         -703.744  |            118.074 |            -292.835  |              -292.835 |
| fii_regime         | FII_net_sell |      167 |    126274     |           756.135  |        64.0719 |                  56.554   |                    70.9569 |         2.97178 |          16200.6   |          451.564  |           1059.16  |             418.68   |              1084.49  |
| dii_regime         | DII_net_buy  |        1 |      -703.744 |          -703.744  |         0      |                   0       |                    79.3451 |         0       |            703.744 |         -703.744  |           -703.744 |            -703.744  |              -703.744 |
| dii_regime         | DII_net_sell |      168 |    126393     |           752.337  |        64.2857 |                  56.7951  |                    71.1376 |         2.97362 |          16200.6   |          449.204  |           1040.33  |             424.953  |              1086.24  |
| global_risk_regime | mixed        |       23 |     22309     |           969.957  |        56.5217 |                  36.8114  |                    74.3654 |         4.42892 |           1838.03  |          306.096  |           1690.91  |             483.613  |              1473.69  |
| global_risk_regime | risk_off     |       75 |     62407.3   |           832.098  |        62.6667 |                  51.355   |                    72.744  |         3.40133 |           5311.57  |          402.987  |           1264.38  |             405.259  |              1303.85  |
| global_risk_regime | risk_on      |       71 |     40972.5   |           577.077  |        67.6056 |                  56.0612  |                    77.3428 |         2.27047 |          16801.5   |           61.7516 |           1056.64  |             -82.0976 |              1133.21  |

## Limitations

Point-in-time quote-level bid/ask data for external markets is not available in the corrected H1 ledger. Corporate-action and news timestamps were not retrospectively imputed. External variables are explanatory context only, not new trading signals.
