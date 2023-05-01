def figures(e):
    return {
    # 'starts_overview': [
    # {'col':['cumstarttime'],'_ylim':(-400,900), 'color':'darkblue'},
    # {'col':['synchronize'],'_ylim':(-20,300)},
    # {'col':['startpreparation'],'_ylim':(-600,900)},
    # {'col':['hochlauf'],'_ylim':(-100,200), 'color':'orange'},
    # {'col':['loadramp'],'_ylim':(-150,900), 'color':'red'},
    # {'col':['ramprate'],'_ylim':(-3,3)},
    # {'col':['no'],'_ylim':(-100,10000),'color':'black'},
    # {'col':['targetload'],'_ylim':(500,5000) }
    # ],
    'actors' : [
    {'col':['Power_PowerAct'], 'ylim':(0,5000), 'color':'red', 'unit':'kW'},
    {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
    {'col':['Ignition_ITPAvg'],'ylim': [0, 30], 'color':'rgba(255,0,255,0.4)', 'unit':'°KW'},
    {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
    {'col':['Various_Values_PosThrottle','Various_Values_PosTurboBypass'],'ylim': [-10, 110], 'color':['rgba(105,105,105,0.6)','rgba(165,42,42,0.4)'], 'unit':'%'},
    #{'col':['Various_Values_PosThrottle','Various_Values_PosTurboBypass'],'ylim': [-10, 110], 'color':['rgba(255,255,255,0.4)','rgba(165,42,42,0.4)'], 'unit':'%'},
    #{'col':['Hyd_PressCrankCase'],'ylim': [-100, 100], 'color':'orange', 'unit':'mbar'},
    #{'col':['Hyd_PressOilDif'],'ylim': [0, 2], 'color':'black', 'unit': 'bar'},
    #{'col':['Hyd_PressOil'],'ylim': [0, 10], 'color':'brown', 'unit': 'bar'},
    #{'col':['Hyd_TempOil','Hyd_TempCoolWat','Hyd_TempWatRetCoolOut'],'ylim': [0, 110], 'color':['#2171b5','orangered','hotpink'], 'unit':'°C'},
    ],
    'lubrication' : [
    {'col':['Power_PowerAct'], 'ylim':(0,5000), 'color':'red', 'unit':'kW'},
    {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
    #{'col':['Hyd_PressCrankCase'],'ylim': [-100, 100], 'color':'orange', 'unit':'mbar'},
    {'col':['Hyd_PressOilDif'],'ylim': [0, 2], 'color':'black', 'unit': 'bar'},
    {'col':['Hyd_PressOil'],'ylim': [0, 10], 'color':'brown', 'unit': 'bar'},
    {'col':['Hyd_TempOil','Hyd_TempCoolWat','Hyd_TempWatRetCoolOut'],'ylim': [0, 110], 'color':['#2171b5','orangered','hotpink'], 'unit':'°C'},
    ],
    'exhaust' : [
    {'col':['Power_PowerAct'], 'ylim':(0,5000), 'color':'red', 'unit':'kW'},
    {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
    {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
    {'col':e.dataItemsCyl('Exhaust_TempCyl*'),'ylim': [400, 700], 'unit':'°C'},
    {'col':e.dataItemsCyl('Knock_Valve_Noise_Cyl*'),'ylim': [0, 4000], 'unit':'V'},
    ],
    'ignition' : [
    {'col':['Power_PowerAct'], 'ylim':(0,5000), 'color':'red', 'unit':'kW'},
    {'col':['Various_Values_SpeedAct'],'ylim': [0, 2500], 'color':'blue', 'unit':'rpm'},
    {'col':['TecJet_Lambda1'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
    {'col':e.dataItemsCyl('Monic_VoltCyl*'),'ylim': [0, 40], 'unit':'kV'},
    {'col':e.dataItemsCyl('Ignition_ITPCyl*'),'ylim': [10, 50], 'unit':'°KW'},
    ],
}
