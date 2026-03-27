#!/usr/bin/env python3
"""
直接导入 Excel 数据到 product_batches 表
"""
import pandas as pd
import pymysql

print("="*70)
print("导入 Excel 数据到 product_batches 表")
print("="*70)

# 1. 读取 Excel
print("\n[1/3] 读取 Excel 文件...")
file_path = r'C:\Users\Administrator\.openclaw\qqbot\downloads\波次号工厂货品编码_1774499615842.xlsx'
df = pd.read_excel(file_path)
print(f"  [OK] {len(df)} 条记录")

# 2. 连接数据库
print("\n[2/3] 连接数据库...")
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='qc_user',
    password='QcUser2025',
    database='qc_system',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 3. 导入数据
print("\n[3/3] 导入数据...")

# 清空表
cursor.execute("TRUNCATE TABLE product_batches")
print("  已清空 product_batches 表")

# 批量插入
batch_size = 500
total_inserted = 0

for i in range(0, len(df), batch_size):
    batch_df = df.iloc[i:i+batch_size]
    values = []
    for _, row in batch_df.iterrows():
        batch_no = str(row['波次号']).strip()
        factory = str(row['工厂']).strip()
        goods_no = str(row['货品编码']).strip()
        values.append(f"('{batch_no}', '{factory}', '{goods_no}')")
    
    sql = "INSERT INTO product_batches (batch_no, factory_name, goods_no) VALUES " + ",\n".join(values)
    cursor.execute(sql)
    conn.commit()
    total_inserted += len(batch_df)
    print(f"  已导入 {total_inserted}/{len(df)} 条")

print(f"\n[OK] 导入完成！共 {total_inserted} 条记录")

# 验证
cursor.execute("SELECT COUNT(*) FROM product_batches")
count = cursor.fetchone()[0]
print(f"[验证] 表中共有 {count} 条记录")

# 统计工厂
cursor.execute("SELECT factory_name, COUNT(*) as count FROM product_batches GROUP BY factory_name ORDER BY count DESC LIMIT 10")
print("\n前 10 个工厂:")
for factory, count in cursor.fetchall():
    print(f"  {factory}: {count} 条")

cursor.close()
conn.close()

print("\n[OK] 导入完成！")
print("="*70)
