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
st.dataframe(pd_df)

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Use the list of fruit names from Pandas DataFrame
    max_selections=5
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ''  # Initialize the ingredients string

    for fruit_chosen in ingredients_list:
        # Concatenate selected ingredients to the string
        ingredients_string += fruit_chosen + ', '

        # Get the SEARCH_ON value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display the selected fruit's nutrition information
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # Make API request using the SEARCH_ON value
            smoothiefroot_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            if smoothiefroot_response.status_code == 200:
                # Display the API response as a DataFrame
                sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"Could not fetch data for {fruit_chosen}. API responded with status: {smoothiefroot_response.status_code}")
        except Exception as e:
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
