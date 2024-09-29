from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import re  # To use regular expressions

app = Flask(__name__)

def convert_to_csv_url(input_url):
    # Regex to extract FILE_ID and SHEET_ID (gid)
    match = re.match(r'https://docs.google.com/spreadsheets/d/([^/]+)/.*gid=([\d]+)', input_url)
    if match:
        file_id = match.group(1)
        sheet_id = match.group(2)
        csv_url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={sheet_id}'
        return csv_url
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        google_sheet_url = request.form.get("sheet_url")

        # Convert input URL to CSV URL
        csv_url = convert_to_csv_url(google_sheet_url)
        if not csv_url:
            result = ["Invalid URL. Please enter a correct Google Sheets URL."]
            return render_template("index.html", result=result)

        try:
            # Read data from Google Sheets
            df = pd.read_csv(csv_url, nrows=100, usecols=range(13))

            # Strip extra spaces in column names
            df.columns = df.columns.str.strip()

            # Initial debt matrix (5 people)
            matrix = np.zeros((5, 5))

            # Columns corresponding to payers and debtors (now 5 columns)
            payer_columns = [3, 4, 5, 6, 7]  # Updated for 5 people
            debtor_columns = [8, 9, 10, 11, 12]  # Updated for 5 people

            # List of people names
            people = ["Vinh", "VAnh", "HAnh", "Bang", "Toi"]  # Added the 5th person

            # Loop through rows in the DataFrame
            for idx, row in df.iterrows():
                # Total amount for the item
                total_money = df.loc[idx, 'Money']

                # Identify who paid (payer columns from Vinh to Toi)
                payer = None
                for i in range(5):  # Changed to 5 for all people
                    if pd.notna(df.iloc[idx, payer_columns[i]]):
                        payer = i
                        break

                if payer is None:
                    continue  # If no payer is found, skip this row

                # Identify debtors (columns from Vinh to Toi)
                debtors = []
                for i in range(5):  # Updated to 5 for all people
                    if pd.notna(df.iloc[idx, debtor_columns[i]]):
                        debtors.append(i)

                # Calculate each person's share and round it up
                if debtors:
                    share = total_money / len(debtors)
                    share = np.ceil(share)  # Round up
                    for debtor in debtors:
                        if debtor != payer:
                            matrix[payer][debtor] += share

            # Prepare result for display
            result = []
            for i in range(5):
                for j in range(i + 1, 5):  # Compare each pair i, j where i < j
                    if matrix[j][i] > matrix[i][j]:
                        difference = matrix[j][i] - matrix[i][j]
                        result.append(f"{people[i]} owes {people[j]}: {difference:.1f}")
                    elif matrix[i][j] > matrix[j][i]:
                        difference = matrix[i][j] - matrix[j][i]
                        result.append(f"{people[j]} owes {people[i]}: {difference:.1f}")
        except Exception as e:
            result = [f"Error reading Google Sheets: {str(e)}"]

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
