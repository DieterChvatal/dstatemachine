import pandas as pd
import numpy as np
import arrow
import concurrent.futures

## data handling
def _load_data(fsm, engine=None, p_data=None, ts_from=None, ts_to=None, p_timeCycle=None, p_forceReload=False, p_slot=99, silent=False, p_suffix='', debug = False):
    if ((ts_from is None) or (ts_to is None)):
        return pd.DataFrame([])
    else:
        engine = engine or fsm._e
        if not p_timeCycle:
            p_timeCycle = 30
        ts_from = ts_from or fsm.first_message 
        ts_to = ts_to or fsm.last_message 
        #return engine.hist_data(
        # changed to hist_data2 8.3.2022 - Dieter
        return engine.hist_data2(
            itemIds = engine.get_dataItems(p_data or ['Various_Values_SpeedAct','Power_PowerAct']),
            p_from = arrow.get(ts_from).to('Europe/Vienna'),
            p_to = arrow.get(ts_to).to('Europe/Vienna'),
            timeCycle=p_timeCycle,
            forceReload=p_forceReload,
            slot=p_slot,
            silent=silent,
            suffix=p_suffix,
            debug = debug
        )

def load_data(fsm, cycletime, tts_from=None, tts_to=None, silent=False, p_data=None, p_forceReload=False, p_suffix = '', debug=False):
    if ((tts_from is None) or (tts_to is None)):
        return pd.DataFrame([])
    else:
        return _load_data(
            fsm, p_data=p_data, p_timeCycle=cycletime, ts_from=tts_from, ts_to=tts_to, 
            p_slot=tts_from or 9999, silent=silent, p_forceReload=p_forceReload, p_suffix=p_suffix, debug=debug)

def get_period_data(fsm, ts0, ts1, cycletime=None, p_data=None):
    lts_from = int(ts0)
    lts_to = int(ts1)
    data = fsm.load_data(cycletime, tts_from=lts_from, tts_to=lts_to, p_data=p_data)
    data[(data['time'] >= lts_from) & 
            (data['time'] <= lts_to)]
    return data

def get_ts_data(fsm, tts, left = -300, right = 150, cycletime=None, p_data=None):
    if not cycletime:
        cycletime = 1 # default for get_ts_data
    lts_from = int(tts + left)
    lts_to = int(tts + right)
    return fsm.get_period_data(lts_from, lts_to, cycletime, p_data=p_data)        

###################
def _resample_data(fsm, data, startversuch):
    # bis 15' nach Start 1" samples
    d1 = startversuch['starttime'] + pd.Timedelta(value=15, unit='min')
    # bis 15' vor Ende 1" samples
    d3 = startversuch['endtime'] - pd.Timedelta(value=15, unit='min')
    
    if (d3 - d1) > pd.Timedelta(value=5,unit='min'):
        # dazwischen auf 10' 
        odata1 = data[data.datetime <= d1]
        odata2 = data[(data.datetime >= d1) & (data.datetime <= d3)]
        odata2 = odata2[::10][1:-1]
        odata3 = data[data.datetime >= d3]
    return pd.concat([odata1,odata2,odata3]).reset_index(drop='index')

###################################################################################
# load data in  1 chunk
###################################################################################
# TODO: make it timezone aware
#def get_cycle_data(fsm,startversuch, max_length=None, min_length=None, cycletime=None, silent=False, p_data=None, reduce=True, pre_period=5*60, post_period=21*60, t_range=(0,100), p_refresh=False):
def get_cycle_data(fsm,startversuch, max_length=None, min_length=None, cycletime=None, silent=False, p_data=None, reduce=True, pre_period=65*60, post_period=81*60, t_range=(0,100), p_refresh=False):
    tns = pd.to_datetime((startversuch['starttime'].timestamp() - pre_period + t_range[0]/100.0 * ((startversuch['endtime']  - startversuch['starttime']).seconds + pre_period + post_period)), unit='s')
    tne = pd.to_datetime((startversuch['starttime'].timestamp() - pre_period + t_range[1]/100.0 * ((startversuch['endtime']  - startversuch['starttime']).seconds + pre_period + post_period)), unit='s')
    t0 = tns.timestamp() * 1e3
    t1 = tne.timestamp() * 1e3
    if max_length:
        if (t1 - t0) > max_length * 1e3:
            t1 = int(t0 + max_length * 1e3)
    if min_length:
        if (t1 - t0) < min_length * 1e3:
            t1 = int(t0 + min_length * 1e3)
    data = load_data(fsm, cycletime, tts_from=t0, tts_to=t1, silent=silent, p_data=p_data, p_forceReload=p_refresh)
    #data = fsm._resample_data(data,startversuch) if reduce else data
    data = data[(data['time'] >= t0) & (data['time'] <= t1)]
    return data
