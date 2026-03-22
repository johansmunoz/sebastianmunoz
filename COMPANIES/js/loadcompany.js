/* ============================================================
   1. FORMATEO DE VALORES (igual al que ya tienes)
============================================================ */
function formatValue(value) {
  if (value === "" || value === null || value === undefined) {
    return "N/A";
  }

  const num = Number(value);
  if (isNaN(num)) return value;

  // Porcentajes
  if (Math.abs(num) < 1 && num !== 0) {
    return (num * 100).toFixed(2) + "%";
  }

  // Número completo con separadores
  return "$" + num.toLocaleString("es-CO");
}


/* ============================================================
   2. OBTENER EMPRESA DESDE LA URL
   Ejemplo: index.html?company=banco-de-bogota
============================================================ */
function getCompanyFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get("company");
}


/* ============================================================
   3. CARGAR JSON DE LA EMPRESA
============================================================ */
async function loadCompanyData(companySlug) {
  try {
    const jsonPath = `data/${companySlug}.json`;
    const response = await fetch(jsonPath);

    if (!response.ok) {
      throw new Error(`No se encontró el archivo JSON: ${jsonPath}`);
    }

    const data = await response.json();

    renderCompanyHeader(data.company);
    renderKPIs(data.kpis);
    renderQuartersTable(data.quarters);

  } catch (error) {
    console.error("Error cargando empresa:", error);
    document.getElementById("company-name").textContent =
      "No se pudo cargar la información.";
  }
}


/* ============================================================
   4. RENDERIZAR HEADER (título + logo)
============================================================ */
function renderCompanyHeader(company) {
  document.getElementById("company-title").textContent = company.nombre;
  document.getElementById("company-name").textContent = company.nombre;

  // Logo dinámico
  if (company.logo) {
    document.getElementById("company-logo").src = `assets/${company.logo}`;
  }
}


/* ============================================================
   5. RENDERIZAR KPIs
============================================================ */
function renderKPIs(kpis) {
  const container = document.getElementById("kpi-container");
  container.innerHTML = "";

  for (const [key, value] of Object.entries(kpis)) {
    const div = document.createElement("div");
    div.classList.add("kpi-card");

    div.innerHTML = `
      <div class="kpi-label">${key.replace(/_/g, " ")}</div>
      <span class="kpi-value">${formatValue(value)}</span>
    `;

    container.appendChild(div);
  }
}


/* ============================================================
   6. RENDERIZAR TABLA DE TRIMESTRES
============================================================ */
function renderQuartersTable(quarters) {
  const head = document.getElementById("quarters-head");
  const body = document.getElementById("quarters-body");

  head.innerHTML = "";
  body.innerHTML = "";

  // Encabezado
  const headerRow = document.createElement("tr");
  headerRow.innerHTML = `
    <th>Métrica</th>
    ${quarters.map(q => `<th>${q.period}</th>`).join("")}
  `;
  head.appendChild(headerRow);

  // Métricas
  const metrics = Object.keys(quarters[0]).filter(k => k !== "period");

  metrics.forEach(metric => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${metric.replace(/_/g, " ")}</td>
      ${quarters.map(q => `<td>${formatValue(q[metric])}</td>`).join("")}
    `;

    body.appendChild(row);
  });
}


/* ============================================================
   7. INICIALIZACIÓN AUTOMÁTICA
============================================================ */
document.addEventListener("DOMContentLoaded", () => {
  const company = getCompanyFromURL();

  if (!company) {
    document.getElementById("company-name").textContent =
      "Seleccione una empresa en el menú.";
    return;
  }

  loadCompanyData(company);
});
