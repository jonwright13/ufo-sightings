import streamlit as st
import pandas as pd
import sqlite3

URL = 'data/ufo_sighting_data.db'


@st.cache_data
def get_variables():

    # Initialise the connection to the database and create a cursor object
    db_connection = sqlite3.connect(URL)
    cursor = db_connection.cursor()

    # SQL query to fetch the min and max years
    cursor.execute("SELECT MIN(Year) as min_value, MAX(Year) as max_value FROM sightings")
    year_min, year_max = cursor.fetchone()

    # SQL query to fetch the min and max hours
    cursor.execute("SELECT MIN(Hour) as min_value, MAX(Hour) as max_value FROM sightings")
    hour_min, hour_max = cursor.fetchone()

    # Close the database connection
    db_connection.close()

    return year_min, year_max, hour_min, hour_max, 

@st.cache_data
def get_dependent_dropdowns(year_start, year_end, hour_start, hour_end, country_incl, country_excl):

    # Initialise the connection to the database and create a cursor object
    db_connection = sqlite3.connect(URL)
    cursor = db_connection.cursor()

    # SQL query to fetch a list of all distinct seasons
    query_base = "SELECT DISTINCT(Season) FROM sightings WHERE Year >= ? AND Year <= ? AND Hour >= ? AND Hour <= ?"
    params = [year_start, year_end, hour_start, hour_end]

    # Append the query with a WHERE clause if the country include option is greater than 0
    if len(country_incl) > 0:
        query_base += " AND Country IN ({})".format(','.join(['?']*len(country_incl)))
        params.extend(country_incl)

    # Append the query with a WHERE clause if the country exclude option is greater than 0
    if len(country_excl) > 0:
        query_base += " AND Country NOT IN ({})".format(','.join(['?']*len(country_excl)))
        params.extend(country_excl)

    cursor.execute(query_base, params)
    seasons = sorted([season[0] for season in cursor.fetchall()])

    # SQL query to fetch a list of all distinct ufo shapes
    query_base = "SELECT DISTINCT(UFO_shape) FROM sightings WHERE Year >= ? AND Year <= ? AND Hour >= ? AND Hour <= ?"
    params = [year_start, year_end, hour_start, hour_end]

    # Append the query with a WHERE clause if the country include option is greater than 0
    if len(country_incl) > 0:
        query_base += " AND Country IN ({})".format(','.join(['?']*len(country_incl)))
        params.extend(country_incl)

    # Append the query with a WHERE clause if the country exclude option is greater than 0
    if len(country_excl) > 0:
        query_base += " AND Country NOT IN ({})".format(','.join(['?']*len(country_excl)))
        params.extend(country_excl)

    cursor.execute(query_base, params)
    ufo_shape = sorted([shape[0] for shape in cursor.fetchall() if shape[0] != None])

    # Close the database connection
    db_connection.close()

    return seasons, ufo_shape

@st.cache_data
def get_country_dropdowns(year_start, year_end, hour_start, hour_end):

    # Initialise the connection to the database and create a cursor object
    db_connection = sqlite3.connect(URL)
    cursor = db_connection.cursor()

    # SQL query to fetch a list of all distinct countries alphabetical list and ordered by count
    cursor.execute("SELECT Country, COUNT(*) as count FROM sightings WHERE Year >= ? AND Year <= ? AND Hour >= ? AND Hour <= ? GROUP BY Country ORDER BY count DESC", (year_start, year_end, hour_start, hour_end))
    fetch_data = cursor.fetchall()
    
    countries_list = sorted([country[0] for country in fetch_data if country[0] != None])
    countries_count_sorted = [country[0] for country in fetch_data if country[0] != None]

    # Close the database connection
    db_connection.close()

    return countries_list, countries_count_sorted
    

@st.cache_data(show_spinner=False)
def filter_data(range_years, ufo_option, season, range_hours, country_incl_option, country_excl_option):

    # Initialise a database connection
    db_connection = sqlite3.connect(URL)

    # Query string for year and hour filtering
    query = "SELECT * FROM sightings WHERE Year >= ? AND Year <= ? AND Hour >= ? AND Hour <= ?"
    params = [range_years[0], range_years[1], range_hours[0], range_hours[1]]

    # Append the query with a WHERE clause if the ufo option is greater than 0
    if len(ufo_option) > 0:
        query += " AND UFO_shape IN ({})".format(','.join(['?']*len(ufo_option)))
        params.extend(ufo_option)

    # Append the query with a WHERE clause if the season option is greater than 0
    if len(season) > 0:
        query += " AND Season IN ({})".format(','.join(['?']*len(season)))
        params.extend(season)

    # Append the query with a WHERE clause if the country include option is greater than 0
    if len(country_incl_option) > 0:
        query += " AND Country IN ({})".format(','.join(['?']*len(country_incl_option)))
        params.extend(country_incl_option)

    # Append the query with a WHERE clause if the country exclude option is greater than 0
    if len(country_excl_option) > 0:
        query += " AND Country NOT IN ({})".format(','.join(['?']*len(country_excl_option)))
        params.extend(country_excl_option)

    # Parse a dataframe using the combined sql query
    df = pd.read_sql_query(query, db_connection, params=params)

    # Close the database connection
    db_connection.close()
    
    return df

@st.cache_resource(show_spinner=False)
def display_table(df):
    
    # Display the data on a table
    st.dataframe(df[[col for col in df if col not in ['Text']]], use_container_width=True)