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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)  # Display the fruit options to the user

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Populate multiselect with fruit names
    max_selections=5
)

# Submit button
if st.button('Submit Order') and ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Concatenate selected ingredients
    st.write(f"You've chosen: {ingredients_string}")
    
    # Loop through selected fruits to fetch nutrition information
    for fruit_chosen in ingredients_list:
        # Retrieve the corresponding SEARCH_ON value for the selected fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # Fetch data from SmoothieFroot API
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            
            if smoothiefroot_response.status_code == 200 and 'application/json' in smoothiefroot_response.headers.get('Content-Type', ''):
                # Parse and display the JSON response
                st.json(smoothiefroot_response.json())  # Display raw JSON response
            else:
                # Log unexpected responses and provide a fallback message
                st.warning(f"Could not fetch data for {fruit_chosen}. SmoothieFroot API is currently unavailable.")
        except requests.exceptions.RequestException as e:
            # Handle generic request exceptions
            st.error(f"An error occurred while fetching data for {fruit_chosen}: {e}")
    
    # Insert the order into the Snowflake table
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""
    try:
        session.sql(my_insert_stmt).collect()
        st.success("Order has been placed successfully!")
    except Exception as e:
        st.error(f"Error inserting order: {e}")
