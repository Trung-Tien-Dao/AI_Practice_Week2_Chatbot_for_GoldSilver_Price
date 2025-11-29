# Chatbot Giá Vàng & Bạc

## Mô tả chương trình

Chương trình chatbot này hỗ trợ truy vấn giá vàng và bạc theo thời gian thực, sử dụng AI để nhận diện nhu cầu người dùng và tự động lấy thông tin từ các API chuyên biệt.

### 1. Truy vấn giá vàng
- Người dùng có thể hỏi giá vàng theo các loại mã vàng sau (liệt kê đầy đủ):
  - XAUUSD: Vàng Thế Giới (XAU/USD)
  - SJL1L10: SJC 9999
  - SJ9999: Nhẫn SJC
  - DOHNL: DOJI Hà Nội
  - DOHCML: DOJI HCM
  - DOJINHTV: DOJI Nữ Trang
  - BTSJC: Bảo Tín SJC
  - BT9999NTT: Bảo Tín 9999
  - PQHNVM: PNJ Hà Nội
  - PQHN24NTT: PNJ 24K
  - VNGSJC: VN Gold SJC
  - VIETTINMSJC: Viettin SJC
- Đơn vị trả về: VNĐ/lượng cho vàng trong nước, USD/oz cho vàng thế giới.
- Nguồn API: [https://www.vang.today/api/prices]

### 2. Truy vấn giá bạc
- Người dùng có thể hỏi giá bạc ở bất kỳ quốc gia nào, chatbot sẽ tự động nhận diện và lấy mã tiền tệ ISO 4217 tương ứng (ví dụ: VND, USD, EUR, JPY, ...).
- Đơn vị trả về: {mã tiền tệ}/oz
- Nguồn API: [https://api.metalpriceapi.com/v1/latest]

### 3. Hỗ trợ proxy
- Chương trình hỗ trợ truy cập qua proxy, cấu hình qua file `proxy_config.json` với template sau:

```json
{
    "hostname": "your_ip:your_port",
    "username": "your_username",
    "password": "your_password"
}
```

### 4. Cách sử dụng
- Chạy chương trình bằng lệnh:
  ```
  py chatbot_getGoldValue.py
  ```
- Nhập câu hỏi tự nhiên về giá vàng hoặc bạc, ví dụ:
  - "Giá vàng PNJ Hà Nội hôm nay?"
  - "Giá bạc tại Mỹ?"
  - "Vàng thế giới bao nhiêu?"

### 5. Yêu cầu
- Python 3.12
- Các thư viện: requests, httpx, openai, urllib3
- Kết nối internet
