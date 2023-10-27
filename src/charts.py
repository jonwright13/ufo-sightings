import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def ten_countries(df, selection):

    if selection == "Top 10":
        data = pd.DataFrame(df['Country'].value_counts()).head(10)
    else:
        data = pd.DataFrame(df['Country'].value_counts()).tail(10)

    fig, ax = plt.subplots()
    sns.barplot(x='count', y='Country', data=data, color='b', ax=ax)
    ax.set_ylabel("Countries")
    ax.set_xlabel("Sightings Count")
    ax.set_title("Top 10 Countries")
    return fig

def ten_ufos(df, selection):

    if selection == "Top 10":
        data = pd.DataFrame(df['UFO_shape'].value_counts()).head(10)
    else:
        data = pd.DataFrame(df['UFO_shape'].value_counts()).tail(10)

    fig, ax = plt.subplots()
    sns.barplot(x='count', y='UFO_shape', data=data, color='b', ax=ax)
    ax.set_ylabel("UFO Shapes")
    ax.set_xlabel("Sightings Count")
    ax.set_title("Top 10 UFO Shapes")
    return fig

def bottom_ten_ufos(df):
    
    data = pd.DataFrame(df['UFO_shape'].value_counts()).head(10)

    fig, ax = plt.subplots()
    sns.barplot(x='count', y='UFO_shape', data=data, color='b', ax=ax)
    ax.set_ylabel("UFO Shapes")
    ax.set_xlabel("Sightings Count")
    ax.set_title("Top 10 UFO Shapes")
    return fig

def ufo_dist_by_season(df):

    top_ufos = pd.DataFrame(df['UFO_shape'].value_counts()).head(10)
    print(top_ufos)
    data = df.loc[df['UFO_shape'].isin(top_ufos.index)]
    print(data)

    # Create a stacked bar chart using Seaborn
    plt.figure(figsize=(10, 6))
    sns.set(style="whitegrid")
    sns.countplot(data=data, x='Season', hue='UFO_shape', palette='Set1')

    # Customize the plot
    plt.title("UFO Sightings by Shape and Season")
    plt.xlabel("Season")
    plt.ylabel("Count")
    plt.legend(title="UFO Shape")
    return plt

def season_pie_chart(df):

    data = df['Season'].value_counts()

    # Create a pie chart using Matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3"))
    ax.axis('equal')  # Equal aspect ratio ensures that the pie chart is circular

    # Add a title
    ax.set_title("Distribution of Seasons")

    return fig
