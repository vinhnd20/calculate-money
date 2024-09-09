from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import re  # Thêm import re để sử dụng biểu thức chính quy

app = Flask(__name__)


def convert_to_csv_url(input_url):
    # Biểu thức chính quy để tìm FILE_ID và SHEET_ID (gid)
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

        # Chuyển đổi URL nhập vào thành URL CSV
        csv_url = convert_to_csv_url(google_sheet_url)
        if not csv_url:
            result = ["URL không hợp lệ. Vui lòng nhập URL Google Sheets đúng định dạng."]
            return render_template("index.html", result=result)

        try:
            # Đọc dữ liệu từ Google Sheets
            df = pd.read_csv(csv_url, nrows=100, usecols=range(11))

            # In ra tên các cột để kiểm tra
            print("Tên các cột:", df.columns.tolist())

            # Loại bỏ khoảng trắng thừa trong tên các cột
            df.columns = df.columns.str.strip()

            # Ma trận nợ ban đầu (4 người)
            matrix = np.zeros((4, 4))

            # Danh sách người ứng với các cột (sử dụng chỉ số cột cụ thể)
            payer_columns = [3, 4, 5, 6]  # Các cột của người trả tiền
            debtor_columns = [7, 8, 9, 10]  # Các cột của người nợ tiền

            # Tên của người theo số thứ tự
            people = ["Vinh", "VAnh", "HAnh", "Bang"]

            # Duyệt qua từng hàng trong DataFrame
            for idx, row in df.iterrows():
                # Xác định tổng số tiền của món đồ
                total_money = df.loc[idx, 'Money']  # Thay 'Money' bằng tên cột thực tế nếu cần

                # Xác định ai là người trả tiền (các cột từ Vinh đến Bang)
                payer = None
                for i in range(4):
                    if pd.notna(df.iloc[idx, payer_columns[i]]):  # Sử dụng chỉ số cột thay vì tên
                        payer = i
                        break

                if payer is None:
                    continue  # Nếu không có người trả tiền thì bỏ qua

                # Xác định những người phải chịu tiền (các cột từ Vinh đến Bang ở cuối)
                debtors = []
                for i in range(4):
                    if pd.notna(df.iloc[idx, debtor_columns[i]]):  # Sử dụng chỉ số cột thay vì tên
                        debtors.append(i)

                # Tính số tiền mỗi người phải trả và làm tròn lên
                if debtors:
                    share = total_money / len(debtors)
                    share = np.ceil(share)  # Làm tròn lên số tiền chia
                    for debtor in debtors:
                        if debtor != payer:
                            matrix[payer][debtor] += share  # Người payer nợ các debtor

            # Chuẩn bị kết quả
            result = []
            for i in range(4):
                for j in range(i + 1, 4):  # Duyệt qua mỗi cặp i, j với i < j để tránh lặp lại
                    if matrix[j][i] > matrix[i][j]:
                        difference = matrix[j][i] - matrix[i][j]
                        result.append(f"{people[i]} nợ {people[j]} số tiền: {difference:.1f}")
                    elif matrix[i][j] > matrix[j][i]:
                        difference = matrix[i][j] - matrix[j][i]
                        result.append(f"{people[j]} nợ {people[i]} số tiền: {difference:.1f}")
        except Exception as e:
            result = [f"Lỗi khi đọc Google Sheets: {str(e)}", f"Tên các cột đọc được: {df.columns.tolist()}"]

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

