#!/usr/bin/env python3
from __future__ import annotations

import argparse, io, json, math, random
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests
from scipy.stats import spearmanr

try:
    import yfinance as yf
except Exception:
    yf = None

try:
    from nseindiapy import NiftyIndicesClient
except Exception:
    NiftyIndicesClient = None

TRADE_CSV_NAME = 'intraday_selected_trades.csv'

def wilson(wins, n, z=1.959963984540054):
    if n == 0: return (float('nan'), float('nan'))
    p = wins/n; den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,ctr-half), min(1,ctr+half)

def metric(df):
    vals=df['net_pnl_inr'].astype(float).to_numpy() if len(df) else np.array([])
    if len(vals)==0:
        return {'trades':0,'net_pnl_inr':0.0,'mean_net_pnl_inr':None,'median_net_pnl_inr':None,'win_rate_pct':None,'profit_factor':None,'max_drawdown_inr':0.0}
    wins=vals[vals>0]; losses=vals[vals<0]
    eq=np.cumsum(vals); peak=np.maximum.accumulate(np.maximum(eq,0)); dd=np.maximum(peak-eq,0)
    gp=wins.sum(); gl=-losses.sum()
    return {'trades':int(len(vals)),'net_pnl_inr':float(vals.sum()),'mean_net_pnl_inr':float(vals.mean()),'median_net_pnl_inr':float(np.median(vals)),'win_rate_pct':float(100*len(wins)/len(vals)),'profit_factor':float(gp/gl) if gl else float('inf'),'max_drawdown_inr':float(dd.max())}

def bootstrap_mean(vals, block=0, reps=5000, seed=20260927):
    vals=np.asarray(vals,dtype=float); n=len(vals); rng=random.Random(seed)
    if n==0: return [float('nan'),float('nan')]
    means=[]
    if block<=1:
        for _ in range(reps): means.append(float(np.mean([vals[rng.randrange(n)] for _ in range(n)])))
    else:
        blocks=int(math.ceil(n/block))
        for _ in range(reps):
            sample=[]
            for _ in range(blocks):
                s=rng.randrange(n)
                for j in range(block):
                    sample.append(vals[(s+j)%n])
                    if len(sample)==n: break
                if len(sample)==n: break
            means.append(float(np.mean(sample)))
    means.sort(); lo=means[int(0.025*reps)]; hi=means[int(0.975*reps)-1]
    return [lo,hi]

def fetch_yf(symbol, start, end):
    if yf is None: return pd.DataFrame()
    try:
        x=yf.download(symbol,start=start,end=end,auto_adjust=False,progress=False,threads=False)
        if x is None or x.empty: return pd.DataFrame()
        x=x.reset_index()
        flat=[]
        for col in x.columns:
            if isinstance(col, tuple):
                names=[str(v).strip() for v in col if str(v).strip() and str(v).strip().lower()!='nan']
                if any(n in {'Open','High','Low','Close','Adj Close','Volume'} for n in names):
                    flat.append(next(n for n in names if n in {'Open','High','Low','Close','Adj Close','Volume'}))
                elif 'Date' in names or 'Datetime' in names:
                    flat.append(next(n for n in names if n in {'Date','Datetime'}))
                else:
                    flat.append(names[0] if names else '')
            else:
                flat.append(str(col))
        x.columns=flat
        datecol='Date' if 'Date' in x.columns else ('Datetime' if 'Datetime' in x.columns else None)
        if datecol is None: return pd.DataFrame()
        x['date']=pd.to_datetime(x[datecol]).dt.date
        ren={c:c.lower().replace(' ','_') for c in x.columns}
        out=x.rename(columns=ren)
        keep=[c for c in ['date','open','high','low','close','volume'] if c in out.columns]
        if 'close' not in out.columns: return pd.DataFrame()
        return out[keep].copy()
    except Exception:
        return pd.DataFrame()

