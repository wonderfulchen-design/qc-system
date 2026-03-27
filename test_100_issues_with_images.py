#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题录入压力测试 - 录入 100 条带图片的真实波次数据
"""
import requests
import random
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

# 测试配置
TEST_COUNT = 100
IMAGE_PLACEHOLDER = "https://picsum.photos/800/800"

# 真实波次号数据（从 product_batches 表）
REAL_BATCHES = [
    {'batch_no': 'F21139', 'factory_name': '三米', 'goods_no': '23181802105'},
    {'batch_no': 'F21140', 'factory_name': '三米', 'goods_no': '23181802104'},
    {'batch_no': 'F21141', 'factory_name': '爱探索', 'goods_no': '24181802186'},
    {'batch_no': 'F21142', 'factory_name': '爱探索', 'goods_no': '23181802121'},
    {'batch_no': 'F21143', 'factory_name': '三米', 'goods_no': '23181813008'},
    {'batch_no': 'F21144', 'factory_name': '春秋', 'goods_no': '23181813015'},
    {'batch_no': 'F21145', 'factory_name': '三米', 'goods_no': '23181813011'},
    {'batch_no': 'F21146', 'factory_name': '三米', 'goods_no': '23181813010'},
    {'batch_no': 'F21147', 'factory_name': '爱探索', 'goods_no': '23181802122'},
    {'batch_no': 'F21148', 'factory_name': '爱探索', 'goods_no': '23181802118'},
    {'batch_no': 'F21149', 'factory_name': '爱探索', 'goods_no': '23181802169'},
    {'batch_no': 'F21150', 'factory_name': '三米', 'goods_no': '23181805061'},
    {'batch_no': 'F21151', 'factory_name': '三米', 'goods_no': '23181805062'},
    {'batch_no': 'F21152', 'factory_name': '三米', 'goods_no': '23181805057'},
    {'batch_no': 'F21153', 'factory_name': '三米', 'goods_no': '23181805056'},
    {'batch_no': 'F21154', 'factory_name': '三米', 'goods_no': '23181805055'},
    {'batch_no': 'F21155', 'factory_name': '三米', 'goods_no': '23181805054'},
    {'batch_no': 'F21156', 'factory_name': '三米', 'goods_no': '23181805052'},
    {'batch_no': 'F21157', 'factory_name': '三米', 'goods_no': '23181805051'},
    {'batch_no': 'F21158', 'factory_name': '三米', 'goods_no': '23181805050'},
]

# 从数据库获取真实波次号
def get_batches(token, count=20):
    """获取真实的波次号数据"""
    # 直接使用硬编码的真实数据
    return REAL_BATCHES[:count]

def login():
    """登录获取 token"""
    print("[1/4] 登录中...")
    r = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}, timeout=10)
    if r.status_code == 200:
        token = r.json()['access_token']
        print(f"  [OK] 登录成功")
        return token
    else:
        print(f"  [ERROR] 登录失败：{r.text}")
        return None

def generate_test_data(batches, index):
    """生成测试数据"""
    batch = random.choice(batches)
    
    # 随机生成图片 URL（模拟上传）
    product_image = f"{IMAGE_PLACEHOLDER}?random={random.randint(1,10000)}&t={time.time()}"
    issue_images = [
        f"{IMAGE_PLACEHOLDER}?img{i}&random={random.randint(1,10000)}&t={time.time()}"
        for i in range(random.randint(1, 3))  # 1-3 张图片
    ]
    
    return {
        'goods_no': batch.get('goods_no', ''),
        'factory_name': batch.get('factory_name', ''),
        'batch_no': batch.get('batch_no', ''),
        'issue_type': random.choice(['污渍', '扣子', '拉链', '掉色', '做工开线等', '破洞', '起球勾线掉毛', '色差']),
        'issue_desc': f'压力测试 #{index} - 自动生成的测试问题',
        'solution_type': random.choice(['退货', '换货', '补偿', '现金补偿']),
        'compensation_amount': random.choice([0, 0, 0, 5, 10, 20, 50]),
        'product_image': product_image,
        'issue_images': issue_images
    }

def submit_issue(token, data):
    """提交单个问题"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    start_time = time.time()
    r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=data, timeout=30)
    elapsed = time.time() - start_time
    
    return {
        'status': r.status_code,
        'elapsed': elapsed,
        'success': r.status_code == 200,
        'issue_no': r.json().get('issue_no') if r.status_code == 200 else None,
        'goods_no': data.get('goods_no'),
        'factory_name': data.get('factory_name'),
        'batch_no': data.get('batch_no'),
        'image_count': len(data.get('issue_images', [])) + (1 if data.get('product_image') else 0)
    }

