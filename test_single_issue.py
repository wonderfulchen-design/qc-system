import requests

API_BASE = "http://localhost:8000"

# 登录
r = requests.post(f"{API_BASE}/token", data={'username': 'admin', 'password': 'admin123'})
token = r.json()['access_token']
print(f'Token: {token[:50]}...')

# 测试提交
data = {
    'goods_no': '23181802104',
    'factory_name': '易茂',
    'batch_no': 'F21140',
    'issue_type': '污渍',
    'issue_desc': '测试问题',
    'solution_type': '退货',
    'compensation_amount': 0,
    'product_image': '/uploads/test.jpg',
    'issue_images': ['/uploads/test1.jpg', '/uploads/test2.jpg']
}

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=data, timeout=30)
print(f'Status: {r.status_code}')
print(f'Response: {r.text}')
