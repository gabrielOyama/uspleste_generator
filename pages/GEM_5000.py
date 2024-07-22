import pandas as pd
import streamlit as st
import plotly.express as px
import utm
import os

# Function to convert percentages to floats
def percentage_to_float(x):
    try:
        if isinstance(x, str):
            x = x.replace('O', '0').replace('o', '0')
        if isinstance(x, str) and '%' in x:
            return float(x.replace(',', '.').strip('%')) / 100
        x = float(x)
    except Exception as e:
        print(e)
        return 0
    return x

# Function to convert UTM coordinates to latitude and longitude
def utm_to_latlon(easting, northing, zone_number=23, zone_letter='K'):
    lat, lon = utm.to_latlon(easting, northing, zone_number, zone_letter)
    return lat, lon

# Custom date parser function
def custom_date_parser(date_str):
    try:
        date_str = date_str.replace(' ', '')
        return pd.to_datetime(date_str.strip(), format='%m_%d_%Y')
    except ValueError:
        return pd.NaT

# Caching the data loading function to improve performance
@st.cache_data
def load_data():
    if not os.path.exists('amostragem_GEM.xlsx') or not os.path.exists('amostragem_GEM_2015.xlsx'):
        st.error('Os arquivos de dados não foram encontrados.')
        return None, None

    df_coordenadas = pd.read_excel('amostragem_GEM.xlsx', sheet_name='Coordenadas', skiprows=1)
    df_coordenadas[['latitude', 'longitude']] = df_coordenadas.apply(lambda row: utm_to_latlon(row['x'], row['y']),
                                                                     axis=1, result_type='expand')

    xls = pd.ExcelFile('amostragem_GEM_2015.xlsx')
    nomes = xls.sheet_names
    st.error(str(nomes))
    st.error(df_coordenadas)
    df_consolidado = pd.DataFrame()
    for nome in nomes:
        try:
            df = pd.read_excel('amostragem_GEM_2015.xlsx', sheet_name=nome)
            if 'id' not in df.columns:
                st.error(f"A coluna 'id' não está presente na planilha: {nome}")
                continue
            df = df.drop_duplicates(subset='id', keep='last')
            df = df.drop(columns=['Z', 'zona'], errors='ignore')
            melted_df = pd.melt(df, id_vars=['id'], var_name='data', value_name=nome)
            melted_df[nome] = melted_df[nome].apply(percentage_to_float)
            if len(df_consolidado) == 0:
                df_consolidado = melted_df
            else:
                df_consolidado = pd.merge(left=df_consolidado, right=melted_df, how='outer', on=['id', 'data'])
        except Exception as e:
            st.error(f"Erro ao processar a planilha: {nome}. Erro: {e}")

    if 'id' not in df_consolidado.columns:
        st.error("A coluna 'id' não foi encontrada nos dados consolidados.")
        return None, None

    df_final = pd.merge(left=df_consolidado, right=df_coordenadas, how='left', on='id')
    df_final['data'] = df_final['data'].apply(custom_date_parser)
    return df_final, nomes

# Load data and list of variable names
df_final, nomes = load_data()

if df_final is not None and nomes is not None:
    # Continue with the rest of your Streamlit app layout and functionality
    st.header("Visão geoespacial")
    selected_variable = st.selectbox("Select variable to plot", sorted(nomes), key="scatter_variable")
    df_final['week'] = df_final['data']
    selected_week = st.selectbox("Select week", sorted(df_final['week'].dropna().unique()), key="scatter_week")

    col1, col2 = st.columns([1, 1])

    with col1:
        plot_scatter = st.button("Plot gráfico")
    with col2:
        download_file = st.download_button(
            label="Baixar NETCDF",
            data=get_local_file(),
            file_name="GRUGEM1N1.B0.20150105.000000.nc",
            mime="application/netcdf"
        )

    if plot_scatter:
        filtered_data = df_final[df_final['week'] == selected_week]
        fig = plot_scatter_data(filtered_data, selected_variable)
        st.plotly_chart(fig, use_container_width=True)

        avg_value, num_sensors, max_value_sensor, max_value, num_sensors_no_data = calculate_statistics(filtered_data, selected_variable)
        st.markdown(
            f"""
            <div style='border: 1px solid #ccc; padding: 10px; border-radius: 5px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <p style='font-size: 12px;'>Average {selected_variable}</p>
                        <p style='font-size: 16px;'>{avg_value:.2f}</p>
                    </div>
                    <div>
                        <p style='font-size: 12px;'>Number of sensors</p>
                        <p style='font-size: 16px;'>{num_sensors}</p>
                    </div>
                    <div>
                        <p style='font-size: 12px;'>Highest value sensor</p>
                        <p style='font-size: 16px;'>ID {max_value_sensor}: {max_value:.2f}</p>
                    </div>
                    <div>
                        <p style='font-size: 12px;'>Sensors without data</p>
                        <p style='font-size: 16px;'>{num_sensors_no_data}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    st.header("Visão linear")
    selected_variable_line = st.selectbox("Select variable to plot over time", sorted(nomes), key="line_variable")
    selected_location = st.selectbox("Select location (ID)", sorted(df_final['id'].unique()), key="line_location")

    if st.button("Plotar gráfico linear"):
        fig = plot_line_data(df_final, selected_variable_line, selected_location)
        st.plotly_chart(fig, use_container_width=True)

        location_data = df_final[df_final['id'] == selected_location]
        avg_value, num_sensors, max_value_sensor, max_value, num_sensors_no_data = calculate_statistics(location_data, selected_variable_line)
        st.markdown(
            f"""
            <div style='border: 1px solid #ccc; padding: 10px; border-radius: 5px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <p style='font-size: 12px;'>Average {selected_variable_line}</p>
                        <p style='font-size: 16px;'>{avg_value:.2f}</p>
                    </div>
                    <div>
                        <p style='font-size: 12px;'>Number of sensors</p>
                        <p style='font-size: 16px;'>{num_sensors}</p>
                    </div>
                    <div>
                        <p style='font-size: 12px;'>Highest value sensor</p>
                        <p style='font-size: 16px;'>ID {max_value_sensor}: {max_value:.2f}</p>
                    </div>
                    <div>
                        <p style='font-size: 12px;'>Sensors without data</p>
                        <p style='font-size: 16px;'>{num_sensors_no_data}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown(create_download_link(fig, f'{selected_variable_line} over Time at Location {selected_location}'), unsafe_allow_html=True)

    st.header("Visão tabular")
    selected_dataframe_variable = st.selectbox("Select variable to view dataframe", sorted(nomes), key="dataframe_variable")

    if st.button("Mostrar dataset"):
        df = pd.read_excel('amostragem_GEM_2015.xlsx', sheet_name=selected_dataframe_variable)
        st.write(df)
