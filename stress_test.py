#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力测试脚本 - 提交 1000 次问题数据
"""

import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
API_BASE = "http://localhost:8000"
TEST_COUNT = 1000
CONCURRENT_WORKERS = 10

# 测试数据
BATCH_NUMBERS = ['F21139', 'F21140', 'F21141', 'F21142', 'F21143', 'F21144', 'F21145']
FACTORIES = ['元合', '三米', '乙超', '浩迅', '丰庆', '春秋', '易茂', '爱探索', '东遇']
ISSUE_TYPES = ['污渍', '扣子', '拉链', '掉色', '做工开线等', '破洞', '起球勾线掉毛', '色差', '其他']
SOLUTIONS = ['退货', '换货', '补偿', '现金补偿', '返工']

def login():
    """登录获取 token"""
    r = requests.post(f"{API_BASE}/token", data={'username': 'admin', 'password': 'admin123'})
    if r.status_code == 200:
        return r.json()['access_token']
    else:
        raise Exception(f"登录失败：{r.text}")

def submit_issue(token, index):
    """提交单个问题"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 随机生成数据
    batch_no = random.choice(BATCH_NUMBERS)
    factory = random.choice(FACTORIES)
    goods_no = str(random.randint(23000000000, 25999999999))
    issue_type = random.choice(ISSUE_TYPES)
    solution = random.choice(SOLUTIONS)
    compensation = random.choice([0, 0, 0, 5, 10, 20, 50])
    
    issue_data = {
        'goods_no': goods_no,
        'factory_name': factory,
        'batch_no': batch_no,
        'issue_type': issue_type,
        'issue_desc': f'压力测试数据 #{index} - 自动生成的测试问题',
        'solution_type': solution,
        'compensation_amount': compensation,
        'product_image': None,
        'issue_images': []
    }
    
    start_time = time.time()
    r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=issue_data, timeout=30)
    elapsed = time.time() - start_time
    
    return {
        'index': index,
        'status': r.status_code,
        'elapsed': elapsed,
        'success': r.status_code == 200
    }

def run_test():
    """运行压力测试"""
    print(f"[START] 压力测试")
    print(f"   提交次数：{TEST_COUNT}")
    print(f"   并发数：{CONCURRENT_WORKERS}")
    print(f"   API 地址：{API_BASE}")
    print()
    
    # 登录
    print("[LOGIN] 登录中...")
    try:
        token = login()
        print(f"[OK] 登录成功")
    except Exception as e:
        print(f"[ERROR] 登录失败：{e}")
        return
    
    # 并发提交
    print(f"\n[SUBMIT] 开始提交 {TEST_COUNT} 条数据...")
    start_time = time.time()
    
    results = []
    success_count = 0
    fail_count = 0
    total_elapsed = 0
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = [executor.submit(submit_issue, token, i) for i in range(TEST_COUNT)]
        
        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                results.append(result)
                
                if result['success']:
                    success_count += 1
                    total_elapsed += result['elapsed']
                else:
                    fail_count += 1
                
                # 进度显示
                if (i + 1) % 100 == 0:
                    print(f"   Progress: {i+1}/{TEST_COUNT} (Success: {success_count}, Fail: {fail_count})")
                    
            except Exception as e:
                fail_count += 1
                print(f"   ❌ 错误：{e}")
    
    total_time = time.time() - start_time
    
    # 统计结果
    print("\n" + "="*60)
    print("STRESS TEST RESULT")
    print("="*60)
    print(f"Total: {TEST_COUNT}")
    print(f"Success: {success_count} ({success_count/TEST_COUNT*100:.1f}%)")
    print(f"Failed: {fail_count} ({fail_count/TEST_COUNT*100:.1f}%)")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Speed: {TEST_COUNT/total_time:.2f} req/s")
    if success_count > 0:
        print(f"Avg Response: {total_elapsed/success_count*1000:.2f} ms")
    print(f"Concurrency: {CONCURRENT_WORKERS}")
    print("="*60)
    
    # 性能评级
    qps = TEST_COUNT / total_time
    if qps >= 50:
        rating = "EXCELLENT"
    elif qps >= 20:
        rating = "GOOD"
    elif qps >= 10:
        rating = "NORMAL"
    else:
        rating = "NEED OPTIMIZE"
    
    print(f"\nPerformance Rating: {rating} ({qps:.1f} QPS)")
    
    # 保存结果
    result_file = f"stress_test_result_{int(time.time())}.txt"
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"Stress Test Result\n")
        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {TEST_COUNT}\n")
        f.write(f"Success: {success_count}\n")
        f.write(f"Failed: {fail_count}\n")
        f.write(f"Total Time: {total_time:.2f} seconds\n")
        f.write(f"Speed: {qps:.2f} req/s\n")
        f.write(f"Avg Response: {total_elapsed/success_count*1000:.2f} ms\n")
        f.write(f"Rating: {rating}\n")
    
    print(f"\nResult saved to: {result_file}")

if __name__ == "__main__":
    run_test()
