import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster
import sqlite3
from datetime import datetime

APP_TITLE = "UFO Sightings"
APP_SUB_TITLE = "Source: [Kaggle](https://www.kaggle.com/datasets/camnugent/ufo-sightings-around-the-world/data)"
URL = 'data/ufo_sighting_data.db'

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """

@st.cache_resource(experimental_allow_widgets=True, show_spinner=False)
def get_map(df):

    # Create a Folium map object
    map = folium.Map(location=[0,0], scrollWheelZoom=True, zoom_start=2)
    
    # JS Callback function with additional information for each marker created -> Namely, tooltip text
    callback = ('function (row) {'
            'var marker = L.marker(new L.LatLng(row[0], row[1]), {color: "red"});'
            'var icon = L.AwesomeMarkers.icon({'
            "icon: 'info-sign',"
            "iconColor: 'white',"
            "markerColor: 'green',"
            "prefix: 'glyphicon',"
            "extraClasses: 'fa-rotate-0'"
            '});'
            'marker.setIcon(icon);'
            "var popup = L.popup({maxWidth: '300'});"
            "const display_text = {text: row[2]};"
            "var mytext = L.DomUtil.create('div', 'display_text');"
            "mytext.innerHTML = display_text.text;"
            "popup.setContent(mytext);"
            "marker.bindPopup(popup);"
            'return marker};')

    # Add the markers to the map using the FastMarkerCluster plugin
    map.add_child(FastMarkerCluster(df[['latitude', 'longitude', 'Text']].values.tolist(), callback=callback))

    # Create the map on the streamlit app
    st_folium(map, height=550, use_container_width=True, key='map')

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

    # SQL query to fetch a list of all distinct seasons
    cursor.execute("SELECT DISTINCT(Season) FROM sightings")
    seasons = sorted([season[0] for season in cursor.fetchall()])

    # SQL query to fetch a list of all distinct ufo shapes
    cursor.execute("SELECT DISTINCT(UFO_shape) FROM sightings")
    ufo_shape = sorted([shape[0] for shape in cursor.fetchall() if shape[0] != None])

    # Close the database connection
    db_connection.close()

    return year_min, year_max, hour_min, hour_max, seasons, ufo_shape

@st.cache_data(show_spinner=False)
def filter_data(range_years, ufo_option, season, range_hours):

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

    # Parse a dataframe using the combined sql query
    df = pd.read_sql_query(query, db_connection, params=params)

    # Close the database connection
    db_connection.close()
    
    return df

@st.cache_resource(show_spinner=False)
def display_table(df):
    
    # Display the data on a table
    st.dataframe(df[[col for col in df if col not in ['Text']]], use_container_width=True)

def main():

    # Create the page and add titles
    st.set_page_config(page_title=APP_TITLE, layout='wide', initial_sidebar_state='expanded')
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # Hide the spinner at the top of the page
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    # Load initial variables
    year_min, year_max, hour_min, hour_max, seasons, ufo_shape = get_variables()

    # Define the range of years for the multi-slider
    range_years = st.sidebar.slider("Select Year Range", year_min, year_max, (year_min, year_max), 1)

    # Define Hours Range
    range_hours = st.sidebar.slider("Select Hour Range", hour_min, hour_max, (hour_min, hour_max), 1)

    # Multi-Select UFO Shape
    ufo_option = st.sidebar.multiselect(label='Select UFO Shape', options=ufo_shape)
    
    # Multi-Select Season
    season = st.sidebar.multiselect(label='Select Season', options=seasons)

    # Filter the data based on the selections
    df = filter_data(range_years, ufo_option, season, range_hours)

    # Display count of sightings
    st.sidebar.metric('Count Sightings', value=df.shape[0])

    # URL links to external sites
    st.sidebar.write("[Buy me a coffee](https://www.buymeacoffee.com/jon.wright)")
    st.sidebar.write("[GitHub](https://github.com/jonwright13/ufo-sightings)")

    # Generate the map
    get_map(df)

    # Display the table of data
    display_table(df)

if __name__ == "__main__":
    main()