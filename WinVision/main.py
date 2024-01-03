import pandas as pd
import streamlit as st
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import time
import seaborn as sns
import plotly.express as px
import numpy as np
import requests

circuits = pd.read_csv(r"archive\circuits.csv")
constructor_results = pd.read_csv(r"archive\constructor_results.csv")
constructor_standings = pd.read_csv(r"archive\constructor_standings.csv")
constructors = pd.read_csv(r"archive\constructors.csv")
driver_standings = pd.read_csv(r"archive\driver_standings.csv")
drivers = pd.read_csv(r"archive\drivers.csv")
lap_times = pd.read_csv(r"archive\lap_times.csv")
pit_stops = pd.read_csv(r"archive\pit_stops.csv")
qualifying = pd.read_csv(r"archive\qualifying.csv")
races = pd.read_csv(r"archive\races.csv")
results = pd.read_csv(r"archive\results.csv")
seasons = pd.read_csv(r"archive\seasons.csv")
sprint_results = pd.read_csv(r"archive\sprint_results.csv")
status = pd.read_csv(r"archive\status.csv")


def loading_animation():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://i.redd.it/dux4xq5v0zs41.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
    
     
    animation_url="https://lottie.host/118405f5-61a3-4d07-bca6-15a28250fb30/CB7vIRAs6z.json"
    st.markdown("<h1 style='text-align: center; color: white;'> WinVision </h1>", unsafe_allow_html=True)
    with st.expander("Description"):
        st.info("""Start your engines and rev up your analysis at WinVision! Set the parameters for your Formula 1 data ride and let the checkered flag drop on insights as fast as a pit stop.""")
    with st.expander("Team WinVision"):
        st.info("""Shivain Singh, Parth Passi, Daksh Rawat, Agneya Mishra""")
    img = st_lottie("https://lottie.host/3248f1e9-c2c3-4f14-b793-92ff84a0b25b/xugqbfeSMP.json")
    
    st.write("Loading...")
    with st.spinner(" "):
        time.sleep(3)
        st.success("Loading complete!")
        main_page()

