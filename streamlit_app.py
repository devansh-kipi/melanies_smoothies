import requests
import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import col

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Input: Mark order as filled
is_filled = st.checkbox("Mark order as FILLED")

# Snowflake session setup
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit name and search term from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()
fruit_names = pd_df["FRUIT_NAME"].tolist()

# Multiselect input for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_names, max_selections=5)

# Display nutrition info if fruits are selected
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + ' Nutrition Information')

        # Lookup SEARCH_ON value from pd_df
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if response.status_code == 200:
            st.dataframe(data=response.json(), use_container_width=True)
        else:
            st.error(f"Sorry, {fruit_chosen} is not in our database.")

    # Insert into database
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders(name_on_order, ingredients, order_filled)
            VALUES ('{name_on_order}', '{ingredients_string.strip()}', {is_filled})
        """
        st.write("Running SQL:", insert_stmt)
        session.sql(insert_stmt).collect()

        st.success("Your Smoothie is ordered!", icon="✅")
