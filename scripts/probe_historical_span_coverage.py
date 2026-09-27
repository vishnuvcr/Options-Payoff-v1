#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
from pathlib import Path

import pandas as pd
import requests

BASE='https://nsearchives.nseindia.com/archives/nsccl/span'
VARIANTS=('i1','i2','i3','i4','i5','s')
HEADERS={
 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
 'Accept':'application/octet-stream,*/*;q=0.8',
 'Accept-Language':'en-IN,en-US;q=0.9,en;q=0.8',
 'Referer':'https://www.nseindia.com/',
}

def probe(task):
    date,variant=task
    url=f'{BASE}/nsccl.{date}.{variant}.zip'
    try:
        r=requests.get(url,headers=HEADERS,timeout=(4,12),stream=True)
        status=r.status_code
        ctype=str(r.headers.get('Content-Type') or '').lower()
        length=r.headers.get('Content-Length') or r.headers.get('Content-Range')
        r.close()
        return {'date':date,'variant':variant,'status':status,'ok':status==200 and 'text/html' not in ctype,'content_type':ctype,'length':length,'url':url}
    except Exception as e:
        return {'date':date,'variant':variant,'status':None,'ok':False,'content_type':'','length':None,'url':url,'error':f'{type(e).__name__}:{e}'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidates',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    df=pd.read_parquet(args.candidates)
    dates=sorted(pd.to_datetime(df['entry_date']).dt.strftime('%Y%m%d').unique())
    tasks=[(d,v) for d in dates for v in VARIANTS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        rows=list(ex.map(probe,tasks))
    out_rows=[]
    for d in dates:
        x=[r for r in rows if r['date']==d]
        by={r['variant']:r for r in x}
        available=[v for v in VARIANTS if by[v]['ok']]
        preferred=next((v for v in ('i1','i2','i3','i4','i5') if by[v]['ok']),None)
        out_rows.append({
          'entry_date':pd.to_datetime(d).strftime('%Y-%m-%d'),
          'available_variants':','.join(available),
          'preferred_no_lookahead_variant':preferred,
          'settlement_fallback_available':bool(by['s']['ok']),
          'i1_available':bool(by['i1']['ok']),
          'i2_available':bool(by['i2']['ok']),
          's_available':bool(by['s']['ok']),
          'probe_errors':json.dumps({v:by[v].get('error') for v in VARIANTS if by[v].get('error')},sort_keys=True),
        })
    result=pd.DataFrame(out_rows)
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(args.out,index=False)
    summary={
      'dates':len(result),
      'i1_coverage_pct':float(100*result['i1_available'].mean()),
      'i2_coverage_pct':float(100*result['i2_available'].mean()),
      'preferred_no_lookahead_coverage_pct':float(100*result['preferred_no_lookahead_variant'].notna().mean()),
      's_fallback_coverage_pct':float(100*result['s_available'].mean()),
      'dates_with_no_span_variant':int(result['preferred_no_lookahead_variant'].isna().sum()),
    }
    Path(args.out).with_suffix('.summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print(result.to_string(index=False))

if __name__=='__main__':
    main()
