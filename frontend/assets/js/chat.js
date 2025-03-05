document.addEventListener("DOMContentLoaded", function () {
    const chatContainer = document.getElementById("chat-container");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const selectProject = document.createElement("select");
    selectProject.id = "project-select";

    // Agregar la lista desplegable debajo del título
    const title = document.querySelector("h1");
    title.insertAdjacentElement("afterend", selectProject);

    let currentProject = ""; // Variable para rastrear el proyecto seleccionado

    // Función para agregar mensajes al chat
    function addMessage(sender, message) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.innerHTML = `<span>${message}</span>`;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // 🔹 Cargar la lista de proyectos (Excels disponibles)
    async function loadProjects() {
        try {
            const response = await fetch("https://sensorydata.onrender.com/api/lista_excels");
            const data = await response.json();

            if (data.archivos && data.archivos.length > 0) {
                selectProject.innerHTML = "<option value=''>Selecciona un proyecto</option>";
                data.archivos.forEach((archivo) => {
                    const option = document.createElement("option");
                    option.value = archivo;
                    option.textContent = archivo;
                    selectProject.appendChild(option);
                });
            } else {
                selectProject.innerHTML = "<option value=''>No hay proyectos disponibles</option>";
            }
        } catch (error) {
            console.error("Error al cargar los proyectos:", error);
        }
    }

    // 🔹 Procesar el archivo seleccionado y limpiar el chat
    async function processSelectedProject() {
        const selectedFile = selectProject.value;
        if (!selectedFile) {
            alert("Por favor, selecciona un archivo antes de enviar una pregunta.");
            return null;
        }

        // Si se cambia el proyecto, limpiar chat y actualizar variable
        if (selectedFile !== currentProject) {
            chatContainer.innerHTML = ""; // Limpia el chat
            addMessage("bot", "📂 Procesando nuevo archivo..."); // Mensaje de carga
            currentProject = selectedFile; // Guardar el nuevo proyecto
        }

        try {
            const response = await fetch("https://sensorydata.onrender.com/api/procesar_excel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ archivo: selectedFile }),
            });

            const data = await response.json();
            if (data.error) {
                alert("Error al procesar el archivo: " + data.error);
                return null;
            }

            chatContainer.innerHTML = ""; // Limpiar mensajes previos una vez que ya está procesado
            addMessage("bot", `✅ Archivo "${selectedFile}" cargado exitosamente. Puedes hacer preguntas.`);

            return data.datos;
        } catch (error) {
            console.error("Error al procesar el archivo:", error);
            return null;
        }
    }

    // 🔹 Enviar la pregunta al backend
    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        const datosProcesados = await processSelectedProject();
        if (!datosProcesados) return;

        addMessage("user", message);
        userInput.value = "";

        try {
            const response = await fetch("https://sensorydata.onrender.com/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pregunta: message, datos: datosProcesados }),
            });

            const data = await response.json();
            const botResponse = data.respuesta || "No pude obtener una respuesta.";

            addMessage("bot", botResponse);
        } catch (error) {
            console.error("Error al enviar mensaje:", error);
            addMessage("bot", "Ocurrió un error al obtener la respuesta.");
        }
    }

    // Evento de botón enviar
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") sendMessage();
    });

    // Evento cuando se cambia el archivo seleccionado
    selectProject.addEventListener("change", processSelectedProject);

    // Cargar la lista de proyectos al inicio
    loadProjects();
});