def fetch_nse():
    if NiftyIndicesClient is None: return pd.DataFrame(), pd.DataFrame(), 'unavailable'
    try:
        client=NiftyIndicesClient()
        idx=client.historical.price_history('NIFTY 50',pd.Timestamp('2020-12-20').date(),pd.Timestamp('2026-09-27').date()).to_pandas()
        vix=client.historical.vix_history(pd.Timestamp('2020-12-20').date(),pd.Timestamp('2026-09-27').date()).to_pandas()
        def norm(x):
            x=x.copy(); x.columns=[str(c).strip().lower().replace(' ','_') for c in x.columns]
            datecol=next((c for c in x.columns if c in ['date','index_date','trading_date']),None)
            if datecol is None: datecol=x.columns[0]
            x['date']=pd.to_datetime(x[datecol]).dt.date
            ren={}
            for c in x.columns:
                if 'open'==c or c.endswith('_open'): ren[c]='open'
                if 'close'==c or c.endswith('_close'): ren[c]='close'
            return x.rename(columns=ren)
        return norm(idx), norm(vix), 'nseindiapy'
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), 'unavailable'

def read_fii_dii_xlsx(url):
    try:
        b=requests.get(url,timeout=60).content; book=pd.ExcelFile(io.BytesIO(b))
        for sheet in book.sheet_names:
            raw=pd.read_excel(io.BytesIO(b),sheet_name=sheet,header=None)
            hit=None
            for i,row in raw.iterrows():
                txt=' '.join(str(v).upper() for v in row.tolist())
                if 'FII' in txt and 'DII' in txt and 'NET' in txt: hit=i; break
            if hit is None: continue
            df=pd.read_excel(io.BytesIO(b),sheet_name=sheet,header=hit)
            df.columns=[' '.join(str(c).split()).strip() for c in df.columns]
            datecol=next((c for c in df.columns if 'DATE' in c.upper()),None)
            if datecol is None: continue
            fcol=next((c for c in df.columns if 'FII' in c.upper() and 'NET' in c.upper()),None)
            dcol=next((c for c in df.columns if 'DII' in c.upper() and 'NET' in c.upper()),None)
            if fcol is None or dcol is None: continue
            out=pd.DataFrame({'date':pd.to_datetime(df[datecol],errors='coerce').dt.date,'fii_net':pd.to_numeric(df[fcol],errors='coerce'),'dii_net':pd.to_numeric(df[dcol],errors='coerce')})
            out=out.dropna(subset=['date']).drop_duplicates('date',keep='last')
            if len(out): return out,'Hareeshkesavan'
    except Exception:
        pass
    return pd.DataFrame(), 'unavailable'

def fetch_fii_json(dates):
    rows=[]
    for d in dates:
        url=f'https://raw.githubusercontent.com/chirag127/fii-dii-activity-api/main/data/{d.isoformat()}.json'
        try:
            r=requests.get(url,timeout=15); r.raise_for_status(); j=r.json(); e=j.get('equity',{})
            rows.append({'date':d,'fii_net':e.get('fii_net'),'dii_net':e.get('dii_net'),'source':j.get('source','unknown')})
        except Exception:
            continue
    return pd.DataFrame(rows)

