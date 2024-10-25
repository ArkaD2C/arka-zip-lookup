import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import streamlit as st

# Load spreadsheet data
data = pd.ExcelFile('D2CARKA_ACTIVE_ZIP_LIST[10.25.2024].xlsx')
active_zipcodes = pd.read_excel(data, 'Active Zipcodes')
zipcode_database = pd.read_excel(data, 'Zipcode Database Lookup')

# Setting up the geolocator
geolocator = Nominatim(user_agent="arka_zip_lookup_tool")

# Utility function to get coordinates for a given zipcode
def get_coordinates(zipcode):
    location = geolocator.geocode(f"{zipcode}, USA")
    if location:
        return (location.latitude, location.longitude)
    return None

# Function to calculate the closest active zipcode and its distance
def calculate_closest_zip(zipcode):
    input_coords = get_coordinates(zipcode)
    if not input_coords:
        return None, None

    min_distance = float('inf')
    closest_zip = None

    for _, row in active_zipcodes.iterrows():
        active_zip = row['Zipcode']
        active_coords = get_coordinates(active_zip)
        if active_coords:
            distance = geodesic(input_coords, active_coords).miles
            if distance < min_distance:
                min_distance = distance
                closest_zip = active_zip

    return closest_zip, min_distance

# Streamlit UI setup
st.title("ARKA ENERGY D2C Active Zip Code Lookup Tool")

# Zipcode Input
zipcode = st.text_input("Enter Zipcode:")
if zipcode:
    if int(zipcode) in active_zipcodes['Zipcode'].values:
        st.markdown("<h1 style='color:green; background-color:#DFF2BF;'>IN TERRITORY 👍</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='color:red; background-color:#FFBABA;'>NOT IN TERRITORY 👎</h1>", unsafe_allow_html=True)
        closest_zip, distance = calculate_closest_zip(zipcode)
        if closest_zip:
            st.write(f"Closest Active Zipcode: {closest_zip} ({distance:.2f} miles away)")
            st.map(pd.DataFrame([get_coordinates(zipcode), get_coordinates(closest_zip)], columns=['lat', 'lon']))

# City Input
city = st.text_input("Enter City:")
if city:
    location = geolocator.geocode(f"{city}, USA")
    if location:
        city_zipcode = zipcode_database[zipcode_database['City'].str.contains(city, case=False, na=False)]
        if not city_zipcode.empty:
            found_zip = city_zipcode.iloc[0]['Zipcode']
            if found_zip in active_zipcodes['Zipcode'].values:
                st.markdown(f"<h1 style='color:green; background-color:#DFF2BF;'>IN TERRITORY - Closest Zipcode: {found_zip} 👍</h1>", unsafe_allow_html=True)
            else:
                closest_zip, distance = calculate_closest_zip(found_zip)
                st.markdown(f"<h1 style='color:red; background-color:#FFBABA;'>NOT IN TERRITORY 👎</h1>", unsafe_allow_html=True)
                if closest_zip:
                    st.write(f"Closest Active Zipcode: {closest_zip} ({distance:.2f} miles away)")

# State Input
state = st.text_input("Enter State:")
if state:
    state_zipcodes = zipcode_database[zipcode_database['State'].str.contains(state, case=False, na=False)]
    if not state_zipcodes.empty:
        active_in_state = state_zipcodes[state_zipcodes['Zipcode'].isin(active_zipcodes['Zipcode'])]
        if not active_in_state.empty:
            st.markdown(f"<h1 style='color:green; background-color:#DFF2BF;'>IN TERRITORY 👍</h1>", unsafe_allow_html=True)
            st.write("Active Zipcodes in State:")
            st.write(active_in_state[['Zipcode', 'City']])
        else:
            st.markdown(f"<h1 style='color:red; background-color:#FFBABA;'>NOT IN TERRITORY 👎</h1>", unsafe_allow_html=True)
            closest_zip, distance = calculate_closest_zip(state_zipcodes.iloc[0]['Zipcode'])
            if closest_zip:
                st.write(f"Closest Active Zipcode: {closest_zip} ({distance:.2f} miles away)")
