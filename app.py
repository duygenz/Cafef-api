import requests
import xmltodict
from flask import Flask, jsonify
from flask_cors import CORS

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Kích hoạt CORS cho tất cả các route
CORS(app)

# URL của RSS feed từ CafeF
RSS_URL = 'https://cafef.vn/thi-truong-chung-khoan.rss'

@app.route("/")
def home():
    # Route mặc định để kiểm tra xem server có hoạt động không
    return "Chào mừng bạn đến với API tin tức CafeF!"

@app.route("/api/news")
def get_news():
    try:
        # Gửi yêu cầu đến URL của RSS feed
        response = requests.get(RSS_URL)
        response.raise_for_status()  # Báo lỗi nếu yêu cầu không thành công

        # Dùng xmltodict để chuyển đổi dữ liệu XML sang Dictionary của Python
        data_dict = xmltodict.parse(response.content)
        
        # Lấy danh sách các bài viết
        news_items = data_dict.get('rss', {}).get('channel', {}).get('item', [])
        
        # Trả về dữ liệu dưới dạng JSON
        return jsonify(news_items)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Lỗi khi lấy dữ liệu: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Lỗi xử lý dữ liệu: {e}"}), 500

# Dòng if __name__ == '__main__': không bắt buộc khi triển khai trên Render với Gunicorn
# nhưng nó hữu ích để chạy thử trên máy tính cá nhân.
