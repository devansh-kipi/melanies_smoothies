# Import required packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")


name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)



# Get Snowpark session and fruit names
# session = get_active_session()
cnx=st.connection("snowflake")
session=cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Multiselect input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# Only proceed if something is selected
if ingredients_list:
    ingredients_string = ''

    # Build the ingredients string with space separator
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Prepare the SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients)
        VALUES ('{ingredients_string}')
    """

    # Submit button to trigger insert
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")


import requests
import pandas as pd

# Call the SmoothieFroot API
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Show raw response (optional)
st.text(f"API Response Code: {smoothiefroot_response.status_code}")

# Parse JSON and show as dataframe
if smoothiefroot_response.status_code == 200:
    data = smoothiefroot_response.json()
    sf_df = pd.json_normalize(data)
    st.dataframe(sf_df)
else:
    st.error("Failed to fetch fruit data.")

