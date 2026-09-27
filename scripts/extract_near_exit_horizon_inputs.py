#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

DATASET = 'thetrademarkk/india-index-options-1m'

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--start', required=True)
    p.add_argument('--end', required=True)
    p.add_argument('--entry-time', default='09:20')
    p.add_argument('--out', default='data/derived/strategy_inputs_near_exit.parquet')
    p.add_argument('--download-workers', type=int, default=6)
    p.add_argument('--horizon-steps', type=int, default=1)
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
        if start - dt.timedelta(days=7) <= expiry <= end + dt.timedelta(days=30):
            out.append((expiry, name))
    return sorted(out)

def nifty_lot_size(expiry):
    if expiry < dt.date(2021, 8, 1):
        return 75
    if expiry < dt.date(2024, 5, 2):
        return 50
    if expiry < dt.date(2024, 11, 21):
        return 25
    if expiry < dt.date(2026, 1, 6):
        return 75
    return 65

def load_index():
    local = hf_hub_download(repo_id=DATASET, filename='index/NIFTY.parquet', repo_type='dataset')
    df = pd.read_parquet(local)
    df['timestamp'] = normalize_timestamp(df['timestamp'])
    df['trading_date'] = df['timestamp'].dt.date
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    return df.dropna(subset=['timestamp','close']).sort_values('timestamp')

