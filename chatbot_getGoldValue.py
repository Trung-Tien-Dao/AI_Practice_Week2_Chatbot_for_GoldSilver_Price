import os
import json
import urllib3
import requests
import httpx
from openai import AzureOpenAI

proxies = None
if os.path.exists("proxy_config.json"):
    with open("proxy_config.json", encoding="utf-8") as pf:
        proxy_json = json.load(pf)
        username = proxy_json.get("username", "")
        password = proxy_json.get("password", "")
        hostname = proxy_json.get("hostname", "")
        if username and password and hostname:
            proxy_url = f"http://{username}:{password}@{hostname}"
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }

with open("keystore.config", encoding="utf-8") as ks:
    endpoint = ks.readline().strip()
    api_key = ks.readline().strip()
os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
os.environ["AZURE_OPENAI_API_KEY"] = api_key

client = AzureOpenAI(
    api_version="2024-07-01-preview",
    azure_endpoint=endpoint,
    api_key=api_key,
    http_client=httpx.Client(verify=False)
)

code_map = {
    "XAUUSD": "Vàng Thế Giới (XAU/USD)",
    "SJL1L10": "SJC 9999",
    "SJ9999": "Nhẫn SJC",
    "DOHNL": "DOJI Hà Nội",
    "DOHCML": "DOJI HCM",
    "DOJINHTV": "DOJI Nữ Trang",
    "BTSJC": "Bảo Tín SJC",
    "BT9999NTT": "Bảo Tín 9999",
    "PQHNVM": "PNJ Hà Nội",
    "PQHN24NTT": "PNJ 24K",
    "VNGSJC": "VN Gold SJC",
    "VIETTINMSJC": "Viettin SJC"
}

### Hàm lấy giá vàng từ vang.today
def get_gold_value(type_of_gold: str) -> str:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Lấy giá vàng từ API vang.today cho mã loại vàng
    url = f"https://www.vang.today/api/prices?type={type_of_gold}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, proxies=proxies, timeout=10, verify=False, headers=headers)
        response.raise_for_status()
        # In ra phản hồi thô từ API (nếu cần debug)
        #print("Phản hồi thô từ API:", response.text)
        data = response.json()
        buy = data.get('buy')
        sell = data.get('sell')
        if buy is None or sell is None:
            return "Không tìm thấy giá vàng cho hôm nay."
        if type_of_gold not in code_map:
            return f"Mã vàng '{type_of_gold}' không được hỗ trợ."
        desc = code_map[type_of_gold]
        unit = "USD/oz" if "USD" in desc else "VNĐ/lượng"
        return f"Giá vàng {type_of_gold} ({desc}): Mua {buy}, Bán {sell} ({unit})"
    except Exception as e:
        return f"Lỗi khi lấy giá vàng của {type_of_gold}: {e}"

### Hàm lấy giá bạc từ MetalPriceAPI
def get_silver_value(currency_code: str) -> str:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Lấy giá bạc từ API MetalPriceAPI cho mã tiền tệ
    url = f"https://api.metalpriceapi.com/v1/latest?api_key=d788a657670523b64ab821e986094ccc&base=XAG&currencies={currency_code}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, proxies=proxies, timeout=10, verify=False, headers=headers)
        response.raise_for_status()
        data = response.json()
        rates = data.get('rates', {})
        price = rates.get(currency_code)
        if price is None:
            return f"Không tìm thấy giá bạc cho đơn vị tiền tệ '{currency_code}'."
        return f"Giá bạc (XAG): {price} {currency_code}/oz"
    except Exception as e:
        return f"Lỗi khi lấy giá bạc cho đơn vị tiền tệ '{currency_code}': {e}"

if __name__ == "__main__":
    # In thông báo khởi động chatbot
    print("Chatbot giá vàng Việt Nam (Azure OpenAI Function Calling). Hãy hỏi về giá vàng hoặc bạc hôm nay!")
    # Khởi tạo danh sách tin nhắn cho hội thoại
    messages = [
        {"role": "system", "content": "Bạn là một trợ lý AI chuyên về giá vàng và bạc Việt Nam."}
    ]
    # Định nghĩa các hàm để AI có thể gọi
    function_definitions = [
        {
            "name": "get_gold_value",
            "description": "Trả về giá vàng cho loại vàng theo mã code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type_of_gold": {
                        "type": "string",
                        "description": "Mã loại vàng (ví dụ: XAUUSD, SJL1L10, SJ9999, DOHNL, DOHCML, DOJINHTV, BTSJC, BT9999NTT, PQHNVM, PQHN24NTT, VNGSJC, VIETTINMSJC)"
                    }
                },
                "required": ["type_of_gold"]
            }
        },
        {
            "name": "get_silver_value",
            "description": "Trả về giá bạc cho mã tiền tệ quốc gia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency_code": {
                        "type": "string",
                        "description": "Mã tiền tệ ISO 4217 (ví dụ: VND, USD, EUR, JPY, XAG)"
                    }
                },
                "required": ["currency_code"]
            }
        }
    ]
    while True:
        # Nhận đầu vào từ người dùng
        user_input = input("Bạn: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Tạm biệt!")
            break
        # Thêm tin nhắn người dùng vào hội thoại
        messages.append({"role": "user", "content": user_input})

        # Gửi hội thoại và hàm cho AI xử lý
        response = client.chat.completions.create(
            model="GPT-4.1-mini",
            messages=messages,
            functions=function_definitions,
            function_call="auto",
            max_tokens=256
        )
        choice = response.choices[0]
        message = choice.message

        # Kiểm tra xem AI có muốn gọi hàm không
        if hasattr(message, "function_call") and message.function_call:
            func_name = message.function_call.name
            func_args = json.loads(message.function_call.arguments)
            if func_name == "get_gold_value":
                type_of_gold = func_args.get("type_of_gold", "")
                if type_of_gold not in code_map:
                    result = f"Mã vàng '{type_of_gold}' không được hỗ trợ."
                else:
                    result = get_gold_value(type_of_gold)
            elif func_name == "get_silver_value":
                currency_code = func_args.get("currency_code", "")
                result = get_silver_value(currency_code)
            else:
                result = "Chức năng không được hỗ trợ."
            # Thêm kết quả hàm vào hội thoại và in ra cho người dùng
            messages.append({
                "role": "function",
                "name": func_name,
                "content": result
            })
            print(f"Chatbot: {result}")
        else:
            # Nếu AI không gọi hàm, in ra phản hồi của AI
            print(f"Chatbot: {message.content}")