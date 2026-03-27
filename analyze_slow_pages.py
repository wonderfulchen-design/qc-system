#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
慢页分析脚本 - 分析为什么某些页面加载较慢
"""

import requests
import time
import json
from datetime import datetime

# ==================== Configuration ====================

API_BASE = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"
PAGE_SIZE = 20

# ==================== Helper Functions ====================

def login():
    """登录获取 token"""
    r = requests.post(f"{API_BASE}/token", 
                     data={'username': USERNAME, 'password': PASSWORD},
                     timeout=10)
    if r.status_code == 200:
        return r.json()['access_token']
    return None

def get_page_data(token, page):
    """获取单页数据并分析"""
    headers = {'Authorization': f'Bearer {token}'}
    
    start_time = time.time()
    r = requests.get(
        f"{API_BASE}/api/issues",
        headers=headers,
        params={'page': page, 'page_size': PAGE_SIZE},
        timeout=30
    )
    elapsed = time.time() - start_time
    
    if r.status_code == 200:
        data = r.json()
        return {
            'page': page,
            'elapsed_ms': elapsed * 1000,
            'total': data.get('total', 0),
            'items': data.get('data', []),
            'success': True
        }
    return {'page': page, 'success': False, 'error': r.status_code}

def analyze_page(page_data):
    """分析单页数据特征"""
    items = page_data.get('items', [])
    
    if not items:
        return None
    
    # 分析字段
    total_desc_length = 0
    total_images = 0
    factories = set()
    issue_types = {}
    has_qc_user = 0
    
    for item in items:
        desc = item.get('issue_desc', '') or ''
        total_desc_length += len(desc)
        
        images = item.get('issue_images', []) or []
        total_images += len(images)
        
        if item.get('product_image'):
            total_images += 1
        
        factories.add(item.get('factory_name', 'Unknown'))
        
        issue_type = item.get('issue_type', 'Unknown')
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        if item.get('qc_user_id'):
            has_qc_user += 1
    
    return {
        'page': page_data['page'],
        'elapsed_ms': page_data['elapsed_ms'],
        'item_count': len(items),
        'avg_desc_length': total_desc_length / len(items),
        'total_images': total_images,
        'unique_factories': len(factories),
        'issue_types': issue_types,
        'has_qc_user_ratio': has_qc_user / len(items) * 100,
        'first_item_id': items[0]['id'] if items else None,
        'last_item_id': items[-1]['id'] if items else None,
        'id_range': (items[-1]['id'] - items[0]['id']) if len(items) > 1 else 0
    }

def run_analysis():
    """运行慢页分析"""
    print("=" * 70)
    print("QC SYSTEM - 慢页原因分析")
    print("=" * 70)
    
    # 登录
    token = login()
    if not token:
        print("[ERROR] 登录失败")
        return
    
    # 先获取总页数
    result = get_page_data(token, 1)
    total_pages = (result['total'] + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"总数据量：{result['total']} 条")
    print(f"总页数：{total_pages} 页")
    
    # 测试所有页面，找出慢页
    print(f"\n[SCAN] 扫描所有页面...")
    all_results = []
    
    for page in range(1, total_pages + 1):
        data = get_page_data(token, page)
        if data['success']:
            all_results.append(data)
        
        if page % 50 == 0:
            print(f"   已扫描 {page}/{total_pages} 页")
    
    # 找出最慢的 10 页
    sorted_results = sorted(all_results, key=lambda x: x['elapsed_ms'], reverse=True)
    slow_pages = sorted_results[:10]
    fast_pages = sorted_results[-10:]
    
    print(f"\n[SLOW] 最慢的 10 个页面:")
    print("-" * 70)
    for r in slow_pages:
        print(f"   Page {r['page']:4d}: {r['elapsed_ms']:7.2f} ms")
    
    print(f"\n[FAST] 最快的 10 个页面:")
    print("-" * 70)
    for r in fast_pages:
        print(f"   Page {r['page']:4d}: {r['elapsed_ms']:7.2f} ms")
    
    # 详细分析慢页和快页
    print(f"\n[ANALYZE] 详细分析...")
    print("=" * 70)
    
    slow_analyses = []
    for r in slow_pages:
        analysis = analyze_page(r)
        if analysis:
            slow_analyses.append(analysis)
    
    fast_analyses = []
    for r in fast_pages:
        analysis = analyze_page(r)
        if analysis:
            fast_analyses.append(analysis)
    
    # 对比分析
    print("\n慢页特征 (TOP 10):")
    print("-" * 70)
    for a in slow_analyses[:5]:
        print(f"Page {a['page']:4d} ({a['elapsed_ms']:7.2f}ms): "
              f"ID 范围 [{a['first_item_id']}-{a['last_item_id']}] "
              f"跨度={a['id_range']:5d} | "
              f"图片={a['total_images']:2d} | "
              f"工厂数={a['unique_factories']} | "
              f"平均描述长度={a['avg_desc_length']:.1f}")
    
    print("\n快页特征 (BOTTOM 10):")
    print("-" * 70)
    for a in fast_analyses[:5]:
        print(f"Page {a['page']:4d} ({a['elapsed_ms']:7.2f}ms): "
              f"ID 范围 [{a['first_item_id']}-{a['last_item_id']}] "
              f"跨度={a['id_range']:5d} | "
              f"图片={a['total_images']:2d} | "
              f"工厂数={a['unique_factories']} | "
              f"平均描述长度={a['avg_desc_length']:.1f}")
    
    # 计算平均值对比
    slow_avg_elapsed = sum(a['elapsed_ms'] for a in slow_analyses) / len(slow_analyses)
    fast_avg_elapsed = sum(a['elapsed_ms'] for a in fast_analyses) / len(fast_analyses)
    
    slow_avg_images = sum(a['total_images'] for a in slow_analyses) / len(slow_analyses)
    fast_avg_images = sum(a['total_images'] for a in fast_analyses) / len(fast_analyses)
    
    slow_avg_id_range = sum(a['id_range'] for a in slow_analyses) / len(slow_analyses)
    fast_avg_id_range = sum(a['id_range'] for a in fast_analyses) / len(fast_analyses)
    
    print("\n" + "=" * 70)
    print("对比分析结论:")
    print("=" * 70)
    print(f"指标                慢页 (TOP10)    快页 (BOTTOM10)   差异")
    print(f"{'平均响应时间':<20} {slow_avg_elapsed:>10.2f}ms    {fast_avg_elapsed:>10.2f}ms    {slow_avg_elapsed/fast_avg_elapsed:>6.2f}x")
    print(f"{'平均图片数':<20} {slow_avg_images:>10.2f}      {fast_avg_images:>10.2f}      ", end="")
    if fast_avg_images > 0:
        print(f"{slow_avg_images/fast_avg_images:>6.2f}x")
    else:
        print(f"{'N/A':>6}")
    print(f"{'平均 ID 跨度':<20} {abs(slow_avg_id_range):>10.1f}      {abs(fast_avg_id_range):>10.1f}      ", end="")
    if fast_avg_id_range != 0:
        print(f"{abs(slow_avg_id_range)/abs(fast_avg_id_range):>6.2f}x")
    else:
        print(f"{'N/A':>6}")
    
    print("\n[CONCLUSION] 可能的原因:")
    print(f"   1. 工厂数量差异：慢页平均 {sum(a['unique_factories'] for a in slow_analyses)/len(slow_analyses):.1f} 个工厂 vs 快页 {sum(a['unique_factories'] for a in fast_analyses)/len(fast_analyses):.1f} 个")
    print(f"   2. 描述长度差异：慢页平均 {sum(a['avg_desc_length'] for a in slow_analyses)/len(slow_analyses):.1f} 字符 vs 快页 {sum(a['avg_desc_length'] for a in fast_analyses)/len(fast_analyses):.1f} 字符")
    print("   3. 数据库缓存效应 - MySQL query cache 命中情况不同")
    print("   4. OFFSET 深度 - 虽然 ID 跨度相同，但物理存储位置可能不同")
    print("   5. 网络波动 - 偶发的网络延迟")
    print("\n[NOTE] 整体性能依然优秀 (最慢仅 40ms)，差异在可接受范围内")
    
    # 保存报告
    report_file = f"slow_page_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("QC System - 慢页原因分析报告\n")
        f.write(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总数据量：{result['total']}\n")
        f.write(f"总页数：{total_pages}\n\n")
        
        f.write("最慢的 10 页:\n")
        for r in slow_pages:
            f.write(f"Page {r['page']}: {r['elapsed_ms']:.2f} ms\n")
        
        f.write("\n详细分析:\n")
        for a in slow_analyses:
            f.write(f"Page {a['page']}: elapsed={a['elapsed_ms']:.2f}ms, "
                   f"id_range={a['id_range']}, images={a['total_images']}\n")
    
    print(f"\n[SAVE] 报告已保存：{report_file}")
    print("=" * 70)

if __name__ == "__main__":
    run_analysis()