def load_option_file(expiry, filename, timestamp_min=None, timestamp_max=None):
    local = hf_hub_download(repo_id=DATASET, filename=filename, repo_type='dataset')
    columns = ['timestamp', 'strike', 'close', 'option_type']
    filters = None
    if timestamp_min is not None and timestamp_max is not None:
        filters = [('timestamp', '>=', timestamp_min), ('timestamp', '<=', timestamp_max)]
    try:
        df = pd.read_parquet(local, columns=columns, filters=filters)
    except Exception:
        df = pd.read_parquet(local, columns=columns)
    df['timestamp'] = normalize_timestamp(df['timestamp'])
    df['trading_date'] = df['timestamp'].dt.date
    df['strike'] = pd.to_numeric(df['strike'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['option_type'] = df['option_type'].astype(str).str.upper()
    df = df[df['option_type'].isin(['CE','PE'])].dropna(subset=['timestamp','strike','close']).copy()
    df['contract_expiry'] = expiry
    return df

def exact_bar(df, ts, strike, option_type):
    x = df[(df['timestamp'] == ts) & (df['strike'] == strike) & (df['option_type'] == option_type)]
    return None if x.empty else float(x.iloc[0]['close'])

def last_bar_on_or_before(df, exit_ts, strike, option_type):
    x = df[
        (df['trading_date'] == exit_ts.date())
        & (df['timestamp'] <= exit_ts)
        & (df['strike'] == strike)
        & (df['option_type'] == option_type)
    ].sort_values('timestamp')
    if x.empty:
        return None, None
    row = x.iloc[-1]
    return float(row['close']), row['timestamp']

def build_entry_lookup(df):
    out = defaultdict(dict)
    for row in df.itertuples(index=False):
        out[row.timestamp].setdefault(float(row.strike), {})[row.option_type] = float(row.close)
    return dict(out)

def build_expiry_exit_lookup(df, exit_ts):
    if exit_ts is None:
        return {}
    out = {}
    x = df[(df['trading_date'] == exit_ts.date()) & (df['timestamp'] <= exit_ts)]
    for row in x.sort_values('timestamp').itertuples(index=False):
        out[(float(row.strike), row.option_type)] = (float(row.close), row.timestamp)
    return out

def common_from_lookup(near_lookup, far_lookup, entry_ts):
    a = near_lookup.get(entry_ts, {})
    b = far_lookup.get(entry_ts, {})
    out = []
    for strike in set(a).intersection(b):
        if {'CE', 'PE'}.issubset(a[strike]) and {'CE', 'PE'}.issubset(b[strike]):
            out.append(float(strike))
    return set(out)
def common_strikes(near, far, entry_ts):
    def strikes(df):
        x = df[(df['timestamp'] == entry_ts) & (df['option_type'].isin(['CE','PE']))]
        both = x.groupby('strike')['option_type'].nunique()
        return set(both[both >= 2].index.tolist())
    return strikes(near).intersection(strikes(far))

def last_index_bar_on_date(index_df, trading_date):
    x = index_df[index_df['trading_date'] == trading_date].sort_values('timestamp')
    if x.empty:
        return None, None
    row = x.iloc[-1]
    return row['timestamp'], float(row['close'])

def expiry_horizon_pair(entry_date, expiries, horizon_steps):
    if horizon_steps < 1:
        raise ValueError('horizon_steps must be >= 1')
    xs = [x for x in expiries if x >= entry_date]
    if len(xs) <= horizon_steps:
        return None
    near, far = xs[0], xs[horizon_steps]
    if (far - near).days > max(10, 8 * horizon_steps + 4):
        return None
    return near, far

def main():
    args = parse_args()
    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)
    hour, minute = [int(x) for x in args.entry_time.split(':')]
    index_df = load_index()
    entry_df = index_df[
        (index_df['trading_date'] >= start)
        & (index_df['trading_date'] <= end)
        & (index_df['timestamp'].dt.hour == hour)
        & (index_df['timestamp'].dt.minute == minute)
    ].copy()
    expiry_files = list_nifty_expiry_files(start, end)
    expiry_dates = [x[0] for x in expiry_files]
    filename_by_expiry = dict(expiry_files)
    needed_expiries = set()
    for entry in entry_df[['trading_date']].itertuples(index=False):
        pair = expiry_horizon_pair(entry.trading_date, expiry_dates, args.horizon_steps)
        if pair is not None:
            needed_expiries.update(pair)
    needed_expiries = sorted(needed_expiries)

    expiry_entry_times = defaultdict(list)
    expiry_exit_ts = {}
    for entry in entry_df[['timestamp', 'trading_date']].itertuples(index=False):
        pair = expiry_horizon_pair(entry.trading_date, expiry_dates, args.horizon_steps)
        if pair is None:
            continue
        near_expiry, far_expiry = pair
        expiry_entry_times[near_expiry].append(entry.timestamp)
        expiry_entry_times[far_expiry].append(entry.timestamp)
        if near_expiry not in expiry_exit_ts:
            exit_ts, _ = last_index_bar_on_date(index_df, near_expiry)
            expiry_exit_ts[near_expiry] = exit_ts

    option_local_paths = {}

    def download_one(expiry):
        return expiry, hf_hub_download(
            repo_id=DATASET,
            filename=filename_by_expiry[expiry],
            repo_type='dataset',
        )

    max_workers = max(1, min(args.download_workers, 8))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(download_one, expiry) for expiry in needed_expiries]
        for fut in as_completed(futures):
            expiry, local = fut.result()
            option_local_paths[expiry] = local

    prepared = {}

    def get_prepared(expiry):
        if expiry in prepared:
            return prepared[expiry]
        ts_list = expiry_entry_times.get(expiry, [])
        exit_ts = expiry_exit_ts.get(expiry)
        if ts_list:
            tmin = min(ts_list)
            tmax = max([max(ts_list), exit_ts] if exit_ts is not None else ts_list)
        else:
            tmin = tmax = None
        df = load_option_file(
            expiry, filename_by_expiry[expiry], timestamp_min=tmin, timestamp_max=tmax
        )
        entry_lookup = build_entry_lookup(df)
        exit_lookup = build_expiry_exit_lookup(df, exit_ts)
        prepared[expiry] = (entry_lookup, exit_lookup)
        return prepared[expiry]

    rows = []
    for entry in entry_df.sort_values('timestamp').itertuples(index=False):
        entry_ts = entry.timestamp
        entry_date = entry.trading_date
        pair = expiry_horizon_pair(entry_date, expiry_dates, args.horizon_steps)
        if pair is None:
            continue
        near_expiry, far_expiry = pair
        near_lookup, near_exit_lookup = get_prepared(near_expiry)
        far_lookup, far_exit_lookup = get_prepared(far_expiry)
        exit_ts, near_settlement = last_index_bar_on_date(index_df, near_expiry)
        if exit_ts is None:
            continue
        common = common_from_lookup(near_lookup, far_lookup, entry_ts)
        if not common:
            continue
        spot = float(entry.close)
        atm = min(common, key=lambda k: abs(k - spot))
        for shift in range(-400, 401, 50):
            strike = atm + shift
            if strike not in common:
                rows.append({
                    'entry_timestamp': entry_ts, 'entry_date': entry_date, 'spot_at_entry': spot,
                    'near_expiry': near_expiry, 'far_expiry': far_expiry, 'near_exit_timestamp': exit_ts,
                    'near_lot_size': nifty_lot_size(near_expiry), 'far_lot_size': nifty_lot_size(far_expiry),
                    'shift_points': shift, 'strike': strike, 'status': 'candidate_strike_unavailable'
                })
                continue
            nrow = near_lookup.get(entry_ts, {}).get(float(strike), {})
            frow = far_lookup.get(entry_ts, {}).get(float(strike), {})
            near_call = nrow.get('CE')
            near_put = nrow.get('PE')
            far_call = frow.get('CE')
            far_put = frow.get('PE')
            vals = [near_call, near_put, far_call, far_put]
            far_call_exit, far_call_exit_ts = far_exit_lookup.get((float(strike), 'CE'), (None, None))
            far_put_exit, far_put_exit_ts = far_exit_lookup.get((float(strike), 'PE'), (None, None))
            missing = any(x is None for x in vals) or near_settlement is None or far_call_exit is None or far_put_exit is None
            status = 'ok' if not missing else 'missing_near_exit_price'
            rows.append({
                'entry_timestamp': entry_ts, 'entry_date': entry_date, 'spot_at_entry': spot,
                'near_expiry': near_expiry, 'far_expiry': far_expiry, 'near_exit_timestamp': exit_ts,
                'far_call_exit_timestamp': far_call_exit_ts, 'far_put_exit_timestamp': far_put_exit_ts,
                'candidate_label': 'ATM' if shift == 0 else ('ATM_PLUS_%d' % shift if shift > 0 else 'ATM_MINUS_%d' % abs(shift)),
                'shift_points': shift, 'strike': strike,
                'near_call_close': near_call, 'near_put_close': near_put,
                'far_call_close': far_call, 'far_put_close': far_put,
                'near_settlement': near_settlement,
                'far_call_exit_close': far_call_exit, 'far_put_exit_close': far_put_exit,
                'execution_fidelity': '09:20 close proxy; far-leg near-expiry exit uses last available option bar at or before index close',
                'near_lot_size': nifty_lot_size(near_expiry), 'far_lot_size': nifty_lot_size(far_expiry),
                'net_entry_cashflow_per_unit': None if any(x is None for x in vals) else near_call - near_put - far_call + far_put,
                'status': status
            })
        for stale in list(cache):
            if stale not in {near_expiry, far_expiry}:
                del cache[stale]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(rows)
    if result.empty:
        raise RuntimeError('No strategy input rows were generated')
    result.to_parquet(out, index=False)
    meta = {
        'dataset': DATASET, 'start': args.start, 'end': args.end, 'entry_time_ist': args.entry_time,
        'rows': len(result), 'status_counts': result['status'].value_counts(dropna=False).to_dict(),
        'grid_shifts': list(range(-400,401,50)),
        'exit_rule': 'All four legs closed at near weekly expiry; far CE/PE manually closed at last option bar on or before near-expiry index close.'
    }
    out.with_suffix('.metadata.json').write_text(json.dumps(meta, indent=2, default=str), encoding='utf-8')
    print(json.dumps(meta, indent=2, default=str))

if __name__ == '__main__':
    main()
