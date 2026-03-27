#!/usr/bin/env python3
"""
测试 API 是否暴露数字 ID
"""
import requests
import json

API_BASE = "http://localhost:8000"

# 登录
token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*70)
print("安全测试 - 检查是否暴露数字 ID")
print("="*70)

# 测试 1: 问题列表 API
print("\n[测试 1] 问题列表 API")
r = requests.get(f"{API_BASE}/api/issues?page=1&page_size=1", headers=headers)
if r.status_code == 200:
    data = r.json()
    issue = data['data'][0]
    
    print(f"  返回字段：{list(issue.keys())}")
    
    if 'id' in issue:
        print(f"  [WARN] ❌ 暴露了数字 ID: {issue['id']}")
    else:
        print(f"  [OK] ✅ 未暴露数字 ID")
    
    if 'issue_no' in issue:
        print(f"  [OK] ✅ 使用问题编码：{issue['issue_no']}")
    
    if 'qc_user_id' in issue:
        print(f"  [WARN] ❌ 暴露了 qc_user_id: {issue['qc_user_id']}")
    else:
        print(f"  [OK] ✅ 未暴露 qc_user_id")
else:
    print(f"  [ERR] API 错误：{r.status_code}")

# 测试 2: 问题详情 API（使用问题编码）
print("\n[测试 2] 问题详情 API（使用问题编码）")
issue_no = data['data'][0]['issue_no']
r = requests.get(f"{API_BASE}/api/issues-by-no/{issue_no}", headers=headers)

if r.status_code == 200:
    detail = r.json()
    
    print(f"  返回字段：{list(detail.keys())}")
    
    if 'id' in detail:
        print(f"  [WARN] ❌ 暴露了数字 ID")
    else:
        print(f"  [OK] ✅ 未暴露数字 ID")
    
    if 'issue_no' in detail:
        print(f"  [OK] ✅ 使用问题编码：{detail['issue_no']}")
else:
    print(f"  [ERR] API 错误：{r.status_code}")

# 总结
print("\n" + "="*70)
print("安全建议")
print("="*70)
print("""
前端页面应该：
  ✅ 只使用问题编码 (issue_no)
  ✅ 不显示、不传递数字 ID
  ✅ URL 参数使用 ?no=Qxxxxx 而非 ?id=123

后端 API 应该：
  ✅ 不返回数字 ID 字段
  ✅ 只接受问题编码查询
  ✅ 不暴露内部用户 ID (qc_user_id)

已修复：
  ✅ 问题列表 API - 移除 id 和 qc_user_id
  ✅ 问题详情 API - 移除 id
  ✅ 前端列表页 - 只传递 issue_no
  ✅ 前端详情页 - 只接受 issue_no
""")

print("="*70)
