import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster


APP_TITLE = "UFO Sightings"
APP_SUB_TITLE = "Source: Kaggle"

def display_map(df):

    map = folium.Map(location=[0,0], scrollWheelZoom=True, zoom_start=2)

    
    
    # for index, row in df.iterrows():

    #     tooltip_text = f"Date: {row['Date_time']}<br>Shape: {row['UFO_shape']}<br>Duration: {row['length_of_encounter_seconds']}"

    #     folium.Marker(
    #         location=[row['latitude'], row['longitude']],
    #         popup=f"Description: {row['description']}",
    #         tooltip=tooltip_text,
            
    #     ).add_to(map)

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
            "mytext.textContent = display_text.text;"
            "popup.setContent(mytext);"
            "marker.bindPopup(popup);"
            'return marker};')

    map.add_child(FastMarkerCluster(df[['latitude', 'longitude', 'UFO_shape']].values.tolist(), callback=callback))

    st_map = st_folium(map, height=550, use_container_width=True)

@st.cache_resource
def get_data():
    # Create a database session object that points to the URL.
    return pd.read_csv("data/ufo_sighting_data.csv", low_memory=False)

def main():
    st.set_page_config(page_title=APP_TITLE, layout='wide')
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # Load data
    df = get_data()

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
    df['Years'] = df['Date_time'].dt.year

    # Slice for testing sake
    df = df[:1000]

    # Define the range of years for the multi-slider
    year_min = int(df['Years'].min())
    year_max = int(df['Years'].max())
    range_years = st.slider("Select Year Range", year_min, year_max, (year_min, year_max), 1)

    # Filter years
    df_slice = df.copy()
    df_slice = df_slice.loc[(df_slice['Years'] >= range_years[0]) & (df_slice['Years'] <= range_years[1])]

    display_map(df_slice)

    st.dataframe(df_slice, use_container_width=True)


if __name__ == "__main__":
    main()