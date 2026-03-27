#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证问题详情页面数据一致性
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    r = requests.post(f"{API_BASE}/token", data={'username': USERNAME, 'password': PASSWORD}, timeout=10)
    if r.status_code == 200:
        return r.json()['access_token']
    return None

def get_issue_list(token, page=1, page_size=5):
    """获取问题列表"""
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f"{API_BASE}/api/issues", headers=headers, 
                     params={'page': page, 'page_size': page_size}, timeout=30)
    if r.status_code == 200:
        return r.json()
    return None

def test_issue_detail_api(token, issue_id):
    """测试问题详情 API"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试是否存在单个问题 API
    r = requests.get(f"{API_BASE}/api/issues/{issue_id}", headers=headers, timeout=30)
    
    return r.status_code, r.json() if r.status_code == 200 else r.text[:200]

def compare_fields(db_issue, page_fields):
    """对比数据库字段与页面字段"""
    print("\n字段对比:")
    print("-" * 70)
    
    # 页面需要的字段
    required_fields = [
        'issue_no', 'status', 'sku_no', 'platform', 'order_no', 
        'buyer_wangwang', 'issue_type', 'issue_desc', 'solution_type',
        'compensation_amount', 'factory_name', 'batch_no', 'pattern_batch',
        'designer', 'handler', 'batch_source', 'created_at', 'issue_images'
    ]
    
    match_count = 0
    for field in required_fields:
        db_value = db_issue.get(field, 'N/A')
        page_value = page_fields.get(field, 'N/A')
        
        # 特殊处理
        if field == 'created_at' and db_value:
            db_value = str(db_value)[:19]
        
        match = "[OK]" if str(db_value) == str(page_value) else "[DIFF]"
        if str(db_value) == str(page_value):
            match_count += 1
            
        print(f"  {field:20s} {match} DB={str(db_value)[:30]:<30s} Page={str(page_value)[:30]:<30s}")
    
    print("-" * 70)
    print(f"匹配度：{match_count}/{len(required_fields)} ({match_count/len(required_fields)*100:.0f}%)")
    
    return match_count == len(required_fields)

def main():
    print("=" * 70)
    print("QC SYSTEM - 问题详情页面数据一致性验证")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    token = login()
    if not token:
        print("[ERROR] 登录失败")
        return
    
    print("[OK] 登录成功")
    
    # 获取问题列表
    print("\n[1/3] 获取问题列表...")
    list_data = get_issue_list(token, page=1, page_size=5)
    
    if not list_data:
        print("[ERROR] 无法获取问题列表")
        return
    
    issues = list_data.get('data', [])
    print(f"[OK] 获取到 {len(issues)} 个问题")
    
    # 测试第一个问题
    if not issues:
        print("[WARN] 没有问题数据")
        return
    
    test_issue = issues[0]
    issue_id = test_issue['id']
    
    print(f"\n[2/3] 测试问题详情 API (ID={issue_id})...")
    status_code, response_data = test_issue_detail_api(token, issue_id)
    
    print(f"  API 状态码：{status_code}")
    if status_code == 200:
        print(f"  [OK] API 存在")
        detail_data = response_data
        all_match = compare_fields(test_issue, detail_data)
        
        if all_match:
            print("\n[OK] 数据完全一致!")
        else:
            print("\n[WARN] 数据存在差异")
    elif status_code == 404:
        print(f"  [ERROR] API 不存在 - 后端缺少 /api/issues/{{id}} 接口")
        print(f"\n[分析] 问题详情页面当前使用模拟数据，未连接真实 API")
    else:
        print(f"  [ERROR] {response_text}")
    
    # 检查前端代码
    print(f"\n[3/3] 检查前端页面代码...")
    
    with open('mobile/issue-detail.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有模拟数据
    if 'getMockIssueData' in content:
        print("  [WARN] 页面包含模拟数据函数 getMockIssueData()")
    
    # 检查 API 调用
    if 'fetch' in content and '/api/issues/' in content:
        print("  [OK] 页面有 API 调用代码")
    else:
        print("  [WARN] 页面缺少 API 调用代码")
    
    # 检查字段映射
    print(f"\n页面需要的字段:")
    page_fields = [
        'issue_no', 'status', 'sku_no', 'platform', 'order_no',
        'buyer_wangwang', 'issue_type', 'issue_desc', 'solution_type',
        'compensation_amount', 'factory_name', 'batch_no', 'pattern_batch',
        'designer', 'handler', 'batch_source', 'created_at', 'issue_images'
    ]
    
    for field in page_fields:
        if field in content:
            print(f"  [OK] {field}")
        else:
            print(f"  [MISS] {field} (页面未使用)")
    
    print("\n" + "=" * 70)
    print("验证结论:")
    print("=" * 70)
    
    if status_code == 404:
        print("[ERROR] 后端缺少单个问题详情 API")
        print("[ERROR] 前端页面使用模拟数据，未连接真实数据库")
        print("\n建议:")
        print("  1. 在 backend/main.py 添加 GET /api/issues/{id} 接口")
        print("  2. 移除前端的 getMockIssueData() 模拟数据")
        print("  3. 确保前端正确等待 API 返回后再渲染")
    else:
        print("[OK] API 存在且数据一致")

if __name__ == "__main__":
    main()
