import json
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
        #print("Raw API response:", response.text)
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
import os
import urllib3
import requests
import httpx
from openai import AzureOpenAI

if __name__ == "__main__":
    print("Chatbot giá vàng Việt Nam (OpenAI Function Calling). Hãy hỏi về giá vàng hôm nay!")
    messages = [
        {"role": "system", "content": "Bạn là một trợ lý AI chuyên về giá vàng Việt Nam."}
    ]
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
        }
    ]
    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Tạm biệt!")
            break
        messages.append({"role": "user", "content": user_input})

        # Dùng AI để xác định nhu cầu người dùng là hỏi giá vàng hay bạc
        intent_prompt = (
            "Người dùng đang hỏi về giá vàng hay giá bạc? Trả về 'gold' hoặc 'silver', không giải thích.\n"
            f"Yêu cầu: {user_input}"
        )
        intent_response = client.chat.completions.create(
            model="GPT-4.1-mini",
            messages=[{"role": "user", "content": intent_prompt}],
            max_tokens=6
        )
        intent = intent_response.choices[0].message.content.strip().lower()

        if intent == "silver":
            # Dùng AI để lấy mã tiền tệ quốc gia từ yêu cầu người dùng
            currency_prompt = (
                "Hãy trả về mã tiền tệ quốc gia phù hợp nhất với yêu cầu người dùng. "
                "Chỉ trả về mã tiền tệ ISO 4217, không giải thích.\n"
                f"Yêu cầu: {user_input}"
            )
            currency_response = client.chat.completions.create(
                model="GPT-4.1-mini",
                messages=[{"role": "user", "content": currency_prompt}],
                max_tokens=10
            )
            currency_code = currency_response.choices[0].message.content.strip().split()[0]
            result = get_silver_value(currency_code)
            print(f"Chatbot: {result}")
        elif intent == "gold":
            # Dùng AI để lấy mã loại vàng từ yêu cầu người dùng
            mapping_prompt = (
                "Dưới đây là các mã loại vàng và mô tả. Hãy trả về mã phù hợp nhất với yêu cầu người dùng. "
                "Chỉ trả về mã, không giải thích.\n" +
                "\n".join([f"{code}: {desc}" for code, desc in code_map.items()]) +
                f"\n\nYêu cầu: {user_input}"
            )
            mapping_response = client.chat.completions.create(
                model="GPT-4.1-mini",
                messages=[{"role": "user", "content": mapping_prompt}],
                max_tokens=20
            )
            mapped_code = mapping_response.choices[0].message.content.strip().split()[0]
            # Kiểm tra mã vàng trước khi gọi hàm lấy giá
            if mapped_code not in code_map:
                print(f"Chatbot: Mã vàng '{mapped_code}' không được hỗ trợ.")
            else:
                result = get_gold_value(mapped_code)
                print(f"Chatbot: {result}")
        else:
            print("Chatbot: Xin lỗi, tôi chỉ hỗ trợ tra cứu giá vàng hoặc bạc.")