import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster


APP_TITLE = "UFO Sightings"
APP_SUB_TITLE = "Source: https://www.kaggle.com/datasets/camnugent/ufo-sightings-around-the-world/data"

@st.cache_resource
def display_map(df):

    map = folium.Map(location=[0,0], scrollWheelZoom=True, zoom_start=2)
    
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

    map.add_child(FastMarkerCluster(df[['latitude', 'longitude', 'Text']].values.tolist(), callback=callback))
    return map
    

@st.cache_resource
def get_data():

    df = pd.read_csv("data/ufo_sighting_data.csv", low_memory=False)

    # Eliminate anomalous latiutude/longitude
    df = df.drop(df[pd.to_numeric(df['latitude'], errors='coerce').isna()].index).reset_index(drop=True)
    df = df.drop(df[pd.to_numeric(df['longitude'], errors='coerce').isna()].index).reset_index(drop=True)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    df = df.drop(df[pd.to_numeric(df['length_of_encounter_seconds'], errors='coerce').isna()].index).reset_index(drop=True)
    df['length_of_encounter_seconds'] = df['length_of_encounter_seconds'].astype(float)

    # Fixing datetime errors and extracting years
    df['Date_time'] = df['Date_time'].str.replace('24:00', '00:00')
    df['Date_time'] = pd.to_datetime(df['Date_time'], format='%m/%d/%Y %H:%M')
    df['Year'] = df['Date_time'].dt.year
    df['Month'] = df['Date_time'].dt.month
    df['Hour'] = df['Date_time'].dt.hour

    # Apply the mapping function to create a 'Season' column
    df['Season'] = df['Month'].apply(map_to_season)

    # Rename columns using the .rename() method
    df = df.rename(columns={'described_duration_of_encounter': 'Encounter_Duration', 'description': 'Description'})

    # Add display text to dataframe
    df['Text'] = df[['Year', 'Season', 'UFO_shape', 'Encounter_Duration', 'Description']].apply(custom_format, axis=1)

    # Slice for testing purposes
    # df = df[:1000]

    return df

@st.cache_resource
def filter_data(df, range_years, ufo_option, season, range_hours):

    df_slice = df.copy()

    df_slice = df_slice.loc[
        (df_slice['Year'] >= range_years[0]) & (df_slice['Year'] <= range_years[1]) & 
        (df_slice['Hour'] >= range_hours[0]) & (df_slice['Hour'] <= range_hours[1])
        ]

    if len(ufo_option) > 0:
        df_slice = df_slice.loc[df_slice['UFO_shape'].isin(ufo_option)]

    if len(season) > 0:
        df_slice = df_slice.loc[df_slice['Season'].isin(ufo_option)]
    
    return df_slice

# Define a custom mapping function to categorize months into seasons
def map_to_season(month):
    if 3 <= month <= 5:
        return 'Spring'
    elif 6 <= month <= 8:
        return 'Summer'
    elif 9 <= month <= 11:
        return 'Autumn'
    else:
        return 'Winter'
    
# Define a custom lambda function to join string columns into a multi-line string with custom formatting
def custom_format(row):
    entries = []
    for column_name, value in row.items():
        entries.append(f'{column_name}: {value}')
    return '<br>'.join(entries)

def main():
    st.set_page_config(page_title=APP_TITLE, layout='wide', initial_sidebar_state='expanded')
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # Load data
    df = get_data()

    # Define the range of years for the multi-slider
    year_min = int(df['Year'].min())
    year_max = int(df['Year'].max())
    range_years = st.sidebar.slider("Select Year Range", year_min, year_max, (year_min, year_max), 1)

    # Define Hours Range
    hour_min = int(df['Hour'].min())
    hour_max = int(df['Hour'].max())
    range_hours = st.sidebar.slider("Select Hour Range", hour_min, hour_max, (hour_min, hour_max), 1)

    # Multi-Select UFO Shape
    ufo_option = st.sidebar.multiselect(
        label='Select UFO Shape', options=sorted([shape for shape in list(df['UFO_shape'].unique()) if shape is not np.nan])
        )
    
    # Multi-Select Season
    season = st.sidebar.multiselect(
        label='Select Season', options=sorted([season for season in list(df['Season'].unique()) if season is not np.nan])
        )

    df_slice = filter_data(df, range_years, ufo_option, season, range_hours)

    st.sidebar.metric(
        'Count Sightings', value=df_slice.shape[0]
    )

    map = display_map(df_slice)
    st_map = st_folium(map, height=550, use_container_width=True, key='map')

    st.dataframe(df_slice[[col for col in df_slice if col not in ['Text']]], use_container_width=True)

    


if __name__ == "__main__":
    main()