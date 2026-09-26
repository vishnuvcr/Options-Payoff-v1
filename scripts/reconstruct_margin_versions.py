#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from marginism import RiskEngine

POSITION = [
    {'symbol':'NIFTY','instrument':'CE','expiry':'2026-09-29','strike':23450,'transaction_type':'SELL','quantity':65},
    {'symbol':'NIFTY','instrument':'PE','expiry':'2026-09-29','strike':23450,'transaction_type':'BUY','quantity':65},
    {'symbol':'NIFTY','instrument':'CE','expiry':'2026-10-06','strike':23450,'transaction_type':'BUY','quantity':65},
    {'symbol':'NIFTY','instrument':'PE','expiry':'2026-10-06','strike':23450,'transaction_type':'SELL','quantity':65},
]

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--span-dir',required=True)
    ap.add_argument('--target-margin',type=float,default=88076.0)
    ap.add_argument('--date',default='2026-09-25')
    ap.add_argument('--out',required=True)
    args=ap.parse_args()

    rows=[]
    for path in sorted(Path(args.span_dir).glob('*.spn')):
        result=RiskEngine.from_file(str(path)).basket(POSITION,as_of_date=args.date)
        final=result['data']['final']
        total=float(final['total'])
        rows.append({
            'file':path.name,
            'margin_inr':total,
            'difference_inr':total-args.target_margin,
            'absolute_difference_inr':abs(total-args.target_margin),
            'difference_pct_of_target':100.0*abs(total-args.target_margin)/args.target_margin,
            'span_inr':float(final['span']),
            'exposure_inr':float(final['exposure']),
            'option_premium_inr':float(final['option_premium']),
            'total_components_reference':{k:final.get(k) for k in ['span','exposure','option_premium','additional']},
        })
    rows.sort(key=lambda x:x['absolute_difference_inr'])
    out={'target_margin_inr':args.target_margin,'date':args.date,'position':POSITION,'versions':rows,'closest_file':rows[0]['file'] if rows else None}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2,default=str),encoding='utf-8')
    print(json.dumps(out,indent=2,default=str))

if __name__=='__main__':
    main()
