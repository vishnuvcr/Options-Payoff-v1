#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Iterable

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

DATASET = "thetrademarkk/india-index-options-1m"

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--start', required=True)
    p.add_argument('--end', required=True)
    p.add_argument('--entry-time', default='09:20')
    p.add_argument('--out', default='data/derived/strategy_inputs.parquet')
    return p.parse_args()

def normalize_timestamp(s):
    x = pd.to_datetime(s, utc=True, errors='coerce')
    return x.dt.tz_convert('Asia/Kolkata')

def list_nifty_expiry_files(start, end):
    api = HfApi()
    names = api.list_repo_files(DATASET, repo_type='dataset')
    out = []
    for name in names:
        if not name.startswith('options/NIFTY/') or not name.endswith('.parquet'):
            continue
        try:
            expiry = dt.date.fromisoformat(Path(name).stem)
        except ValueError:
            continue
        if start - dt.timedelta(days=7) <= expiry <= end + dt.timedelta(days=14):
            out.append((expiry, name))
    return sorted(out)

def load_index():
    local = hf_hub_download(repo_id=DATASET, filename='index/NIFTY.parquet', repo_type='dataset')
    df = pd.read_parquet(local)
    df['timestamp'] = normalize_timestamp(df['timestamp'])
    df['trading_date'] = df['timestamp'].dt.date
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    return df.dropna(subset=['timestamp','close']).sort_values('timestamp')

def load_option_file(expiry, filename):
    local = hf_hub_download(repo_id=DATASET, filename=filename, repo_type='dataset')
    df = pd.read_parquet(local)
    df['timestamp'] = normalize_timestamp(df['timestamp'])
    df['strike'] = pd.to_numeric(df['strike'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['option_type'] = df['option_type'].astype(str).str.upper()
    df = df[df['option_type'].isin(['CE','PE'])].dropna(subset=['timestamp','strike','close']).copy()
    df['contract_expiry'] = expiry
    return df

def exact_bar(df, entry_ts, strike, option_type):
    x = df[(df['timestamp'] == entry_ts) & (df['strike'] == strike) & (df['option_type'] == option_type)]
    return None if x.empty else float(x.iloc[0]['close'])

def common_strikes(near, nxt, entry_ts):
    def strikes(df):
        x = df[(df['timestamp'] == entry_ts) & (df['option_type'].isin(['CE','PE']))]
        both = x.groupby('strike')['option_type'].nunique()
        return set(both[both >= 2].index.tolist())
    return strikes(near).intersection(strikes(nxt))

def settlement_map(index_df):
    last = index_df.sort_values('timestamp').groupby('trading_date', as_index=False).tail(1)
    return {row.trading_date: float(row['close']) for _, row in last.iterrows()}

def expiry_pair(entry_date, expiries):
    xs = [x for x in expiries if x >= entry_date]
    if len(xs) < 2:
        return None
    near, nxt = xs[0], xs[1]
    if (nxt - near).days > 10:
        return None
    return near, nxt

def main():
    args = parse_args()
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    if start > end:
        raise ValueError('start must be <= end')
    hour, minute = [int(x) for x in args.entry_time.split(':')]
    index_df = load_index()
    entry_df = index_df[(index_df['trading_date'] >= start) & (index_df['trading_date'] <= end) & (index_df['timestamp'].dt.hour == hour) & (index_df['timestamp'].dt.minute == minute)].copy()
    if entry_df.empty:
        raise RuntimeError('No index observations at the requested entry time')
    expiry_files = list_nifty_expiry_files(start, end)
    if len(expiry_files) < 2:
        raise RuntimeError('Fewer than two NIFTY expiry files available')
    expiry_dates = [x[0] for x in expiry_files]
    filename_by_expiry = dict(expiry_files)
    settle = settlement_map(index_df)
    cache = {}
    def get_option(expiry):
        if expiry not in cache:
            cache[expiry] = load_option_file(expiry, filename_by_expiry[expiry])
        if len(cache) > 3:
            for old in sorted(cache)[:-3]:
                del cache[old]
        return cache[expiry]
    rows = []
    for entry in entry_df.sort_values('timestamp').itertuples(index=False):
        entry_ts = entry.timestamp
        entry_date = entry.trading_date
        pair = expiry_pair(entry_date, expiry_dates)
        if pair is None:
            continue
        near_expiry, next_expiry = pair
        near = get_option(near_expiry)
        nxt = get_option(next_expiry)
        common = common_strikes(near, nxt, entry_ts)
        if not common:
            continue
        spot = float(entry.close)
        atm = min(common, key=lambda k: abs(k - spot))
        for label, shift in [('ATM',0.0),('ATM_MINUS_400',-400.0),('ATM_PLUS_400',400.0)]:
            strike = atm + shift
            if strike not in common:
                rows.append({'entry_timestamp':entry_ts,'entry_date':entry_date,'spot_at_entry':spot,'near_expiry':near_expiry,'next_expiry':next_expiry,'candidate_label':label,'strike':strike,'status':'candidate_strike_unavailable'})
                continue
            vals = [exact_bar(near,entry_ts,strike,'CE'), exact_bar(near,entry_ts,strike,'PE'), exact_bar(nxt,entry_ts,strike,'CE'), exact_bar(nxt,entry_ts,strike,'PE')]
            near_call, near_put, next_call, next_put = vals
            missing = any(x is None for x in vals)
            near_settle = settle.get(near_expiry)
            next_settle = settle.get(next_expiry)
            status = 'ok'
            if missing:
                status = 'missing_option_bar'
            elif near_settle is None or next_settle is None:
                status = 'missing_settlement'
            net_entry_cashflow = None if missing else near_call - near_put - next_call + next_put
            rows.append({'entry_timestamp':entry_ts,'entry_date':entry_date,'spot_at_entry':spot,'near_expiry':near_expiry,'next_expiry':next_expiry,'candidate_label':label,'strike':strike,'near_call_close':near_call,'near_put_close':near_put,'next_call_close':next_call,'next_put_close':next_put,'near_settlement':near_settle,'next_settlement':next_settle,'net_entry_cashflow_per_unit':net_entry_cashflow,'execution_fidelity':'09:20 close proxy; bid/ask unavailable','lot_size':None,'status':status})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows)
    if result.empty:
        raise RuntimeError('No strategy input rows were generated')
    result.to_parquet(out,index=False)
    metadata = {'dataset':DATASET,'start':args.start,'end':args.end,'entry_time_ist':args.entry_time,'rows':len(result),'status_counts':result['status'].value_counts(dropna=False).to_dict(),'execution_fidelity':'close-only proxy','lot_size':'not inferred; Phase 3 requires a verified dated NSE lot-size calendar'}
    out.with_suffix('.metadata.json').write_text(json.dumps(metadata,indent=2,default=str),encoding='utf-8')
    print(json.dumps(metadata,indent=2,default=str))

if __name__ == '__main__':
    main()