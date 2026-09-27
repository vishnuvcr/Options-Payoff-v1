#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input-dir',required=True)
    p.add_argument('--out-selected',required=True)
    p.add_argument('--out-audit',required=True)
    p.add_argument('--out-surface',required=True)
    args=p.parse_args()

    root=Path(args.input_dir)
    selected_files=sorted(root.glob('*/intraday_selected_near_exit.parquet'))
    audit_files=sorted(root.glob('*/intraday_scan_audit.parquet'))
    surface_files=sorted(root.glob('*/intraday_decision_surface.parquet'))
    if not selected_files or not audit_files or not surface_files:
        raise RuntimeError('Missing one or more yearly intraday artifacts')

    selected=pd.concat([pd.read_parquet(f) for f in selected_files],ignore_index=True)
    audit=pd.concat([pd.read_parquet(f) for f in audit_files],ignore_index=True)
    surface=pd.concat([pd.read_parquet(f) for f in surface_files],ignore_index=True)

    selected['entry_timestamp']=pd.to_datetime(selected['entry_timestamp'],errors='coerce')
    audit['timestamp']=pd.to_datetime(audit['timestamp'],errors='coerce')
    surface['timestamp']=pd.to_datetime(surface['timestamp'],errors='coerce')

    # A near-expiry weekly cycle may straddle a calendar year. Keep exactly
    # the earliest selected timestamp for each near expiry after combining chunks.
    selected=selected.sort_values('entry_timestamp').drop_duplicates(subset=['near_expiry'],keep='first').reset_index(drop=True)
    selected=selected.sort_values('entry_timestamp').reset_index(drop=True)

    Path(args.out_selected).parent.mkdir(parents=True,exist_ok=True)
    selected.to_parquet(args.out_selected,index=False)
    audit.to_parquet(args.out_audit,index=False)
    surface.to_parquet(args.out_surface,index=False)

    meta={
        'selected_rows_before_cycle_dedup': int(sum(len(pd.read_parquet(f)) for f in selected_files)),
        'selected_rows_after_cycle_dedup': int(len(selected)),
        'weekly_cycles': int(selected['near_expiry'].nunique()),
        'audit_rows': int(len(audit)),
        'decision_surface_rows': int(len(surface)),
        'earliest_selection_per_near_expiry_enforced': True,
    }
    Path(args.out_selected).with_suffix('.metadata.json').write_text(json.dumps(meta,indent=2,default=str),encoding='utf-8')
    print(json.dumps(meta,indent=2,default=str))

if __name__=='__main__':
    main()
