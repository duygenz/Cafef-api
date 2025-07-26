from flask import Flask, jsonify
import feedparser
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Danh sách các RSS feed bạn muốn lấy tin tức
RSS_FEEDS = [
    "https://vietstock.vn/830/chung-khoan/co-phieu.rss",
    "https://cafef.vn/thi-truong-chung-khoan.rss",
    "https://vietstock.vn/145/chung-khoan/y-kien-chuyen-gia.rss",
    "https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh-doanh.rss",
    "https://vietstock.vn/1328/dong-duong/thi-truong-chung-khoan.rss",
]

# Sử dụng ThreadPoolExecutor để lấy dữ liệu từ nhiều RSS feed song song
executor = ThreadPoolExecutor(max_workers=5)

def fetch_feed(url):
    """
    Hàm để lấy và phân tích cú pháp một RSS feed.
    """
    try:
        # Sử dụng requests để đảm bảo có thể thiết lập user-agent nếu cần
        # hoặc xử lý các lỗi kết nối tốt hơn.
        # Tuy nhiên, feedparser thường tự xử lý các URL HTTP/HTTPS.
        # response = requests.get(url, timeout=10)
        # feed = feedparser.parse(response.text)

        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries:
            title = getattr(entry, 'title', 'No Title')
            link = getattr(entry, 'link', 'No Link')
            published = getattr(entry, 'published', getattr(entry, 'updated', 'No Date'))
            summary = getattr(entry, 'summary', getattr(entry, 'description', 'No Summary'))

            news_items.append({
                'title': title,
                'link': link,
                'published': published,
                'summary': summary
            })
        return news_items
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

@app.route('/news', methods=['GET'])
def get_news():
    """
    Endpoint để lấy tin tức từ tất cả các RSS feed đã cấu hình.
    """
    all_news = []
    # Lấy dữ liệu từ tất cả các feed song song
    futures = [executor.submit(fetch_feed, feed_url) for feed_url in RSS_FEEDS]
    for future in futures:
        all_news.extend(future.result())

    # Sắp xếp tin tức theo ngày xuất bản (tùy chọn)
    # Cần một cách chuẩn hóa để so sánh ngày tháng nếu muốn sắp xếp chính xác.
    # Hiện tại chỉ sắp xếp đơn giản, có thể không hoàn hảo nếu định dạng ngày khác nhau.
    # all_news.sort(key=lambda x: x['published'], reverse=True)

    return jsonify(all_news)

@app.route('/', methods=['GET'])
def home():
    """
    Trang chủ đơn giản để kiểm tra API đang chạy.
    """
    return "API tin tức đang chạy! Truy cập /news để xem tin tức."

if __name__ == '__main__':
    # Chạy ứng dụng Flask. Trong môi trường production (như Render),
    # bạn sẽ sử dụng Gunicorn hoặc một WSGI server khác.
    # Đối với local testing:
    app.run(debug=True, host='0.0.0.0', port=5000)

