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

# Fetch data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop


ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:
    ingredients_string = '' 
    
    for fruit_chosen in ingredients_list:
ingredients_string + fruit_chosen +
search_on=pd_df.loc [pd_df ['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0] st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
st.subheader (fruit_chosen Nutrition Information')
fruityvice response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)

      
