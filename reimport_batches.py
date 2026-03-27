#!/usr/bin/env python3
"""
重新导入 Excel 数据，确保编码正确
"""
import pandas as pd
import pymysql

print("="*70)
print("重新导入 Excel 数据（修复编码）")
print("="*70)

# 1. 读取 Excel
print("\n[1/3] 读取 Excel 文件...")
file_path = r'C:\Users\Administrator\.openclaw\qqbot\downloads\波次号工厂货品编码_1774499615842.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')
print(f"  [OK] {len(df)} 条记录")

# 检查工厂列
factories = df['工厂'].unique()
print(f"  工厂数量：{len(factories)} 个")

# 检查浩茂和东遇
print(f"\n  特定工厂检查:")
if '浩茂' in factories:
    print(f"    ✅ 浩茂：{(df['工厂'] == '浩茂').sum()} 条")
else:
    print(f"    ❌ 浩茂：不存在")

if '东遇' in factories:
    print(f"    ✅ 东遇：{(df['工厂'] == '东遇').sum()} 条")
else:
    print(f"    ❌ 东遇：不存在")

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

batch_size = 500
total_inserted = 0

for i in range(0, len(df), batch_size):
    batch_df = df.iloc[i:i+batch_size]
    values = []
    for _, row in batch_df.iterrows():
        batch_no = str(row['波次号']).strip()
        factory = str(row['工厂']).strip()
        goods_no = str(row['货品编码']).strip()
        # 确保编码正确
        values.append(f"('{batch_no}', '{factory}', '{goods_no}')")
    
    sql = "INSERT INTO product_batches (batch_no, factory_name, goods_no) VALUES " + ",\n".join(values)
    cursor.execute(sql)
    conn.commit()
    total_inserted += len(batch_df)
    if total_inserted % 2500 == 0:
        print(f"  已导入 {total_inserted}/{len(df)} 条")

print(f"\n[OK] 导入完成！共 {total_inserted} 条记录")

# 验证
cursor.execute("SELECT COUNT(*) FROM product_batches")
count = cursor.fetchone()[0]
print(f"[验证] 表中共有 {count} 条记录")

# 检查工厂
cursor.execute("SELECT DISTINCT factory_name FROM product_batches ORDER BY factory_name")
factories_in_db = [row[0] for row in cursor.fetchall()]
print(f"\n数据库中的工厂 ({len(factories_in_db)} 个):")
for factory in factories_in_db:
    print(f"  {factory}")

# 检查浩茂和东遇
print(f"\n特定工厂检查:")
if '浩茂' in factories_in_db:
    cursor.execute("SELECT COUNT(*) FROM product_batches WHERE factory_name = '浩茂'")
    count = cursor.fetchone()[0]
    print(f"  ✅ 浩茂：{count} 条")
else:
    print(f"  ❌ 浩茂：不存在")

if '东遇' in factories_in_db:
    cursor.execute("SELECT COUNT(*) FROM product_batches WHERE factory_name = '东遇'")
    count = cursor.fetchone()[0]
    print(f"  ✅ 东遇：{count} 条")
else:
    print(f"  ❌ 东遇：不存在")

cursor.close()
conn.close()

print("\n[OK] 导入完成！")
print("="*70)
