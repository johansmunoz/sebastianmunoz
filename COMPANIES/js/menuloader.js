/* ============================================================
   Cargar menú dinámico desde menu.json
============================================================ */
async function loadMenu() {
  try {
    const response = await fetch("data/menu.json");
    if (!response.ok) {
      throw new Error("No se pudo cargar menu.json");
    }

    const menuData = await response.json();
    buildMenu(menuData);

  } catch (error) {
    console.error("Error cargando el menú:", error);
  }
}


/* ============================================================
   Construir menú multinivel
============================================================ */
function buildMenu(menuData) {
  const container = document.getElementById("menu-container");
  container.innerHTML = ""; // limpiar

  // Recorrer sectores
  for (const [sector, companies] of Object.entries(menuData)) {
    const groupDiv = document.createElement("div");
    groupDiv.classList.add("dropdown-group");

    // Título del sector
    const titleDiv = document.createElement("div");
    titleDiv.classList.add("dropdown-title");
    titleDiv.textContent = sector;
    groupDiv.appendChild(titleDiv);

    // Empresas dentro del sector
    companies.forEach(company => {
      const link = document.createElement("a");

      // Enlace universal
      link.href = `index.html?company=${company.slug}`;

      link.textContent = company.name;
      groupDiv.appendChild(link);
    });

    container.appendChild(groupDiv);
  }
}


/* ============================================================
   Inicializar menú al cargar la página
============================================================ */
document.addEventListener("DOMContentLoaded", loadMenu);