#################

def _debug(start, ende, data, dataname):
    def todate(ts):
        return pd.to_datetime(ts * 1000000).strftime('%d.%m.%Y %H:%M:%S')
    print(f"########## debug {dataname } ##########")
    if not data.empty:
        print(f"soll: start={todate(start)} end={todate(ende)}")
        print(f" ist: start={todate(data.iloc[0]['time'])} end={todate(data.iloc[-1]['time'])}")
        print(f"diff: start={(data.iloc[0]['time']-start) // 1000}s end={(ende - data.iloc[-1]['time']) // 1000}s")
    else:
        print(f"soll: start={todate(start)} end={todate(ende)}")
        print(f"=> empty dataset!!!")
    print(f"-----------------------------------------")

###################################################################################
# load data split into 1 sec chunks at start and end, and 30s chunks in the middle
###################################################################################
def _load_reduced_data(fsm, startversuch, ptts_from, ptts_to, pdata=None, p_refresh=False):
    # Hires 1" von 'starttime' bis 15' danach und von 15' vor 'endtime' bis Ende
    # dazwischen alle 30" einen Messwert. 
    data1 = pd.DataFrame([]);data2 = pd.DataFrame([]);data3 = pd.DataFrame([]);
    d1t = int(arrow.get(startversuch['starttime'] + pd.Timedelta(value=15, unit='min')).to('Europe/Vienna').timestamp() * 1000)
    d3t = int(arrow.get(startversuch['endtime'] - pd.Timedelta(value=15, unit='min')).to('Europe/Vienna').timestamp() * 1000)
    d3t = max(d3t, ptts_from); d1t = min(d1t,d3t)
    data1 = load_data(fsm,cycletime=1, tts_from=ptts_from, tts_to=d1t, silent=True, p_data=pdata, p_forceReload=p_refresh)
    if 'time' in data1:
        data1 = data1[(data1['time'] >= ptts_from) & (data1['time'] < d1t)]
    data2 = load_data(fsm, cycletime=30, tts_from=d1t, tts_to=d3t, silent=True, p_data=pdata, p_forceReload=p_refresh)
    if 'time' in data2:
        data2 = data2[(data2['time'] >= d1t) & (data2['time'] < d3t)]
    data3 = load_data(fsm,cycletime=1, tts_from=d3t, tts_to=ptts_to, silent=True, p_data=pdata, p_forceReload=p_refresh)
    if 'time' in data3:
        data3 = data3[(data3['time'] >= d3t) & (data3['time'] <= ptts_to)]
    #_debug(ptts_from,d1t, data1, 'data1')
    #_debug(d1t,d3t, data2, 'data2')
    #_debug(d3t,ptts_to,data3, 'data3')
    return pd.concat([data1,data2,data3]).reset_index(drop='index')

def get_cycle_data2(fsm,startversuch, max_length=None, min_length=None, cycletime=None, silent=False, p_data=None, pre_period=5*60, post_period=21*60, t_range=(0,100), p_refresh=False):
    tns = pd.to_datetime((startversuch['starttime'].timestamp() - pre_period + t_range[0]/100.0 * ((startversuch['endtime']  - startversuch['starttime']).seconds + pre_period + post_period)), unit='s')
    tne = pd.to_datetime((startversuch['starttime'].timestamp() - pre_period + t_range[1]/100.0 * ((startversuch['endtime']  - startversuch['starttime']).seconds + pre_period + post_period)), unit='s')
    t0 = tns.timestamp() * 1e3
    t1 = tne.timestamp() * 1e3
    if max_length:
        if (t1 - t0) > max_length * 1e3:
            t1 = int(t0 + max_length * 1e3)
    if min_length:
        if (t1 - t0) < min_length * 1e3:
            t1 = int(t0 + min_length * 1e3)
    data = _load_reduced_data(fsm, startversuch, t0, t1, pdata=p_data, p_refresh=p_refresh)
    if not data.empty:
        data = data[(data['time'] >= t0) & (data['time'] <= t1)]
    return data

