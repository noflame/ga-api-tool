import json
import os

from google.oauth2 import service_account
import requests
from google.auth.transport.requests import Request

# 1. 載入您的服務帳戶金鑰文件
SERVICE_ACCOUNT_FILE = 'ga-service-account.json'  # 替換為您的金鑰文件路徑
GA4_PROPERTY_ID = os.environ.get('GA4_PROPERTY_ID')  # 從環境變數讀取 GA4 屬性 ID

# 2. 定義所需的 API 範圍
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

# 3. 嘗試獲取令牌並進行 API 調用
def fetch_device_category_all_time_data():
    if not GA4_PROPERTY_ID:
        print("錯誤：GA4_PROPERTY_ID 環境變數未設定。請設定該變數再執行。")
        return False
        
    try:
        print("步驟 1: 嘗試載入服務帳戶金鑰...")
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            key_data = json.load(f)
            print(f"金鑰資訊: 專案 ID: {key_data.get('project_id')}, 客戶端 Email: {key_data.get('client_email')}")
        
        print("\n步驟 2: 建立憑證...")
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        print("\n步驟 3: 獲取訪問令牌...")
        credentials.refresh(Request())
        token = credentials.token
        print(f"令牌獲取成功: {token[:20]}...")
        
        # 4. 設定 API 請求
        print("\n步驟 4: 發送 API 請求以獲取各裝置類別的總計使用者數據...")
        url = f'https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY_ID}:runReport'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 設定一個非常早的開始日期以獲取近似「所有時間」的數據
        # 您可以根據您 GA4 資源的實際開始日期調整此處的 startDate
        # 例如，如果您的資源從 2021-01-15 開始，可以使用 "2021-01-15"
        # GA4 正式發布是在 2020 年 10 月，所以 "2020-07-01" 或 "2020-01-01" 通常是安全的起點
        all_time_start_date = "2020-07-01" 
        print(f"注意：將使用 startDate '{all_time_start_date}' 和 endDate 'today' 來模擬獲取總計數據。")

        data = {
            "dateRanges": [
                {
                    "startDate": all_time_start_date,
                    "endDate": "today"
                }
            ],
            "dimensions": [
                {
                    "name": "deviceCategory"
                }
            ],
            "metrics": [
                {
                    "name": "activeUsers"
                }
            ]
        }
        
        # 5. 發送請求並輸出結果
        response = requests.post(url, headers=headers, json=data)
        print(f"API 響應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("\n成功! 各裝置類別的總計使用者數據 API 響應內容:")
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            # 可以加入更友好的格式化輸出
            if result.get("rows"):
                print("\n格式化輸出:")
                for row in result["rows"]:
                    device = row.get("dimensionValues", [{}])[0].get("value", "未知裝置")
                    users = row.get("metricValues", [{}])[0].get("value", "0")
                    print(f"- 裝置類別: {device}, 活躍使用者 (總計): {users}")
            elif result.get("rowCount", 0) == 0:
                print("\n在指定的廣泛日期範圍內，未找到任何裝置類別的數據。")
            else:
                print("\n回應中未找到預期的 'rows' 數據結構。")
            return True
        else:
            print("\n請求失敗! 錯誤詳情:")
            try:
                error_details = response.json()
                print(json.dumps(error_details, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"無法解析錯誤詳情: {response.text}: {e}")
            return False
            
    except FileNotFoundError:
        print(f"\n錯誤: 服務帳戶金鑰文件 '{SERVICE_ACCOUNT_FILE}' 未找到。請確認文件路徑是否正確。")
        return False
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# ... (run_diagnostics 函數可以省略或根據需要添加)

# 7. 主函數
if __name__ == "__main__":
    print("===== Google Analytics Data API - 各裝置類別總計使用者數據測試工具 =====")
    if not os.environ.get('GA4_PROPERTY_ID'):
        print("錯誤：GA4_PROPERTY_ID 環境變數未設定。")
        print('請先設定 GA4_PROPERTY_ID 環境變數再執行此腳本。')
    else:
        success = fetch_device_category_all_time_data()
        
    print("\n===== 測試完成 ======") 