def verify_data(token, count):
    """验证数据库中的数据"""
    print("\n[3/4] 验证数据库数据...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 获取最新的问题列表
    r = requests.get(f"{API_BASE}/api/issues?page=1&page_size={count}", headers=headers)
    if r.status_code != 200:
        print(f"  [ERROR] 获取数据失败")
        return None
    
    issues = r.json().get('data', [])
    
    # 统计数据
    stats = {
        'total': len(issues),
        'with_goods_no': 0,
        'with_factory': 0,
        'with_batch_no': 0,
        'with_images': 0,
        'complete': 0
    }
    
    for issue in issues[:count]:  # 只检查最新的 count 条
        has_goods = bool(issue.get('goods_no'))
        has_factory = bool(issue.get('factory_name'))
        has_batch = bool(issue.get('batch_no'))
        has_images = bool(issue.get('product_image') or issue.get('issue_images'))
        
        if has_goods: stats['with_goods_no'] += 1
        if has_factory: stats['with_factory'] += 1
        if has_batch: stats['with_batch_no'] += 1
        if has_images: stats['with_images'] += 1
        if has_goods and has_factory and has_batch and has_images:
            stats['complete'] += 1
    
    return stats

def run_test():
    """运行测试"""
    print("="*70)
    print("问题录入压力测试 - 100 条带图片真实波次数据")
    print("="*70)
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 获取真实波次号
    print("\n[2/4] 获取真实波次号...")
    batches = get_batches(token, count=20)
    print(f"  [OK] 获取到 {len(batches)} 个波次号")
    if batches:
        print(f"  示例：{batches[0]}")
    
    # 3. 批量提交
    print(f"\n[3/4] 开始提交 {TEST_COUNT} 条问题...")
    print("-"*70)
    
    results = []
    success_count = 0
    fail_count = 0
    total_images = 0
    total_elapsed = 0
    
    start_time = time.time()
    
    for i in range(1, TEST_COUNT + 1):
        data = generate_test_data(batches, i)
        result = submit_issue(token, data)
        results.append(result)
        
        if result['success']:
            success_count += 1
            total_elapsed += result['elapsed']
            total_images += result['image_count']
        else:
            fail_count += 1
        
        # 进度显示
        if i % 10 == 0 or i == 1 or i == TEST_COUNT:
            print(f"   进度：{i:3d}/{TEST_COUNT} | 成功：{success_count:3d} | 失败：{fail_count:3d} | "
                  f"图片：{total_images:4d} 张 | 速度：{i/(time.time()-start_time):.1f} 条/秒")
        
        # 避免过快
        if i % 20 == 0:
            time.sleep(0.5)
    
    total_time = time.time() - start_time
    
    # 4. 验证数据
    stats = verify_data(token, TEST_COUNT)
    
    # 5. 统计结果
    print("\n" + "="*70)
    print("测试结果统计")
    print("="*70)
    
    print(f"\n基本统计:")
    print(f"  目标数量：{TEST_COUNT} 条")
    print(f"  成功数量：{success_count} 条 ({success_count/TEST_COUNT*100:.1f}%)")
    print(f"  失败数量：{fail_count} 条 ({fail_count/TEST_COUNT*100:.1f}%)")
    print(f"  总耗时：{total_time:.2f} 秒")
    print(f"  平均速度：{TEST_COUNT/total_time:.2f} 条/秒")
    
    if success_count > 0:
        print(f"\n图片统计:")
        print(f"  总图片数：{total_images} 张")
        print(f"  平均每问题：{total_images/success_count:.2f} 张")
        print(f"  平均响应时间：{total_elapsed/success_count*1000:.2f} ms")
    
    if stats:
        print(f"\n数据库完整性验证（最新 {stats['total']} 条）:")
        print(f"  有货品编码：{stats['with_goods_no']} 条 ({stats['with_goods_no']/stats['total']*100:.1f}%)")
        print(f"  有工厂：{stats['with_factory']} 条 ({stats['with_factory']/stats['total']*100:.1f}%)")
        print(f"  有波次号：{stats['with_batch_no']} 条 ({stats['with_batch_no']/stats['total']*100:.1f}%)")
        print(f"  有图片：{stats['with_images']} 条 ({stats['with_images']/stats['total']*100:.1f}%)")
        print(f"  数据完整：{stats['complete']} 条 ({stats['complete']/stats['total']*100:.1f}%)")
        
        # 性能评级
        completeness = stats['complete']/stats['total']*100
        if completeness >= 99:
            rating = "EXCELLENT ⭐⭐⭐⭐⭐"
        elif completeness >= 95:
            rating = "GOOD ⭐⭐⭐⭐"
        elif completeness >= 90:
            rating = "NORMAL ⭐⭐⭐"
        else:
            rating = "NEED IMPROVE ⭐⭐"
        
        print(f"\n  数据完整性评级：{rating}")
    
    # 6. 保存结果
    result_file = f'batch_test_100_issues_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    import json
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_count': TEST_COUNT,
        'success_count': success_count,
        'fail_count': fail_count,
        'total_time': total_time,
        'total_images': total_images,
        'stats': stats,
        'details': results[:20]  # 只保存前 20 条详情
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] 详细报告已保存：{result_file}")
    print("="*70)

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\n\n[INFO] 测试被用户中断")
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
