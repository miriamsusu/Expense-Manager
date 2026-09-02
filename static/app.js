// Since the frontend is served from the same backend, the API is at the same origin.
const API = "";

// In-memory token. Cleared on page refresh — simple and fine for this project.
let token = null;

// --- Tab switching ---
function showTab(which) {
    document.getElementById("login-form").classList.toggle("hidden", which !== "login");
    document.getElementById("register-form").classList.toggle("hidden", which !== "register");
    document.getElementById("tab-login").classList.toggle("active", which === "login");
    document.getElementById("tab-register").classList.toggle("active", which === "register");
    document.getElementById("auth-message").textContent = "";
}

function setMessage(id, text, type) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = "message " + (type || "");
}

// --- Register ---
document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
        email: document.getElementById("register-email").value,
        phone_number: document.getElementById("register-phone").value,
        password: document.getElementById("register-password").value,
    };
    const res = await fetch(API + "/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (res.ok) {
        setMessage("auth-message", "Account created — you can log in now.", "success");
        showTab("login");
    } else {
        const err = await res.json();
        setMessage("auth-message", detailToText(err.detail) || "Registration failed.", "error");
    }
});

// --- Login ---
document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
        email: document.getElementById("login-email").value,
        password: document.getElementById("login-password").value,
    };
    const res = await fetch(API + "/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        await enterApp();
    } else {
        setMessage("auth-message", "Incorrect email or password.", "error");
    }
});

// --- Enter the logged-in view ---
async function enterApp() {
    const res = await fetch(API + "/users/me", {
        headers: { "Authorization": "Bearer " + token },
    });
    const user = await res.json();
    document.getElementById("user-email").textContent = user.email;
    document.getElementById("auth-section").classList.add("hidden");
    document.getElementById("app-section").classList.remove("hidden");
    await refreshExpenses();
}

function logout() {
    token = null;
    document.getElementById("app-section").classList.add("hidden");
    document.getElementById("auth-section").classList.remove("hidden");
    document.getElementById("login-form").reset();
}

// --- Add an expense ---
document.getElementById("expense-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
        amount: parseFloat(document.getElementById("expense-amount").value),
        descr: document.getElementById("expense-descr").value,
        date: document.getElementById("expense-date").value,
    };
    const notes = document.getElementById("expense-notes").value;
    if (notes) body.notes = notes;

    const res = await fetch(API + "/expenses", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
        body: JSON.stringify(body),
    });
    if (res.ok) {
        document.getElementById("expense-form").reset();
        setMessage("expense-message", "Expense added.", "success");
        await refreshExpenses();
    } else {
        const err = await res.json();
        setMessage("expense-message", detailToText(err.detail) || "Could not add expense.", "error");
    }
});

// --- Load and render expenses + summary ---
async function refreshExpenses() {
    const res = await fetch(API + "/expenses", {
        headers: { "Authorization": "Bearer " + token },
    });
    const expenses = await res.json();
    const list = document.getElementById("expense-list");
    list.innerHTML = "";
    if (expenses.length === 0) {
        list.innerHTML = "<p>No expenses yet.</p>";
    }
    for (const exp of expenses) {
        const div = document.createElement("div");
        div.className = "expense-item";
        div.innerHTML = `
            <div class="details">
                ${escapeHtml(exp.descr)}
                <span class="category">${escapeHtml(exp.category)}</span>
                <div><small>${escapeHtml(exp.date)}${exp.notes ? " · " + escapeHtml(exp.notes) : ""}</small></div>
            </div>
            <span class="amount">$${exp.amount.toFixed(2)}</span>
            <button class="delete-btn" data-id="${exp.id}">Delete</button>
        `;
        div.querySelector(".delete-btn").addEventListener("click", () => deleteExpense(exp.id));
        list.appendChild(div);
    }

    const sumRes = await fetch(API + "/expenses/summary", {
        headers: { "Authorization": "Bearer " + token },
    });
    const summary = await sumRes.json();
    const summaryEl = document.getElementById("summary");
    summaryEl.innerHTML = "";
    if (summary.length === 0) {
        summaryEl.innerHTML = "<p>Nothing to summarize yet.</p>";
    }
    for (const row of summary) {
        const div = document.createElement("div");
        div.className = "summary-row";
        div.innerHTML = `<span>${escapeHtml(row.category)}</span><span class="total">$${row.total.toFixed(2)}</span>`;
        summaryEl.appendChild(div);
    }

    renderChart(summary);
}

// A fixed palette so each category keeps a consistent, distinct color.
const CATEGORY_COLORS = {
    groceries: "#4f46e5",
    entertainment: "#db2777",
    gas: "#ea580c",
    housing: "#0891b2",
    dining: "#16a34a",
    utilities: "#ca8a04",
    other: "#6b7280",
};

let summaryChart = null;

function renderChart(summary) {
    const canvas = document.getElementById("summary-chart");

    // With no data, tear down any existing chart and stop.
    if (summary.length === 0) {
        if (summaryChart) { summaryChart.destroy(); summaryChart = null; }
        return;
    }

    const labels = summary.map(row => row.category);
    const data = summary.map(row => row.total);
    const colors = labels.map(c => CATEGORY_COLORS[c] || "#6b7280");

    // If the chart already exists, just swap its data in — smoother than rebuilding.
    if (summaryChart) {
        summaryChart.data.labels = labels;
        summaryChart.data.datasets[0].data = data;
        summaryChart.data.datasets[0].backgroundColor = colors;
        summaryChart.update();
        return;
    }

    summaryChart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{ data: data, backgroundColor: colors, borderWidth: 2, borderColor: "#fff" }],
        },
        options: {
            plugins: {
                legend: { position: "bottom" },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.label}: $${ctx.parsed.toFixed(2)}`,
                    },
                },
            },
        },
    });
}

// --- Delete an expense ---
async function deleteExpense(id) {
    const res = await fetch(API + "/expenses/" + id, {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + token },
    });
    if (res.ok) await refreshExpenses();
}

// --- Helpers ---
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// FastAPI validation errors come back as a list; plain errors as a string.
function detailToText(detail) {
    if (!detail) return null;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map(d => d.msg).join(", ");
    return null;
}