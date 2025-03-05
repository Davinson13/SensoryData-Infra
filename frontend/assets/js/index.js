const sideMenu = document.querySelector("aside");
const menuBtn = document.getElementById("menu-btn");
const closeBtn = document.getElementById("close-btn");
const darkMode = document.querySelector(".dark-mode");
const chatbotButton = document.getElementById("chatbot-button");
const chatbotWindow = document.getElementById("chatbot-window");
const closeChatbot = document.getElementById("close-chatbot");

// Función para aplicar el modo oscuro basado en localStorage
function applyDarkMode() {
  const isDarkMode = localStorage.getItem("darkMode") === "enabled";

  if (isDarkMode) {
    document.body.classList.add("dark-mode-variables");
    darkMode.querySelector("span:nth-child(1)").classList.remove("active");
    darkMode.querySelector("span:nth-child(2)").classList.add("active");
  } else {
    document.body.classList.remove("dark-mode-variables");
    darkMode.querySelector("span:nth-child(1)").classList.add("active");
    darkMode.querySelector("span:nth-child(2)").classList.remove("active");
  }
}

// Aplicar el modo oscuro al cargar la página
applyDarkMode();

if (darkMode) {
  darkMode.addEventListener("click", () => {
    // Alternar el modo oscuro
    const isDarkMode = document.body.classList.toggle("dark-mode-variables");

    // Alternar iconos
    darkMode.querySelector("span:nth-child(1)").classList.toggle("active");
    darkMode.querySelector("span:nth-child(2)").classList.toggle("active");

    // Guardar preferencia en localStorage
    localStorage.setItem("darkMode", isDarkMode ? "enabled" : "disabled");
  });
}

// Evento para abrir el menú
if (menuBtn && sideMenu) {
  menuBtn.addEventListener("click", () => {
    sideMenu.style.display = "block";
  });
}

// Evento para cerrar el menú
if (closeBtn && sideMenu) {
  closeBtn.addEventListener("click", () => {
    sideMenu.style.display = "none";
  });
}

// Verificar si Orders está definido y es un array antes de iterar
if (typeof Orders !== "undefined" && Array.isArray(Orders)) {
  const tableBody = document.querySelector("table tbody");

  if (tableBody) {
    Orders.forEach((order) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${order.productName}</td>
        <td>${order.productNumber}</td>
        <td>${order.paymentStatus}</td>
        <td class="${
          order.status === "Declined"
            ? "danger"
            : order.status === "Pending"
            ? "warning"
            : "primary"
        }">${order.status}</td>
        <td class="primary">Details</td>
      `;
      tableBody.appendChild(tr);
    });
  }
}

// Chatbot functionality
if (chatbotButton && chatbotWindow) {
  chatbotButton.addEventListener("click", () => {
    chatbotWindow.classList.toggle("active");
  });
}

if (closeChatbot && chatbotWindow) {
  closeChatbot.addEventListener("click", () => {
    chatbotWindow.classList.remove("active");
  });
}
