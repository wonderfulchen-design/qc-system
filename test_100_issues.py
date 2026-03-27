#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题录入压力测试 - 提交 100 条含图片问题
"""

import requests
import random
import time
from datetime import datetime

# 配置
API_BASE = "http://localhost:8000"
TEST_COUNT = 100

# 测试数据
BATCH_NUMBERS = ['F21139', 'F21140', 'F21141', 'F21142', 'F21143', 'F21144', 'F21145', 'F21146', 'F21147', 'F21148']
FACTORIES = ['元合', '三米', '乙超', '浩迅', '丰庆', '春秋', '易茂', '爱探索', '东遇']
ISSUE_TYPES = ['污渍', '扣子', '拉链', '尺码不符', '掉色', '印花问题', '做工开线等', '破洞', '起球勾线掉毛', 'AQL2.5', '洗唛和吊牌不符', '有味道', '面料硬不舒服', '色差', '松紧坏', '其他']
SOLUTIONS = ['退货', '换货', '补偿', '现金补偿', '返工']

def login():
    """登录获取 Token"""
    r = requests.post(f"{API_BASE}/token", data={'username': 'admin', 'password': 'admin123'})
    if r.status_code == 200:
        return r.json()['access_token']
    else:
        print(f"登录失败：{r.status_code}")
        return None

def generate_test_data():
    """生成测试数据"""
    return {
        'goods_no': str(random.randint(23000000000, 25999999999)),
        'factory_name': random.choice(FACTORIES),
        'batch_no': random.choice(BATCH_NUMBERS),
        'issue_type': random.choice(ISSUE_TYPES),
        'issue_desc': f'压力测试 #{random.randint(1, 1000)} - 自动生成的测试问题描述',
        'solution_type': random.choice(SOLUTIONS),
        'compensation_amount': random.choice([0, 0, 0, 5, 10, 20]),
        'product_image': f'/uploads/test_{random.randint(1, 1000)}.jpg',
        'issue_images': [
            f'/uploads/test_{random.randint(1, 1000)}_1.jpg',
            f'/uploads/test_{random.randint(1, 1000)}_2.jpg',
            f'/uploads/test_{random.randint(1, 1000)}_3.jpg'
        ]
    }

def submit_issue(token, data):
    """提交问题"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=data, timeout=30)
    return r.status_code == 200

def run_test():
    """运行测试"""
    print('='*80)
    print('问题录入压力测试 - 提交 100 条含图片问题')
    print('='*80)
    print()
    
    # 登录
    print('[1/3] 登录...')
    token = login()
    if not token:
        return False
    print('[OK] 登录成功')
    print()
    
    # 提交 100 条问题
    print('[2/3] 提交 100 条含图片问题...')
    success_count = 0
    fail_count = 0
    start_time = time.time()
    
    for i in range(TEST_COUNT):
        data = generate_test_data()
        
        if submit_issue(token, data):
            success_count += 1
        else:
            fail_count += 1
        
        # 进度显示
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            qps = (i + 1) / elapsed
            print(f'  进度：{i+1}/{TEST_COUNT} (成功：{success_count}, 失败：{fail_count}, QPS: {qps:.1f})')
    
    elapsed = time.time() - start_time
    qps = TEST_COUNT / elapsed
    
    print()
    print(f'完成：{TEST_COUNT} 条提交')
    print(f'总耗时：{elapsed:.2f} 秒')
    print(f'吞吐量：{qps:.1f} 条/秒')
    print(f'成功：{success_count} ({success_count/TEST_COUNT*100:.1f}%)')
    print(f'失败：{fail_count} ({fail_count/TEST_COUNT*100:.1f}%)')
    print()
    
    # 验证数据库
    print('[3/3] 验证数据库...')
    import pymysql
    try:
        conn = pymysql.connect(
            host='localhost',
            user='qc_user',
            password='QcUser2025',
            database='qc_system',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 统计测试数据
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                COUNT(CASE WHEN issue_desc LIKE '%压力测试%' THEN 1 END) AS test_count,
                COUNT(CASE WHEN product_image IS NOT NULL AND product_image != '' THEN 1 END) AS with_product_image,
                COUNT(CASE WHEN issue_images IS NOT NULL AND issue_images != '[]' THEN 1 END) AS with_issue_images
            FROM quality_issues
        """)
        
        result = cursor.fetchone()
        print(f'  数据库总记录：{result[0]}')
        print(f'  测试数据记录：{result[1]}')
        print(f'  含商品图记录：{result[2]}')
        print(f'  含问题图记录：{result[3]}')
        
        conn.close()
        print('[OK] 数据库验证完成')
    except Exception as e:
        print(f'⚠️ 数据库验证失败：{e}')
    
    print()
    print('='*80)
    if success_count == TEST_COUNT:
        print('[PASS] 测试通过 - 成功提交 100 条含图片问题')
    else:
        print(f'[FAIL] 测试失败 - 成功{success_count}条，失败{fail_count}条')
    print('='*80)
    
    return success_count == TEST_COUNT

if __name__ == "__main__":
    success = run_test()
    exit(0 if success else 1)
