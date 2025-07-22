import requests
import xmltodict
from flask import Flask, jsonify
from flask_cors import CORS

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Kích hoạt CORS cho tất cả các route
CORS(app)

# --- QUẢN LÝ CÁC NGUỒN CẤP RSS ---
# Lưu trữ các nguồn cấp RSS theo danh mục để dễ quản lý và mở rộng
RSS_FEEDS = {
    "chung-khoan": "https://cafef.vn/thi-truong-chung-khoan.rss",
    "bat-dong-san": "https://vietstock.vn/rss/bat-dong-san.rss",
    "tai-chinh": "https://vietstock.vn/rss/tai-chinh.rss",
    "vi-mo": "https://vietstock.vn/rss/vi-mo.rss",
    "doanh-nghiep": "https://vietstock.vn/rss/doanh-nghiep.rss",
    "cong-nghe": "https://vietstock.vn/rss/cong-nghe.rss"
    # Bạn có thể thêm các nguồn RSS khác vào đây
}

# --- HÀM TRỢ GIÚP (HELPER FUNCTION) ---
def fetch_and_parse_rss(url):
    """
    Hàm này nhận một URL, tìm nạp dữ liệu RSS, và phân tích cú pháp thành một dictionary.
    Trả về một tuple: (danh_sách_tin_tức, lỗi).
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Báo lỗi nếu yêu cầu HTTP không thành công (ví dụ: 404, 500)

        # Dùng xmltodict để chuyển đổi dữ liệu XML sang Dictionary của Python
        data_dict = xmltodict.parse(response.content)
        
        # [span_0](start_span)Lấy danh sách các bài viết từ cấu trúc RSS[span_0](end_span)
        news_items = data_dict.get('rss', {}).get('channel', {}).get('item', [])
        return news_items, None
    except requests.exceptions.RequestException as e:
        return None, f"Lỗi khi lấy dữ liệu từ URL: {e}"
    except Exception as e:
        return None, f"Lỗi xử lý dữ liệu XML: {e}"

# --- CÁC ĐỊNH TUYẾN API (API ROUTES) ---

@app.route("/")
def home():
    """
    [span_1](start_span)Route mặc định để cung cấp thông tin hướng dẫn sử dụng API.[span_1](end_span)
    """
    return (
        "<html><body>"
        "<h1>Chào mừng bạn đến với API Tin tức!</h1>"
        "<p>Sử dụng các endpoint sau:</p>"
        "<ul>"
        "<li><a href='/api/categories'>/api/categories</a> - Lấy danh sách tất cả các danh mục tin tức.</li>"
        "<li>/api/news/&lt;category_name&gt; - Lấy tin tức cho một danh mục cụ thể.</li>"
        "</ul>"
        "</body></html>"
    )

@app.route("/api/categories")
def get_categories():
    """
    API endpoint để lấy danh sách tất cả các danh mục tin tức có sẵn.
    """
    return jsonify(list(RSS_FEEDS.keys()))

@app.route("/api/news/<string:category>")
def get_news_by_category(category):
    """
    API endpoint động để lấy tin tức dựa trên danh mục được cung cấp.
    """
    # Lấy URL RSS từ dictionary dựa trên category key
    rss_url = RSS_FEEDS.get(category)

    # Nếu không tìm thấy danh mục, trả về lỗi 404
    if not rss_url:
        return jsonify({"error": f"Danh mục '{category}' không tồn tại."}), 404

    # Lấy và phân tích cú pháp dữ liệu RSS
    news_items, error = fetch_and_parse_rss(rss_url)

    # Nếu có lỗi, trả về thông báo lỗi và mã trạng thái 500
    if error:
        return jsonify({"error": error}), 500
    
    # Trả về dữ liệu tin tức dưới dạng JSON
    return jsonify(news_items)

# Dòng if __name__ == '__main__' hữu ích để chạy thử trên máy tính cá nhân.
# [span_2](start_span)Nó không bắt buộc khi triển khai trên các dịch vụ như Render với Gunicorn.[span_2](end_span)
if __name__ == '__main__':
    app.run(debug=True, port=5000)

