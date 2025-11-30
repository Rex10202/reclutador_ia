const chatWindow = document.getElementById("chat-window");
const queryForm = document.getElementById("query-form");

function addMessage(text, sender = "bot") {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender);

  const avatarDiv = document.createElement("div");
  avatarDiv.classList.add("avatar");
  avatarDiv.textContent = sender === "user" ? "🧑" : "🤖";

  const bubbleDiv = document.createElement("div");
  bubbleDiv.classList.add("bubble");
  bubbleDiv.innerHTML = text;

  if (sender === "user") {
    messageDiv.appendChild(bubbleDiv);
    messageDiv.appendChild(avatarDiv);
  } else {
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);
  }

  chatWindow.appendChild(messageDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

queryForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const role = document.getElementById("role").value.trim();
  const skills = document.getElementById("skills").value.trim();
  const languages = document.getElementById("languages").value.trim();
  const experience_years = parseInt(
    document.getElementById("experience_years").value || "0",
    10
  );
  const location = document.getElementById("location").value.trim();
  const num_candidates = parseInt(
    document.getElementById("num_candidates").value || "1",
    10
  );

  const userSummary = `
    Cargo: <strong>${role || "-"}</strong><br/>
    Skills: <strong>${skills || "-"}</strong><br/>
    Idiomas: <strong>${languages || "-"}</strong><br/>
    Experiencia mínima: <strong>${experience_years} años</strong><br/>
    Ubicación: <strong>${location || "-"}</strong><br/>
    Cantidad de candidatos: <strong>${num_candidates}</strong>
  `;
  addMessage(userSummary, "user");

  const payload = {
    role,
    skills,
    languages,
    experience_years,
    location,
    num_candidates,
  };

  const thinkingId = "thinking-" + Date.now();
  addMessage("Estoy analizando los candidatos más afines... ⏳", "bot");

  try {
    const response = await fetch("/recomendar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const messages = chatWindow.querySelectorAll(".message.bot");
    const lastBot = messages[messages.length - 1];
    if (lastBot) {
      chatWindow.removeChild(lastBot);
    }

    if (!response.ok) {
      addMessage(
        "Hubo un error llamando al servicio de recomendación. Intenta de nuevo más tarde.",
        "bot"
      );
      return;
    }

    const data = await response.json();
    const candidatos = data.candidatos || [];

    if (candidatos.length === 0) {
      addMessage(
        "No encontré candidatos que cumplan con los criterios especificados.",
        "bot"
      );
      return;
    }

    const mejor = candidatos[0];

    let respuestaHTML = `
      El candidato más afín es:<br/><br/>
      <strong>${mejor.nombre}</strong><br/>
      Cargo: ${mejor.cargo}<br/>
      Habilidades: ${mejor.habilidades}<br/>
      Experiencia: ${mejor.experiencia_anios} años<br/>
      Idiomas: ${mejor.idiomas || "No especificados"}<br/>
      Ubicación: ${mejor.ubicacion || "No especificada"}<br/>
      Modalidad: ${mejor.modalidad || "No especificada"}<br/>
      Disponibilidad: ${mejor.disponibilidad || "No especificada"}<br/>
      Score de afinidad: <strong>${mejor.score}</strong>
    `;

    if (candidatos.length > 1) {
      respuestaHTML += "<br/><br/>Otros candidatos sugeridos:<br/>";
      for (let i = 1; i < Math.min(candidatos.length, 3); i++) {
        const c = candidatos[i];
        respuestaHTML += `
          • ${c.nombre} (${c.cargo}) — score: ${c.score}<br/>
        `;
      }
    }

    addMessage(respuestaHTML, "bot");
  } catch (error) {
    console.error(error);
    addMessage(
      "Ocurrió un error de conexión con el servidor. Revisa que la API esté activa.",
      "bot"
    );
  }
});
