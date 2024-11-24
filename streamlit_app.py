import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Título y descripción de la aplicación
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("""Choose the fruits you want in your custom smoothie!""")

# Solicitar el nombre del pedido
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Obtener opciones de frutas desde la base de datos Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Mostrar la lista de frutas en un multiselect
ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe.to_pandas()['FRUIT_NAME'])

# Mostrar la información nutricional de cada fruta seleccionada
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Crear una cadena con los ingredientes seleccionados
    
    for fruit_chosen in ingredients_list:
        st.subheader(f'{fruit_chosen} Nutrition Information')
        
        # Obtener la información nutricional de la fruta desde la API
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        
        # Mostrar los datos obtenidos de la API como un DataFrame
        if smoothiefroot_response.status_code == 200:
            fruit_data = smoothiefroot_response.json()
            st.dataframe(fruit_data, use_container_width=True)
        else:
            st.error(f"Error retrieving data for {fruit_chosen}")
    
    st.write(f"Your selected ingredients: {ingredients_string}")

# Insertar el pedido en la base de datos Snowflake
my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients)
                     VALUES ('{ingredients_string}')"""

# Botón para confirmar el pedido
time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")


