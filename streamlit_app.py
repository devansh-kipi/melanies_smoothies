import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake session setup
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit list from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
fruit_names = my_dataframe["FRUIT_NAME"].tolist()

# Multiselect input
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_names, max_selections=5)

# Display nutrition info if fruits are selected
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')

        # Call SmoothieFroot API using fruit name
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}")

        # If found, display in dataframe. If not, show fallback message
        if smoothiefroot_response.status_code == 200:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Sorry, {fruit_chosen} is not in our database.")

    # Display nutrition info in a DataFrame
    if all_nutrition_data:
        st.dataframe(data=all_nutrition_data, use_container_width=True)

    # Insert into database
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        insert_stmt = f"INSERT INTO smoothies.public.orders(ingredients) VALUES ('{ingredients_string}')"
        session.sql(insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
