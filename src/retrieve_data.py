from xml.etree import ElementTree as ET
import json
import pandas as pd
import requests
import time



def get_stations_information():

    """
    In the following we extract the information from all weather stations by requesting the meteoapi. We create a pandas
    dataframe object with this information.

    :return: A pandas dataframe with station id, station name, longitude, latitude, altitude of a station and the start
             and end date of the observation.
    :rtype: Pandas dataframe object

    :raises Exception: if URL request fails
    """

    # get request of the data
    URL = "http://meteoapi.discdown.org/api/station-search?format=xml"
    req = requests.get(URL)

    # checking if connection was successful
    if req.status_code // 100 != 2:
        raise Exception('Can\'t connect to valid API address. Check URL')

    doc = ET.fromstring(req.content)

    # parsing data information from all stations
    stations = doc.findall("./station")
    _id = [None] * len(stations)
    name = [None] * len(stations)
    lon = [None] * len(stations)
    lat = [None] * len(stations)
    alt = [None] * len(stations)
    date_start = [None] * len(stations)
    date_end = [None] * len(stations)
    for i, station in enumerate(stations):
        _id[i] = station.attrib['id']
        name[i] = station.find("name").text
        lon[i] = station.find("longitude").text
        lat[i] = station.find("latitude").text
        alt[i] = station.find("altitude").text
        date_start[i] = station.attrib["data_from"]
        date_end[i] = station.attrib["data_to"]

    # store the data information in a pandas dataframe
    df = pd.DataFrame(list(zip(_id, name, lon, lat, alt, date_start, date_end)),
                      columns=['STATION_ID', 'NAME', 'LON', 'LAT', 'ALT', 'DATE_START', 'DATE_END'])

    return df


def get_station_id(station_name):

    """
    Function returns the station id of input name of a station.

    :param station_name: name of a station
    :type station_name: str

    :return: station id
    :rtype: int

    :raises TypeError: if the argument type is not str
    :raises ValueError: if station name can not be found in the API
    """

    # Checking input type
    if type(station_name) != str:
        raise TypeError(f'Input argument {station_name} should be of type: str')

    df = get_stations_information()

    if station_name not in list(df.NAME):
        raise ValueError(f'The station name {station_name} can not be found.')
    else:
        return int(df.loc[df.NAME == station_name, 'STATION_ID'].iloc[0])


def get_station_data(ID, year="", parameters='tlmin:tlmax:tl_mittel'):

    """
    Function parses data of a specific station and creates a pandas dataframe of the station data.
    (Other parameters can be found on:
    https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/DESCRIPTION_obsgermany_climate_daily_kl_historical_en.pdf)

    :param ID: station id of the observed station.
    :type ID: int

    :param year: limits the data to a specific year. By default empty, to retrieve all available years.
    :type year: int, str

    :param parameters: specifies which parameters one wants to retrieve from the API. Default is tlmin:tlmax:tl_mittel, meaning
    daily minimum, maximum and mean temperature.
    :type parameters: str

    :return: a pandas dataframe with date as index, id, and daily minimum, maximum and mean temperature as columns.
    Returns None if URL request fails.
    :rtype: pandas dataframe object

    :raises Exception: if URL request fails
    :raises TypeError: if ID, year or parameters are not of the desired type
    :raises ValueError: if the arguments do not fulfill given constraints
    """

    # Sanity checks
    if type(ID) != int:
        raise TypeError('ID must be of type: int')
    if not isinstance(year, (int, str)):
        raise TypeError('year must be of type: int or str')
    if type(parameters) != str:
        raise TypeError('parameters must be of type: str')

    # Checking for correct input values
    station_data = get_stations_information()
    PARAMETERS = ['ffx', 'p_mittel', 'rf_mittel', 'rr', 'sh', 'shneu_manu', 'so_h', 'tl_mittel', 'tlmax', 'tlmin', 'tsmin', 'vv_mittel']

    if ID not in [int(id_) for id_ in station_data.STATION_ID]:
        raise ValueError(f'The is no such ID: {ID}')

    param_split = parameters.split(':')
    for param in param_split:
        if param not in PARAMETERS:
            raise ValueError(f'The parameter {param} is not a valid parameter')

    # get request of the data
    URL = f"http://meteoapi.discdown.org/api/data/198822/xml/{ID}/{year}?parameters={parameters}"
    req = requests.get(URL)

    # checking if connection was successful
    if req.status_code // 100 != 2:
        raise Exception('Can\'t connect to valid API address. Check URL')

    doc = ET.fromstring(req.content)

    # get temp data and DATUM from the request
    observations = doc.findall("./observations")
    data = [json.loads(observations[0].text)]

    # get the station id
    station_id = doc.find("./station").attrib['id']

    # create pandas dataframe from the data
    df = pd.DataFrame.from_dict(data[0])
    df.insert(0, 'STATION_ID', station_id)
    df = df.set_index(pd.to_datetime(df['datum']))
    df.pop('datum')

    return df


def get_time_period(station_id, START_YEAR=1990, END_YEAR=2019):

    """
    Function that gets pandas dataframe from get_station_data() for specific years
    and combines them into one pandas dataframe.

    :param station_id: ID of a station
    :type station_id: int

    :param START_YEAR: start of the reference year
    :type START_YEAR: int

    :param END_YEAR: end of the reference year
    :type END_YEAR: int

    :return: a pandas dataframe with date as index, id, and daily minimum, maximum and mean temperature as columns for
    the desired years. Returns None if URL request fails.
    :rtype: pandas dataframe object
    """

    # Sanity checks (station name is checked at get_station_id() function)
    if type(START_YEAR) != int:
        raise TypeError('START_YEAR must be of type: int')
    if type(END_YEAR) != int:
        raise TypeError('END_YEAR must be of type: int')

    # list to store dataframes
    dfs = []

    # loop over each reference year and appends each dataframe to list
    for reference_year in range(START_YEAR, END_YEAR + 1):
        df = get_station_data(station_id, reference_year)
        dfs.append(df)

    # merge dataframes
    merged_df = pd.concat(dfs)

    return merged_df



if __name__ == '__main__':

    t1 = time.time()
    print(get_stations_information())
    stat_id = get_station_id('Linz Hörsching Flughafen')
    print(get_time_period(stat_id))
    timing = time.time() - t1
    print(f"Time required: {timing:.5f} seconds")
