function formatValue(value) {
  if (value === "" || value === null || value === undefined) {
    return "N/A";
  }

  // Convertir strings numéricos a número real
  const num = Number(value);

  if (isNaN(num)) {
    return value; // Si no es número, lo devolvemos tal cual
  }

  // Detectar porcentajes (valores entre -1 y 1)
  if (Math.abs(num) < 1 && num !== 0) {
    return (num * 100).toFixed(2) + "%";
  }

  // Mostrar número completo con separadores de miles
  return "$" + num.toLocaleString("es-CO");
}


///////////////////////////////////////////

async function loadBankData(jsonPath) {
    try {
        // 1. Cargar el JSON
        const response = await fetch(jsonPath);
        const data = await response.json();

        // -----------------------------
        // 2. Insertar información general
        // -----------------------------
        document.getElementById("company-name").textContent = data.company.nombre;

        // -----------------------------
        // 3. Insertar KPIs
        // -----------------------------
        const kpiContainer = document.getElementById("kpi-container");
        kpiContainer.innerHTML = ""; // limpiar

        for (const [key, value] of Object.entries(data.kpis)) {
            const kpiDiv = document.createElement("div");
            kpiDiv.classList.add("kpi-item");

            kpiDiv.innerHTML = `
                <h3>${key.replace(/_/g, " ").toUpperCase()}</h3>
                <p>${formatValue(value)}</p>
                `;


            kpiContainer.appendChild(kpiDiv);
        }

        // -----------------------------
        // 4. Construir tabla de trimestres
        // -----------------------------
        const head = document.getElementById("quarters-head");
        const body = document.getElementById("quarters-body");

        head.innerHTML = "";
        body.innerHTML = "";

        // Encabezados
        const headerRow = document.createElement("tr");
        headerRow.innerHTML = `
            <th>Métrica</th>
            ${data.quarters.map(q => `<th>${q.period}</th>`).join("")}
        `;
        head.appendChild(headerRow);

        // Filas
        const metrics = Object.keys(data.quarters[0]).filter(k => k !== "period");

        metrics.forEach(metric => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${metric.replace(/_/g, " ")}</td>
                ${data.quarters.map(q => `<td>${formatValue(q[metric])}</td>`).join("")}
            `;


            body.appendChild(row);
        });

    } catch (error) {
        console.error("Error cargando el JSON:", error);
    }
}
