# ufo-sightings
Geospatial mapping of the [UFO Sightings Dataset](https://www.kaggle.com/datasets/jonwright13/ufo-sightings-around-the-world-better) on a Streamlit hosted application using the Folium library.

Original dataset was based on [this dataset](https://www.kaggle.com/datasets/camnugent/ufo-sightings-around-the-world), which was updated using a script to retrieve addresses from the geocode API using coordinates to provide additional, location specific information related to each sighting.

## Features
- Mart, Chart, and Table views
- Choropleth and Marker map type options
- Filters on datetime, countries, seasons, and UFO type

Application: [UFO Sightings App](http://ufo-sightings.streamlit.app/)
Geocode API Address Fix Script: [GitHub](https://github.com/jonwright13/geo-locate)
