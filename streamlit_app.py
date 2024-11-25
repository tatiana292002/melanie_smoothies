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

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Use a list of fruit names
    max_selections=5
)

# Display nutrition information and collect the ingredients string
ingredients_string = ''  # Initialize the ingredients string

if ingredients_list:
    for fruit_chosen in ingredients_list:
        # Concatenate selected ingredients to the string
        ingredients_string += fruit_chosen + ', '

        # Get the SEARCH_ON value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display the selected fruit's nutrition information
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            # Make the API request
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            
            # Check the response status and content type
            if fruityvice_response.status_code == 200 and 'application/json' in fruityvice_response.headers.get('Content-Type', ''):
                # Parse and display the JSON response
                fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
            else:
                # Log unexpected responses
                st.error(f"Could not fetch data for {fruit_chosen}. API responded with status: {fruityvice_response.status_code}")
                st.text(f"Response content: {fruityvice_response.text}")
        except requests.exceptions.JSONDecodeError as e:
            st.error(f"Error decoding JSON for {fruit_chosen}: {e}")
        except Exception as e:
            st.error(f"An error occurred for {fruit_chosen}: {e}")

# Button to submit the order
if st.button("Submit Order"):
    if not name_on_order:
        st.error("Please provide a name for your Smoothie.")
    elif not ingredients_list:
        st.error("Please select at least one ingredient for your Smoothie.")
