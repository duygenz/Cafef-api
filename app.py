from flask import Flask, jsonify
from flask_cors import CORS  # Import thư viện CORS
import requests
from bs4 import BeautifulSoup

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Kích hoạt CORS cho tất cả các route trong ứng dụng
CORS(app)

def get_cafef_news():
    """
    Hàm này thực hiện scraping tin tức từ trang CafeF.
    """
    url = "https://m.cafef.vn/thi-truong-chung-khoan.chn"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Báo lỗi nếu request không thành công

        soup = BeautifulSoup(response.content, 'html.parser')
        news_list = []
        
        # Selector đã được kiểm tra để lấy đúng các bài viết
        articles = soup.select('ul.post-listing li a')
        
        for article in articles:
            title = article.get('title')
            link = article.get('href')
            
            if title and link:
                # Đảm bảo link là một URL đầy đủ
                if not link.startswith('http'):
                    link = "https://m.cafef.vn" + link
                
                news_list.append({"title": title, "link": link})
                
        return news_list

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi request đến CafeF: {e}")
        return None

@app.route('/api/news', methods=['GET'])
def get_news_api():
    """
    Đây là endpoint API của bạn.
    """
    news_data = get_cafef_news()
    if news_data:
        return jsonify(news_data)
    else:
        return jsonify({"error": "Không thể lấy được dữ liệu tin tức từ CafeF."}), 500

# Dòng này để Render biết cách chạy ứng dụng
if __name__ == '__main__':
    # Khi chạy trên local, bạn có thể để debug=True
    # Khi deploy, gunicorn sẽ được sử dụng
    app.run(host='0.0.0.0', port=8080)
