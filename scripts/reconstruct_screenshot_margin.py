#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from marginism import RiskEngine


POSITION = [
    {"symbol": "NIFTY", "instrument": "CE", "expiry": "2026-09-29", "strike": 23450, "transaction_type": "SELL", "quantity": 65},
    {"symbol": "NIFTY", "instrument": "PE", "expiry": "2026-09-29", "strike": 23450, "transaction_type": "BUY", "quantity": 65},
    {"symbol": "NIFTY", "instrument": "CE", "expiry": "2026-10-06", "strike": 23450, "transaction_type": "BUY", "quantity": 65},
    {"symbol": "NIFTY", "instrument": "PE", "expiry": "2026-10-06", "strike": 23450, "transaction_type": "SELL", "quantity": 65},
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--span-file", required=True)
    ap.add_argument("--date", default="2026-09-25")
    ap.add_argument("--target-margin", type=float, default=88076.0)
    ap.add_argument("--spot", type=float, default=23140.50)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    engine = RiskEngine.from_file(args.span_file)
    result = engine.basket(POSITION, as_of_date=args.date)
    final = result["data"]["final"]

    spot_notional = args.spot * 65.0
    target_ratio = 100.0 * args.target_margin / spot_notional
    flatline_value_at_2p5 = args.target_margin * 0.025

    output = {
        "calibration_date": args.date,
        "position": POSITION,
        "screenshot_target_margin_inr": args.target_margin,
        "screenshot_spot": args.spot,
        "lot_size": 65,
        "spot_notional_inr": spot_notional,
        "screenshot_margin_as_pct_spot_notional": target_ratio,
        "flatline_required_for_2p5pct_of_target_margin_inr": flatline_value_at_2p5,
        "span_result": result,
        "reconstructed_basket_initial_margin_inr": final["total"],
        "reconstructed_span_inr": final["span"],
        "reconstructed_exposure_inr": final["exposure"],
        "reconstructed_option_premium_reported_inr": final["option_premium"],
        "reconstructed_additional_inr": final["additional"],
        "difference_vs_screenshot_inr": final["total"] - args.target_margin,
        "absolute_difference_inr": abs(final["total"] - args.target_margin),
        "match_within_1pct": abs(final["total"] - args.target_margin) <= 0.01 * args.target_margin,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
