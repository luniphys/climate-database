from retrieve_data import *

import os.path
import sqlite3
import time
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parents[1]


def connect_to_db():

    """
    Function that connects to db and returns database connection handler

    :return: database connection handler
    :rtype: sqlite3.connection
    """

    # set data path and database
    DATA_PATH = BASE_DIR / "data"
    DATABASE = os.path.join(DATA_PATH, "stations.db")

    # create the data directory if needed
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    # if database already exists, remove it
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    # connect to a SQLite database
    db_con = sqlite3.connect(DATABASE)
    db_con.row_factory = sqlite3.Row

    # excecute PRAGMA statement to enable foreign key constraints
    db_con.execute("PRAGMA foreign_keys = ON;")

    return db_con


def modify_datatype_stations():

    """
    Function that transforms the station information data type from pandas dataframe into a dictionary.

    :type: dict
    :return: a dictionary of a pandas dataframe
    """

    # get stations information
    df_stations_arg = get_stations_information()

    # extract columns we want
    all_stations = df_stations_arg[["NAME", "STATION_ID", "LON", "LAT", "ALT", "DATE_START", "DATE_END"]]

    # turn dataframe into dict
    all_stations = all_stations.to_dict(orient='records')

    return all_stations


def convert_station_id_to_int(a_obs_list):

    """
    Function hat converts STATION_ID to int in list


    :param a_obs_list: list of tuple with STATION_ID as text
    :type a_obs_list: list

    :return: list with STATION_ID AS int
    :rtype: list
    """

    # Apply function 'int' on each element in column STATION_ID
    a_obs_list.STATION_ID.apply(int)

    # Save back to original object
    a_obs_list.STATION_ID = a_obs_list.STATION_ID.apply(int)

    return a_obs_list


def convert_to_list_of_tuple(a_dataframe):

    """
    Function that converts pandas dataframe into a list of tuple representing a row and includes the date
    as the first element and the other values from the row as subsequent elements.

    :param a_dataframe: pandas dataframe needed to be converted into list of tuple
    :type a_dataframe: pandas dataframe

    :return: list of tuple
    :rtype: list
    """

    # Transform df into list of tuple
    list_of_tuple = [(row.Index.strftime('%Y-%m-%d'), *row[1:]) for row in a_dataframe.itertuples()]

    return list_of_tuple


def insert_into_obs_table(a_obs_list):

    """
    Function that inserts the observation data into observations table.

    :param a_obs_list: a list
    :type a_obs_list: list

    :return: print of successful insert
    :rtype: text
    """

    # Query for inserting into observation table, if exist ignore
    query_obs = '''INSERT OR IGNORE INTO observations (obs_date, obs_station_id, obs_TMK, obs_TXK, obs_TNK)
            VALUES (?, ?, ?, ?, ?);'''
            # VALUES (:DATUM, :STATION_ID, :TMK, :TXK, :TNK); Before ?,?,?,...

    # Executing query
    executing_query = cursor.executemany(query_obs, a_obs_list)

    return executing_query


def format_print(rows_arg):

    """
    Function to print the query database in rows format

    :param rows_arg: database
    :type rows_arg: list
    """

    for row in rows_arg:
        print("obs_date: {:s}, obs_station_id: {:d}, obs_TMK: {:f}, "
              "obs_TXK: {:f}, obs_TNK: {:f},".format(row["obs_date"],
                                                     row["obs_station_id"],
                                                     row["obs_TMK"],
                                                     row["obs_TXK"],
                                                     row["obs_TNK"]))



