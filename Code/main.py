import pandas as pd
import numpy as np

# URL của Google Sheets sau khi chỉnh sửa
google_sheet_url = 'https://docs.google.com/spreadsheets/d/1GKKCltEtf9OfNIN9QxMXpyE01fyAqaXnvKnYIhNO3ro/export?format=csv&gid=539814940'

# Đọc dữ liệu từ Google Sheets vào pandas DataFrame
df = pd.read_csv(google_sheet_url, nrows=100, usecols=range(11))

# In ra tên các cột để kiểm tra trùng lặp hoặc vấn đề khác
print("Columns:", df.columns)

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
    total_money = df.loc[idx, 'Money']

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

# Bây giờ kiểm tra các cặp giá trị a[i][j] và a[j][i]
print("\nKết quả kiểm tra nợ giữa các người:")
for i in range(4):
    for j in range(i+1, 4):  # Duyệt qua mỗi cặp i, j với i < j để tránh lặp lại
        if matrix[j][i] > matrix[i][j]:
            difference = matrix[j][i] - matrix[i][j]
            print(f"{people[i]} nợ {people[j]} số tiền: {difference:.1f}")
        elif matrix[i][j] > matrix[j][i]:
            difference = matrix[i][j] - matrix[j][i]
            print(f"{people[j]} nợ {people[i]} số tiền: {difference:.1f}")
