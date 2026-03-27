#!/usr/bin/env python3
"""
测试提交带图片的问题并验证显示
"""
import requests
import base64
import os

API_BASE = "http://localhost:8000"

# 登录
print("="*70)
print("测试：提交带图片的问题")
print("="*70)

token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("\n[1/4] 登录成功")

# 准备测试图片（使用占位图）
test_images = []
print("\n[2/4] 上传图片...")

for i in range(1, 4):  # 上传 3 张图片
    # 创建测试图片（简单 JPEG）
    img_data = f"FAKE_IMAGE_DATA_{i}".encode('utf-8')
    
    files = {'file': (f'test_img_{i}.jpg', img_data, 'image/jpeg')}
    r = requests.post(f"{API_BASE}/uploads", headers=headers, files=files)
    
    if r.status_code == 200:
        url = r.json()['url']
        test_images.append(url)
        print(f"  [OK] 图片 {i}: {url}")
    else:
        print(f"  [ERR] 图片 {i} 上传失败：{r.text}")

if not test_images:
    print("\n[ERROR] 没有成功上传的图片，使用模拟 URL")
    test_images = [
        "/uploads/1_20260325223002.jpg",
        "/uploads/1_20260325223003.jpg",
        "/uploads/1_20260325223004.jpg"
    ]

# 提交问题
print("\n[3/4] 提交问题...")

issue_data = {
    "goods_no": "25675168959",
    "factory_name": "春秋",
    "batch_no": "F21142",
    "issue_type": "做工开线等",
    "issue_desc": "测试多图片显示 - 衣服下摆处开线，约 5cm 长度。这是测试描述，用于验证问题详情页面的图片显示功能。",
    "solution_type": "退货",
    "compensation_amount": 0,
    "product_image": test_images[0] if test_images else None,
    "issue_images": test_images
}

r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=issue_data)

if r.status_code == 200:
    issue = r.json()
    issue_id = issue['id']
    issue_no = issue['issue_no']
    print(f"  [OK] 问题提交成功!")
    print(f"    ID: {issue_id}")
    print(f"    编码：{issue_no}")
    print(f"    商品图：{issue.get('product_image')}")
    print(f"    问题图：{len(issue.get('issue_images', []))} 张")
else:
    print(f"  [ERR] 提交失败：{r.text}")
    exit(1)

# 验证问题详情
print("\n[4/4] 验证问题详情（使用问题编码）...")

r = requests.get(f"{API_BASE}/api/issues-by-no/{issue_no}", headers=headers)

if r.status_code == 200:
    detail = r.json()
    print(f"  [OK] 获取详情成功!")
    print(f"\n图片验证:")
    print(f"  商品图：{detail.get('product_image')}")
    print(f"  问题图：{len(detail.get('issue_images', []))} 张")
    
    for i, img in enumerate(detail.get('issue_images', []), 1):
        print(f"    [{i}] {img}")
    
    # 测试图片访问
    print(f"\n图片访问测试:")
    all_ok = True
    
    # 测试商品图
    if detail.get('product_image'):
        img_url = f"{API_BASE}{detail['product_image']}"
        r = requests.get(img_url, timeout=5)
        status = "[OK]" if r.status_code == 200 else "[ERR]"
        print(f"  {status} 商品图：{r.status_code} ({len(r.content)} bytes)")
        if r.status_code != 200:
            all_ok = False
    
    # 测试问题图
    for i, img in enumerate(detail.get('issue_images', []), 1):
        img_url = f"{API_BASE}{img}"
        r = requests.get(img_url, timeout=5)
        status = "[OK]" if r.status_code == 200 else "[ERR]"
        print(f"  {status} 问题图 {i}: {r.status_code} ({len(r.content)} bytes)")
        if r.status_code != 200:
            all_ok = False
    
    print("\n" + "="*70)
    if all_ok:
        print("[OK] 所有图片都能正常显示!")
    else:
        print("[WARN] 部分图片无法访问")
    print("="*70)
    
    # 生成访问 URL
    print(f"\n访问链接:")
    print(f"  问题详情：http://localhost/qc-mobile/issue-detail.html?no={issue_no}")
    
else:
    print(f"  [ERR] 获取详情失败：{r.text}")
