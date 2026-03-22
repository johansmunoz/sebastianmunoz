import pandas as pd
import json
import os
import unicodedata
import re


# ============================================================
# Función para crear slugs limpios
# ============================================================
def slugify(text):
    text = text.lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# ============================================================
# Convertir un Excel → JSON individual
# ============================================================
def excel_to_json(excel_path, output_folder="data"):
    # Leer hojas
    general_df = pd.read_excel(excel_path, sheet_name="general").fillna("")
    kpis_df = pd.read_excel(excel_path, sheet_name="kpis").fillna("")
    trimestres_df = pd.read_excel(excel_path, sheet_name="trimestres").fillna("")

    # -----------------------------
    # 1. Procesar hoja "general"
    # -----------------------------
    company_info = {
        row["campo"]: row["valor"]
        for _, row in general_df.iterrows()
    }

    nombre = company_info.get("nombre", "empresa")
    sector = company_info.get("sector", "Otros")
    logo = company_info.get("logo", "")

    slug = slugify(nombre)

    # -----------------------------
    # 2. Procesar KPIs
    # -----------------------------
    kpis = {
        row["kpi"]: row["valor"]
        for _, row in kpis_df.iterrows()
    }

    # -----------------------------
    # 3. Procesar trimestres
    # -----------------------------
    quarters = []
    metrics = trimestres_df["metric"].tolist()
    periods = trimestres_df.columns[1:]

    for period in periods:
        quarter_data = {"period": period}
        for i, metric in enumerate(metrics):
            quarter_data[metric] = trimestres_df.loc[i, period]
        quarters.append(quarter_data)

    # -----------------------------
    # 4. JSON final
    # -----------------------------
    final_json = {
        "company": {
            "nombre": nombre,
            "sector": sector,
            "logo": logo,
            "slug": slug
        },
        "kpis": kpis,
        "quarters": quarters
    }

    # -----------------------------
    # 5. Guardar JSON
    # -----------------------------
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{slug}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=4, ensure_ascii=False)

    print(f"JSON generado: {output_path}")

    return sector, nombre, slug, logo


# ============================================================
# Generar TODOS los JSON + menu.json
# ============================================================
def generate_all(excel_folder="excel", data_folder="data"):
    menu = {}

    for file in os.listdir(excel_folder):
        if file.endswith(".xlsx"):
            excel_path = os.path.join(excel_folder, file)

            sector, nombre, slug, logo = excel_to_json(excel_path, data_folder)

            if sector not in menu:
                menu[sector] = []

            menu[sector].append({
                "name": nombre,
                "slug": slug,
                "logo": logo
            })

    # Guardar menu.json
    menu_path = os.path.join(data_folder, "menu.json")
    with open(menu_path, "w", encoding="utf-8") as f:
        json.dump(menu, f, indent=4, ensure_ascii=False)

    print(f"menu.json generado: {menu_path}")


# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    generate_all()
