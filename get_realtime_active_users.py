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
def fetch_realtime_active_users():
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
        
        # 4. 設定 API 請求 (使用 Realtime Reporting API)
        print("\n步驟 4: 發送 API 請求以獲取即時活躍使用者數量...")
        # 注意：Realtime API 的端點與 Beta Reporting API 不同
        url = f'https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY_ID}:runRealtimeReport'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "metrics": [
                {
                    "name": "activeUsers" # 即時報告中的活躍使用者
                }
            ]
            # Realtime API 通常不需要 dateRanges
            # 可以根據需要加入 dimensions，例如： "dimensions": [{"name": "minutesAgo"}]
        }
        
        # 5. 發送請求並輸出結果
        response = requests.post(url, headers=headers, json=data)
        print(f"API 響應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("\n成功! 即時活躍使用者數量 API 響應內容:")
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            # 可以加入更友好的格式化輸出
            if result.get("rows"):
                realtime_users = result["rows"][0].get("metricValues", [{}])[0].get("value", "0")
                print(f"\n格式化輸出:")
                print(f"- 目前在線使用者 (活躍使用者): {realtime_users}")
            elif result.get("rowCount", 0) == 0:
                 print(f"\n目前沒有即時活躍使用者數據。")
            else:
                print(f"\n回應中未找到預期的 'rows' 數據結構。")

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

# ... (run_diagnostics 函數可以省略或複製之前的版本)

# 7. 主函數
if __name__ == "__main__":
    print("===== Google Analytics Data API - 即時在線使用者測試工具 =====")
    if not os.environ.get('GA4_PROPERTY_ID'):
        print("錯誤：GA4_PROPERTY_ID 環境變數未設定。")
        print('請先設定 GA4_PROPERTY_ID 環境變數再執行此腳本。')
    else:
        success = fetch_realtime_active_users()
        
    print("\n===== 測試完成 ======") 