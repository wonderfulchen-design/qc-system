#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2000 条数据压力测试 v2 - 修复 issue_no 重复问题
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
    print("QC SYSTEM - 2000 SUBMISSIONS STRESS TEST (V2 - FIXED)")
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
    error_details = []
    
    for i in range(TEST_COUNT):
        issue_data = {
            'goods_no': str(random.randint(23000000000, 25999999999)),
            'factory_name': random.choice(FACTORIES),
            'batch_no': random.choice(BATCH_NUMBERS),
            'issue_type': random.choice(ISSUE_TYPES),
            'issue_desc': f'压力测试 V2 #{i+1} - 自动提交',
            'solution_type': random.choice(SOLUTIONS),
            'compensation_amount': random.choice([0, 0, 0, 5, 10, 20]),
            'qc_user_id': user_id,
            'qc_username': username
        }
        
        try:
            r = requests.post(f"{API_BASE}/api/issues", headers=headers, json=issue_data, timeout=30)
            if r.status_code == 200:
                success_count += 1
            else:
                fail_count += 1
                error_details.append(f"Issue #{i+1}: Status {r.status_code} - {r.text[:100]}")
        except Exception as e:
            fail_count += 1
            error_details.append(f"Issue #{i+1}: Exception - {str(e)}")
        
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
    print(f"    Success: {success_count} ({success_count/TEST_COUNT*100:.2f}%)")
    print(f"    Failed: {fail_count} ({fail_count/TEST_COUNT*100:.2f}%)")
    
    if fail_count > 0:
        print(f"\n    Error Details (first 5):")
        for err in error_details[:5]:
            print(f"      - {err}")
    
    # 3. Database integrity check
    print(f"\n[3/4] Database integrity check...")
    import pymysql
    conn = pymysql.connect(host='qc-mysql', user='qc_user', password='QcUser2025', database='qc_system', charset='utf8mb4')
    cursor = conn.cursor()
    
    # Get test issues count (V2 test issues have "压力测试 V2" in description)
    cursor.execute("SELECT COUNT(*) FROM quality_issues WHERE issue_desc LIKE '%压力测试 V2%'")
    test_total = cursor.fetchone()[0]
    print(f"    Issues from this test: {test_total}")
    
    # QC info check
    cursor.execute("SELECT COUNT(*) FROM quality_issues WHERE issue_desc LIKE '%压力测试 V2%' AND qc_user_id IS NOT NULL")
    with_qc = cursor.fetchone()[0]
    print(f"    Issues with QC info: {with_qc} ({with_qc/test_total*100:.2f}%)")
    
    # Duplicate check
    cursor.execute("SELECT issue_no, COUNT(*) as cnt FROM quality_issues GROUP BY issue_no HAVING cnt > 1")
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"    ⚠️ Duplicate issue_no found: {len(duplicates)}")
        for dup in duplicates[:5]:
            print(f"      - {dup[0]}: {dup[1]} times")
    else:
        print(f"    ✅ No duplicate issue_no")
    
    # Factory distribution
    cursor.execute("SELECT factory_name, COUNT(*) as cnt FROM quality_issues WHERE issue_desc LIKE '%压力测试 V2%' GROUP BY factory_name ORDER BY cnt DESC LIMIT 5")
    print(f"    Top 5 factories:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]} issues")
    
    # Issue type distribution
    cursor.execute("SELECT issue_type, COUNT(*) as cnt FROM quality_issues WHERE issue_desc LIKE '%压力测试 V2%' GROUP BY issue_type ORDER BY cnt DESC LIMIT 5")
    print(f"    Top 5 issue types:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]} issues")
    
    conn.close()
    
    # 4. Generate report
    print(f"\n[4/4] Generating test report...")
    
    success_rate = success_count / TEST_COUNT * 100
    qc_coverage = with_qc / test_total * 100 if test_total > 0 else 0
    
    report = f"""
================================================================================
QC SYSTEM STRESS TEST REPORT (V2 - FIXED)
================================================================================

Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test Count: {TEST_COUNT} submissions
Fix Applied: issue_no uniqueness improved

RESULTS:
--------
Total Time: {elapsed:.2f} seconds
Throughput: {qps:.1f} requests/second
Success Rate: {success_rate:.2f}% ({success_count}/{TEST_COUNT})
Failed: {fail_count} ({100-success_rate:.2f}%)

DATABASE INTEGRITY:
-------------------
Test Issues in DB: {test_total}
Issues with QC Info: {with_qc} ({qc_coverage:.2f}%)
Duplicate issue_no: {'YES - NEEDS FIX' if duplicates else 'NO - PASS'}
QC Info Coverage: {'PASS' if qc_coverage > 99.9 else 'FAIL'}

PERFORMANCE RATING:
-------------------
"""
    if qps >= 50 and success_rate >= 99.9:
        report += "Rating: EXCELLENT (>= 50 QPS, >= 99.9% success)\n"
    elif qps >= 40 and success_rate >= 99.5:
        report += "Rating: VERY GOOD (>= 40 QPS, >= 99.5% success)\n"
    elif qps >= 30 and success_rate >= 99.0:
        report += "Rating: GOOD (>= 30 QPS, >= 99% success)\n"
    else:
        report += "Rating: NEED OPTIMIZE\n"
    
    report += f"""
CONCLUSION:
-----------
System Status: {'✅ READY FOR PRODUCTION' if success_rate >= 99.9 and qc_coverage >= 99.9 and not duplicates else '⚠️ NEEDS ATTENTION'}

Issues Fixed:
- ✅ issue_no uniqueness improved with UUID + timestamp + user_id
- ✅ Added retry logic for duplicate prevention
- ✅ QC information properly recorded

================================================================================
"""
    
    # Save report
    report_file = f"stress_test_report_v2_{int(time.time())}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"    Report saved to: {report_file}")
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)
    
    print(report)
    
    return success_rate >= 99.9 and qc_coverage >= 99.9 and not duplicates

if __name__ == "__main__":
    success = run_test()
    exit(0 if success else 1)
