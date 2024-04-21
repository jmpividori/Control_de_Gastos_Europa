import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import datetime as dt
import matplotlib.pyplot as plt


# Configuración de la página
st.set_page_config(page_title="Tablero de Control de Gastos")  # Nombre para configurar la página web

# Estilos CSS para el título
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-family: 'Arial', sans-serif;
        font-size: 32px;
        font-weight: bold;
        color: #000000; /* Color negro */
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título centrado y con estilos personalizados
st.markdown('<p class="title">Análisis de Gastos</p>', unsafe_allow_html=True)
st.subheader("", divider="grey")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing records data
df = conn.read(worksheet="DB", usecols=list(range(5)), ttl=5)
df.dropna(how="all")

#### Metricas financieras#####

# Filtrar y calcular ingreso total
ingreso_total = df[df['Tipo'] == "Ingreso"]['Monto'].sum()
# Filtrar y calcular gasto total
gasto_total = df[df['Tipo'] == "Egreso"]['Monto'].sum()
# Calcular ahorro total
ahorro_total = ingreso_total - gasto_total

# Determinar el color de fondo para la tarjeta de Ahorro
color_ahorro = "lightgreen" if ahorro_total >= 0 else "lightcoral"

# Mostrar las métricas en tarjetas con estilos personalizados
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader(" Ingreso Total :chart_with_upwards_trend:")
    st.markdown(f'<div style="border: 1px solid #ccc; padding: 10px; text-align: center; font-weight: bold;">${ingreso_total:,.2f}</div>', unsafe_allow_html=True)

with col2:
    st.subheader(" Gasto Total :chart_with_downwards_trend:")
    st.markdown(f'<div style="border: 1px solid #ccc; padding: 10px; text-align: center; font-weight: bold;">${gasto_total:,.2f}</div>', unsafe_allow_html=True)

with col3:
    st.subheader(" Ahorro Total :moneybag:")
    st.markdown(f'<div style="border: 1px solid #ccc; padding: 10px; text-align: center; font-weight: bold; background-color: {color_ahorro};">{ahorro_total:,.2f}</div>', unsafe_allow_html=True)

st.subheader("", divider="grey")
############################
# Evolución en el tiempo para el gráfico de líneas
# Convertir la columna 'Fecha' a tipo datetime y crear la columna 'Mes'
df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
df['Mes'] = df['Fecha'].dt.to_period('M')

# Ordenar el DataFrame por fecha para asegurar el orden en el gráfico de líneas
df = df.sort_values(by='Fecha')

# Calcular sumas por categoría para el gráfico de torta
df_egreso = df[df['Tipo'] == "Egreso"]
sum_categorias = df_egreso.groupby('Categoria')['Monto'].sum()


# Calcular sumas por mes y tipo (Ingreso/Egreso) para el gráfico de líneas
ingresos_egresos = df.pivot_table(index='Mes', columns='Tipo', values='Monto', aggfunc='sum', fill_value=0)
ingresos_egresos['Ahorros'] = ingresos_egresos['Ingreso'] - ingresos_egresos['Egreso']

# Crear gráfico de torta (suma de montos por categoría)
fig1, ax1 = plt.subplots()
wedges, texts, autotexts = ax1.pie(sum_categorias, labels=None, autopct='%1.1f%%', startangle=90)

# Modificar color de los números (autotexts) a blanco
for autotext in autotexts:
    autotext.set_color('white')

# Crear leyenda personalizada fuera del gráfico
legend_labels = [f'{label}: {value:.1f}%' for label, value in zip(sum_categorias.index, sum_categorias / sum_categorias.sum() * 100)]
ax1.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

ax1.set_title('Distribución de Gastos por Categoría', weight='bold', pad=20, fontsize=16)

# Calcular sumas por mes y tipo (Ingreso/Egreso) para el gráfico de líneas
ingresos_egresos.index = ingresos_egresos.index.astype(str)

# Crear gráfico de líneas (evolución en el tiempo de ingresos, egresos y ahorros)
fig2, ax2 = plt.subplots()
ax2.plot(ingresos_egresos.index, ingresos_egresos['Ingreso'], label='Ingresos', marker='o')
ax2.plot(ingresos_egresos.index, ingresos_egresos['Egreso'], label='Egresos', marker='x')
ax2.plot(ingresos_egresos.index, ingresos_egresos['Ahorros'], label='Ahorros', marker='s')
ax2.set_xlabel('Mes')
ax2.set_ylabel('Monto')
ax2.set_title('Evolución Mensual de Ingresos, Egresos y Ahorros', weight='bold', pad=20, fontsize=16)
ax2.legend()

# Dividir la pantalla en dos columnas
col1, col2 = st.columns(2)

# Mostrar el gráfico de torta en la primera columna
with col1:
    st.pyplot(fig1)

# Mostrar el gráfico de líneas en la segunda columna
with col2:
    st.pyplot(fig2)

st.subheader("", divider="grey")

# Widget para seleccionar el mes

# Convertir la columna de fecha a tipo datetime
df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')

# Obtener meses únicos en español ordenados
meses_unicos_esp = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]

# Widget para seleccionar el mes en español
mes_seleccionado_esp = st.selectbox('Selecciona un mes:', meses_unicos_esp)

# Obtener el índice numérico del mes seleccionado en español (1 para enero, 2 para febrero, etc.)
indice_mes_seleccionado = meses_unicos_esp.index(mes_seleccionado_esp) + 1

# Filtrar datos por el mes seleccionado
df = df[df['Tipo'] == "Egreso"]
df_filtrado = df[df['Fecha'].dt.month == indice_mes_seleccionado].dropna(subset=['Fecha'])

# Verificar el DataFrame de Categorías después del filtro
df_Cat = df_filtrado.groupby(['Categoria'], as_index=False)['Monto'].sum()

# Crear gráfico de pastel (pie chart) con Plotly Express
if not df_filtrado.empty:
    pie_chart = px.pie(df_Cat,
                       title=f'Distribución de gastos en {mes_seleccionado_esp.capitalize()}',
                       values='Monto',
                       names='Categoria',
                       hole=0)  # Agregar un agujero al gráfico (opcional)

# Configurar el diseño del título del gráfico
    pie_chart.update_layout(
        title={'text': f'Distribución de gastos en {mes_seleccionado_esp.capitalize()}', 'x': 0.5, 'y': 0.95, 'xanchor': 'center', 'yanchor': 'top', 'font_size': 24}
    )
    # Mostrar el gráfico interactivo en Streamlit
    st.plotly_chart(pie_chart)
else:
    st.warning(f"No hay datos disponibles para {mes_seleccionado_esp.capitalize()}.")

st.subheader("", divider="grey")