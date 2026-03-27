#!/usr/bin/env python3
"""
查询浩茂工厂的波次号
"""
import pymysql

print("="*70)
print("查询浩茂工厂的波次号")
print("="*70)

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='qc_user',
    password='QcUser2025',
    database='qc_system',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 查询浩茂工厂的波次号
cursor.execute("""
    SELECT batch_no, factory_name, goods_no 
    FROM product_batches 
    WHERE factory_name = '浩茂'
    LIMIT 50
""")

rows = cursor.fetchall()
print(f"\n浩茂工厂的波次号 (共 {len(rows)} 条):")
print("-"*70)
print(f"{'波次号':<15} {'工厂':<10} {'货品编码':<15}")
print("-"*70)

for batch_no, factory, goods_no in rows:
    print(f"{batch_no:<15} {factory:<10} {goods_no:<15}")

# 统计
cursor.execute("""
    SELECT COUNT(DISTINCT batch_no) as unique_batches,
           COUNT(*) as total_records
    FROM product_batches 
    WHERE factory_name = '浩茂'
""")
stats = cursor.fetchone()
print(f"\n统计:")
print(f"  唯一波次号数：{stats[0]} 个")
print(f"  总记录数：{stats[1]} 条")

# 列出所有波次号
cursor.execute("""
    SELECT DISTINCT batch_no 
    FROM product_batches 
    WHERE factory_name = '浩茂'
    ORDER BY batch_no
""")
batches = [row[0] for row in cursor.fetchall()]
print(f"\n浩茂工厂的所有波次号 ({len(batches)} 个):")
print(", ".join(batches))

cursor.close()
conn.close()

print("\n" + "="*70)
