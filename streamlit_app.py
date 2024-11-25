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

# Query data from the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Create a list of fruit names for the multiselect widget
fruit_names = pd_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_names,  # Pass the list of fruit names
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Fetch the corresponding SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # Display nutrition information
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
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
