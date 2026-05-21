[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# Weather Station Database — Data Management Project

An academic group project completed as part of the **Digital Science Minor** at the University of Innsbruck.

## Overview

This project retrieves, processes, and analyzes meteorological data from weather stations across Austria using a public meteo API. The core focus areas are:

- **XML data processing** — parsing station metadata and observation records from XML API responses using Python's `xml.etree.ElementTree`
- **SQL / relational data management** — storing and querying the processed data in a SQLite database with proper schema design, foreign key constraints and correct use of relational databases.

## Project Structure

```
src/
  retrieve_data.py   # Fetches and parses XML data from the meteo API
  database.py        # Manages the SQLite database (schema, inserts, queries)
  graphics.py        # Data retrieval, processing & analysis
data/                # Generated SQLite database
images/              # Plotted data
```

## Results

|                                          Min Temperature                                           |                                          Max Temperature                                           |                                          Mean Temperature                                           |
| :------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------: |
| ![TMK Flughafen](images/TMK_Temperature_Anomaly_2022_Linz%20Hörsching%20Flughafen.png) | ![TXK Flughafen](images/TXK_Temperature_Anomaly_2022_Linz%20Hörsching%20Flughafen.png) | ![TNK Flughafen](images/TNK_Temperature_Anomaly_2022_Linz%20Hörsching%20Flughafen.png) |

|                                  High Altitude Stations                                  |                                 Low Altitude Stations                                  |
| :--------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------: |
| ![TMK High Altitude](images/TMK_Temperature_Anomaly_2022_High%20Altitude%20Stations.png) | ![TMK Low Altitude](images/TMK_Temperature_Anomaly_2022_Low%20Altitude%20Stations.png) |

|                     Temperature Anomaly                     |
| :--------------------------------------------------------------: |
| ![Temperature Anomaly 2022](images/Temperature_Anomaly_2022.png) |
