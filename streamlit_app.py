import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
    "https://media.githubusercontent.com/media/Javortper/NY_traffic/main/crash_data.csv"
)

st.title("Colisiones de vehiculos en la ciudad de Nueva York")
st.markdown("Esta aplicación es un dashboard basado en Streamlist usada para analizar los accidentes de traficos en NY 🗽")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[["CRASH DATE", "CRASH TIME"]])
    #Si inplace está activo la función no retorna los datos modificados, lo hace en la misma
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    no_spaces = lambda x: str(x).replace(" ", "_")
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(no_spaces, axis="columns", inplace=True)
    return data

data = load_data(10000)
original_data = data

st.header("¿Dónde ha sido el accidente con mayor número de personas implicadas?")
injured_people = st.slider("", 0, 16)
st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))
st.header(" ")

st.header("¿Cuantos choques ocurren a una hora determinada?")
hour = st.slider("Hora", 0, 23)
data = data[data['crash_date_crash_time'].dt.hour==hour]

st.markdown("Choques entre las {}:00 y las {}:00".format(hour, (hour+1)%24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.header("ESTE MAPA NO FUNCIONA BIEN, SE CRASHEA. EL RESTO DE COSAS VAN BIEN")
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,  
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data = data[['crash_date_crash_time','latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            get_color='[10, 255, 255, 160]',
            extruded=True,
            pickable=True,
            elevation_scale=3,
            elevation_range=[0,1000],
        ),
    ],
))

st.subheader("Desglose por minutos entre las {} y las {}".format(hour, (hour+1)%24))
hist = np.histogram(data['crash_date_crash_time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(0, 60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)


st.header(" ")
st.header("Top 5 de calles peligrosas según el tipo de afectado")
select = st.selectbox('Tipo de persona afectada', ['Peatón', 'Ciclista', 'Motorista'])

if select=='Peatón':
    st.write(original_data.query("number_of_pedestrians_injured >= 1")[['on_street_name', 'number_of_pedestrians_injured']].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how='any')[:5])
elif select=='Ciclista':
    st.write(original_data.query("number_of_cyclist_injured >= 1")[['on_street_name', 'number_of_cyclist_injured']].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how='any')[:5])
elif select=='Motorista':
    st.write(original_data.query("number_of_motorist_injured >= 1")[['on_street_name', 'number_of_motorist_injured']].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how='any')[:5])

st.header(" ")
st.header("Raw data")
raw_data = st.checkbox("Raw data", True)
if raw_data:
    st.dataframe(data)