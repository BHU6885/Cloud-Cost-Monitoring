import boto3
import sqlite3
import os
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "cloud_costs.db")

def sync_aws_to_database(days=14):
    """
    Connects to AWS Cost Explorer, queries daily service costs,
    and saves them into the SQLite database.
    """
    print("Connecting to AWS Cost Explorer...")
    try:
        ce = boto3.client('ce', region_name='us-east-1')

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        new_records = 0
        for period in response.get('ResultsByTime', []):
            day = period['TimePeriod']['Start']
            for group in period.get('Groups', []):
                service_name = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])

                # Only record costs greater than $0
                if cost > 0.001:
                    cursor.execute("""
                        INSERT INTO expenses (date, service, cost)
                        VALUES (?, ?, ?)
                    """, (day, service_name, round(cost, 2)))
                    new_records += 1

        connection.commit()
        connection.close()

        print(f"Successfully synced {new_records} cost records from AWS.")
        return {"status": "success", "records_synced": new_records}

    except Exception as e:
        print(f"AWS Sync Notice: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    sync_aws_to_database()