def main_page():
    selected_driver = st.sidebar.selectbox("Select Driver", drivers["forename"] + " " + drivers["surname"])
    selected_constructor = st.sidebar.selectbox("Select Constructor", constructors["name"])
    selected_year = st.sidebar.selectbox("Select Year", races["year"].unique())
    user_choice_circuit = st.sidebar.checkbox("Filter by Circuit")
    
    races_df = races.copy()
    races_df = races_df[races_df["year"] == selected_year]
    races_df = races_df.drop(columns = ['url',
       'fp1_date', 'fp1_time', 'fp2_date', 'fp2_time', 'fp3_date', 'fp3_time',
       'quali_date', 'quali_time', 'sprint_date', 'sprint_time', 'time'])
    races_df = races_df.rename(columns ={'name':'race_name'})

    circuits_df = circuits.copy()
    circuits_df =circuits_df.drop(columns = ['lat', 'lng','alt', 'url'])
    circuits_df = circuits_df.rename(columns={'name':'circuit_name', 'location':'city'})

    drivers_df = drivers.copy()
    drivers_df =drivers_df.drop(columns =['driverRef', 'number', 'code', 'url'])
    drivers_df['driver_name'] = drivers_df['forename'] + ' ' + drivers_df['surname']
    drivers_df = drivers_df.drop(columns =['forename', 'surname'])

    constructors_df=constructors.copy()
    constructors_df =constructors_df.drop(columns = ['url','constructorRef'])
    constructors_df = constructors_df.rename(columns = {'name':'constructors_name'})

    results_copy_df = results.copy()

    merged_df = results_copy_df.merge(status , on = 'statusId')
    merged_df = merged_df.merge(races_df, on = 'raceId')
    merged_df = merged_df.merge(drivers_df, on = 'driverId')
    merged_df = merged_df.merge(constructors_df, on = 'constructorId')
    merged_df = merged_df.merge(circuits_df , on = 'circuitId')
    merged_df['year'] = merged_df['year'] = pd.to_datetime(merged_df['date']).dt.year

    selected_driver_id = merged_df.loc[
        (merged_df['driver_name']) == selected_driver, 'driverId'
    ].values[0]

    selected_constructor_id = merged_df.loc[
        merged_df['constructors_name'] == selected_constructor, 'constructorId'
    ].values[0]

    filtered_df = merged_df[
        (merged_df['driverId'] == selected_driver_id) &
        (merged_df['constructorId'] == selected_constructor_id) &
        (merged_df['year'] == selected_year)
    ]

    if user_choice_circuit:
        selected_circuit = st.sidebar.selectbox("Select Circuit", merged_df["circuit_name"])
        selected_circuit_id = merged_df.loc[
            merged_df['circuit_name'] == selected_circuit, 'circuitId'
        ].values[0]

        filtered_df = filtered_df[filtered_df['circuitId'] == selected_circuit_id]

    st.subheader(f"Results for {selected_driver} driving for {selected_constructor} in {selected_year}")
    st.dataframe(filtered_df[['race_name', 'date', 'circuit_name', 'position', 'points', 'laps', 'time', 'status']])

    st.subheader(f"Results for {selected_constructor} in {selected_year}")
    constructor_results_df = constructor_results.merge(races_df, on='raceId')
    constructor_results_df = constructor_results_df[
        (constructor_results_df['constructorId'] == selected_constructor_id) &
        (constructor_results_df['year'] == selected_year)
    ]
    st.dataframe(constructor_results_df[['race_name', 'points', 'year',"date"]])

    if st.checkbox("Show Constructor Points Across Races"):
        selected_races_constructor = st.multiselect("Select Races", constructor_results_df["race_name"].unique())
        fig_constructor_points = px.bar(
            constructor_results_df[constructor_results_df['race_name'].isin(selected_races_constructor)],
            x='race_name',
            y='points',
            color="race_name",
            title=f'Constructor Points Across Races ({selected_year})',
            labels={'points': 'Points'},
            hover_data=['points', 'date'],
        )
        st.plotly_chart(fig_constructor_points)

    if st.checkbox("Show Driver Distribution by Nationality"):
        selected_nationalities = st.multiselect("Select Nationalities", drivers_df["nationality"].unique())
        filtered_drivers_df = drivers_df[drivers_df['nationality'].isin(selected_nationalities)]
        fig_driver_nationality = px.pie(
            filtered_drivers_df,
            names='nationality',
            title='Driver Distribution by Nationality',
        )
        st.plotly_chart(fig_driver_nationality)
    if st.checkbox("Show Lap Times vs. Race Position"):
        selected_drivers_lap_time = st.multiselect("Select Drivers", filtered_df["driver_name"].unique())
        fig_lap_time_position = px.scatter(
            filtered_df[filtered_df['driver_name'].isin(selected_drivers_lap_time)],
            x='position',
            y='time',
            color='race_name',
            size='laps',
            title='Lap Times vs. Race Position',
            labels={'time': 'Lap Time'},
            hover_data=['race_name', 'position', 'time'],
        )
        st.plotly_chart(fig_lap_time_position)

    if st.checkbox("Show Driver Standings Over Races"):
        selected_drivers_standings = st.multiselect("Select Drivers", merged_df["driver_name"].unique())
        fig_driver_standings = px.line(
            merged_df[merged_df['driver_name'].isin(selected_drivers_standings)],
            x='race_name',
            y='points',
            color='driver_name',
            title='Driver Standings Over Races',
            labels={'points': 'Points'},
            hover_data=['points', 'race_name'],
        )
        fig_driver_standings.update_layout(width=1000, height=500) 
        st.plotly_chart(fig_driver_standings)
loading_animation()