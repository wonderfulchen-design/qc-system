#!/usr/bin/env python3
"""
检测问题列表排序 - 验证最新问题是否在首位
"""
import requests

API_BASE = "http://localhost:8000"

# 登录
token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*70)
print("问题列表排序检测")
print("="*70)

# 获取问题列表
r = requests.get(f"{API_BASE}/api/issues?page=1&page_size=5", headers=headers)
data = r.json()

issues = data['data']
print(f"\n当前显示前 {len(issues)} 条问题:")
print()

for i, issue in enumerate(issues, 1):
    print(f"{i}. 编号：{issue['issue_no']}")
    print(f"   类型：{issue['issue_type']}")
    print(f"   工厂：{issue['factory_name']}")
    print(f"   时间：{issue['created_at']}")
    print()

# 检查排序
if len(issues) >= 2:
    first_time = issues[0]['created_at']
    last_time = issues[-1]['created_at']
    
    print("="*70)
    print("排序验证:")
    print(f"  第 1 条时间：{first_time}")
    print(f"  第{len(issues)}条时间：{last_time}")
    print()
    
    if first_time > last_time:
        print("[OK] 最新问题显示在首位（按时间降序）")
    else:
        print("[WARN] 排序可能有问题")
