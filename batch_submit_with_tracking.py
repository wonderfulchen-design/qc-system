#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提交测试 - 带详细错误跟踪
"""
import requests
import json
import time
from datetime import datetime

# 配置
API_BASE = 'http://localhost:8000'
USERNAME = 'admin'
PASSWORD = 'admin123'

# 测试数据
BATCH_NUMBERS = ['F21139', 'F21140', 'F21141', 'F21142', 'F21143']
FACTORIES = ['三米', '春秋', '丰庆', '乙超', '元合', '爱探索', '浩迅']
GOODS_NO_LIST = [
    '23181802105', '23181802104', '24181802186', '23181802121',
    '23181813008', '23181813015', '23181813011', '23181813010',
    '23181802122', '23181802118'
]
ISSUE_TYPES = ['污渍', '扣子', '拉链', '掉色', '做工开线等', '破洞', '起球勾线掉毛', '色差']
SOLUTION_TYPES = ['返工', '拒收', '全检', '代卖', '报废']

# 错误跟踪
errors = []
success_details = []

def login():
    """登录获取 token"""
    print("="*70)
    print("正在登录...")
    print("="*70)
    
    try:
        response = requests.post(
            f'{API_BASE}/token',
            data={'username': USERNAME, 'password': PASSWORD}
        )
        
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"[OK] 登录成功！")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"❌ 登录失败：{response.status_code}")
            print(f"错误信息：{response.text}")
            errors.append({
                'step': '登录',
                'status_code': response.status_code,
                'error': response.text
            })
            return None
            
    except Exception as e:
        print(f"[ERROR] 登录错误：{e}")
        errors.append({
            'step': '登录',
            'error': str(e)
        })
        return None

def submit_issue(token, index):
    """提交单个问题"""
    import random
    
    # 生成随机数据
    batch_no = random.choice(BATCH_NUMBERS)
    factory = random.choice(FACTORIES)
    goods_no = random.choice(GOODS_NO_LIST)
    issue_type = random.choice(ISSUE_TYPES)
    solution_type = random.choice(SOLUTION_TYPES)
    issue_desc = f"自动化测试问题 #{index + 1} - 这是通过脚本自动生成的测试数据，用于验证提交功能"
    
    print(f"\n提交第 {index + 1} 条问题...")
    print(f"   波次号：{batch_no}")
    print(f"   工厂：{factory}")
    print(f"   货品编码：{goods_no}")
    print(f"   问题类型：{issue_type}")
    print(f"   解决方式：{solution_type}")
    
    start_time = time.time()
    
    try:
        formData = {
            'goods_no': goods_no,
            'factory_name': factory,
            'batch_no': batch_no,
            'issue_type': issue_type,
            'issue_desc': issue_desc,
            'solution_type': solution_type,
            'compensation_amount': 0,
            'product_image': None,
            'issue_images': []
        }
        
        response = requests.post(
            f'{API_BASE}/api/issues',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json=formData,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            issue_no = result.get('issue_no', 'Unknown')
            print(f"   [OK] 提交成功！耗时：{elapsed:.2f}s")
            print(f"   问题编号：{issue_no}")
            
            success_details.append({
                'index': index + 1,
                'batch_no': batch_no,
                'factory': factory,
                'goods_no': goods_no,
                'issue_type': issue_type,
                'issue_no': issue_no,
                'elapsed': elapsed
            })
            
            return True
        else:
            error_text = response.text
            print(f"   [FAIL] 提交失败！状态码：{response.status_code}")
            print(f"   错误信息：{error_text}")
            
            errors.append({
                'step': f'提交第{index + 1}条',
                'batch_no': batch_no,
                'factory': factory,
                'goods_no': goods_no,
                'status_code': response.status_code,
                'error': error_text,
                'elapsed': elapsed
            })
            
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   [ERROR] 提交错误：{e}")
        print(f"   耗时：{elapsed:.2f}s")
        
        errors.append({
            'step': f'提交第{index + 1}条',
            'batch_no': batch_no,
            'factory': factory,
            'goods_no': goods_no,
            'error': str(e),
            'elapsed': elapsed
        })
        
        return False

def run_test(count=10):
    """运行测试"""
    print("\n" + "="*70)
    print("批量问题录入测试")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"提交数量：{count} 条")
    print("="*70)
    
    # 登录
    token = login()
    if not token:
        print("\n[FAIL] 登录失败，测试终止")
        return
    
    # 批量提交
    print("\n" + "="*70)
    print("开始批量提交...")
    print("="*70)
    
    success_count = 0
    fail_count = 0
    
    for i in range(count):
        if submit_issue(token, i):
            success_count += 1
        else:
            fail_count += 1
        
        # 显示进度
        progress = (i + 1) / count * 100
        bar_len = int(progress/5)
        print(f"\n进度：[{'=' * bar_len}{' ' * (20 - bar_len)}] {progress:.0f}% ({i + 1}/{count})")
        
        # 等待一下
        time.sleep(0.5)
    
    # 统计结果
    print("\n" + "="*70)
    print("测试结果统计")
    print("="*70)
    print(f"提交总数：{count}")
    print(f"成功：{success_count} 条 ({success_count/count*100:.1f}%)")
    print(f"失败：{fail_count} 条 ({fail_count/count*100:.1f}%)")
    print("="*70)
    
    # 成功详情
    if success_details:
        print("\n[OK] 成功详情:")
        print("-"*70)
        for item in success_details:
            print(f"#{item['index']:2d} | {item['batch_no']} | {item['factory']:6s} | {item['goods_no']} | {item['issue_type']:8s} | {item['issue_no']} | {item['elapsed']:.2f}s")
    
    # 错误详情
    if errors:
        print("\n" + "="*70)
        print("[ERROR] 错误详情:")
        print("="*70)
        for i, error in enumerate(errors, 1):
            print(f"\n错误 #{i}:")
            for key, value in error.items():
                print(f"  {key}: {value}")
    
    # 保存报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'total': count,
        'success': success_count,
        'fail': fail_count,
        'success_rate': success_count/count*100,
        'success_details': success_details,
        'errors': errors
    }
    
    report_file = f'batch_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] 测试报告已保存：{report_file}")
    print("="*70)
    
    if success_count == count:
        print("[OK] 所有问题提交成功！")
    elif success_count > 0:
        print("[WARN] 部分问题提交成功")
    else:
        print("[FAIL] 所有问题提交失败")

if __name__ == '__main__':
    import sys
    
    count = 10
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    
    run_test(count)
