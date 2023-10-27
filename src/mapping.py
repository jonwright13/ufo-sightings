import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster
from urllib.request import urlopen
import json, geopandas, branca
import pandas as pd
from functools import partial
from branca.colormap import linear

# Choropleth json for countries: https://github.com/johan/world.geo.json/blob/master/countries.geo.json

@st.cache_resource(experimental_allow_widgets=True, show_spinner=False)
def get_map(df, tile=None):

    # Create a Folium map object
    map = folium.Map(location=[0,0], scrollWheelZoom=True, zoom_start=2, tiles='OpenStreetMap')
    
    if tile == 'Markers':
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
        
    elif tile == 'Choropleth':

        url = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'

        with urlopen(url) as response:
            countries = json.load(response)

        countries['features'] = [country for country in countries['features'] if country.get('id') != "-99"]

        geodata = geopandas.GeoDataFrame.from_features(countries, crs="EPSG:4326")

        country_map = dict(zip(
            [name['properties']['name'] for name in countries['features']],
            [name['id'] for name in countries['features']]
            ))

        geodata['code'] = geodata['name'].map(country_map)
        geodata['count'] = geodata['code'].map(df['Country_Code'].value_counts()).fillna(0)

        colormap = branca.colormap.LinearColormap(
            vmin=geodata["count"].quantile(0.0),
            vmax=geodata["count"].quantile(1),
            colors=["gray", "orange", "lightblue", "green", "darkgreen"],
            caption="Sightings per Country",
        )

        country_counts_dict = geodata.set_index('code')['count']

        tooltip = folium.GeoJsonTooltip(
            fields=['name', 'count'],
            aliases=["Country:  ", "Count: "],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        )

        folium.GeoJson(
            geodata,

            style_function=lambda x: {
                "fillColor": colormap(x["properties"]["count"])
                if x["properties"]["count"] is not None
                else "transparent",
                "color": "black",
                "fillOpacity": 0.4,
            },
            tooltip=tooltip
            ).add_to(map)

        colormap.add_to(map)

    # Create the map on the streamlit app
    st_folium(map, height=550, use_container_width=True, key='map')