###################################################################################
# load data split into 1 sec chunks at start and end, and 30s chunks in the middle
# use concurrent loading.
###################################################################################
def _load_reduced_data_ccr(fsm, startversuch, ptts_from, ptts_to, pdata=None, p_refresh=False):
    # Hires 1" von 'starttime' bis 15' danach und von 15' vor 'endtime' bis Ende
    # dazwischen alle 30" einen Messwert. 
    d1t = int(arrow.get(startversuch['starttime'] + pd.Timedelta(value=15, unit='min')).to('Europe/Vienna').timestamp() * 1000)
    d3t = int(arrow.get(startversuch['endtime'] - pd.Timedelta(value=15, unit='min')).to('Europe/Vienna').timestamp() * 1000)
    d3t = max(d3t, ptts_from); d1t = min(d1t,d3t)

    data1 = pd.DataFrame([]);data2 = pd.DataFrame([]);data3 = pd.DataFrame([]);
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = []
        future_list.append(executor.submit(load_data,fsm,cycletime=1,  tts_from=ptts_from, tts_to=d1t, silent=True, p_data=pdata, p_forceReload=p_refresh))
        future_list.append(executor.submit(load_data,fsm,cycletime=30, tts_from=d1t, tts_to=d3t, silent=True, p_data=pdata, p_forceReload=p_refresh))
        future_list.append(executor.submit(load_data,fsm,cycletime=1,  tts_from=d3t, tts_to=ptts_to, silent=True, p_data=pdata, p_forceReload=p_refresh))
        concurrent.futures.wait(future_list)
        data1 = future_list[0].result()
        data2 = future_list[1].result()
        data3 = future_list[2].result()

    #_debug(ptts_from,d1t, data1, 'data1')
    #_debug(d1t,d3t, data2, 'data2')
    #_debug(d3t,ptts_to,data3, 'data3')

    if 'time' in data2:
        data2 = data2[(data2['time'] >= d1t) & (data2['time'] < d3t)]
    if 'time' in data1:
        data1 = data1[(data1['time'] >= ptts_from) & (data1['time'] < d1t)]
    if 'time' in data3:
        data3 = data3[(data3['time'] >= d3t) & (data3['time'] <= ptts_to)]

    return pd.concat([data1,data2,data3]).reset_index(drop='index')

def get_cycle_data3(fsm,startversuch, max_length=None, min_length=None, cycletime=None, silent=False, p_data=None, pre_period=5*60, post_period=21*60, t_range=(0,100), p_refresh=False):
    tns = pd.to_datetime((startversuch['starttime'].timestamp() - pre_period + t_range[0]/100.0 * ((startversuch['endtime']  - startversuch['starttime']).seconds + pre_period + post_period)), unit='s')
    tne = pd.to_datetime((startversuch['starttime'].timestamp() - pre_period + t_range[1]/100.0 * ((startversuch['endtime']  - startversuch['starttime']).seconds + pre_period + post_period)), unit='s')
    t0 = tns.timestamp() * 1e3
    t1 = tne.timestamp() * 1e3
    if max_length:
        if (t1 - t0) > max_length * 1e3:
            t1 = int(t0 + max_length * 1e3)
    if min_length:
        if (t1 - t0) < min_length * 1e3:
            t1 = int(t0 + min_length * 1e3)
    data = _load_reduced_data_ccr(fsm, startversuch, t0, t1, pdata=p_data, p_refresh=p_refresh)
    if not data.empty:
        data = data[(data['time'] >= t0) & (data['time'] <= t1)]
    return data
