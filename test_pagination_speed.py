#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题列表翻页速度测试 - 测试所有页面的加载性能
"""

import requests
import time
import statistics
from datetime import datetime

# ==================== Configuration ====================

API_BASE = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

# 测试配置
PAGE_SIZE = 20  # 每页条数
MAX_PAGES = 100  # 最大测试页数 (设为 0 表示测试所有页)

# ==================== Helper Functions ====================

def login():
    """登录获取 token"""
    try:
        r = requests.post(f"{API_BASE}/token", 
                         data={'username': USERNAME, 'password': PASSWORD},
                         timeout=10)
        if r.status_code == 200:
            return r.json()['access_token']
        else:
            print(f"[ERROR] 登录失败：{r.status_code} - {r.text}")
            return None
    except Exception as e:
        print(f"[ERROR] 登录异常：{e}")
        return None

def test_page(token, page, page_size=PAGE_SIZE):
    """测试单页加载速度"""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    start_time = time.time()
    try:
        r = requests.get(
            f"{API_BASE}/api/issues",
            headers=headers,
            params={'page': page, 'page_size': page_size},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if r.status_code == 200:
            data = r.json()
            actual_count = len(data.get('data', []))
            return {
                'page': page,
                'status': 'success',
                'elapsed_ms': elapsed * 1000,
                'items': actual_count,
                'total': data.get('total', 0)
            }
        else:
            return {
                'page': page,
                'status': 'error',
                'elapsed_ms': elapsed * 1000,
                'error_code': r.status_code,
                'error_msg': r.text
            }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'page': page,
            'status': 'exception',
            'elapsed_ms': elapsed * 1000,
            'error': str(e)
        }

def run_pagination_test():
    """运行翻页速度测试"""
    print("=" * 70)
    print("QC SYSTEM - 问题列表翻页速度测试")
    print("=" * 70)
    print(f"API 地址：{API_BASE}")
    print(f"页面大小：{PAGE_SIZE} 条/页")
    print(f"最大测试页数：{MAX_PAGES if MAX_PAGES > 0 else '所有页'}")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 登录
    print("\n[1/3] 登录中...")
    token = login()
    if not token:
        print("[ERROR] 无法登录，请确保后端服务正在运行")
        return
    
    print(f"[OK] 登录成功")
    
    # 获取总页数
    print("\n[2/3] 获取总数据量...")
    result = test_page(token, 1)
    if result['status'] != 'success':
        print(f"[ERROR] 无法获取数据：{result}")
        return
    
    total_items = result['total']
    total_pages = (total_items + PAGE_SIZE - 1) // PAGE_SIZE
    
    print(f"[OK] 总数据量：{total_items} 条")
    print(f"[OK] 总页数：{total_pages} 页")
    
    # 确定实际测试页数
    if MAX_PAGES > 0:
        test_pages = min(MAX_PAGES, total_pages)
    else:
        test_pages = total_pages
    
    print(f"[INFO] 将测试前 {test_pages} 页")
    
    # 开始测试
    print(f"\n[3/3] 开始翻页测试...")
    print("-" * 70)
    
    results = []
    success_count = 0
    error_count = 0
    
    for page in range(1, test_pages + 1):
        result = test_page(token, page)
        results.append(result)
        
        if result['status'] == 'success':
            success_count += 1
            status_icon = "[OK]"
        else:
            error_count += 1
            status_icon = "[ERR]"
        
        # 进度显示
        if page % 10 == 0 or page == 1 or page == test_pages:
            print(f"   Page {page:4d}: {result['elapsed_ms']:7.2f} ms {status_icon}")
        elif page % 5 == 0:
            print(f"   Page {page:4d}: {result['elapsed_ms']:7.2f} ms {status_icon}")
    
    # 统计分析
    print("\n" + "=" * 70)
    print("测试结果统计")
    print("=" * 70)
    
    success_results = [r for r in results if r['status'] == 'success']
    
    if len(success_results) > 0:
        elapsed_times = [r['elapsed_ms'] for r in success_results]
        
        avg_time = statistics.mean(elapsed_times)
        median_time = statistics.median(elapsed_times)
        min_time = min(elapsed_times)
        max_time = max(elapsed_times)
        std_dev = statistics.stdev(elapsed_times) if len(elapsed_times) > 1 else 0
        
        # 计算百分位数
        sorted_times = sorted(elapsed_times)
        p90_idx = int(len(sorted_times) * 0.9)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        
        p90_time = sorted_times[p90_idx] if p90_idx < len(sorted_times) else sorted_times[-1]
        p95_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1]
        p99_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else sorted_times[-1]
        
        print(f"\n[PERF] 性能指标:")
        print(f"   成功页数：{success_count} / {test_pages} ({success_count/test_pages*100:.1f}%)")
        print(f"   失败页数：{error_count}")
        print()
        print(f"   平均响应时间：{avg_time:7.2f} ms")
        print(f"   中位数时间：  {median_time:7.2f} ms")
        print(f"   最小时间：    {min_time:7.2f} ms")
        print(f"   最大时间：    {max_time:7.2f} ms")
        print(f"   标准差：      {std_dev:7.2f} ms")
        print()
        print(f"   P90 响应时间： {p90_time:7.2f} ms")
        print(f"   P95 响应时间： {p95_time:7.2f} ms")
        print(f"   P99 响应时间： {p99_time:7.2f} ms")
        
        # 性能评级
        print(f"\n[RATING] 性能评级:")
        if avg_time < 100:
            rating = "EXCELLENT [5/5]"
            comment = "非常快！用户体验极佳"
        elif avg_time < 300:
            rating = "GOOD [4/5]"
            comment = "良好，满足日常使用"
        elif avg_time < 500:
            rating = "NORMAL [3/5]"
            comment = "一般，可以考虑优化"
        elif avg_time < 1000:
            rating = "SLOW [2/5]"
            comment = "较慢，建议优化数据库查询"
        else:
            rating = "VERY SLOW [1/5]"
            comment = "需要立即优化！"
        
        print(f"   评级：{rating}")
        print(f"   评价：{comment}")
        
        # 慢查询分析
        slow_pages = [r for r in success_results if r['elapsed_ms'] > 500]
        if len(slow_pages) > 0:
            print(f"\n[WARN] 慢查询页面 (>500ms):")
            for r in sorted(slow_pages, key=lambda x: x['elapsed_ms'], reverse=True)[:10]:
                print(f"   第 {r['page']} 页：{r['elapsed_ms']:.2f} ms")
    
    # 保存结果
    result_file = f"pagination_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("QC System - 问题列表翻页速度测试报告\n")
        f.write(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"API 地址：{API_BASE}\n")
        f.write(f"页面大小：{PAGE_SIZE}\n")
        f.write(f"测试页数：{test_pages}\n")
        f.write(f"总数据量：{total_items}\n")
        f.write("\n")
        f.write("性能指标:\n")
        if len(success_results) > 0:
            f.write(f"成功率：{success_count/test_pages*100:.1f}%\n")
            f.write(f"平均响应时间：{avg_time:.2f} ms\n")
            f.write(f"中位数时间：{median_time:.2f} ms\n")
            f.write(f"P95 响应时间：{p95_time:.2f} ms\n")
            f.write(f"评级：{rating}\n")
        f.write("\n详细数据:\n")
        for r in results:
            f.write(f"Page {r['page']}: {r['elapsed_ms']:.2f} ms - {r['status']}\n")
    
    print(f"\n[SAVE] 结果已保存至：{result_file}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_pagination_test()
    except KeyboardInterrupt:
        print("\n\n[INFO] 测试被用户中断")
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
