import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def read_data():
    """Lee los archivos de datos desde la carpeta 'data'."""
    df_demo = pd.read_csv('data/df_final_demo.txt', delimiter=',')
    df_exp = pd.read_csv('data/df_final_experiment_clients.txt', delimiter=',')
    df_web_pt1 = pd.read_csv('data/df_final_web_data_pt_1.txt', delimiter=',')
    df_web_pt2 = pd.read_csv('data/df_final_web_data_pt_2.txt', delimiter=',')
    
    print("Columnas en df_final_demo.txt:")
    print(df_demo.columns)
    
    print("Columnas en df_final_experiment_clients.txt:")
    print(df_exp.columns)
    
    print("Columnas en df_final_web_data_pt_1.txt:")
    print(df_web_pt1.columns)
    
    print("Columnas en df_final_web_data_pt_2.txt:")
    print(df_web_pt2.columns)
    
    return df_demo, df_exp, df_web_pt1, df_web_pt2

def merge_web_data(df_web_pt1, df_web_pt2):
    """Fusiona los datos de web_pt1 y web_pt2."""
    merge_columns = ['client_id', 'visitor_id', 'visit_id', 'process_step', 'date_time']
    
    for col in merge_columns:
        if col not in df_web_pt1.columns:
            print(f"Advertencia: La columna '{col}' no está en df_web_pt1")
        if col not in df_web_pt2.columns:
            print(f"Advertencia: La columna '{col}' no está en df_web_pt2")
    
    # Verifica si las columnas de fusión están presentes en ambos DataFrames
    if not all(col in df_web_pt1.columns and col in df_web_pt2.columns for col in merge_columns):
        raise ValueError("No todas las columnas de fusión están presentes en ambos DataFrames.")
    
    return pd.merge(df_web_pt1, df_web_pt2, on=merge_columns, how='outer', suffixes=('_pt1', '_pt2'))

def clean_gender_column(df):
    """Limpia la columna 'gendr'."""
    if 'gendr' in df.columns:
        df['gendr'] = df['gendr'].fillna('U')  # Reemplaza 'nan' con 'U'
        df['gendr'] = df['gendr'].replace('X', 'U')  # Reemplaza 'X' con 'U'
    return df

