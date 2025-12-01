const API_URL = "http://127.0.0.1:8000/query";

const inputEl = document.getElementById("query-input");
const sendBtn = document.getElementById("send-btn");
const candidatesContainer = document.getElementById("candidates");
const searchWrapper = document.getElementById("search-wrapper");

async function sendQuery() {
  const text = inputEl.value.trim();
  if (!text) return;

  sendBtn.disabled = true;
  sendBtn.textContent = "Buscando...";

  candidatesContainer.innerHTML = "<p>Procesando consulta...</p>";

	// Animar barra hacia estado compacto (arriba) en el primer uso
  if (!searchWrapper.classList.contains("compact")) {
    searchWrapper.classList.add("compact");
  }

  try {
    const resp = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
	      body: JSON.stringify({ text }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || "Error en la API");
    }

    const data = await resp.json();
    renderCandidates(data.candidates);
  } catch (err) {
    candidatesContainer.innerHTML = `<p style="color:#f97316">Error: ${err.message}</p>`;
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Buscar";
  }
}

function renderCandidates(list) {
  if (!list || !list.length) {
    candidatesContainer.innerHTML = "<p>No se encontraron candidatos.</p>";
    return;
  }

  candidatesContainer.innerHTML = "<h2>Candidatos recomendados</h2>";

  list.forEach((c) => {
    const card = document.createElement("div");
    card.className = "candidate-card";
    card.innerHTML = `
      <div class="candidate-header">
        <div class="candidate-id">${c.id} · ${c.role}</div>
        <div class="candidate-score">score: ${c.score.toFixed(3)}</div>
      </div>
      <div class="candidate-meta">
        ${c.location} · ${c.years_experience} años · Idiomas: ${c.languages || "-"}
      </div>
      <div class="candidate-skills">
        Skills: ${c.skills || "-"}
      </div>
    `;
    candidatesContainer.appendChild(card);
  });
}

sendBtn.addEventListener("click", sendQuery);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendQuery();
  }
});