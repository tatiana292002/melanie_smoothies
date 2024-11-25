# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Application title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

# Input for Smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()


my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

pd_df=my_dataframe.to_pandas ()
st.dataframe (pd_df)
st.stop()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.collect(),  # Ensure proper format for Streamlit
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # Call API for fruit nutrition info
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
            if smoothiefroot_response.status_code == 200:
                sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"Could not fetch data for {fruit_chosen}. API responded with status: {smoothiefroot_response.status_code}")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Insert order into Snowflake table
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                         VALUES ('{ingredients_string.strip()}', '{name_on_order}')"""
    try:
        session.sql(my_insert_stmt).collect()
        st.success("Order has been placed successfully!")
    except Exception as e:
        st.error(f"Error inserting order: {e}")

