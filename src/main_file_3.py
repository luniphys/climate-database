import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.pyplot

import os.path
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parents[1]


def get_all_station_data(db_connector_arg):

    """
    Function loads the data from the database and stores in a pandas df.

    :param db_connector_arg: connection to db
    :type db_connector_arg: sqlite3.connection

    :return: pandas dataframe
    :rtype: df
    """

    sql_query = pd.read_sql_query(f'SELECT * FROM observations', db_connector_arg)
    return pd.DataFrame(sql_query)


def get_station_data(obs_id, db_connector_arg):

    """
    Function loads the data from the database and stores in a pandas df.

    :param obs_id: id of a station
    :type obs_id: int

    :param db_connector_arg: connection to db
    :type db_connector_arg: sqlite3.connection

    :return: pandas dataframe
    :rtype: df
    """

    sql_query = pd.read_sql_query(f'SELECT * FROM observations WHERE obs_station_id={obs_id}', db_connector_arg)
    return pd.DataFrame(sql_query)


def get_stations_information(db_connector_arg):

    """
    Function loads the metadata from the database and stores in a pandas df.

    :param db_connector_arg: connection to db
    :type db_connector_arg: sqlite3.connection

    :return pandas dataframe
    :rtype df
    """

    sql_query = pd.read_sql_query(f'SELECT * FROM stations', db_connector_arg)
    return pd.DataFrame(sql_query)


def process_data(df):

    """
    Function processes the data: splits it up, checks for wrong values and aggregates it.

    :param df: pandas dataframe of the raw data
    :type df: df

    :return df_2022_agg: aggregated pandas dataframe for 2022
    :rtype df_2022_agg: df

    :return df_2022_ref: aggregated pandas dataframe for ref. period
    :rtype df_2022_ref: df
    """

    # convert data string to datetime object and set it as index
    if 'obs_date' in df.columns:
        df.set_index(pd.to_datetime(df.obs_date), inplace=True)
        df.pop('obs_date')

    # substitute wrong values(-999) with NaN
    for var in ["obs_TMK", "obs_TXK", "obs_TNK"]:
        df.loc[df[var] <= -999, var] = np.nan

    # split dataframe, assume that no data is available in 2020 and 2021
    split_date = pd.to_datetime('2019-12-31')
    df_ref_raw = df.loc[df.index <= split_date]
    df_2022_raw = df.loc[df.index > split_date]

    # aggregate monthly
    df_ref_agg = df_ref_raw.groupby(df_ref_raw.index.strftime('%b')).agg('mean').round(1)
    df_2022_agg = df_2022_raw.groupby(df_2022_raw.index.strftime('%b')).agg('mean').round(1)

    # sort df based on months
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    df_ref_agg = df_ref_agg.reindex(months, axis=0)
    df_2022_agg = df_2022_agg.reindex(months, axis=0)

    return df_2022_agg, df_ref_agg


def process_all_data(df, df_meta_data_arg):

    """
    Function processes the data: splits it up, checks for wrong values and aggregates it.

    :param df: pandas dataframe of the all raw data
    :type df: df

    :return df_2022_agg: aggregated pandas dataframe for 2022
    :rtype df_2022_agg: df

    :return df_2022_ref: aggregated pandas dataframe for ref. period
    :rtype df_2022_ref: df

    :param df_meta_data_arg: pandas dataframe witch contains metadata from all stations
    :type df_meta_data_arg: df
    """

    # convert data string to datetime object and set it as index
    if 'obs_date' in df.columns:
        df.set_index(pd.to_datetime(df.obs_date), inplace=True)
        df.pop('obs_date')

    # substitute wrong values(-999) with NaN
    for var in ["obs_TMK", "obs_TXK", "obs_TNK"]:
        df.loc[df[var] <= -999, var] = np.nan

    # split dataframe, assume that no data is available in 2020 and 2021
    split_date = pd.to_datetime('2019-12-31')
    df_ref_raw = df.loc[df.index <= split_date]
    df_2022_raw = df.loc[df.index > split_date]

    # split data, high altitude and low altitude
    # but first get altitude from metadata, only for the stations in our database
    df_meta_our_stations = df_meta_data_arg[df_meta_data_arg.station_id.isin(df_2022_raw.obs_station_id.unique())]
    # get ids of the 5 highest and lowest stations
    high_station_id = df_meta_our_stations.sort_values(by=['station_alt'])[-5:].station_id
    low_station_id = df_meta_our_stations.sort_values(by=['station_alt'])[:5].station_id

    # now split data into high and low values
    df_2022_high = df_2022_raw[df_2022_raw.obs_station_id.isin(high_station_id)]
    df_2022_low = df_2022_raw[df_2022_raw.obs_station_id.isin(low_station_id)]
    df_ref_high = df_ref_raw[df_ref_raw.obs_station_id.isin(high_station_id)]
    df_ref_low = df_ref_raw[df_ref_raw.obs_station_id.isin(low_station_id)]

    # aggregate monthly
    df_ref_high_agg = df_ref_high.groupby(df_ref_high.index.strftime('%b')).agg('mean').round(1)
    df_2022_high_agg = df_2022_high.groupby(df_2022_high.index.strftime('%b')).agg('mean').round(1)
    df_ref_low_agg = df_ref_low.groupby(df_ref_low.index.strftime('%b')).agg('mean').round(1)
    df_2022_low_agg = df_2022_low.groupby(df_2022_low.index.strftime('%b')).agg('mean').round(1)

    # sort df based on months
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    df_ref_high_agg = df_ref_high_agg.reindex(months, axis=0)
    df_2022_high_agg = df_2022_high_agg.reindex(months, axis=0)
    df_ref_low_agg = df_ref_low_agg.reindex(months, axis=0)
    df_2022_low_agg = df_2022_low_agg.reindex(months, axis=0)

    return df_ref_high_agg, df_ref_low_agg, df_2022_high_agg, df_2022_low_agg


