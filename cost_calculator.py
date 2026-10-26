import csv

# 1. Set the monthly budget
monthly_budget = 30000

# 2. Define the CSV file path
file_path = "data/cloud_costs.csv"


# 3. Read cloud expenses from the CSV file
def read_cloud_costs(path):
    expenses = []

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            expense = {
                "Date": row["Date"],
                "Service": row["Service"],
                "Cost": float(row["Cost"])
            }

            expenses.append(expense)

    return expenses


# 4. Calculate total spending
def calculate_total(expenses):
    total = 0

    for expense in expenses:
        total += expense["Cost"]

    return total


# 5. Calculate service-wise spending
def calculate_service_costs(expenses):
    service_costs = {}

    for expense in expenses:
        service = expense["Service"]
        cost = expense["Cost"]

        if service in service_costs:
            service_costs[service] += cost
        else:
            service_costs[service] = cost

    return service_costs


# 6. Calculate budget utilisation
def calculate_budget_percentage(spending, budget):
    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    return (spending / budget) * 100


# 7. Load the data
expenses = read_cloud_costs(file_path)


# 8. Calculate results
total_spending = calculate_total(expenses)

remaining_budget = monthly_budget - total_spending

budget_percentage = calculate_budget_percentage(
    total_spending,
    monthly_budget
)

service_costs = calculate_service_costs(expenses)


# 9. Display the report
print("========== CLOUD COST REPORT ==========")

print("Number of expense records:", len(expenses))

print("Monthly Budget: ₹", monthly_budget)

print("Total Spending: ₹", round(total_spending, 2))

print("Remaining Budget: ₹", round(remaining_budget, 2))

print("Budget Used:", round(budget_percentage, 2), "%")


# 10. Display service-wise costs
print("\n========== SERVICE-WISE COSTS ==========")

for service, cost in service_costs.items():
    print(service, ": ₹", round(cost, 2))


# 11. Generate a budget alert
print("\n========== BUDGET ALERT ==========")

if budget_percentage >= 100:
    print("ALERT: Budget reached or exceeded!")

elif budget_percentage >= 90:
    print("CRITICAL: Spending reached 90% of the budget.")

elif budget_percentage >= 75:
    print("WARNING: Spending reached 75% of the budget.")

elif budget_percentage >= 50:
    print("NOTICE: Spending reached 50% of the budget.")

else:
    print("NORMAL: Spending is below 50% of the budget.")