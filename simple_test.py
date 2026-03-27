#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单测试 API"""

import requests
import json

BASE_URL = "http://localhost:8000"

# 1. 登录
print("1. 登录...")
login_response = requests.post(f"{BASE_URL}/token", data={
    "username": "admin",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"登录失败：{login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"登录成功！Token: {token[:50]}...")
headers = {"Authorization": f"Bearer {token}"}

# 2. 测试创建
print("\n2. 创建波次关系...")
create_response = requests.post(f"{BASE_URL}/api/batches", json={
    "batch_no": "TEST20260327001",
    "factory_name": "广州制衣厂",
    "goods_no": "SKU123456"
}, headers=headers)

print(f"状态码：{create_response.status_code}")
print(f"响应：{json.dumps(create_response.json(), ensure_ascii=False, indent=2)}")

if create_response.status_code == 200:
    print("创建成功！")
else:
    print(f"创建失败：{create_response.text}")

# 3. 测试查询列表
print("\n3. 查询列表...")
list_response = requests.get(f"{BASE_URL}/api/batches/list", params={
    "page": 1,
    "page_size": 10
}, headers=headers)

print(f"状态码：{list_response.status_code}")
if list_response.status_code == 200:
    data = list_response.json()
    print(f"总数：{data.get('total', 0)}")
    print(f"数据：{json.dumps(data.get('data', []), ensure_ascii=False, indent=2)}")
else:
    print(f"查询失败：{list_response.text}")

# 4. 测试更新
print("\n4. 更新波次关系...")
update_response = requests.put(f"{BASE_URL}/api/batches/TEST20260327001", json={
    "factory_name": "深圳制衣厂"
}, headers=headers)

print(f"状态码：{update_response.status_code}")
if update_response.status_code == 200:
    print(f"响应：{json.dumps(update_response.json(), ensure_ascii=False, indent=2)}")
    print("更新成功！")
else:
    print(f"更新失败：{update_response.text}")

# 5. 测试删除
print("\n5. 删除波次关系...")
delete_response = requests.delete(f"{BASE_URL}/api/batches/TEST20260327001", headers=headers)

print(f"状态码：{delete_response.status_code}")
if delete_response.status_code == 200:
    print(f"响应：{json.dumps(delete_response.json(), ensure_ascii=False, indent=2)}")
    print("删除成功！")
else:
    print(f"删除失败：{delete_response.text}")

print("\n测试完成！")
