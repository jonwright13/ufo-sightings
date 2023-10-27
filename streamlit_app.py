import streamlit as st
import pandas as pd

from src.table_funcs import get_variables, filter_data, display_table, get_dependent_dropdowns, get_country_dropdowns
from src.mapping import get_map
from src.charts import ten_countries, ten_ufos, ufo_dist_by_season, season_pie_chart, bottom_ten_ufos


APP_TITLE = "UFO Sightings"
APP_SUB_TITLE = "Source: [Kaggle](https://www.kaggle.com/datasets/camnugent/ufo-sightings-around-the-world/data)"
URL = 'data/ufo_sighting_data.db'

choropleth_fill_colors = [
    'Accent', 'BrBg', 'BuGn', 'BuPu', 'Dark2', 'GnBu', 'OrRd', 'PRGn', 'Paired', 'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 
    'PuOr', 'PuRd', 'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Set1', 'Set2', 'Set3', 'Spectral', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd'
    ]


tiles = ["Default", "Choropleth"]

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

def main():

    # Create the page and add titles
    st.set_page_config(page_title=APP_TITLE, layout='wide', initial_sidebar_state='expanded')
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # Hide the spinner at the top of the page
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    view = st.sidebar.selectbox(label='Select View', options=['Map', 'Chart', 'Table'], index=0)
    
    # Controls title
    st.sidebar.title("Controls")

    # Load initial variables
    year_min, year_max, hour_min, hour_max = get_variables()
    
    with st.sidebar.container():

        if view == 'Map':

            # Select chart type dropdown
            chart_type = st.selectbox(label="Select Chart Type", options=("Choropleth", "Markers"), index=0)

        st.header("Range Filters")

        # Define the range of years for the multi-slider
        range_years = st.slider("Select Year Range", year_min, year_max, (year_min, year_max), 1)

        # Define Hours Range
        range_hours = st.slider("Select Hour Range", hour_min, hour_max, (hour_min, hour_max), 1)

        st.header("Country Selection")

        # Get country lists based on year and hour ranges
        countries, countries_ranked = get_country_dropdowns(range_years[0], range_years[1], range_hours[0], range_hours[1])

        # Multi-select countries
        country_incl = st.multiselect(label='Select Countries to Include', options=countries)

        # Multi-Select countries to exclude -> Ordered by countries with highest counts
        country_excl = st.multiselect(label='Select Countries to Exclude', options=countries_ranked)

        st.header("Additional Filters")

        # Get the seasons and ufo_shape lists based on the year and hour ranges
        seasons, ufo_shape = get_dependent_dropdowns(range_years[0], range_years[1], range_hours[0], range_hours[1], country_incl, country_excl)

        # Multi-Select UFO Shape
        ufo_option = st.multiselect(label='Select UFO Shape', options=ufo_shape)
        
        # Multi-Select Season
        season = st.multiselect(label='Select Season', options=seasons)

    # Filter the data based on the selections
    df = filter_data(range_years, ufo_option, season, range_hours, country_incl, country_excl)

    with st.sidebar.container():
        # Display count of sightings
        st.metric('Count Sightings', value=df.shape[0])

    with st.sidebar.container():
        # URL links to external sites
        st.write("[Buy me a coffee](https://www.buymeacoffee.com/jon.wright)")
        st.write("[GitHub](https://github.com/jonwright13/ufo-sightings)")

    if view == 'Map':

        st.dataframe(pd.DataFrame(df['Country'].value_counts()).T, height=80)
        get_map(df, tile=chart_type)    # Generate the map

    elif view == 'Chart':

        col1, col2 = st.columns(2)
        col1.write("Sightings per Year")
        col1.line_chart(df['Year'].value_counts())
        col2.write("Sightings per Month")
        col2.line_chart(df['Month'].value_counts())

        country_chart_selection = col1.selectbox(label="Select Top or Bottom 10 Countries", options=["Top 10", "Bottom 10"])
        col1.pyplot(ten_countries(df, country_chart_selection))
        
        ufo_chart_selection = col2.selectbox(label="Select Top or Bottom 10 UFO Shapes", options=["Top 10", "Bottom 10"])
        col2.pyplot(ten_ufos(df, ufo_chart_selection))

        col1.pyplot(ufo_dist_by_season(df))
        col2.pyplot(season_pie_chart(df))

    elif view == 'Table':
        
        display_table(df) # Display the table of data

if __name__ == "__main__":
    main()