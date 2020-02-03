# 2020-01-31
# get availability of generators for all hours by fuel type and by zone
# wind and solar are based on forecasts
# the rest of the fuel types are based on capability
import os
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

matplotlib.style.use('ggplot')

def read_and_consolidate_data():
    try:
        print('trying to load pickles...')
        df_capabilities = pd.read_pickle('capabilities.pkl')
        df_forecasts = pd.read_pickle('forecasts.pkl')
        df_outputs = pd.read_pickle('outputs.pkl')
        print('pickles loaded!')
    except FileNotFoundError:
        lst_capabilities = [] # max output - derates and outages
        lst_forecasts = [] # variable generation forecasts
        lst_outputs = [] # Pgen
        print('reading Excel files...')
        xlsx = pd.ExcelFile('GOC-2019-Jan-April.xlsx')
        lst_capabilities.append(pd.read_excel(xlsx, 'Capability'))
        lst_forecasts.append(pd.read_excel(xlsx, 'Forecasts'))
        lst_outputs.append(pd.read_excel(xlsx, 'Output'))

        print('reading 2nd file...')
        xlsx = pd.ExcelFile('GOC-2018.xlsx')
        lst_capabilities.append(pd.read_excel(xlsx, 'Available Capacities'))
        lst_forecasts.append(pd.read_excel(xlsx, 'Capabilities'))
        lst_outputs.append(pd.read_excel(xlsx, 'Output'))

        print('reading 3rd file...')
        xlsx = pd.ExcelFile('GOC-2017.xlsx')
        lst_capabilities.append(pd.read_excel(xlsx, 'Avail Capability'))
        lst_forecasts.append(pd.read_excel(xlsx, 'Capability'))
        lst_outputs.append(pd.read_excel(xlsx, 'Output'))

        print('reading 4th file...')
        xlsx = pd.ExcelFile('GOC-2016.xlsx')
        lst_capabilities.append(pd.read_excel(xlsx, 'Available Capacities'))
        lst_forecasts.append(pd.read_excel(xlsx, 'Capabilities'))
        lst_outputs.append(pd.read_excel(xlsx, 'Output'))

        print('reading 5th file...')
        xlsx = pd.ExcelFile('GOC-2015.xlsx')
        lst_capabilities.append(pd.read_excel(xlsx, 'Available Capacities'))
        lst_forecasts.append(pd.read_excel(xlsx, 'Capability'))
        lst_outputs.append(pd.read_excel(xlsx, 'Output'))
        print('done reading Excel files')

        df_capabilities = pd.concat(lst_capabilities, ignore_index=True)
        df_forecasts = pd.concat(lst_forecasts, ignore_index=True)
        df_outputs = pd.concat(lst_outputs, ignore_index=True)

        df_capabilities.index = (pd.to_datetime(df_capabilities['Date']) + 
            (df_capabilities['Hour'] - 1).apply(lambda x: np.timedelta64(x, 'h')))
        df_forecasts.index = (pd.to_datetime(df_forecasts['Date']) + 
            (df_forecasts['Hour'] - 1).apply(lambda x: np.timedelta64(x, 'h')))
        df_outputs.index = (pd.to_datetime(df_outputs['Date']) + 
            (df_outputs['Hour'] - 1).apply(lambda x: np.timedelta64(x, 'h')))
        
        df_capabilities.sort_index(inplace=True)
        df_forecasts.sort_index(inplace=True)
        df_outputs.sort_index(inplace=True)

        df_capabilities.to_pickle('capabilities.pkl')
        df_forecasts.to_pickle('forecasts.pkl')
        df_outputs.to_pickle('outputs.pkl')

    df_map = pd.read_csv('gen_to_zone_and_fuel_type.csv', index_col='Plant')
    df_map['Fuel+Zone'] = ['+'.join(x) for x in 
                    zip(df_map['Fuel'].map(str), df_map['Zone'].map(str))]
    VGs = list(df_map[df_map['Fuel'].isin(['Wind', 'Solar'])].index)
    non_VGs = list(df_map[~df_map['Fuel'].isin(['Wind', 'Solar'])].index)

    df_availabilities = df_capabilities.loc[:, ['Date', 'Hour'] + non_VGs]
    df_availabilities[VGs] = df_forecasts.loc[:, VGs]
    #df_availabilities.to_csv('availabilities.csv')
    
    df_avail_groups = df_availabilities.loc[:, ['Date', 'Hour']]
    for group in df_map.groupby('Fuel+Zone'):
        name, df = group
        # print(name, df.index.values)
        # print(df_availabilities.loc[:, df.index.values].sum(axis=1))
        df_avail_groups[name] = df_availabilities.loc[:, df.index.values].sum(axis=1)
        # df_avail_groups[name] = df_availabilities.loc[:, df.index.values]
    df_avail_groups.to_csv('availabilities_by_fuel_and_zone.csv')

    df_avail_groups_fuel = df_availabilities.loc[:, ['Date', 'Hour']]
    for group in df_map.groupby('Fuel'):
        name, df = group
        df_avail_groups_fuel[name] = df_availabilities.loc[:, df.index.values].sum(axis=1)
    df_avail_groups_fuel.to_csv('availabilities_by_fuel.csv')

    df_avail_groups_zone = df_availabilities.loc[:, ['Date', 'Hour']]
    for group in df_map.groupby('Zone'):
        name, df = group
        # print(name, df.index.values)
        # print(df_availabilities.loc[:, df.index.values].sum(axis=1))
        df_avail_groups_zone[name] = df_availabilities.loc[:, df.index.values].sum(axis=1)
        # df_avail_groups[name] = df_availabilities.loc[:, df.index.values]
    df_avail_groups_zone.to_csv('availabilities_by_zone.csv')

    print(df_avail_groups_fuel)
    fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8)) = plt.subplots(2, 4)
    ax1.hist(df_avail_groups_fuel['Bio Fuel'], bins=50, label='Bio Fuel')
    ax2.hist(df_avail_groups_fuel['Gas'], bins=50, label='Gas')
    ax3.hist(df_avail_groups_fuel['Oil'], bins=50, label='Oil')
    ax4.hist(df_avail_groups_fuel['Solar'], bins=50, label='Solar')
    ax5.hist(df_avail_groups_fuel['Steam'], bins=50, label='Steam')
    ax6.hist(df_avail_groups_fuel['Uranium'], bins=50, label='Uranium')
    ax7.hist(df_avail_groups_fuel['Water'], bins=50, label='Water')
    ax8.hist(df_avail_groups_fuel['Wind'], bins=50, label='Wind')
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()
    ax5.legend()
    ax6.legend()
    ax7.legend()
    ax8.legend()
    df_avail_groups_fuel[['Bio Fuel', 'Gas', 'Oil', 'Solar', 'Steam', 'Uranium', 'Water', 'Wind']].plot()
    df = df_avail_groups_fuel[['Bio Fuel', 'Gas', 'Oil', 'Solar', 'Steam', 'Uranium', 'Water', 'Wind']].sum(axis=1)
    print(df)
    print(df.mean())
    fig2, f2ax1 = plt.subplots(1, 1)
    f2ax1.hist(df, bins=200)
    plt.show()


    # #print(list(df_map.groupby('Fuel'))[0])
    # plant = 'PINEPORTAGE' # 'ZURICH' PINEPORTAGE
    # # plt.plot(df_capabilities[plant])
    # # plt.plot(df_forecasts[plant])
    # # plt.plot(df_outputs[plant])
    # plt.plot(df_availabilities[plant])
    # plt.show()
    
    # df_capabilities.plot('ZURICH')
    # plt.show()
    # print(df_forecasts)
    # print(df_outputs)


    # create availabilities from capabilities for all non-VG, and forecasts from VG
    
    
    # print(lst_capabilities[0])
    # print(xlsx.sheet_names)

    
def main():
    read_and_consolidate_data()

if __name__ == '__main__':
    main()


# df_capabilities['temp'] = df_capabilities.index.values
# df_capabilities = df_capabilities[df_capabilities.temp.notnull()]
# df_capabilities.drop(['temp'], axis=1, inplace=True)