import requests

# 测试图片访问
test_urls = [
    'http://localhost:8000/uploads/1_20260325223002.jpg',
    'http://localhost:8000/api/issues?page=1&page_size=1'
]

for url in test_urls:
    print(f"\n测试：{url}")
    try:
        r = requests.get(url, timeout=5)
        print(f"  状态码：{r.status_code}")
        if r.status_code == 200:
            print(f"  [OK] 成功！大小：{len(r.content)} bytes")
            if 'image' in r.headers.get('content-type', ''):
                print(f"  [OK] Content-Type: {r.headers['content-type']}")
        else:
            print(f"  [ERROR] {r.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] {e}")
