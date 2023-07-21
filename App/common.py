from dataclasses import dataclass
import os, sys
import json
import pickle
import pandas as pd; 
import math
pd.options.mode.chained_assignment = None
pd.set_option("display.precision", 2)
import ipywidgets as widgets
from IPython.display import display, HTML
from ipywidgets import AppLayout, Button, Text, Select, Tab, Layout, VBox, HBox, Label, HTML, interact, interact_manual, interactive, IntSlider, Output
import dmyplant2 as dmp2
from pprint import pprint as pp

try:
    dmp2.cred()
    mp = dmp2.MyPlant(0)
    #mp._fetch_installed_base(); # refresh local installed fleet database
except Exception as err:
    print(str(err))
    sys.exit(1)

def _dfigures(e = None):
    def fake_cyl(dataItem):
        return [dataItem[:-1] + '01']
    func_cyl = fake_cyl if e is None else e.dataItemsCyl

    func_power = 5000 if e is None else math.ceil(e['Power_PowerNominal'] / 1000.0) * 1000.0 * 1.2
    
    f_figure = os.getcwd() + '/App/figures.json'
    figures = dmp2.load_json(f_figure)
    #print(f"{f_figure}, existiert ? {os.path.exists(f_figure)}")
    #pp(figures['exhaust'][-1])
    lfigures = figures.copy()
    for key in lfigures.keys():
        for i,r in enumerate(lfigures[key]):
            if 'ylim' in r:
                if r['ylim'] == "$func_power$":
                    #print(key)
                    #print(r)
                    figures[key][i]['ylim'] = [0,func_power]
            for j , dataitem in enumerate(r['col']):
                if 'func_cyl|' in dataitem:
                    #print(f"in {key}, row {i}, dataitem {j}, {dataitem} => func_cyl('{dataitem[len('func_cyl|'):]}')")
                    #print(func_cyl(f"{dataitem[len('func_cyl|'):]}"))
                    lcol = figures[key][i]['col'].copy()
                    rlcol = func_cyl(f"{dataitem[len('func_cyl|'):]}")
                    #print(rlcol)
                    #remove the "symbol"
                    lcol.remove(dataitem)
                    for item in rlcol[::-1]:
                        lcol.insert(j, item)
                    figures[key][i]['col'] = lcol

    #pp(figures['exhaust'][-1])
    return figures

