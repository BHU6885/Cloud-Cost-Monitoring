from flask import Flask, jsonify, render_template, Response, request
from aws_sync import sync_aws_to_database
import sqlite3
import os
import csv
import io



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

DATABASE = os.path.join(BASE_DIR, "cloud_costs.db")
MONTHLY_BUDGET = 3000

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# HOME API
@app.route("/")
def home():
    return jsonify({
        "message": "Cloud Cost Monitoring API is running!",
        "endpoints": [
            "/dashboard",
            "/api/summary",
            "/api/services",
            "/api/expenses",
            "/api/alerts"
        ]
    })


# DASHBOARD PAGE
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# SPENDING SUMMARY
@app.route("/api/summary")
def summary():
    connection = get_connection()

    result = connection.execute("""
        SELECT
            COUNT(*) AS expense_count,
            COALESCE(SUM(cost), 0) AS total_spending
        FROM expenses
    """).fetchone()

    connection.close()

    total = result["total_spending"]
    remaining = MONTHLY_BUDGET - total
    percentage = (total / MONTHLY_BUDGET) * 100

    return jsonify({
        "monthly_budget": MONTHLY_BUDGET,
        "total_spending": round(total, 2),
        "remaining_budget": round(remaining, 2),
        "budget_used_percentage": round(percentage, 2),
        "expense_count": result["expense_count"]
    })


# SERVICE-WISE COSTS
@app.route("/api/services")
def services():
    connection = get_connection()

    rows = connection.execute("""
        SELECT service, SUM(cost) AS total_cost
        FROM expenses
        GROUP BY service
        ORDER BY total_cost DESC
    """).fetchall()

    connection.close()

    return jsonify([
        {
            "service": row["service"],
            "total_cost": round(row["total_cost"], 2)
        }
        for row in rows
    ])


# EXPENSE RECORDS
@app.route("/api/expenses")
def expenses():
    connection = get_connection()

    rows = connection.execute("""
        SELECT id, date, service, cost
        FROM expenses
        ORDER BY date DESC, id DESC
    """).fetchall()

    connection.close()

    return jsonify([
        {
            "id": row["id"],
            "date": row["date"],
            "service": row["service"],
            "cost": row["cost"]
        }
        for row in rows
    ])


# BUDGET ALERTS
@app.route("/api/alerts")
def alerts():
    connection = get_connection()

    result = connection.execute("""
        SELECT COALESCE(SUM(cost), 0) AS total_spending
        FROM expenses
    """).fetchone()

    connection.close()

    total = result["total_spending"]
    percentage = (total / MONTHLY_BUDGET) * 100

    if percentage >= 100:
        level = "CRITICAL"
        message = "Budget exceeded! Review your cloud spending."
    elif percentage >= 90:
        level = "HIGH"
        message = "90% or more of your budget has been used."
    elif percentage >= 75:
        level = "WARNING"
        message = "75% or more of your budget has been used."
    elif percentage >= 50:
        level = "NOTICE"
        message = "50% or more of your budget has been used."
    else:
        level = "NORMAL"
        message = "Cloud spending is within the normal range."

    return jsonify({
        "alert_level": level,
        "budget_used_percentage": round(percentage, 2),
        "message": message
    })

@app.route("/export/csv")
def export_csv():
    connection = get_connection()

    rows = connection.execute("""
        SELECT date, service, cost
        FROM expenses
        ORDER BY date DESC
    """).fetchall()

    connection.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Date", "Service", "Cost"])

    for row in rows:
        writer.writerow([
            row["date"],
            row["service"],
            row["cost"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=cloud_cost_report.csv"
        }
    )
@app.route("/api/daily-spending")
def daily_spending():
    connection = get_connection()

    rows = connection.execute("""
        SELECT date, SUM(cost) AS total_cost
        FROM expenses
        GROUP BY date
        ORDER BY date
    """).fetchall()

    connection.close()

    return jsonify([
        {
            "date": row["date"],
            "total_cost": round(row["total_cost"], 2)
        }
        for row in rows
    ])


@app.route("/api/monthly-spending")
def monthly_spending():
    connection = get_connection()

    rows = connection.execute("""
        SELECT substr(date, 1, 7) AS month,
               SUM(cost) AS total_cost
        FROM expenses
        GROUP BY substr(date, 1, 7)
        ORDER BY month
    """).fetchall()

    connection.close()

    return jsonify([
        {
            "month": row["month"],
            "total_cost": round(row["total_cost"], 2)
        }
        for row in rows
    ])
# UPDATE MONTHLY BUDGET
@app.route("/api/budget", methods=["POST"])
def update_budget():
    global MONTHLY_BUDGET

    data = request.get_json()

    if not data or "budget" not in data:
        return jsonify({"error": "Budget is required"}), 400

    try:
        new_budget = float(data["budget"])
    except (TypeError, ValueError):
        return jsonify({"error": "Enter a valid budget"}), 400

    if not 0 < new_budget < float("inf"):
        return jsonify({"error": "Budget must be greater than zero"}), 400

    MONTHLY_BUDGET = new_budget

    return jsonify({
        "message": "Budget updated successfully",
        "monthly_budget": MONTHLY_BUDGET
    })


# AWS SYNC ENDPOINT
@app.route("/api/sync-aws", methods=["POST"])
def sync_aws():
    result = sync_aws_to_database()
    return jsonify(result)



# START FLASK SERVER
if __name__ == "__main__":
    app.run(debug=True)