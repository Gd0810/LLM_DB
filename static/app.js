const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const tableSelect = document.getElementById("tableSelect");
const rowLimit = document.getElementById("rowLimit");
const loadTableBtn = document.getElementById("loadTableBtn");
const summaryBtn = document.getElementById("summaryBtn");
const summaryBox = document.getElementById("summaryBox");
const tableWrap = document.getElementById("tableWrap");

function addBubble(text, role) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function renderTable(rows) {
  if (!rows || rows.length === 0) {
    tableWrap.innerHTML = '<p class="placeholder">No rows found.</p>';
    return;
  }

  const columns = Object.keys(rows[0]);
  const table = document.createElement("table");

  const head = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((column) => {
    const th = document.createElement("th");
    th.textContent = column;
    headRow.appendChild(th);
  });
  head.appendChild(headRow);

  const body = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((column) => {
      const td = document.createElement("td");
      const value = row[column];
      td.textContent = value === null ? "NULL" : String(value);
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });

  table.appendChild(head);
  table.appendChild(body);

  tableWrap.innerHTML = "";
  tableWrap.appendChild(table);
}

async function fetchTables() {
  const response = await fetch("/api/tables");
  const data = await response.json();

  tableSelect.innerHTML = "";
  (data.tables || []).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    tableSelect.appendChild(option);
  });
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  addBubble(question, "user");
  questionInput.value = "";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();

    if (!response.ok) {
      addBubble(data.error || "Something went wrong.", "bot");
      return;
    }

    addBubble(data.answer || "No response.", "bot");
  } catch (_error) {
    addBubble("Network error while calling chatbot API.", "bot");
  }
});

loadTableBtn.addEventListener("click", async () => {
  const tableName = tableSelect.value;
  const limit = rowLimit.value || "50";
  if (!tableName) return;

  try {
    const response = await fetch(`/api/table/${encodeURIComponent(tableName)}?limit=${encodeURIComponent(limit)}`);
    const data = await response.json();

    if (!response.ok) {
      tableWrap.innerHTML = `<p class="placeholder">${data.error || "Failed to load table."}</p>`;
      return;
    }

    renderTable(data.rows || []);
  } catch (_error) {
    tableWrap.innerHTML = '<p class="placeholder">Network error while loading table.</p>';
  }
});

summaryBtn.addEventListener("click", async () => {
  try {
    const response = await fetch("/api/summary");
    const data = await response.json();

    summaryBox.textContent = response.ok
      ? data.summary || ""
      : data.error || "Failed to fetch summary.";
  } catch (_error) {
    summaryBox.textContent = "Network error while fetching summary.";
  }
});

fetchTables();
addBubble("Hello. Ask me anything about your database.", "bot");