# DEFINITION OF PLOTS & OVERVIEW
def dfigures(e = None):
    def fake_cyl(dataItem):
        return [dataItem[:-1] + '01']
    func_cyl = fake_cyl if e is None else e.dataItemsCyl
    def fake_power():
        return 5000
    func_power = fake_power if e is None else math.ceil(e['Power_PowerNominal'] / 1000.0) * 1000.0 * 1.2
    return {
        'actuators' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['Ignition_ITPAvg'],'ylim': [-10, 30], 'color':'rgba(255,0,255,0.4)', 'unit':'°KW'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['Aux_PreChambDifPress'],'_ylim': [0, 3], 'color':'purple', 'unit':'-'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['Various_Values_PressBoost'],'_ylim': [0, 3], 'color':'dodgerblue', 'unit':'bar'},
        {'col':['Various_Values_TempMixture'],'ylim': [0, 200], 'color':'orange', 'unit':'°C'},
        {'col':['Aux_RoomTemp'],'ylim': [-50, 100], 'color':'hotpink', 'unit':'°C'},
        {'col':['Various_Values_PosThrottle','Various_Values_PosTurboBypass'],'ylim': [-10, 110], 'color':['rgba(105,105,105,0.6)','rgba(165,42,42,0.4)'], 'unit':'%'},
        ],
        'tecjet' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['bmep'], 'ylim':(-10,40), 'color':'orange', 'unit':'bar'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['Ignition_ITPAvg'],'ylim': [-10, 30], 'color':'limegreen', 'unit':'°KW'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['TecJet_GasPress1'],'_ylim': [0, 3], 'color':'rgba(255,0,0,0.4)', 'unit':'mbar'},
        {'col':['TecJet_GasTemp1'],'_ylim': [0, 3], 'color':'rgba(255,0,255,0.4)', 'unit':'°C'},
        {'col':['TecJet_GasDiffPress'],'_ylim': [0, 3], 'color':'olive', 'unit':'mbar'},
        {'col':['TecJet_ValvePos1'],'ylim': [0, 200], 'color':'purple', 'unit':'%'},
        ],
        'various' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Hyd_OilCount_Trend_OilConsumption','RMD_ListBuffMAvgOilConsume_OilConsumption'],'ylim': [0, 1], 'color':['orange','rgba(255, 224, 130,0.8)'], 'unit':'g/kWh'},
        {'col':['Aux_RoomTemp'],'ylim': [-50, 100], 'color':'hotpink', 'unit':'°C'},
        {'col':['CMU_rDPr_Ch_AirFilt','CMU_rDPr_BbFilt'],'ylim': [-50, 50], 'color':['blue','dodgerblue'], 'unit':'mbar'},
        {'col':['Aux_rPr_Baro'],'ylim': [900, 1100], 'color':'gray', 'unit': 'mbar'},
        ],
        'hydraulics' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['Hyd_PressCrankCase'],'ylim': [-100, 100], 'color':'orange', 'unit':'mbar'},
        {'col':['Hyd_PressOilDif'],'ylim': [0, 3], 'color':'black', 'unit': 'bar'},
        {'col':['Hyd_PressOil'],'ylim': [0, 10], 'color':'brown', 'unit': 'bar'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['Hyd_TempOil','Hyd_TempCoolWat','Hyd_TempWatRetPreEng','Hyd_TempWatRet'],'ylim': [0, 110], 'color':['#2171b5','orangered','hotpink','darkred'], 'unit':'°C'},
        {'col':['Hyd_PressCoolWat'],'ylim': [0, 10], 'color':'dodgerblue', 'unit': 'bar'},
        ],
        'ctr_10' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['Hyd_TempWatRetPreEng','Hyd_TempWatRet'],'ylim': [0, 110], 'color':['hotpink','darkred'], 'unit':'°C'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['CtrModule_Ctr10_X','CtrModule_Ctr10_W'],'ylim': [0, 110], 'color':['indianred','crimson'], 'unit':'°C'},
        {'col':['CtrModule_Ctr10_Y'],'ylim': [0, 110], 'color':'midnightblue', 'unit':'%'},
        {'col':['CtrModule_Ctr10_Error'],'ylim': [-100, 100], 'color':'darkmagenta', 'unit':'%'},
        ],
        'ctr_14' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['Hyd_TempWatRetPreEng','Hyd_TempWatRet'],'ylim': [0, 110], 'color':['hotpink','darkred'], 'unit':'°C'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['CtrModule_Ctr14_X','CtrModule_Ctr14_W'],'ylim': [0, 110], 'color':['brown','lightpink'], 'unit':'°C'},
        {'col':['CtrModule_Ctr14_Y'],'ylim': [0, 110], 'color':'gray', 'unit':'%'},
        {'col':['CtrModule_Ctr14_Error'],'ylim': [-100, 100], 'color':'darkmagenta', 'unit':'%'},
        ],
        'exh_detail' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':func_cyl('Exhaust_TempCyl*')+['Exhaust_TempCylMax','Exhaust_TempCylMin'],'ylim': [300, 700], 'unit':'°C'},
        ],
        'exhaust' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['Exhaust_TempHexIn'], 'ylim': [0,700], 'color': 'purple', 'unit':'°C'},
        {'col':func_cyl('Exhaust_TempCyl*')+['Exhaust_TempCylMax','Exhaust_TempCylMin'],'ylim': [0, 700], 'unit':'°C'},
        ],
        'valvenoise' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':['Exhaust_TempHexIn'], 'ylim': [0,700], 'color': 'purple', 'unit':'°C'},
        {'col':func_cyl('Knock_Valve_Noise_Cyl*'),'ylim': [0, 12000], 'unit':'mV'},
        ],
        'knocking' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':func_cyl('Knock_KLS98_Knock_Cyl*'),'ylim': [0, 1000], 'unit':'mv'},
        {'col':func_cyl('Knock_KLS98_IntKnock_Cyl*'),'ylim': [-80, 10], 'unit':'%'},
        ],
        'ignition1' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':func_cyl('Monic_VoltCyl*'),'ylim': [0, 100], 'unit':'kV'},
        ],
        'ignition2' : [
        {'col':['Power_SetPower','Power_PowerAct'], 'ylim':(0,func_power), 'color':['lightblue','red'], 'unit':'kW'},
        {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
        {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
        {'col':func_cyl('Ignition_ITPCyl*'),'ylim': [0, 40], 'unit':'°KW'},
        ],   
    }

def overview_figure():
    return {
        'basic': [
        {'col':['cumstarttime'],'_ylim':(-600,800), 'color':'darkblue', 'unit':'sec' },
        {'col':['runout'],'_ylim':(0,100) , 'unit':'sec' },
        {'col':['targetload'],'_ylim':(-4000,26000) , 'unit':'kW' },
        {'col':['ramprate'],'_ylim':(-5,7), 'unit':'-' },
        {'col':['loadramp'],'_ylim':(-150,900), 'color':'red', 'unit':'sec' },
        {'col':['speedup'],'_ylim':(-100,200), 'color':'orange', 'unit':'sec' },
        {'col':['synchronize'],'_ylim':(-20,400), 'unit':'sec' },
        {'col':['oilfilling'],'_ylim':(-1000,800), 'unit':'sec' },
        {'col':['degasing'],'_ylim':(-1000,800), 'unit':'sec' },
        {'col':['W','A','isuccess'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,128,0,0.2)'] , 'unit':'-' },
        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.1)'] , 'unit':'-' },
        #{'col':['W','A','no'],'ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,0,0,0.1)'] }
        ],
        'basic2': [
        {'col':['targetload','maxload'],'ylim':(-4000,26000), 'unit':'kW' },
        {'col':['idle'],'ylim':(-100,1000), 'color':'dodgerblue', 'unit':'sec' },
        {'col':['PCDifPress_min'],'ylim':(-3500,500), 'color':'red', 'unit':'mbar' },
        {'col':['PressBoost_max'],'ylim':(0,10), 'color':'blue', 'unit':'bar' },
        {'col':['CrankCasePressure'],'ylim': (-100, 100), 'color':'orange', 'unit':'mbar'},
        {'col':['W','A','isuccess'],'ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,128,0,0.2)'] , 'unit':'-' },
        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.1)'] , 'unit':'-' },
        #{'col':['W','A','no'],'ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,0,0,0.1)'] }
        ],        
    }