def clean_data(df_merged):
    """Limpia y organiza los datos del DataFrame fusionado."""
    print("Columnas en df_merged:")
    print(df_merged.columns)
    
    # Limpieza de la columna 'gendr'
    df_merged = clean_gender_column(df_merged)
    
    # Manejo de 'visitor_id'
    if 'visitor_id_pt1' in df_merged.columns and 'visitor_id_pt2' in df_merged.columns:
        df_merged['visitor_id'] = df_merged['visitor_id_pt1'].combine_first(df_merged['visitor_id_pt2'])
    elif 'visitor_id' in df_merged.columns:
        df_merged['visitor_id'] = df_merged['visitor_id']
    else:
        print("Advertencia: Las columnas 'visitor_id_pt1' y 'visitor_id_pt2' no están en df_merged.")
    
    # Eliminación de columnas duplicadas
    cols_to_drop = [col for col in ['visitor_id_pt1', 'visitor_id_pt2'] if col in df_merged.columns]
    df_cleaned = df_merged.drop(columns=cols_to_drop)
    
    # Renombrar columnas
    df_cleaned.columns = [col.replace('_pt1', '_web_pt1').replace('_pt2', '_web_pt2') if col.endswith('_pt1') or col.endswith('_pt2') else col for col in df_cleaned.columns]
    
    # Rellenar valores faltantes
    df_cleaned = df_cleaned.fillna('Desconocido')
    
    # Convertir columnas a numérico, manejando errores
    for column in ['clnt_age', 'bal', 'calls_6_mnth', 'logons_6_mnth']:
        df_cleaned[column] = pd.to_numeric(df_cleaned[column], errors='coerce')
        df_cleaned[column] = df_cleaned[column].fillna(0)
    
    # Asegurarse de que 'clnt_age' sea un entero y no contenga valores extraños
    if 'clnt_age' in df_cleaned.columns:
        df_cleaned['clnt_age'] = pd.to_numeric(df_cleaned['clnt_age'], errors='coerce')  # Convertir a numérico primero
        df_cleaned['clnt_age'] = df_cleaned['clnt_age'].apply(lambda x: x if pd.notna(x) and x > 0 and x == int(x) else pd.NA)  # Manejo de NA y valores no enteros
        df_cleaned['clnt_age'] = df_cleaned['clnt_age'].astype('Int64')  # Convertir a entero con soporte para NA
    
    # Asegurarse de que 'bal' tenga solo dos decimales
    if 'bal' in df_cleaned.columns:
        df_cleaned['bal'] = df_cleaned['bal'].apply(lambda x: round(x, 2) if pd.notna(x) else x)
    
    # Separar la columna 'date_time'
    if 'date_time' in df_cleaned.columns:
        df_cleaned['year'] = pd.to_datetime(df_cleaned['date_time'], errors='coerce').dt.year
        df_cleaned['month'] = pd.to_datetime(df_cleaned['date_time'], errors='coerce').dt.month
        df_cleaned['weekday'] = pd.to_datetime(df_cleaned['date_time'], errors='coerce').dt.day_name()
        df_cleaned['day'] = pd.to_datetime(df_cleaned['date_time'], errors='coerce').dt.day
    
    df_cleaned = df_cleaned.fillna({
        'year': 'Desconocido',
        'month': 'Desconocido',
        'weekday': 'Desconocido',
        'day': 'Desconocido'
    })
    
    # Manejo de la columna 'Variation'
    if 'Variation' in df_cleaned.columns:
        df_cleaned['Variation'] = df_cleaned['Variation'].fillna('Desconocido')  # Rellenar NaN con 'Desconocido'
        df_cleaned['Variation'] = df_cleaned['Variation'].replace({'Test': 'Prueba', 'Control': 'Controlado'})  # Opcional: Renombrar valores
    
    # Crear gráficos
    plot_data(df_cleaned)
    
    # Guardar el DataFrame limpio en un archivo Excel
    df_cleaned.to_excel('data/cleaned_data.xlsx', index=False)
    print("Datos limpiados y guardados en 'data/cleaned_data.xlsx'.")
    
    return df_cleaned

def plot_data(df):
    """Genera gráficos a partir del DataFrame limpio."""
    sns.set(style="whitegrid")

    # Gráfico de distribución de edades
    plt.figure(figsize=(10, 6))
    sns.histplot(df['clnt_age'].dropna(), bins=20, kde=True)
    plt.title('Distribución de Edades de los Clientes')
    plt.xlabel('Edad')
    plt.ylabel('Frecuencia')
    plt.grid(True)
    plt.savefig('data/age_distribution.png')
    plt.show()
    plt.close()

    # Gráfico de balance promedio por género
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='gendr', y='bal', estimator='mean')
    plt.title('Balance Promedio por Género')
    plt.xlabel('Género')
    plt.ylabel('Balance Promedio')
    plt.grid(True)
    plt.savefig('data/balance_by_gender.png')
    plt.show()
    plt.close()

    # Gráfico de número de clientes por variación del experimento
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Variation')
    plt.title('Número de Clientes por Variación del Experimento')
    plt.xlabel('Variación')
    plt.ylabel('Número de Clientes')
    plt.grid(True)
    plt.savefig('data/clients_by_variation.png')
    plt.show()
    plt.close()

    # Gráfico de número de clientes en cada paso del proceso
    plt.figure(figsize=(12, 7))
    sns.countplot(data=df, x='process_step')
    plt.title('Número de Clientes en Cada Paso del Proceso')
    plt.xlabel('Paso del Proceso')
    plt.ylabel('Número de Clientes')
    plt.grid(True)
    plt.savefig('data/clients_process_step.png')
    plt.show()
    plt.close()
