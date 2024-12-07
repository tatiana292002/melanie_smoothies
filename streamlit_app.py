import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Create the connection to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get the fruit data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert the Snowflake dataframe to pandas for easier manipulation
pd_df = my_dataframe.to_pandas()

# Display the available fruits in a multiselect dropdown
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Display the selected ingredients
if ingredients_list:
    ingredients_string = ''

    # Loop through the selected ingredients to create the smoothie
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Fetch the SEARCH_ON value from the dataframe
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display nutritional info using the SmoothieFroot API
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if smoothiefroot_response.status_code == 200:
            st.json(smoothiefroot_response.json())
        else:
            st.write(f"Could not retrieve data for {fruit_chosen}.")

# Input field for the name on the smoothie order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Button to submit the order
if st.button('Submit Order'):
    if ingredients_list and name_on_order:
        # Insert the order into Snowflake
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your order has been placed successfully!')
    else:
        st.error('Please select ingredients and enter a name on your smoothie order.')



    
  

