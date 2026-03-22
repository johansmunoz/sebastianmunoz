import pandas as pd
import json
import os

def excel_to_json(excel_path, output_folder="data"):
    # Leer las hojas del Excel
    general_df = pd.read_excel(excel_path, sheet_name="general")
    kpis_df = pd.read_excel(excel_path, sheet_name="kpis")
    trimestres_df = pd.read_excel(excel_path, sheet_name="trimestres")

    # Reemplazar NaN por strings vacíos 
    general_df = general_df.fillna("")
    kpis_df = kpis_df.fillna("")
    trimestres_df = trimestres_df.fillna("")

    # -----------------------------
    # 1. Procesar hoja "general"
    # -----------------------------
    company_info = {
        row["campo"]: row["valor"]
        for _, row in general_df.iterrows()
    }

    # -----------------------------
    # 2. Procesar hoja "kpis"
    # -----------------------------
    kpis = {
        row["kpi"]: row["valor"]
        for _, row in kpis_df.iterrows()
    }

    # -----------------------------
    # 3. Procesar hoja "trimestres"
    # -----------------------------
    quarters = []
    metrics = trimestres_df["metric"].tolist()
    periods = trimestres_df.columns[1:]  # Todas las columnas excepto "metric"

    for period in periods:
        quarter_data = {"period": period}
        for i, metric in enumerate(metrics):
            quarter_data[metric] = trimestres_df.loc[i, period]
        quarters.append(quarter_data)

    # -----------------------------
    # 4. Construir JSON final
    # -----------------------------
    final_json = {
        "company": company_info,
        "kpis": kpis,
        "quarters": quarters
    }

    # -----------------------------
    # 5. Guardar JSON en carpeta /data
    # -----------------------------
    os.makedirs(output_folder, exist_ok=True)

    company_name = company_info.get("nombre", "empresa").lower().replace(" ", "-")
    output_path = os.path.join(output_folder, f"{company_name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=4, ensure_ascii=False)

    print(f"JSON generado correctamente: {output_path}")


# -----------------------------
# EJEMPLO DE USO
# -----------------------------
if __name__ == "__main__":
    excel_to_json("BOGOTA/BOGOTA.xlsx")