def prior_merge(trades, ctx, prefix):
    ctx=ctx.copy(); ctx['date']=pd.to_datetime(ctx['date'])
    t=trades.copy(); t['entry_date']=pd.to_datetime(t['entry_date'])
    t=t.sort_values('entry_date'); ctx=ctx.sort_values('date')
    out=pd.merge_asof(t,ctx,left_on='entry_date',right_on='date',direction='backward',allow_exact_matches=False,suffixes=('','_ctx'))
    ren={c:f'{prefix}_{c}' for c in ctx.columns if c!='date' and c in out.columns}
    return out.rename(columns=ren)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--trades',required=True); ap.add_argument('--out-dir',required=True); ap.add_argument('--seed',type=int,default=20260927); args=ap.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    trades=pd.read_csv(args.trades)
    if len(trades)!=169: raise SystemExit(f'Expected 169 complete trades, got {len(trades)}')
    trades['entry_date']=pd.to_datetime(trades['entry_date']).dt.date
    start=min(trades.entry_date).isoformat(); end=(pd.Timestamp(max(trades.entry_date))+pd.Timedelta(days=2)).date().isoformat()

    nse_idx,nse_vix,nse_source=fetch_nse()
    if nse_idx.empty: nse_idx=fetch_yf('^NSEI','2021-01-01',end); nse_source='yfinance fallback' if not nse_idx.empty else 'unavailable'
    if nse_vix.empty: nse_vix=fetch_yf('^INDIAVIX','2021-01-01',end); vix_source='yfinance fallback' if not nse_vix.empty else 'unavailable'
    else: vix_source=nse_source
    nifty=nse_idx.copy(); nifty['date']=pd.to_datetime(nifty['date']).dt.date
    if {'open','close'}.issubset(nifty.columns):
        nifty['nifty_prev_close']=nifty['close'].shift(1); nifty['nifty_open_gap']=nifty['open']/nifty['nifty_prev_close']-1
        nifty['nifty_prev_ret']=nifty['close'].pct_change()
    vix=nse_vix.copy(); vix['date']=pd.to_datetime(vix['date']).dt.date
    if 'close' in vix.columns: vix['india_vix_prev']=vix['close'].shift(1)

    symbols={'sp500':'^GSPC','nasdaq':'^IXIC','nikkei':'^N225','hangseng':'^HSI','shanghai':'000001.SS','gold':'GC=F','usdinr':'USDINR=X','global_vix':'^VIX'}
    global_frames={k:fetch_yf(sym,'2020-12-01',end) for k,sym in symbols.items()}
    global_ctx=None
    for name,df in global_frames.items():
        if df.empty: continue
        q=df[['date','close']].copy(); q['ret_1d']=q['close'].pct_change(); q=q.rename(columns={'close':f'{name}_close','ret_1d':f'{name}_ret'})
        global_ctx=q if global_ctx is None else global_ctx.merge(q,on='date',how='outer')
    if global_ctx is None: global_ctx=pd.DataFrame({'date':[]})

    fii_url='https://raw.githubusercontent.com/Hareeshkesavan/Stock-Market-Dataset/main/FII%20and%20DII.xlsx'
    fii,dsrc=read_fii_dii_xlsx(fii_url)
    json_fii=fetch_fii_json(sorted(set(trades.entry_date)))
    if not json_fii.empty:
        if fii.empty: fii=json_fii[['date','fii_net','dii_net']].copy()
        else:
            fii=fii.copy(); fii['date']=pd.to_datetime(fii['date']).dt.date
            m=json_fii.set_index('date'); fii=fii.set_index('date'); fii.update(m[['fii_net','dii_net']]); fii=fii.reset_index()
    if isinstance(fii,pd.DataFrame) and not fii.empty: fii['date']=pd.to_datetime(fii['date']).dt.date

    joined=trades.copy()
    joined=prior_merge(joined,nifty,'nifty') if not nifty.empty else joined
    joined=prior_merge(joined,vix[['date','india_vix_prev']] if 'india_vix_prev' in vix.columns else vix,'vix') if not vix.empty else joined
    joined=prior_merge(joined,global_ctx,'global') if not global_ctx.empty else joined
    if not fii.empty: joined=prior_merge(joined,fii,'fii_dii')

    # Same-day opening gap is known by 09:20, and remains known for later entries.
    if not nifty.empty and {'open','close'}.issubset(nifty.columns):
        op=nifty[['date','open','close']].copy(); op['date']=pd.to_datetime(op['date']); op['prev_close']=op['close'].shift(1); op['nifty_same_day_open_gap']=op['open']/op['prev_close']-1; op=op.drop(columns=['open','close','prev_close'])
        joined=joined.merge(op,left_on='entry_date',right_on='date',how='left').drop(columns=['date'],errors='ignore')

    # Predeclared descriptive regimes.
    def qbin(s):
        s=pd.to_numeric(s,errors='coerce'); ok=s.dropna()
        if len(ok)<8: return pd.Series([np.nan]*len(s),index=s.index)
        qs=ok.quantile([.25,.5,.75]).to_list(); return pd.cut(s,[-np.inf,*qs,np.inf],labels=['Q1','Q2','Q3','Q4'])
    if 'vix_india_vix_prev' in joined: joined['india_vix_regime']=qbin(joined['vix_india_vix_prev'])
    if 'nifty_same_day_open_gap' in joined: joined['nifty_gap_regime']=np.select([joined.nifty_same_day_open_gap < -0.002, joined.nifty_same_day_open_gap > 0.002],['negative','positive'],default='flat')
    if 'fii_dii_fii_net' in joined: joined['fii_regime']=np.where(joined.fii_dii_fii_net>=0,'FII_net_buy','FII_net_sell')
    if 'fii_dii_dii_net' in joined: joined['dii_regime']=np.where(joined.fii_dii_dii_net>=0,'DII_net_buy','DII_net_sell')
    if {'global_sp500_ret','global_nasdaq_ret'}.issubset(joined.columns): joined['global_risk_regime']=np.where((joined.global_sp500_ret>=0)&(joined.global_nasdaq_ret>=0),'risk_on',np.where((joined.global_sp500_ret<0)&(joined.global_nasdaq_ret<0),'risk_off','mixed'))

    joined.to_csv(out/'context_joined.csv',index=False)

    regime_cols=[c for c in ['india_vix_regime','nifty_gap_regime','fii_regime','dii_regime','global_risk_regime'] if c in joined.columns]
    reg=[]
    for c in regime_cols:
        for label,g in joined.groupby(c,dropna=False):
            m=metric(g); lo,hi=wilson(int((g.net_pnl_inr.astype(float)>0).sum()),len(g)); bi=bootstrap_mean(g.net_pnl_inr.astype(float).to_numpy(),0,5000,args.seed); bb=bootstrap_mean(g.net_pnl_inr.astype(float).to_numpy(),4,5000,args.seed+1)
            reg.append({'variable':c,'regime':str(label),'trades':m['trades'],'net_pnl_inr':m['net_pnl_inr'],'mean_net_pnl_inr':m['mean_net_pnl_inr'],'win_rate_pct':m['win_rate_pct'],'win_rate_wilson_low_pct':100*lo,'win_rate_wilson_high_pct':100*hi,'profit_factor':m['profit_factor'],'max_drawdown_inr':m['max_drawdown_inr'],'iid_mean_ci_low':bi[0],'iid_mean_ci_high':bi[1],'block4_mean_ci_low':bb[0],'block4_mean_ci_high':bb[1]})
    pd.DataFrame(reg).to_csv(out/'regime_summary.csv',index=False)

    corr=[]
    numeric=[c for c in joined.columns if any(k in c for k in ['india_vix_prev','nifty_same_day_open_gap','nifty_nifty_open_gap','nifty_nifty_prev_ret','global_','fii_dii_'])]
    for c in numeric:
        x=pd.to_numeric(joined[c],errors='coerce'); y=pd.to_numeric(joined.net_pnl_inr,errors='coerce'); mask=x.notna()&y.notna()
        if mask.sum()<10: continue
        rho,p=spearmanr(x[mask],y[mask]); corr.append({'variable':c,'n':int(mask.sum()),'spearman_rho':float(rho),'p_value':float(p)})
    if corr:
        cd=pd.DataFrame(corr).sort_values('p_value'); m=len(cd); cd['bh_q_value']=[min(1.0,(float(p)*m/(i+1))) for i,p in enumerate(cd.p_value)]; cd.to_csv(out/'continuous_associations.csv',index=False)
    else: pd.DataFrame(columns=['variable','n','spearman_rho','p_value','bh_q_value']).to_csv(out/'continuous_associations.csv',index=False)

    coverage=[]
    for c in joined.columns:
        if c in ['net_pnl_inr','entry_date','entry_timestamp']: continue
        s=joined[c]; coverage.append({'variable':c,'non_missing':int(s.notna().sum()),'coverage_pct':float(100*s.notna().mean())})
    pd.DataFrame(coverage).to_csv(out/'coverage.csv',index=False)

    meta={'phase':'9F','status':'complete','trades':169,'nse_source':nse_source,'vix_source':vix_source,'fii_dii_source':dsrc,'global_sources':'yfinance where available','regime_variables':regime_cols,'note':'Descriptive only; no new trading rule or filter was created. Corporate/news variables were not imputed where reliable point-in-time reconstruction was unavailable.'}
    (out/'summary.json').write_text(json.dumps(meta,indent=2))

    report=[]
    report += ['# Phase 9F — Cross-market and regime audit','',f"Trades joined: **{len(joined)}**",f"NSE context source: **{nse_source}**",f"India VIX source: **{vix_source}**",f"FII/DII source: **{dsrc}**",'','This phase is descriptive only. No regime-based entry filter was adopted.','']
    if regime_cols:
        report += ['## Regime coverage','',pd.DataFrame(reg).to_markdown(index=False) if reg else 'No regime groups had sufficient coverage.','']
    report += ['## Limitations','','Point-in-time quote-level bid/ask data for external markets is not available in the corrected H1 ledger. Corporate-action and news timestamps were not retrospectively imputed. External variables are explanatory context only, not new trading signals.']
    (out/'PHASE9F_AUDIT.md').write_text(chr(10).join(report)+chr(10))

if __name__=='__main__': main()