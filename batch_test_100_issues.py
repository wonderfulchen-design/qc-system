#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测试录入 100 条问题，包含随机多张图片
"""
import requests
import random
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

# 测试数据
BATCH_NUMBERS = ['F21139', 'F21140', 'F21141', 'F21142', 'F21143', 'F21144', 'F21145', 'F21146', 'F21147', 'F21148']
FACTORIES = ['元合', '三米', '乙超', '浩迅', '丰庆', '春秋', '易茂', '爱探索', '东遇', '浩茂']
ISSUE_TYPES = ['污渍', '扣子', '拉链', '掉色', '做工开线等', '破洞', '起球勾线掉毛', '色差', '尺码不符', '其他']
SOLUTIONS = ['退货', '换货', '补偿', '现金补偿', '返工']
GOODS_NO_PREFIX = ['25', '26', '27']

# 测试图片 URL（使用占位图服务，800x800 像素）
IMAGE_PLACEHOLDER = "https://picsum.photos/800/800"

def login():
    """登录获取 token"""
    print("[1/3] 登录中...")
    r = requests.post(f"{API_BASE}/token", data={'username': 'admin', 'password': 'admin123'}, timeout=10)
    if r.status_code == 200:
        token = r.json()['access_token']
        print(f"  [OK] 登录成功")
        return token
    else:
        print(f"  [ERROR] 登录失败：{r.text}")
        return None

def generate_random_images(min_count=1, max_count=7):
    """生成随机数量的图片 URL"""
    count = random.randint(min_count, max_count)
    images = []
    for i in range(count):
        # 使用 picsum 随机图片服务，添加随机参数避免缓存
        img_url = f"{IMAGE_PLACEHOLDER}?random={random.randint(1, 10000)}&time={time.time()}"
        images.append(img_url)
    return images

def generate_issue_data(index):
    """生成单条问题数据"""
    batch_no = random.choice(BATCH_NUMBERS)
    factory = random.choice(FACTORIES)
    goods_no = random.choice(GOODS_NO_PREFIX) + str(random.randint(10000000000, 99999999999))
    issue_type = random.choice(ISSUE_TYPES)
    solution = random.choice(SOLUTIONS)
    compensation = random.choice([0, 0, 0, 5, 10, 20, 50, 100])
    
    # 随机生成 1-7 张图片（70% 概率含多图）
    if random.random() < 0.7:
        issue_images = generate_random_images(2, 7)  # 多图
    else:
        issue_images = generate_random_images(1, 1)  # 单图
    
    # 商品图
    product_image = f"{IMAGE_PLACEHOLDER}?product={random.randint(1, 10000)}"
    
    issue_data = {
        'goods_no': goods_no,
        'factory_name': factory,
        'batch_no': batch_no,
        'issue_type': issue_type,
        'issue_desc': f'批量测试 #{index} - 自动生成的测试问题。{issue_type}问题，需要检验处理。',
        'solution_type': solution,
        'compensation_amount': compensation,
        'product_image': product_image,
        'issue_images': issue_images
    }
    
    return issue_data, len(issue_images)

def submit_issue(token, index):
    """提交单个问题"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    issue_data, image_count = generate_issue_data(index)
    
    start_time = time.time()
    r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=issue_data, timeout=30)
    elapsed = time.time() - start_time
    
    return {
        'index': index,
        'status': r.status_code,
        'elapsed': elapsed,
        'success': r.status_code == 200,
        'image_count': image_count,
        'issue_no': r.json().get('issue_no') if r.status_code == 200 else None,
        'error': r.text if r.status_code != 200 else None
    }

def run_batch_test(count=100):
    """运行批量测试"""
    print("="*70)
    print("QC 系统 - 批量问题录入测试")
    print(f"目标：录入 {count} 条问题")
    print(f"图片：800x800 像素，随机 1-7 张")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 登录
    token = login()
    if not token:
        return
    
    # 批量提交
    print(f"\n[2/3] 开始批量提交...")
    print("-"*70)
    
    results = []
    success_count = 0
    fail_count = 0
    total_images = 0
    total_elapsed = 0
    
    start_time = time.time()
    
    for i in range(1, count + 1):
        result = submit_issue(token, i)
        results.append(result)
        
        if result['success']:
            success_count += 1
            total_elapsed += result['elapsed']
            total_images += result['image_count']
            
            # 进度显示
            if i % 10 == 0 or i == 1 or i == count:
                print(f"   进度：{i:3d}/{count} | 成功：{success_count:3d} | 失败：{fail_count:3d} | "
                      f"图片：{total_images:4d} 张 | 速度：{i/(time.time()-start_time):.1f} 条/秒")
        else:
            fail_count += 1
            print(f"   [ERROR] 第{i}条失败：{result['error'][:50]}")
        
        # 避免过快请求
        if i % 20 == 0:
            time.sleep(0.5)
    
    total_time = time.time() - start_time
    
    # 统计结果
    print("\n" + "="*70)
    print("测试结果统计")
    print("="*70)
    
    print(f"\n基本统计:")
    print(f"  目标数量：{count} 条")
    print(f"  成功数量：{success_count} 条 ({success_count/count*100:.1f}%)")
    print(f"  失败数量：{fail_count} 条 ({fail_count/count*100:.1f}%)")
    print(f"  总耗时：{total_time:.2f} 秒")
    print(f"  平均速度：{count/total_time:.2f} 条/秒")
    
    if success_count > 0:
        print(f"\n图片统计:")
        print(f"  总图片数：{total_images} 张")
        print(f"  平均每问题：{total_images/success_count:.2f} 张")
        print(f"  图片总数：{total_images} 张 (800x800 像素)")
        
        print(f"\n性能统计:")
        avg_time = total_elapsed / success_count * 1000
        print(f"  平均响应时间：{avg_time:.2f} ms")
        
        # 性能评级
        qps = count / total_time
        if qps >= 10:
            rating = "EXCELLENT"
        elif qps >= 5:
            rating = "GOOD"
        elif qps >= 2:
            rating = "NORMAL"
        else:
            rating = "NEED OPTIMIZE"
        
        print(f"  吞吐量：{qps:.2f} 条/秒")
        print(f"  性能评级：{rating}")
    
    # 保存结果
    result_file = f'batch_test_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    import json
    report = {
        'timestamp': datetime.now().isoformat(),
        'target_count': count,
        'success_count': success_count,
        'fail_count': fail_count,
        'total_time': total_time,
        'total_images': total_images,
        'avg_images_per_issue': total_images/success_count if success_count > 0 else 0,
        'avg_response_ms': (total_elapsed / success_count * 1000) if success_count > 0 else 0,
        'qps': count / total_time,
        'details': results[:20]  # 只保存前 20 条详情
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] 详细报告已保存：{result_file}")
    print("="*70)
    
    # 验证最后一条数据
    if success_count > 0:
        print(f"\n[3/3] 验证最新数据...")
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.get(f"{API_BASE}/api/issues?page=1&page_size=1", headers=headers)
        if r.status_code == 200:
            latest = r.json()['data'][0]
            print(f"  最新问题：{latest.get('issue_no')}")
            print(f"  工厂：{latest.get('factory_name')}")
            print(f"  图片数：{len(latest.get('issue_images', []))} 张")
            print(f"  QC 用户：{latest.get('qc_username')}")
            print(f"  [OK] 数据验证成功")

if __name__ == "__main__":
    try:
        run_batch_test(100)
    except KeyboardInterrupt:
        print("\n\n[INFO] 测试被用户中断")
    except Exception as e:
        print(f"\n[ERROR] 测试异常：{e}")
        import traceback
        traceback.print_exc()
