#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

ORDER=["same_timestamp_any_candidate","second_valid_timestamp","delay_15m","delay_30m","delay_60m","delay_120m","best_later_frozen_selector","best_later_any_candidate"]
def main():
    p=argparse.ArgumentParser(); p.add_argument('--input-dir',required=True); p.add_argument('--out-dir',required=True); a=p.parse_args()
    root=Path(a.input_dir)
    lf=sorted(root.rglob('loss_trade_entry_detail.csv'))
    vf=sorted(root.rglob('entry_variant_trade_rows.csv'))
    if not lf or not vf: raise SystemExit('No Phase 9H loss artifacts found')
    losses=pd.concat([pd.read_csv(x) for x in lf],ignore_index=True)
    variants=pd.concat([pd.read_csv(x) for x in vf],ignore_index=True)
    variants=variants.dropna(subset=['net_pnl_inr']).copy()
    rows=[]
    for v,g in variants.groupby('variant'):
        if v=='first_positive': continue
        rows.append({
            'variant':v,'loss_cycles':len(g),'rescued_to_positive':int(g.rescues_loss.sum()),
            'rescue_rate_pct':float(g.rescues_loss.mean()*100),
            'sum_variant_pnl_inr':float(g.net_pnl_inr.sum()),
            'sum_baseline_loss_pnl_inr':float(g.baseline_net_pnl_inr.sum()),
            'mean_delta_inr':float((g.net_pnl_inr-g.baseline_net_pnl_inr).mean()),
            'median_delta_inr':float((g.net_pnl_inr-g.baseline_net_pnl_inr).median()),
        })
    summary=pd.DataFrame(rows)
    summary['order']=summary.variant.map({v:i for i,v in enumerate(ORDER)}).fillna(999)
    summary=summary.sort_values(['order','variant']).drop(columns='order')
    losses=losses.sort_values(['entry_date','entry_timestamp']).reset_index(drop=True)
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    losses.to_csv(out/'loss_trade_entry_detail.csv',index=False)
    variants.to_csv(out/'entry_variant_trade_rows.csv',index=False)
    summary.to_csv(out/'loss_entry_rescue_summary.csv',index=False)
    out.joinpath('PHASE9H_LOSS_ENTRY_RESULTS.md').write_text(
        '# Phase 9H — Loss-trade entry analysis\n\n'
        f'Analyzed {len(losses)} realized H1 loss cycles from the frozen Phase 9G rule.\n\n'
        'The tests are loss-level diagnostics only: same-timestamp strike substitution, next valid timestamp, '
        'fixed 15/30/60/120-minute delays, unchanged-selector later entry, and an ex-post later-entry/strike upper bound. '
        'No exit rule was changed. No ex-post variant is a deployable strategy.\n\n'
        '## Rescue summary\n\n'+summary.to_markdown(index=False)+'\n\n'
        '## Interpretation\n\n'
        'A rescue means the same historical trade becomes positive under the stated entry counterfactual. '
        'This does not establish that the counterfactual is predictable ex ante. Any rule suggested by these diagnostics '
        'requires a separate full-sample prospective test and an untouched holdout before adoption.\n',
        encoding='utf-8')
    out.joinpath('summary.json').write_text(json.dumps({
        'phase':'9H','loss_cycles':int(len(losses)),
        'variants_tested':ORDER,
        'rescue_summary':summary.to_dict(orient='records')
    },indent=2))

if __name__=='__main__': main()