if __name__ == '__main__':
    
    # Connect to db
    db_connector = connect_to_db()
    cursor = db_connector.cursor()



    # create a reference table to store the ID of the stations.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stations (
        station_id      INTEGER PRIMARY KEY  NOT NULL,
        station_name    TEXT                 NOT NULL, 
        station_lon     REAL                 NOT NULL,
        station_lat     REAL                 NOT NULL,
        station_alt     REAL                 NOT NULL,
        station_start   TEXT                 NOT NULL, 
        station_end     TEXT                 NOT NULL
        );''')

    # get modified stations data from function
    dict_stations = modify_datatype_stations()

    # Query for inserting df_stations data into stations table
    queryA = """INSERT OR IGNORE INTO stations (station_id, station_name, station_lon, 
    station_lat, station_alt, station_start, station_end)
                VALUES (:STATION_ID, :NAME, :LON, :LAT, :ALT, :DATE_START, :DATE_END);"""

    # Inserting into stations table
    cursor.executemany(queryA, dict_stations)

    # print to make sure it works - Spoiler it works
    '''
    rows = cursor.execute("SELECT * FROM stations ").fetchall()
    row_count = 0
    for row in rows:
        row_count += 1
        print("Station id: {:d}, Station name: {:s}, Longitude: {:f}, Latitude: {:f}, Altitude: {:f}, Start Date: {:s}, End Date: {:s}".format(
            row["station_id"], row["station_name"], row["station_lon"], row["station_lat"], row["station_alt"], row["station_start"], row["station_end"]))
        print(f"Number of Stations: {row_count}")   
    # Number of Stations: 1346
    '''


    # create a table to store the observations data from the stations.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS observations (
            obs_station_id  INTEGER,
            obs_date        DATE,
            obs_TMK         REAL,
            obs_TXK         REAL,
            obs_TNK         REAL,
            CONSTRAINT PK_observations PRIMARY KEY (obs_station_id, obs_date)

             CONSTRAINT fk_stations
                    FOREIGN KEY (obs_station_id)
                    REFERENCES stations(station_id)
        );''')


    # Start the timing
    t1 = time.time()

    # get id for station Linz Hörsching Flughafen
    stat_id = get_station_id('Linz Hörsching Flughafen')

    # get df for the year 2022 for Linz Hörsching Flughafen
    obs_2022 = get_station_data(stat_id, 2022)

    # convert station id to int
    conv_obs_2022 = convert_station_id_to_int(obs_2022)

    # convert pandas df to list of tuples
    obs_list_2022 = convert_to_list_of_tuple(conv_obs_2022)

    # insert observations into table observations
    insert_into_obs_table(obs_list_2022)

    # print rows to check if insert into table observation was successful - works
    # rows = cursor.execute(f"SELECT * FROM observations WHERE obs_station_id={stat_id}").fetchall()
    # format_print(rows)

    # Measure time needed for loading, transforming and inserting observations from 2022 for Linz Hörsching Flughafen into observations table
    timing = time.time() - t1
    print(f"Time required to get station data for Linz Hörsching Flughafen for year 2022: {timing:.5f} seconds")

    # Measure database disk space table size in bytes for observations table
    table_size = cursor.execute(
        "SELECT page_count * page_size as table_size FROM pragma_page_count(), pragma_page_size()").fetchall()
    table_size = table_size[0]["table_size"] / 1024 / 1024  # convert byte to MB
    print(f"Database disk space of Linz Hörsching Flughafen for year 2022: {table_size:.5f} MB")

    # Estimate for time required to load in 31 years of observations from all 566 Stations:
    time_all_stations = timing * 31 * 566
    print(f"Estimate for time required to load in 31 years of observations from all 566 Stations: {time_all_stations:.2f} sec or {time_all_stations/60:.2f} min or "
          f"{time_all_stations/360:.2f} hours or {time_all_stations/86400:.2f} days!")
    # Estimate for disc space for 31 years of observations for all 566 Stations:
    disc_space_all_stations = table_size * 31 * 566
    print(f"Estimate for disc space for 31 years of observations for all 566 Stations: {disc_space_all_stations:.2f} MB or {disc_space_all_stations/1024:.2f} GB")



    # timing start to measure time needed for loading, transforming and inserting observations
    # from 1990-2019 for Linz Hörsching Flughafen into observations table

    # Start the timing
    t2 = time.time()
    
    # get df for the reference years 1990-2019 for Linz Hörsching Flughafen
    obs_ref = get_time_period(stat_id)

    # convert station id to int
    conv_obs_ref = convert_station_id_to_int(obs_ref)

    # convert pandas df to list of tuples
    obs_list_ref = convert_to_list_of_tuple(conv_obs_ref)

    # insert reference observations into table observations
    insert_into_obs_table(obs_list_ref)
    
    # Measure time needed for loading, transforming and for Linz Hörsching Flughafen for year 1990-2022 into observations table
    timing = time.time() - t2
    print(f"Time required to get reference station data for Linz Hörsching Flughafen for year 1990-2022: {timing:.5f} seconds")

    
    # query to get all rows from table observations for station Linz Hörsching Flughafen from 1990 to 2022 - works for including year 1990
    # rows = cursor.execute(f"SELECT * FROM observations WHERE obs_station_id={stat_id}").fetchall()
    # print the first 10 rows to check if inserts into table observation were successful - works
    # format_print(rows[:10])
    


    """
    # Commented out/ not advised to insert observations from 1990 to 2022 from all 566 Stations,
    # as it will take longer than the estimate of 0.94 days to insert and a disc space of 1.41 GB!
    
    # get station information
    df_stations = get_stations_information()
    
    # loop over every station, get observations from 1990 to 2022, transforms and insert into table
    for station in df_stations.STATION_ID:
        # get df for the reference years 1990-2022 for Station
        obs_station = get_reference_obs(station, 1990, 2022)

        # convert station id to int
        conv_obs_station = convert_station_id_to_int(obs_station)

        # convert pandas df to list of tuples
        obs_list_station = convert_to_list_of_tuple(conv_obs_station)

        # insert reference observations into table observations
        insert_into_obs_table(obs_list_station)
    """



    # load and insert observational data from 5 low altitude and 5 high altitude stations into observations table
    # stations to load in: Low altitude: Neusiedl am See, Hohenau, Groß-Enzersdorf, Gänserdorf, Bruckneudorf
    #                      High alitutde: Sonnblick, Pitztaler Gletscher, Ischgl-Idalpe, Rudolfshütte, Patscherkofel

    additional_stations = [65, 158, 31, 134, 18, 213, 184, 17005, 82, 196]

    for station in additional_stations:
        
        # get df for the year 2022 for station
        obs_2022 = get_station_data(station, 2022)

        # convert station id to int
        conv_obs_2022 = convert_station_id_to_int(obs_2022)

        # convert pandas df to list of tuples
        obs_list_2022 = convert_to_list_of_tuple(conv_obs_2022)

        # insert observations into table observations
        insert_into_obs_table(obs_list_2022)

        # get df for the reference years 1990-2019 for Station
        obs_station = get_time_period(station, 1990, 2019)

        # convert station id to int
        conv_obs_station = convert_station_id_to_int(obs_station)

        # convert pandas df to list of tuples
        obs_list_station = convert_to_list_of_tuple(conv_obs_station)

        # insert reference observations into table observations
        insert_into_obs_table(obs_list_station)

        # print statement to see successful insert after each station
        print("Station data insert was successful.")


    # check if data is inserted
    """
    rows = cursor.execute("SELECT * FROM observations WHERE obs_station_id = 5142 AND strftime('%Y', obs_date)='1990'").fetchall()
    # print the first 10 rows to check if inserts into table observation were successful - works
    format_print(rows[:100])
    # checked years of 2 stations, everything was included, rest probably also
    """
    
    db_connector.commit()
    db_connector.close()
