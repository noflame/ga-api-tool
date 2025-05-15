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
# GA4 中活躍使用者即為不重複使用者
def fetch_active_users():
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
        print("\n步驟 4: 發送 API 請求以獲取活躍使用者人數...")
        url = f'https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY_ID}:runReport'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "dateRanges": [
                {
                    "startDate": "7daysAgo",
                    "endDate": "today"
                }
            ],
            "dimensions": [
                {
                    "name": "date"
                }
            ],
            "metrics": [
                {
                    "name": "activeUsers"  # GA4 中活躍使用者即為不重複使用者
                }
            ]
        }
        
        # 5. 發送請求並輸出結果
        response = requests.post(url, headers=headers, json=data)
        print(f"API 響應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("\n成功! 活躍使用者人數 API 響應內容:")
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
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

# 6. 執行額外的診斷測試 (可選，但有助於調試)
def run_diagnostics():
    if not GA4_PROPERTY_ID:
        print("警告：GA4_PROPERTY_ID 環境變數未設定，部分診斷測試可能無法執行。")

    print("\n====== 執行診斷測試 ======")
    
    # 測試服務帳戶基本資訊
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            key_data = json.load(f)
        
        print("\n服務帳戶診斷:")
        print(f"- 專案 ID: {key_data.get('project_id')}")
        print(f"- 客戶端 Email: {key_data.get('client_email')}")
        print(f"- 令牌 URI: {key_data.get('token_uri')}")
        print(f"- 私鑰 ID: {key_data.get('private_key_id')}")
        print(f"- 私鑰格式正確: {'是' if key_data.get('private_key', '').startswith('-----BEGIN PRIVATE KEY-----') else '否'}")
    except FileNotFoundError:
        print(f"讀取服務帳戶文件 '{SERVICE_ACCOUNT_FILE}' 時出錯: 文件未找到。")
    except Exception as e:
        print(f"讀取服務帳戶文件時出錯: {str(e)}")
    
    # 測試 GA4 屬性列表 API
    if GA4_PROPERTY_ID:
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            credentials.refresh(Request())
            token = credentials.token
            
            print("\n嘗試列出可存取的 GA4 屬性:")
            admin_url = 'https://analyticsadmin.googleapis.com/v1beta/properties'
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.get(admin_url, headers=headers)
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'properties' in result and result.get('properties'):
                    print(f"找到 {len(result['properties'])} 個屬性:")
                    for prop in result['properties']:
                        prop_id = prop.get('name', '').split('/')[-1]
                        display_name = prop.get('displayName', '未知')
                        print(f"- 屬性 ID: {prop_id} | 顯示名稱: {display_name} {'<-- 目前設定使用' if prop_id == GA4_PROPERTY_ID else ''}")
                else:
                    print("未發現任何可存取的 GA4 屬性!")
            else:
                print(f"無法列出屬性。錯誤: {response.text}")
        except FileNotFoundError:
            print(f"列出屬性時出錯: 服務帳戶金鑰文件 '{SERVICE_ACCOUNT_FILE}' 未找到。")
        except Exception as e:
            print(f"列出屬性時出錯: {str(e)}")
    else:
        print("\n跳過 GA4 屬性列表測試，因為 GA4_PROPERTY_ID 未設定。")

# 7. 主函數
if __name__ == "__main__":
    print("===== Google Analytics Data API - 活躍使用者人數測試工具 =====")
    if not os.environ.get('GA4_PROPERTY_ID'):
        print("錯誤：GA4_PROPERTY_ID 環境變數未設定。")
        print('請先設定 GA4_PROPERTY_ID 環境變數再執行此腳本。')
        print('例如：export GA4_PROPERTY_ID="YOUR_PROPERTY_ID" (Linux/macOS)')
        print('或：set GA4_PROPERTY_ID=YOUR_PROPERTY_ID (Windows Command Prompt)')
        print('或：$env:GA4_PROPERTY_ID="YOUR_PROPERTY_ID" (Windows PowerShell)')
    else:
        success = fetch_active_users()
        
        if not success:
            run_diagnostics()
            
    print("\n===== 測試完成 ======") 