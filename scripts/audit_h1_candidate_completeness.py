#!/usr/bin/env python3
from __future__ import annotations

import argparse, json
from pathlib import Path
import pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument('--audit',required=True)
ap.add_argument('--selected',required=True)
ap.add_argument('--surface',required=True)
ap.add_argument('--out',required=True)
a=ap.parse_args()

audit=pd.read_parquet(a.audit)
sel=pd.read_parquet(a.selected)
surface=pd.read_parquet(a.surface)
required_a={'near_expiry','timestamp','candidate_count','positive_count','decision'}
required_s={'near_expiry','entry_timestamp'}
required_surface={'near_expiry','timestamp','shift_points','near_call','near_put','far_call','far_put'}
missing_a=required_a-set(audit.columns)
missing_s=required_s-set(sel.columns)
missing_surface=required_surface-set(surface.columns)
if missing_a or missing_s or missing_surface:
    raise SystemExit(f'Missing columns audit={sorted(missing_a)} selected={sorted(missing_s)} surface={sorted(missing_surface)}')

audit['near_expiry']=audit['near_expiry'].astype(str)
audit['timestamp']=pd.to_datetime(audit['timestamp'],errors='coerce')
sel['near_expiry']=sel['near_expiry'].astype(str)
sel['entry_timestamp']=pd.to_datetime(sel['entry_timestamp'],errors='coerce')
audit_keys=['near_expiry','timestamp']
selected_keys=['near_expiry','entry_timestamp']
decision=sel[selected_keys].drop_duplicates().rename(columns={'entry_timestamp':'timestamp'})
joined=decision.merge(audit[audit_keys+['candidate_count','positive_count','decision']],on=audit_keys,how='left')
if joined['candidate_count'].isna().any():
    raise SystemExit('Selected timestamps could not be matched to scan audit.')
incomplete_selected=joined[joined['candidate_count']!=17].copy()
positive_incomplete=audit[(audit['positive_count']>0)&(audit['candidate_count']!=17)].copy()
summary={
    'selected_trades':int(len(joined)),
    'selected_timestamps_with_exactly_17':int((joined['candidate_count']==17).sum()),
    'selected_timestamps_with_less_than_17':int((joined['candidate_count']<17).sum()),
    'selected_timestamps_with_more_than_17':int((joined['candidate_count']>17).sum()),
    'all_selected_timestamps_have_17':bool((joined['candidate_count']==17).all()),
    'positive_scan_timestamps':int((audit['positive_count']>0).sum()),
    'positive_scan_timestamps_with_less_than_17':int(len(positive_incomplete)),
    'max_candidate_count':int(audit['candidate_count'].max()),
    'min_candidate_count_positive_timestamps':int(positive_incomplete['candidate_count'].min()) if not positive_incomplete.empty else None,
}
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
(out/'h1_17_strike_completeness.json').write_text(json.dumps(summary,indent=2))
joined.to_csv(out/'h1_selected_timestamp_completeness.csv',index=False)
positive_incomplete.to_csv(out/'h1_positive_incomplete_scan_timestamps.csv',index=False)
print(json.dumps(summary,indent=2))
if not summary['all_selected_timestamps_pass_strict_completeness']:
    raise SystemExit('FAIL: at least one authoritative H1 selected timestamp failed unique-17-strike completeness or had conflicting duplicate quotes.')
