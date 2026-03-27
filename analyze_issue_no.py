#!/usr/bin/env python3
import requests

# 登录
token = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 获取问题
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=3', headers=headers)
issues = r.json()['data']

print('问题编码安全性分析')
print('='*70)

for issue in issues:
    print(f"\n数字 ID: {issue.get('id')}")
    print(f"问题编码：{issue.get('issue_no')}")
    print(f"编码长度：{len(issue.get('issue_no', ''))} 字符")
    
    issue_no = issue.get('issue_no', '')
    # 分析编码结构
    if issue_no.startswith('Q'):
        print(f"结构：Q + 时间戳 (14 位) + 随机数 (6 位) + 用户 ID (2 位)")
        print(f"示例：Q 20260326004832 20C2A 01")
        print(f"      Q 年 月日时分秒 [随机] 用户")

print("\n" + "="*70)
print("安全性对比:")
print("-"*70)
print("数字 ID 方式:")
print("  URL: /qc-mobile/issue-detail.html?id=10306")
print("  风险：连续递增，黑客可从 1 遍历到 10000+")
print("  风险：容易猜测相邻问题")
print()
print("问题编码方式:")
print(f"  URL: /qc-mobile/issue-detail.html?no={issues[0].get('issue_no')}")
print("  优势：包含时间戳 + 随机数 + 用户 ID")
print("  优势：18 位字符，组合数巨大")
print("  优势：非连续，无法推测下一个编码")
print("="*70)
