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
        # Concatenate selected ingredients to the string
        ingredients_string += fruit_chosen + ', '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # Make API request using the SEARCH_ON value
            response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            if response.status_code == 200:
                # Display the API response as a DataFrame
                nutrition_data = response.json()
                st.write(nutrition_data)  # Display raw JSON data for now
            else:
                st.warning(f"Could not fetch data for {fruit_chosen}. API responded with status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Insert order into Snowflake table
    ingredients_string = ingredients_string.strip(', ')  # Remove the trailing comma and space
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""
    try:
        session.sql(my_insert_stmt).collect()
        st.success("Order has been placed successfully!")
    except Exception as e:
        st.error(f"Error inserting order: {e}")


