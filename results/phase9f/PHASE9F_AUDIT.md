# Phase 9F — Cross-market and regime audit

Trades joined: **169**
NSE context source: **yfinance fallback**
India VIX source: **yfinance fallback**
FII/DII source: **Hareeshkesavan_sparse_unusable**

This phase is descriptive only. No regime-based entry filter was adopted.

## Regime coverage

| variable                | regime            |   trades |   net_pnl_inr |   mean_net_pnl_inr |   win_rate_pct |   win_rate_wilson_low_pct |   win_rate_wilson_high_pct |   profit_factor |   max_drawdown_inr |   iid_mean_ci_low |   iid_mean_ci_high |   block4_mean_ci_low |   block4_mean_ci_high |
|:------------------------|:------------------|---------:|--------------:|-------------------:|---------------:|--------------------------:|---------------------------:|----------------:|-------------------:|------------------:|-------------------:|---------------------:|----------------------:|
| india_vix_regime        | Q1                |       43 |      53977    |          1255.28   |        72.093  |                   57.309  |                    83.2534 |         8.48212 |            3477.12 |          755.577  |           1781.8   |             724.003  |              1784.66  |
| india_vix_regime        | Q2                |       42 |      31223.2  |           743.411  |        59.5238 |                   44.4943 |                    72.9571 |         3.0229  |            4296.04 |          208.964  |           1319.71  |             319.627  |              1215.03  |
| india_vix_regime        | Q3                |       42 |      37563.3  |           894.363  |        66.6667 |                   51.5525 |                    78.9875 |         3.93087 |            4738.17 |          363.062  |           1472.12  |             423.201  |              1395.88  |
| india_vix_regime        | Q4                |       42 |       2925.31 |            69.6503 |        57.1429 |                   42.2062 |                    70.8823 |         1.09991 |           10052.1  |         -654.746  |            719.802 |            -504.08   |               665.794 |
| nifty_gap_regime        | flat              |       66 |      46353.8  |           702.33   |        66.6667 |                   54.6563 |                    76.8436 |         2.59186 |           21683    |          152.187  |           1211.63  |             -16.1653 |              1311.74  |
| nifty_gap_regime        | negative          |       46 |      31681.9  |           688.737  |        60.8696 |                   46.4568 |                    73.6068 |         2.79657 |            6100.09 |          170.417  |           1243.85  |             182.374  |              1249.68  |
| nifty_gap_regime        | positive          |       57 |      47653.1  |           836.02   |        63.1579 |                   50.1778 |                    74.4764 |         3.64877 |            5006.8  |          373.5    |           1297.32  |             369.471  |              1308.6   |
| nse_bse_relative_regime | NIFTY_outperform  |       70 |      28788.4  |           411.263  |        61.4286 |                   49.7157 |                    71.9523 |         1.77194 |           15050.3  |         -123.907  |            879.1   |            -174.708  |               950.473 |
| nse_bse_relative_regime | SENSEX_outperform |       99 |      96900.4  |           978.792  |        65.6566 |                   55.8756 |                    74.2679 |         4.5299  |            5556.48 |          624.606  |           1351.45  |             645.187  |              1343.68  |
| global_risk_regime      | mixed             |       24 |      21576.5  |           899.023  |        54.1667 |                   35.0749 |                    72.1087 |         3.98077 |            1838.03 |          255.315  |           1582.23  |             443.648  |              1403.37  |
| global_risk_regime      | risk_off          |       74 |      63139.8  |           853.24   |        63.5135 |                   52.1318 |                    73.5614 |         3.49998 |            5311.57 |          438.366  |           1264.52  |             409.759  |              1336.69  |
| global_risk_regime      | risk_on           |       71 |      40972.5  |           577.077  |        67.6056 |                   56.0612 |                    77.3428 |         2.27047 |           16801.5  |           61.7516 |           1056.64  |             -82.0976 |              1133.21  |

## Limitations

Point-in-time quote-level bid/ask data for external markets is not available in the corrected H1 ledger. Corporate-action and news timestamps were not retrospectively imputed. External variables are explanatory context only, not new trading signals.