def plot_anomaly(df_2022_arg, df_ref_arg, parameter, df_meta_data_arg):

    """
    Function plots the temperature difference between the two periods.

    :param df_2022_arg: aggregated pandas dataframe for 2022
    :type df_2022_arg: df

    :param df_ref_arg: aggregated pandas dataframe for ref. period
    :type df_ref_arg: df

    :param parameter: the parameter we want to plot
    :type parameter: string

    :param df_meta_data_arg: pandas dataframe witch contains metadata from all stations
    :type df_meta_data_arg: df
    """

    # calculate anomaly
    df_dif = df_2022_arg - df_ref_arg
    # get values of the parameter from df
    para_val = df_dif[f'obs_{parameter}'].values

    # get min and max temperature
    temp_min = np.min(para_val)
    temp_max = np.max(para_val)

    # choose colormap
    cmap = matplotlib.pyplot.get_cmap('RdBu_r')

    fig, ax = plt.subplots()

    # Create a TwoSlopeNorm object
    norm = mcolors.TwoSlopeNorm(vmin=temp_min, vcenter=0, vmax=temp_max)

    # Plot the bars with relative colors
    bars = ax.bar(df_dif.index.values, para_val, color=cmap(norm(para_val)))
    ax.bar_label(bars, padding=1)

    # set y-limit, depends on maximum of the highest or the lowest temp value
    y_lim = max(np.abs(temp_min), temp_max) + 0.5
    ax.set_ylim([-y_lim, y_lim])

    # 0 line
    ax.axhline(y=0, color='grey')

    # shaded area represents the mean
    ax.axhspan(ymin=0, ymax=para_val.mean(), alpha=0.05, color='k', label='Annual mean temp dif')

    # Set labels and title
    # get the name of the station from df_meta_data
    station_name = \
    df_meta_data_arg.loc[df_meta_data_arg.station_id == df_2022_arg.obs_station_id[0]].station_name.values[0]

    ax.set_ylabel('Temperature Difference [deg C]')
    ax.set_title(f'{parameter} Temperature Anomaly 2022, {station_name}')

    # format non data elements
    plt.legend(loc='lower right')
    ax.tick_params(bottom=False)
    ax.spines[['top', 'right', 'bottom']].set_visible(False)
    plt.savefig(BASE_DIR / 'images' / f'{parameter}_Temperature_Anomaly_2022_{station_name}.png', format='png')
    plt.show()


def plot_anomaly_line_all(df_2022_arg, df_ref_arg):

    """
    Function plots the temperature difference between the two periods.

    :param df_2022_arg: aggregated pandas dataframe for 2022
    :type df_2022_arg: df

    :param df_ref_arg: aggregated pandas dataframe for ref. period
    :type df_ref_arg: df
    """

    # calculate anomaly
    df_dif = df_2022_arg - df_ref_arg

    fig, ax = plt.subplots()

    # Plot the lines with specified colors
    line_tmk = ax.plot(df_dif.index.values, df_dif.obs_TMK.values, color='grey', label='Daily mean temp')
    line_tnk = ax.plot(df_dif.index.values, df_dif.obs_TNK.values, color='blue', label='Daily min temp')
    line_txk = ax.plot(df_dif.index.values, df_dif.obs_TXK.values, color='red', label='Daily max temp')

    # Set y-limit, depends on maximum of the highest or the lowest temperature value
    temp_min = np.min(df_dif[['obs_TMK', 'obs_TNK', 'obs_TXK']].values)
    temp_max = np.max(df_dif[['obs_TMK', 'obs_TNK', 'obs_TXK']].values)
    y_lim = max(np.abs(temp_min), temp_max) + 0.5
    ax.set_ylim([-y_lim, y_lim])

    # Add a 0 line
    ax.axhline(y=0, color='grey')

    # Set labels and title
    ax.set_ylabel('Temperature Difference [deg C]')
    ax.set_title('Temperature Anomaly 2022')

    # Format non-data elements
    plt.legend(loc='lower right')
    ax.tick_params(bottom=False)
    ax.spines[['top', 'right', 'bottom']].set_visible(False)

    plt.show()



if __name__ == '__main__':
    
    # could import DATABASE from main_file_2, but this takes very long
    DATA_PATH = "_data"
    DATABASE = os.path.join(DATA_PATH, "_stations.db")

    # connect to sql database
    db_connector = sqlite3.connect(DATABASE)

    # get information/metadata off all stations
    df_meta_data = get_stations_information(db_connector)

    '''
    # get data from database for all stations
    df_all_raw = get_all_station_data(db_connector)

    # process data from database all stations
    df_ref_high, df_ref_low, df_2022_high, df_2022_low = process_all_data(df_all_raw, df_meta_data)

    # plot temperature anomaly TMK high stations
    plot_anomaly(df_2022_high, df_ref_high, 'TMK', df_meta_data)

    # plot temperature anomaly TMK low stations
    plot_anomaly(df_2022_low, df_ref_low, 'TMK', df_meta_data)
    '''

    # get data from database for station 701
    df_raw = get_station_data(701, db_connector)

    # process data from database
    df_2022, df_ref = process_data(df_raw)

    # plot temperature anomaly TMK
    plot_anomaly(df_2022, df_ref, 'TNK', df_meta_data)
    # plot_anomaly(df_2022, df_ref, 'TXK', df_meta_data)
    # plot_anomaly(df_2022, df_ref, 'TMK', df_meta_data)

    # plot temperature anomaly TMK, TXK, TNK as linechart
    # plot_anomaly_line_all(df_2022, df_ref)

    # close connection to sql database
    db_connector.close()
