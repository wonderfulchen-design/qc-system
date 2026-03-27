#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复工厂名称 - 使用简称
"""

import pymysql

# 数据库配置
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='QcSystem2025!@#',
    database='qc_system',
    charset='utf8mb4'
)

cursor = conn.cursor()

# 工厂名称映射（全称 -> 简称）
factory_mapping = {
    '元合服装厂': '元合',
    '三米制衣': '三米',
    '乙超服饰': '乙超',
    '浩迅服装': '浩迅',
    '丰庆制衣': '丰庆',
    '春秋服饰': '春秋',
    '易茂服装': '易茂',
    '爱探索': '爱探索',
}

# 更新数据库
print("更新工厂名称...")
for full_name, short_name in factory_mapping.items():
    sql = "UPDATE product_batches SET factory_name = %s WHERE factory_name = %s"
    cursor.execute(sql, (short_name, full_name))
    updated = cursor.rowcount
    if updated > 0:
        print(f"[OK] {full_name} -> {short_name} ({updated} 条)")

conn.commit()

# 验证
print("\n验证结果:")
cursor.execute("SELECT DISTINCT factory_name FROM product_batches LIMIT 20")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.close()
conn.close()

print("\n[OK] 工厂名称已更新为简称")
