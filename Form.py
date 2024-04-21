import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description

st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display centered title and description
st.markdown("<h1 class='title'>Carga de movimientos</h1>", unsafe_allow_html=True)

# Constants
TIPOS = ["Egreso", "Ingreso"]

CATEGORIAS = {
    "Ingreso": ["Salario", "Trabajo particular", "Otro"],
    "Egreso": [
        "Mercado", "Compras", "Alquiler", "Deporte", "Farmacia",
        "Transporte", "Turismo", "Tramites", "Imprevisto"
    ]
}

# State variables
selected_type = st.radio("Tipo*", options=TIPOS)

# Selectbox for categories based on selected type
if selected_type == "Ingreso":
    selected_category = st.selectbox("Categoría*", options=["Seleccione una categoría"] + CATEGORIAS["Ingreso"])
elif selected_type == "Egreso":
    selected_category = st.selectbox("Categoría*", options=["Seleccione una categoría"] + CATEGORIAS["Egreso"])

# Form for new mov registration
with st.form(key="mov_form"):
    Fecha = st.date_input(label="Fecha*", format="DD/MM/YYYY")
    Monto = st.number_input("Monto*", min_value=0.0)
    Descripcion = st.text_area(label="Descripción*")

    # Mark mandatory fields
    st.markdown("**Obligatorio*")

    submit_button = st.form_submit_button(label="Registrar movimiento")

    # If the submit button is pressed
    if submit_button:
        # Validate form fields
        if not Fecha or not selected_type or not selected_category or Monto <= 0 or not Descripcion:
            st.warning("Por favor complete todos los campos obligatorios correctamente.")
        else:
            # Create a new row of mov data
            mov_data = pd.DataFrame({
                "Fecha": [Fecha.strftime("%d-%m-%Y")],
                "Tipo": [selected_type],
                "Categoria": [selected_category],
                "Monto": [Monto],
                "Descripcion": [Descripcion]
            })

            # Establishing a Google Sheets connection
            conn = st.connection("gsheets", type=GSheetsConnection)

            # Fetch existing records data
            existing_data = conn.read(worksheet="DB", usecols=list(range(4)), ttl=5)
            existing_data = existing_data.dropna(how="all")

            # Add the new mov data to the existing data
            updated_df = pd.concat([existing_data, mov_data], ignore_index=True)

            # Update Google Sheets with the new data
            conn.update(worksheet="DB", data=updated_df)

            st.success("Movimiento Registrado Exitosamente")

#st.page_link("dashboard.py", label="Ir al Dashboard", icon="🏠")
st.link_button("Ir al Dashboard", "pages/dashboard.py")