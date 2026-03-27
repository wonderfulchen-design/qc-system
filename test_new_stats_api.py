#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增的统计 API
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

def test_api(token, endpoint, name):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=30)
        print(f"\n{name}:")
        print(f"  状态码：{r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  返回数据：{json.dumps(data, ensure_ascii=False)[:200]}...")
            return True, data
        else:
            print(f"  错误：{r.text[:100]}")
            return False, None
    except Exception as e:
        print(f"  异常：{e}")
        return False, None

def main():
    print("=" * 70)
    print("QC SYSTEM - 新增统计 API 测试")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    token = login()
    if not token:
        print("[ERROR] 登录失败")
        return
    
    print("[OK] 登录成功")
    
    results = []
    
    # 测试各个 API
    print("\n" + "=" * 70)
    print("开始测试统计 API...")
    print("=" * 70)
    
    # 1. 摘要统计
    ok, data = test_api(token, "/api/stats/summary?days=90", "1. 统计摘要 (近 90 天)")
    results.append(('summary', ok, data))
    
    # 2. 按工厂统计
    ok, data = test_api(token, "/api/stats/by-factory?top=5", "2. 工厂统计 (TOP5)")
    results.append(('by_factory', ok, data))
    
    # 3. 按类型统计
    ok, data = test_api(token, "/api/stats/by-type", "3. 问题类型统计")
    results.append(('by_type', ok, data))
    
    # 4. 按平台统计
    ok, data = test_api(token, "/api/stats/by-platform", "4. 平台分布统计")
    results.append(('by_platform', ok, data))
    
    # 5. 月度趋势
    ok, data = test_api(token, "/api/stats/monthly-trend?months=6", "5. 月度趋势 (近 6 个月)")
    results.append(('monthly', ok, data))
    
    # 6. 按状态统计
    ok, data = test_api(token, "/api/stats/by-status", "6. 状态统计")
    results.append(('by_status', ok, data))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试结果总结")
    print("=" * 70)
    
    success_count = sum(1 for _, ok, _ in results if ok)
    total_count = len(results)
    
    print(f"成功：{success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n[OK] 所有统计 API 工作正常!")
    else:
        print("\n[WARN] 部分 API 失败，请检查后端日志")
    
    # 展示详细数据
    print("\n" + "=" * 70)
    print("详细数据展示")
    print("=" * 70)
    
    for name, ok, data in results:
        if ok and data:
            if name == 'summary':
                print(f"\n统计摘要:")
                print(f"  总问题数：{data.get('total_issues', 'N/A')}")
                print(f"  总补偿金额：RMB {data.get('total_compensation', 0):,.2f}")
                print(f"  涉及工厂数：{data.get('factory_count', 'N/A')}")
                print(f"  解决率：{data.get('solve_rate', 0):.1f}%")
            
            elif name == 'by_factory':
                print(f"\n工厂 TOP5:")
                for i, f in enumerate(data[:5], 1):
                    print(f"  {i}. {f.get('factory')}: {f.get('count')} 条")
            
            elif name == 'by_type':
                print(f"\n问题类型 TOP5:")
                for i, t in enumerate(data[:5], 1):
                    print(f"  {i}. {t.get('type')}: {t.get('count')} 条 ({t.get('percentage', 0):.1f}%)")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
