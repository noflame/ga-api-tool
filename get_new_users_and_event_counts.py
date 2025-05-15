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

def make_ga_report_call(token, property_id, request_body):
    url = f'https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=request_body)
    print(f"API 響應狀態碼: {response.status_code} (查詢: {request_body.get('metrics')[0].get('name')} / {request_body.get('dimensionFilter')})")
    if response.status_code == 200:
        return response.json()
    else:
        print("\n請求失敗! 錯誤詳情:")
        try:
            error_details = response.json()
            print(json.dumps(error_details, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"無法解析錯誤詳情: {response.text}")
        return None

def fetch_new_users_and_event_counts():
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

        # 請求 1: 獲取 newUsers 指標
        print("\n正在查詢 newUsers...")
        new_users_request = {
            "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
            "metrics": [{"name": "newUsers"}]
        }
        new_users_result = make_ga_report_call(token, GA4_PROPERTY_ID, new_users_request)
        total_new_users = "0"
        if new_users_result and new_users_result.get("rows"):
            total_new_users = new_users_result["rows"][0].get("metricValues", [{}])[0].get("value", "0")
        print(f"總新使用者 (newUsers): {total_new_users}")
        # print(json.dumps(new_users_result, indent=2, ensure_ascii=False))

        # 請求 2: 獲取觸發 first_visit 事件的 activeUsers
        print("\n正在查詢觸發 first_visit 的活躍使用者...")
        first_visit_request = {
            "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
            "metrics": [{"name": "activeUsers"}],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "eventName",
                    "stringFilter": {
                        "matchType": "EXACT",
                        "value": "first_visit"
                    }
                }
            }
        }
        first_visit_users_result = make_ga_report_call(token, GA4_PROPERTY_ID, first_visit_request)
        users_with_first_visit = "0"
        if first_visit_users_result and first_visit_users_result.get("rows"):
            users_with_first_visit = first_visit_users_result["rows"][0].get("metricValues", [{}])[0].get("value", "0")
        print(f"觸發 first_visit 事件的活躍使用者: {users_with_first_visit}")
        # print(json.dumps(first_visit_users_result, indent=2, ensure_ascii=False))

        # 請求 3: 獲取觸發 first_open 事件的 activeUsers
        print("\n正在查詢觸發 first_open 的活躍使用者...")
        first_open_request = {
            "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
            "metrics": [{"name": "activeUsers"}],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "eventName",
                    "stringFilter": {
                        "matchType": "EXACT",
                        "value": "first_open"
                    }
                }
            }
        }
        first_open_users_result = make_ga_report_call(token, GA4_PROPERTY_ID, first_open_request)
        users_with_first_open = "0"
        if first_open_users_result and first_open_users_result.get("rows"):
            users_with_first_open = first_open_users_result["rows"][0].get("metricValues", [{}])[0].get("value", "0")
        print(f"觸發 first_open 事件的活躍使用者: {users_with_first_open}")
        # print(json.dumps(first_open_users_result, indent=2, ensure_ascii=False))

        print("\n--- 數據總結 --- ")
        print(f"總新使用者 (newUsers): {total_new_users}")
        print(f"觸發 first_visit 的活躍使用者: {users_with_first_visit}")
        print(f"觸發 first_open 的活躍使用者: {users_with_first_open}")
        return True

    except FileNotFoundError:
        print(f"\n錯誤: 服務帳戶金鑰文件 '{SERVICE_ACCOUNT_FILE}' 未找到。請確認文件路徑是否正確。")
        return False
    except Exception as e:
        print(f"\n發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("===== Google Analytics Data API - 新使用者及相關事件計數工具 =====")
    if not os.environ.get('GA4_PROPERTY_ID'):
        print("錯誤：GA4_PROPERTY_ID 環境變數未設定。")
        print('請先設定 GA4_PROPERTY_ID 環境變數再執行此腳本。')
    else:
        fetch_new_users_and_event_counts()
    print("\n===== 測試完成 =====") 