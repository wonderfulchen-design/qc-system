#!/usr/bin/env python3
"""
测试问题列表排序 - 创建新数据验证最新问题在首位
"""
import requests
import time

API_BASE = "http://localhost:8000"

# 登录
token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*70)
print("问题列表排序测试 - 验证最新问题在首位")
print("="*70)

# 1. 创建测试问题
print("\n[1/3] 创建测试问题...")

issue_data = {
    "goods_no": "25675168959",
    "factory_name": "春秋",
    "batch_no": "F21142",
    "issue_type": "做工开线等",
    "issue_desc": f"排序测试问题 - {time.time()}",
    "solution_type": "退货",
    "compensation_amount": 0,
    "product_image": None,
    "issue_images": []
}

r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=issue_data)
if r.status_code == 200:
    new_issue = r.json()
    print(f"  [OK] 创建成功")
    print(f"  编号：{new_issue['issue_no']}")
    print(f"  时间：{new_issue.get('created_at')}")
    new_issue_no = new_issue['issue_no']
else:
    print(f"  [ERR] 创建失败：{r.text}")
    exit(1)

# 等待 1 秒确保时间戳不同
time.sleep(1)

# 2. 获取问题列表
print("\n[2/3] 获取问题列表...")

r = requests.get(f"{API_BASE}/api/issues?page=1&page_size=5", headers=headers)
data = r.json()
issues = data['data']

print(f"  [OK] 获取到 {len(issues)} 条问题")
print(f"\n  前 5 条问题:")
for i, issue in enumerate(issues, 1):
    print(f"  {i}. {issue['issue_no']} - {issue['created_at']}")

# 3. 验证排序
print("\n[3/3] 验证排序...")

# 检查最新问题是否在首位
first_issue = issues[0]
print(f"\n  第 1 条问题：{first_issue['issue_no']}")
print(f"  创建时间：{first_issue['created_at']}")

# 检查是否是我们刚创建的问题
if first_issue['issue_no'] == new_issue_no:
    print("\n  [OK] ✅ 最新问题正确显示在首位!")
else:
    print(f"\n  [WARN] ⚠️ 最新问题不在首位")
    print(f"  期望：{new_issue_no}")
    print(f"  实际：{first_issue['issue_no']}")

# 检查时间降序
print(f"\n  时间顺序验证:")
all_desc = True
for i in range(len(issues) - 1):
    curr_time = issues[i].get('created_at')
    next_time = issues[i+1].get('created_at')
    
    if curr_time and next_time:
        if curr_time < next_time:
            print(f"  [WARN] 第{i+1}条和第{i+2}条时间顺序错误")
            all_desc = False

if all_desc:
    print(f"  [OK] ✅ 所有问题按时间降序排列")
else:
    print(f"  [WARN] ⚠️ 部分问题时间顺序不正确")

print("\n" + "="*70)
print("测试完成")
print("="*70)
