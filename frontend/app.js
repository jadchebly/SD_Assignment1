// --- API base: use localhost to avoid IPv4/IPv6 mismatches ---
const API = "http://localhost:8000";

// --- Grab elements explicitly (no relying on globals) ---
const els = {
  title: document.getElementById("title"),
  weight: document.getElementById("weight"),
  due: document.getElementById("due"),
  score: document.getElementById("score"),
  addBtn: document.getElementById("add"),
  tableBody: document.querySelector("#table tbody"),
  current: document.getElementById("current"),
  remaining: document.getElementById("remaining"),
  weightsMsg: document.getElementById("weightsMsg"),
  target: document.getElementById("target"),
  calcBtn: document.getElementById("calc"),
  answer: document.getElementById("answer"),
};

async function fetchJSON(url, opts) {
  const r = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!r.ok) {
    // Log server error details for debugging (e.g., 422 validation messages)
    let detail = "";
    try { detail = await r.text(); } catch {}
    throw new Error(`HTTP ${r.status}: ${detail || r.statusText}`);
  }
  return r.json();
}

async function load() {
  // List assessments
  const rows = await fetchJSON(`${API}/assessments`);
  els.tableBody.innerHTML = "";
  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.title}</td>
      <td>${r.weight_pct}%</td>
      <td>${r.due_date}</td>
      <td>${(r.score_pct !== null && r.score_pct !== undefined) ? r.score_pct : ""}</td>
      <td><button data-id="${r.id}" class="del">Delete</button></td>`;
    els.tableBody.appendChild(tr);
  });

  // Stats
  const stats = await fetchJSON(`${API}/stats/current`);
  els.current.textContent = stats.current_weighted.toFixed(2);
  els.remaining.textContent = stats.remaining_weight.toFixed(2);

  // Weight validation
  const v = await fetchJSON(`${API}/stats/validate`);
  els.weightsMsg.textContent = v.message;
}

// Create (Add / Update button)
els.addBtn.onclick = async () => {
  try {
    // Basic client-side validation to avoid 422s
    if (!els.title.value.trim()) return alert("Please enter a title.");
    if (!els.weight.value) return alert("Please enter a weight % (0–100).");
    if (!els.due.value) return alert("Please pick a due date (YYYY-MM-DD).");

    const payload = {
      title: els.title.value.trim(),
      weight_pct: Number(els.weight.value),
      due_date: els.due.value, // yyyy-mm-dd comes from <input type="date">
      score_pct: els.score.value ? Number(els.score.value) : null,
    };

    await fetchJSON(`${API}/assessments`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    // Clear form and reload list/stats
    els.title.value = "";
    els.weight.value = "";
    els.due.value = "";
    els.score.value = "";
    await load();
  } catch (err) {
    console.error(err);
    alert(`Could not add assessment:\n${err.message}`);
  }
};

// Delete via event delegation
document.querySelector("#table").onclick = async (e) => {
  if (e.target.classList.contains("del")) {
    const id = e.target.getAttribute("data-id");
    await fetch(`${API}/assessments/${id}`, { method: "DELETE" });
    await load();
  }
};

// What-if
els.calcBtn.onclick = async () => {
  const t = Number(els.target.value);
  if (Number.isNaN(t)) return (els.answer.textContent = "Enter a target %");
  const r = await fetchJSON(`${API}/stats/what-if?target=${t}`);
  els.answer.textContent =
    r.required_avg == null
      ? `No remaining work. Target ${r.target}% is ${r.attainable ? "already met" : "not met"}.`
      : `You need an average of ${r.required_avg}% on remaining work. (${r.attainable ? "attainable" : "not attainable"})`;
};

load();
