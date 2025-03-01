import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis
import glob
import re

import warnings
warnings.filterwarnings('ignore')

def rutes(batery = 1): 
    cycles_path = glob.glob(path_origin + f'\Cell{batery}\*')
    dictionay_values = {x: int(re.findall(r'\d+',x.split('\\')[-1])[0] ) for x in cycles_path}
    final_rute = list(dict(sorted(dictionay_values.items(), key=lambda item: item[1])).keys())
    return dictionay_values, final_rute
def archives_(archive_num = 0, batery = 1): return glob.glob(rutes(batery)[1][archive_num]+ "\*.csv")
def csv_selector(csvv = 0, batery = 1): 
    values = [archives_(archive_num = x, batery = batery)[csvv] for x in range(len(rutes(batery = batery)[1]))  ]
    return [pd.read_csv(x, sep = ',') for x in values]

def plotting_results(names,  validation, test, x = [0, 1]):
    X_axis = np.arange(len(names))
    fig1, ax1 = plt.subplots(figsize = (27, 8))
    plt.bar(X_axis - 0.1, validation, 0.2, color = palette[0], label = 'Charge')
    plt.bar(X_axis + 0.1, test, 0.2, color = palette[5], label = 'Discharge')
    plt.ylim(x[0], x[1]), plt.xticks(fontsize=16), plt.yticks(fontsize=16), plt.grid(linestyle='--',linewidth=1.5, alpha = 0.5);
    plt.xlabel('Cells', fontdict=font), plt.ylabel('Charge values', fontdict=font),  plt.title(f'Porcentual difference from the first and last charge value', fontdict=font);
    for p in ax1.patches: plt.annotate(format(p.get_height(), '.2f'), (p.get_x() + p.get_width() / 2, p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points', fontsize=15)
    plt.legend(loc='upper right', fontsize=18, bbox_to_anchor=(1.12,1), borderaxespad=0);
    plt.show()

path_origin = "../02_data/original_data/"
palette = ['#264653','#2A9D8F','#85CAC2','#DFF6F4' ,'#E9C46A','#F4A261','#E76F51','#C53D1B', '#7E2711']
cells = [f'\Cell{x}\*' for x in range(1, 9)]
font = {'size': 16, 'color': 'black', 'weight': 'bold'}

elements  = os.listdir(path_origin)
for r in elements:
    
    path = path_origin + f'/{r}'
    dirs = sorted(os.listdir(path), key=lambda x: float(x[3:]))
    
    for i in dirs:
        path2 = path+'/'+i
        archives = [archive for archive in os.listdir(path2) if 'V' not in archive]
        cyc_discharge = pd.read_csv(path2 + f'/{archives[0]}')
        cyc_charge = pd.read_csv(path2 + f'/{archives[1]}')
        if i == 'cyc0': 
            initial_capacity = cyc_discharge.q.values[-1]

        SoH = (cyc_discharge.q.values[-1]/initial_capacity)*100
        cyc_discharge['SoH'], cyc_charge['SoH'] = SoH, SoH
        cyc_discharge['SoC'], cyc_charge['SoC'] = (cyc_discharge.q/cyc_discharge.q.values[-1])*100, (cyc_charge.q/cyc_charge.q.values[-1])*100

        cyc_discharge.to_csv(path_or_buf=path2+f'/{archives[0]}',index= False)
        cyc_charge.to_csv(path_or_buf=path2+f'/{archives[1]}',index= False)

charge_every_cell, discharge_every_cell = [csv_selector(csvv = 0, batery = i) for i in range(1,9)], [csv_selector(csvv = 1, batery = i) for i in range(1,9)]

cyc0ch, cyc0dc = charge_every_cell[0][0], discharge_every_cell[0][0]
cyc8200ch, cyc8200dc = charge_every_cell[0][-1], discharge_every_cell[0][-1]

plt.plot(cyc0ch.q, cyc0ch.v, label='Charge cyc0', color=palette[0], linewidth=3)
plt.plot(cyc0dc.q, cyc0dc.v, label='Discharge cyc0', color=palette[1], linewidth=3)
plt.plot(cyc8200ch.q, cyc8200ch.v, label='Charge cyc8200', color=palette[5], linewidth=3)
plt.plot(cyc8200dc.q, cyc8200dc.v, label='Discharge cyc8200', color=palette[6], linewidth=3)
plt.legend(), plt.xticks(fontsize=16), plt.yticks(fontsize=16), plt.grid(linestyle='--',linewidth=1.5, alpha = 0.5);
plt.xlabel('Capacity (mAh)', fontsize=16), plt.ylabel('Voltage (v)', fontsize=16), plt.title('Charge and discharge curves in cicle 0 vs cicle 8200', fontsize=16, fontweight='bold');

print(f'The time of charge in cicle 0 is {cyc0ch.t.values[-1]-cyc0ch.t.values[0]} seconds.')
print(f'The time of discharge in cicle 0 is {cyc0dc.t.values[-1]-cyc0dc.t.values[0]} seconds.')
print(f'The time of charge in cicle 8200 is {cyc8200ch.t.values[-1]-cyc8200ch.t.values[0]} seconds.')
print(f'The time of discharge in cicle 8200 is {cyc8200dc.t.values[-1]-cyc8200dc.t.values[0]} seconds.')

plt.plot(cyc0ch.t, cyc0ch.SoC, label='Charge cyc0', color=palette[0], linewidth=3)
plt.plot(cyc0dc.t, cyc0dc.SoC, label='Discharge cyc0', color=palette[1], linewidth=3)
plt.legend(), plt.xticks(fontsize=16), plt.yticks(fontsize=16), plt.grid(linestyle='--',linewidth=1.5, alpha = 0.5);
plt.xlabel('Time (s)', fontsize=16), plt.ylabel('SoC (%)', fontsize=16), plt.title('Relation between time and SoC', fontsize=16, fontweight='bold');

def begin_end_percent_difference(variable = 'q', types = 0):
    list_empty = []
    if types == 0: dff = charge_every_cell
    else: dff = discharge_every_cell
    for x in dff: 
        q_mean_list = [i[variable].mean() for i in x]
        list_empty += [q_mean_list[-1]/q_mean_list[0]]
    return list_empty

def begin_end_percent_without_difference(variable = 'q', types = 0):
    list_empty = []
    if types == 0: dff = charge_every_cell
    else: dff = discharge_every_cell
    for x in dff: list_empty += [x[-1][variable][len(x[-1])-1]/x[0][variable][len(x[0])-1]]
    return list_empty

q_charge_differences, q_discarge_differences = begin_end_percent_without_difference('q',0), begin_end_percent_without_difference('q',1)
plotting_results(cells, q_charge_differences, q_discarge_differences, [0.5, 0.9])

modified_palette = palette.copy()
modified_palette.pop(3)

def plotting_time_difference(dff = charge_every_cell, title = 'Charge', legend_num = 1):
    for k, i in enumerate(dff):
        time_diference_charge = [x.t[len(x)-1] - x.t[0] for x in i]
        cycle_value = sorted(list(rutes(batery = k+1)[0].values()))
        plt.plot(cycle_value, time_diference_charge, label=f"{title} cell {k+1}", linewidth=2, color=modified_palette[k])
    plt.xticks(fontsize=16), plt.yticks(fontsize=16), plt.grid(linestyle='--',linewidth=1.5);
    plt.xlabel('Cycle', fontsize = 16), plt.ylabel('Tine difference', fontsize = 16),  plt.title(f'Time difference between the first and last value by cycle', fontdict=font);
    plt.legend(fontsize=10);


#Preprocessing
df_full = pd.DataFrame(columns=['cell','cycle','type','t','v','q','T','SoH'])

for r in elements:
    
    path = path_origin + f'/{r}'
    dirs = sorted(os.listdir(path), key=lambda x: float(x[3:]))
    
    for i in dirs:
        df_partial = pd.DataFrame(columns=['cell','cycle','type','t','v','q','T','SoH'])
        path2 = path+'/'+i
        archives = [archive for archive in os.listdir(path2) if 'V' not in archive]
        cyc_discharge = pd.read_csv(path2 + f'/{archives[0]}')
        cyc_charge = pd.read_csv(path2 + f'/{archives[1]}')
        types, types_str = [cyc_discharge,cyc_charge], ['dc','ch']
        
        for j in range(len(types)):
            df_partial['t'], df_partial['v'], df_partial['q'], df_partial['T'], df_partial['SoH'] = types[j]['t'], types[j]['v'], types[j]['q'], types[j]['T'], types[j]['SoH']
            df_partial['cell'], df_partial['cycle'], df_partial['type'] = r[4:], i[3:], types_str[j]
            df_full = df_full.append(df_partial, ignore_index=True)

df_desc = pd.pivot_table(df_full, values=['t','v','q','T','SoH'], index=['cell','cycle','type'], aggfunc={'t':['max','min'], 'v':['max','min','mean','std', skew, kurtosis],
                                                               'q':['max','min','mean','std', skew, kurtosis],'T':['max','min','mean','std', skew, kurtosis],'SoH':'max'})

df_desc.columns = [i[0]+'_'+i[1] for i in df_desc.columns]
df_desc['t_total'] = df_desc['t_max'] - df_desc['t_min']
df_desc.drop(columns=['t_max','t_min'], inplace=True)

df_desc_final = pd.DataFrame(columns = ['cell','cycle'] + [col + '_ch' for col in list(df_desc.columns)] + [col + '_dc' for col in list(df_desc.columns)])
for ind in range(len(df_desc.index)):
    if ind % 2 == 0:
        values = list(df_desc.loc[df_desc.index[ind],:]) + list(df_desc.loc[df_desc.index[ind+1],:])
        df_desc_final.loc[ind//2,:] = [df_desc.index[ind][0],df_desc.index[ind][1]] + values
        
df_desc_final = df_desc_final.apply(pd.to_numeric, errors='coerce')
df_desc_final.sort_values(by=['cell','cycle'], inplace=True)
df_desc_final.set_index(['cell','cycle'], inplace=True)
df_desc_final.head()

eol, percentage_diff = dict(), dict()
for bateria in df_desc_final.index.get_level_values(0).unique().tolist():
    df_part = df_desc_final.loc[bateria,:]
    for ciclo in range(len(df_part)):
        if df_part.iloc[ciclo, 0] < 80:
            eol[bateria] = df_part.index.to_list()[ciclo]
            percentage_diff[bateria] = df_part.iloc[ciclo, 0]
            break

df_desc_final['RUL'] = df_desc_final.index.get_level_values(0).astype(int).map(eol)
df_desc_final['RUL'] = df_desc_final['RUL'] - df_desc_final.index.get_level_values(1).astype(int)

fig = plt.figure(figsize=(8, 5))

for x in range(1, 9):
    cycles, values = df_desc_final[df_desc_final.index.get_level_values(0) == x]['SoH_max_ch'].index.get_level_values(1).tolist(), df_desc_final[df_desc_final.index.get_level_values(0) == x]['SoH_max_ch'].values
    plt.plot(cycles, values, label=f"Cell {x}", linewidth=2, color=modified_palette[x-1])
plt.xticks(fontsize=16, family = 'serif'), plt.yticks(fontsize=16, family = 'serif'), plt.grid(linestyle='--',linewidth=1.5);
plt.xlabel('Cycle', fontsize = 16, family = 'serif'), plt.ylabel('SoH', fontsize = 16, family = 'serif'),  plt.title(f'SoH evolution', fontdict=font, family = 'serif'), plt.legend(fontsize=10);
plt.ylim(50, 100);
plt.axhspan(70, 50, facecolor='#f50400', alpha=0.3), plt.axhspan(80, 70, facecolor='#f4b41a', alpha=0.4), \
                                                                   plt.axhspan(100, 80, facecolor='#68da3e', alpha=0.4);

for text in plt.gca().get_legend().get_texts():
    plt.setp(text, family='serif')
    
    
df_desc_final.to_pickle('../02_data/processed_data/df_desc_final.pkl')