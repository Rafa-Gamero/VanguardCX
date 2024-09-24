from functions import read_data, merge_web_data, clean_data

def main():
    # Leer los datos
    df_demo, df_exp, df_web_pt1, df_web_pt2 = read_data()

    # Fusionar los datos de web
    df_web_merged = merge_web_data(df_web_pt1, df_web_pt2)
    
    # Verificar la presencia de 'client_id' en el DataFrame fusionado de web
    if 'client_id' in df_web_merged.columns:
        # Fusionar df_demo y df_exp con los datos web fusionados
        df_merged = df_web_merged.merge(df_demo, on='client_id', how='left')
        df_merged = df_merged.merge(df_exp, on='client_id', how='left')
    else:
        print("Error: 'client_id' no está en el DataFrame fusionado de web.")
        return
    
    # Limpiar los datos
    cleaned_df = clean_data(df_merged)
    
    # Confirmar que los datos se han limpiado correctamente
    print("Proceso completado. Los datos han sido limpiados y guardados en 'data/cleaned_data.xlsx'.")

if __name__ == "__main__":
    main()
