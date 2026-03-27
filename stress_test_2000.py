#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2000 条数据压力测试 + 数据库完整性检查
"""

import requests
import time
import random
from datetime import datetime

# 配置
API_BASE = "http://localhost:8000"
TEST_COUNT = 2000

# 测试数据
BATCH_NUMBERS = ['F21139', 'F21140', 'F21141', 'F21142', 'F21143', 'F21144', 'F21145', 'F21146', 'F21147', 'F21148']
FACTORIES = ['元合', '三米', '乙超', '浩迅', '丰庆', '春秋', '易茂', '爱探索', '东遇']
ISSUE_TYPES = ['污渍', '扣子', '拉链', '掉色', '做工开线等', '破洞', '起球勾线掉毛', '色差', '其他']
SOLUTIONS = ['退货', '换货', '补偿', '现金补偿', '返工']

def run_test():
    print("="*70)
    print("QC SYSTEM - 2000 SUBMISSIONS STRESS TEST")
    print("="*70)
    
    # 1. Login
    print("\n[1/4] Login...")
    r = requests.post(f"{API_BASE}/token", data={'username': 'admin', 'password': 'admin123'})
    if r.status_code != 200:
        print(f"    FAILED: {r.text}")
        return
    token = r.json()['access_token']
    user_id = r.json()['user_id']
    username = r.json()['username']
    print(f"    SUCCESS: {username} (ID: {user_id})")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 2. Submit 2000 issues
    print(f"\n[2/4] Submitting {TEST_COUNT} issues...")
    start_time = time.time()
    success_count = 0
    fail_count = 0
    
    for i in range(TEST_COUNT):
        issue_data = {
            'goods_no': str(random.randint(23000000000, 25999999999)),
            'factory_name': random.choice(FACTORIES),
            'batch_no': random.choice(BATCH_NUMBERS),
            'issue_type': random.choice(ISSUE_TYPES),
            'issue_desc': f'压力测试 #{i+1} - 自动提交',
            'solution_type': random.choice(SOLUTIONS),
            'compensation_amount': random.choice([0, 0, 0, 5, 10, 20]),
            'qc_user_id': user_id,
            'qc_username': username
        }
        
        r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=issue_data, timeout=30)
        if r.status_code == 200:
            success_count += 1
        else:
            fail_count += 1
        
        # Progress
        if (i + 1) % 500 == 0:
            elapsed = time.time() - start_time
            qps = (i + 1) / elapsed
            print(f"    Progress: {i+1}/{TEST_COUNT} (Success: {success_count}, Fail: {fail_count}, QPS: {qps:.1f})")
    
    elapsed = time.time() - start_time
    qps = TEST_COUNT / elapsed
    
    print(f"\n    Completed: {TEST_COUNT} submissions")
    print(f"    Time: {elapsed:.2f} seconds")
    print(f"    Speed: {qps:.1f} requests/second")
    print(f"    Success: {success_count} ({success_count/TEST_COUNT*100:.1f}%)")
    print(f"    Failed: {fail_count} ({fail_count/TEST_COUNT*100:.1f}%)")
    
    # 3. Database integrity check
    print(f"\n[3/4] Database integrity check...")
    import pymysql
    conn = pymysql.connect(host='qc-mysql', user='qc_user', password='QcUser2025', database='qc_system', charset='utf8mb4')
    cursor = conn.cursor()
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM quality_issues")
    total = cursor.fetchone()[0]
    print(f"    Total issues in DB: {total}")
    
    # QC info check
    cursor.execute("SELECT COUNT(*) FROM quality_issues WHERE qc_user_id IS NOT NULL")
    with_qc = cursor.fetchone()[0]
    print(f"    Issues with QC info: {with_qc} ({with_qc/total*100:.1f}%)")
    
    # Factory distribution
    cursor.execute("SELECT factory_name, COUNT(*) as cnt FROM quality_issues WHERE qc_user_id IS NOT NULL GROUP BY factory_name ORDER BY cnt DESC LIMIT 5")
    print(f"    Top 5 factories:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]} issues")
    
    # Issue type distribution
    cursor.execute("SELECT issue_type, COUNT(*) as cnt FROM quality_issues WHERE qc_user_id IS NOT NULL GROUP BY issue_type ORDER BY cnt DESC LIMIT 5")
    print(f"    Top 5 issue types:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]} issues")
    
    # Time range
    cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM quality_issues WHERE qc_user_id IS NOT NULL")
    time_range = cursor.fetchone()
    print(f"    Time range: {time_range[0]} to {time_range[1]}")
    
    conn.close()
    
    # 4. Generate report
    print(f"\n[4/4] Generating test report...")
    report = f"""
================================================================================
QC SYSTEM STRESS TEST REPORT
================================================================================

Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test Count: {TEST_COUNT} submissions

RESULTS:
--------
Total Time: {elapsed:.2f} seconds
Throughput: {qps:.1f} requests/second
Success Rate: {success_count/TEST_COUNT*100:.1f}% ({success_count}/{TEST_COUNT})
Failed: {fail_count} ({fail_count/TEST_COUNT*100:.1f}%)

DATABASE INTEGRITY:
-------------------
Total Issues: {total}
Issues with QC Info: {with_qc} ({with_qc/total*100:.1f}%)
QC Info Coverage: {'PASS' if with_qc/total > 0.99 else 'FAIL'}

PERFORMANCE RATING:
-------------------
"""
    if qps >= 50:
        report += "Rating: EXCELLENT (>= 50 QPS)\n"
    elif qps >= 20:
        report += "Rating: GOOD (>= 20 QPS)\n"
    elif qps >= 10:
        report += "Rating: NORMAL (>= 10 QPS)\n"
    else:
        report += "Rating: NEED OPTIMIZE (< 10 QPS)\n"
    
    report += f"""
CONCLUSION:
-----------
System Status: {'READY FOR PRODUCTION' if success_count/TEST_COUNT > 0.99 and with_qc/total > 0.99 else 'NEEDS ATTENTION'}

================================================================================
"""
    
    # Save report
    report_file = f"stress_test_report_{int(time.time())}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"    Report saved to: {report_file}")
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)
    
    print(report)

if __name__ == "__main__":
    run_test()
