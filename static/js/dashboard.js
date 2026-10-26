// ========================================
// GLOBAL VARIABLES
// ========================================

let expenses = [];

let serviceChart = null;
let budgetChart = null;
let dailyChart = null;
let monthlyChart = null;


// ========================================
// FORMAT CURRENCY
// ========================================

const money = value =>
    new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(value);


// ========================================
// FETCH JSON DATA FROM FLASK
// ========================================

async function getJSON(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error("Could not load " + url);
    }

    return response.json();
}


// ========================================
// LOAD ALL DASHBOARD DATA
// ========================================

async function loadDashboard() {
    document.getElementById("status").textContent =
        "Loading dashboard...";

    try {
        const [
            summary,
            services,
            records,
            alert,
            dailyData,
            monthlyData
        ] = await Promise.all([
            getJSON("/api/summary"),
            getJSON("/api/services"),
            getJSON("/api/expenses"),
            getJSON("/api/alerts"),
            getJSON("/api/daily-spending"),
            getJSON("/api/monthly-spending")
        ]);

        expenses = records;

        updateSummary(summary);
        updateAlert(alert);
        updateServiceFilter(services);

        drawCharts(services, summary, dailyData);

        renderExpenses();
        renderDailySpending(dailyData);
        renderMonthlySpending(monthlyData);

        document.getElementById("status").textContent =
            "Dashboard updated successfully.";

    } catch (error) {
        document.getElementById("status").textContent =
            "Unable to load dashboard data.";

        console.error("Dashboard error:", error);
    }
}


// ========================================
// UPDATE KPI CARDS
// ========================================

function updateSummary(summary) {
    document.getElementById("budget").textContent =
        money(summary.monthly_budget);

    document.getElementById("spending").textContent =
        money(summary.total_spending);

    document.getElementById("remaining").textContent =
        money(summary.remaining_budget);

    document.getElementById("percentage").textContent =
        summary.budget_used_percentage + "%";

    document.getElementById("count").textContent =
        summary.expense_count;
}


// ========================================
// UPDATE BUDGET ALERT
// ========================================

function updateAlert(alert) {
    const alertBox = document.getElementById("alertBox");

    alertBox.className = "alert-" + alert.alert_level;

    alertBox.textContent =
        alert.alert_level +
        " — " +
        alert.message +
        " Budget used: " +
        alert.budget_used_percentage +
        "%";
}


// ========================================
// UPDATE SERVICE FILTER
// ========================================

function updateServiceFilter(services) {
    const filter = document.getElementById("serviceFilter");

    const previous = filter.value;

    filter.innerHTML =
        '<option value="all">All Services</option>';

    services.forEach(item => {
        const option = document.createElement("option");

        option.value = item.service;
        option.textContent = item.service;

        filter.appendChild(option);
    });

    if ([...filter.options].some(option =>
        option.value === previous
    )) {
        filter.value = previous;
    }
}


// ========================================
// CREATE ANALYTICS CHARTS
// ========================================

function drawCharts(services, summary, dailyData) {

    if (serviceChart) serviceChart.destroy();
    if (budgetChart) budgetChart.destroy();
    if (dailyChart) dailyChart.destroy();

    // Spending by service

    serviceChart = new Chart(
        document.getElementById("serviceChart"),
        {
            type: "doughnut",

            data: {
                labels: services.map(item => item.service),

                datasets: [{
                    label: "Service Spending",

                    data: services.map(item => item.total_cost)
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        }
    );


    // Budget utilization

    const spent = Number(summary.total_spending);
    const budget = Number(summary.monthly_budget);

    budgetChart = new Chart(
        document.getElementById("budgetChart"),
        {
            type: "doughnut",

            data: {
                labels: ["Spent", "Remaining"],

                datasets: [{
                    data: [
                        spent,
                        Math.max(budget - spent, 0)
                    ]
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        }
    );


    // Daily spending trend

    dailyChart = new Chart(
        document.getElementById("dailyChart"),
        {
            type: "line",

            data: {
                labels: dailyData.map(item => item.date),

                datasets: [{
                    label: "Daily Spending (₹)",

                    data: dailyData.map(item => item.total_cost),

                    borderWidth: 3,
                    tension: 0.3,
                    fill: false
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,

                        title: {
                            display: true,
                            text: "Cost (₹)"
                        }
                    }
                }
            }
        }
    );
}


// ========================================
// DISPLAY DAILY SPENDING TABLE
// ========================================

function renderDailySpending(data) {
    const table = document.getElementById("dailyTable");

    table.innerHTML = "";

    if (!data.length) {
        table.innerHTML =
            '<tr><td colspan="2">No daily spending data found.</td></tr>';

        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");

        const dateCell = document.createElement("td");
        dateCell.textContent = item.date;

        const costCell = document.createElement("td");
        costCell.textContent = money(item.total_cost);

        row.appendChild(dateCell);
        row.appendChild(costCell);

        table.appendChild(row);
    });
}


// ========================================
// MONTHLY SPENDING CHART AND TABLE
// ========================================

function renderMonthlySpending(data) {
    const table = document.getElementById("monthlyTable");

    table.innerHTML = "";

    if (!data.length) {
        table.innerHTML =
            '<tr><td colspan="2">No monthly spending data found.</td></tr>';
    } else {
        data.forEach(item => {
            const row = document.createElement("tr");

            const monthCell = document.createElement("td");
            monthCell.textContent = item.month;

            const costCell = document.createElement("td");
            costCell.textContent = money(item.total_cost);

            row.appendChild(monthCell);
            row.appendChild(costCell);

            table.appendChild(row);
        });
    }

    if (monthlyChart) {
        monthlyChart.destroy();
    }

    monthlyChart = new Chart(
        document.getElementById("monthlyChart"),
        {
            type: "bar",

            data: {
                labels: data.map(item => item.month),

                datasets: [{
                    label: "Monthly Spending (₹)",

                    data: data.map(item => item.total_cost),

                    borderWidth: 1
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,

                        title: {
                            display: true,
                            text: "Cost (₹)"
                        }
                    }
                }
            }
        }
    );
}


// ========================================
// DISPLAY EXPENSE HISTORY
// ========================================

function renderExpenses() {
    const selected =
        document.getElementById("serviceFilter").value;

    const filtered = expenses.filter(item =>
        selected === "all" || item.service === selected
    );

    const table = document.getElementById("expenseTable");

    table.innerHTML = "";

    if (!filtered.length) {
        table.innerHTML =
            '<tr><td colspan="3">No expenses found.</td></tr>';

        return;
    }

    filtered.forEach(item => {
        const row = document.createElement("tr");

        [
            item.date,
            item.service,
            money(item.cost)
        ].forEach(value => {
            const cell = document.createElement("td");

            cell.textContent = value;

            row.appendChild(cell);
        });

        table.appendChild(row);
    });
}

// ========================================
// UPDATE MONTHLY BUDGET
// ========================================

async function updateBudget() {
    const input = document.getElementById("budgetInput");
    const message = document.getElementById("budgetMessage");

    const budget = Number(input.value);

    if (!Number.isFinite(budget) || budget <= 0) {
        message.textContent = "Please enter a valid budget greater than zero.";
        return;
    }

    message.textContent = "Updating budget...";

    try {
        const response = await fetch("/api/budget", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ budget: budget })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to update budget.");
        }

        message.textContent = result.message;

        await loadDashboard();

        input.value = "";

    } catch (error) {
        message.textContent = error.message;
        console.error("Budget update error:", error);
    }
}


// ========================================
// START DASHBOARD
// ========================================

loadDashboard();