#with open('/opt/notebooks/assets/Misterious_mist.gif', 'rb') as f:
with open('./assets/Misterious_mist.gif', 'rb') as f:
    img = f.read()    
loading_bar = widgets.Image(
    value=img
)

qfn = './engines.pkl'
query_list_fn = './query_list.json'

def init_query_list():
    return ['Forsa Hartmoor','BMW Landshut']

def get_query_list_pkl():
    if os.path.exists(qfn):
        with open(qfn, 'rb') as handle:
            query_list = pickle.load(handle)
    else:  
        query_list = init_query_list()
    return query_list

def get_query_list():
    if os.path.exists(query_list_fn):
        query_list=dmp2.load_json(query_list_fn)
    else:  
        query_list = init_query_list()
    return query_list

def save_query_list(query_list):
    query_list = [q for q in query_list if not q in ['312','316','320','412','416','420','424','612','616','620','624','920']]
    dmp2.save_json(query_list_fn,query_list)    


global V

@dataclass
class V:
    hh = '350px' # window height
    dfigsize = (18,8)
    dfigsize_big = (20,8)
    fleet = None
    e = None
    lfigures = None
    plotdef, vset = ([],[])
    fsm = None
    rdf = pd.DataFrame([])
    selected = None
    selected_number = None
    modes_value = ['MAN','AUTO']
    succ_value = ['undefined','success','failed']
    alarm_warning_value = ['-']
    query_list = []

def init_globals():
    V.e = None
    V.lfigures = dfigures()
    V.plotdef, V.vset = dmp2.cplotdef(mp, V.lfigures)
    V.fsm = None
    V.rdf = pd.DataFrame([])
    V.query_list = get_query_list()

# el = Text(
#     value='-', description='selected:', disabled=True, 
#     layout=Layout(width='603px'))

init_globals()
tabs_out = widgets.Output()
tabs_html = widgets.HTML(
    value='',
    Layout=widgets.Layout(
        overflow='scroll',
        border ='1px solid black',
        width  ='auto',
        height ='auto',
        flex_flow = "column wrap",
        align_items = "flex-start",
        display='flex')
)

def status(tbname ,text=''):
    with tabs_out:
        tabs_out.clear_output()
        print(f'{tbname}{" - " if text != "" else ""}{text}')

def disp_alwr(row, key):
    rec = row[key]
    style = '''<style>
        table, 
        td, 
        th {
            border: 0px solid grey;
            border-collapse: collapse;
            padding: 0px; 
            margin: 0px;
            font-size:0.7rem;
            line-height: 18px;
            min-width: 110px;
        }
    </style>'''
    ll = []
    for m in rec:
        ll.append({
            'sno': row['no'],
            'datetime':pd.to_datetime(int(m['msg']['timestamp'])*1e6).strftime('%Y-%m-%d %H:%M:%S'),
            'state': m['state'],
            'number': m['msg']['name'],
            'type': 'Alarm' if m['msg']['severity'] == 800 else 'Warning',
            'severity': m['msg']['severity'],
            'message': m['msg']['message']
        })
    if len(rec) > 0:
        display(HTML(style + pd.DataFrame(ll).to_html(index=False, header=False)))

def display_fmt(df):
    display(df[['starttime'] + V.fsm.results['run2_content']['startstop']]                    
                        .style
                        .set_table_styles([
                            {'selector':'table,td,th', 'props': 'font-size: 0.7rem; '}
                        ])
                        .hide()
                        .format(
                    precision=2,
                    na_rep='-',
                    formatter={
                        'starttime': "{:%Y-%m-%d %H:%M:%S %z}",
                        'startpreparation': "{:.0f}",                        
                        'starter': "{:.1f}",
                        'speedup': "{:.1f}",
                        'idle': "{:.1f}",
                        'synchronize': "{:.1f}",
                        'loadramp': "{:.0f}",
                        'cumstarttime': "{:.0f}",
                        'targetload': "{:.0f}",
                        'ramprate':"{:.2f}",
                        'maxload': "{:.0f}",
                        'targetoperation': "{:.0f}",
                        'rampdown': "{:.1f}",
                        'coolrun': "{:.1f}",
                        'runout': lambda x: f"{x:0.1f}"
                    }
                ))