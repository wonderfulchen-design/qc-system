#!/usr/bin/env python3
import requests

# 登录
token = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 获取问题列表
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=5', headers=headers)
issues = r.json()['data']

print('='*60)
print('图片显示测试')
print('='*60)

for issue in issues:
    print(f"\n问题：{issue.get('issue_no')}")
    print(f"商品图：{issue.get('product_image') or '无'}")
    
    images = issue.get('issue_images', [])
    if images:
        print(f"问题图：{len(images)} 张")
        for i, img in enumerate(images[:3], 1):
            print(f"  [{i}] {img}")
    else:
        print("问题图：无")

print("\n" + "="*60)

# 测试图片访问
if issues:
    first_issue = issues[0]
    images = first_issue.get('issue_images', [])
    if images:
        img_url = f"http://localhost:8000{images[0]}"
        print(f"\n测试访问图片：{img_url}")
        try:
            r = requests.get(img_url, timeout=5)
            print(f"状态码：{r.status_code}")
            print(f"文件大小：{len(r.content)} bytes")
            print(f"Content-Type: {r.headers.get('content-type')}")
            if r.status_code == 200:
                print("[OK] 图片可以正常访问!")
            else:
                print("[ERROR] 图片访问失败")
        except Exception as e:
            print(f"[ERROR] {e}")
