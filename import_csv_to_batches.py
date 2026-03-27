#!/usr/bin/env python3
"""
用新的 CSV 文件（UTF-8 编码）重新导入 product_batches 表
"""
import pandas as pd
import pymysql

print("="*70)
print("用 CSV 文件重新导入 product_batches 表")
print("="*70)

# 1. 读取 CSV 文件
print("\n[1/3] 读取 CSV 文件...")
file_path = r'C:\Users\Administrator\.openclaw\qqbot\downloads\波次号工厂货品编码_1774500684885.csv'

# 尝试不同编码
df = None
for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        print(f"  [OK] 使用 {encoding} 编码读取成功")
        break
    except Exception as e:
        print(f"  尝试 {encoding} 编码失败：{e}")
        continue

if df is None:
    # 如果都失败，尝试无表头
    df = pd.read_csv(file_path, encoding='gbk', header=None, names=['波次号', '工厂', '货品编码'])
    print(f"  [OK] 使用 gbk 编码（无表头）读取成功")

print(f"  记录数：{len(df)} 条")
print(f"  列名：{list(df.columns)}")

# 确保列名正确
if list(df.columns) != ['波次号', '工厂', '货品编码']:
    df.columns = ['波次号', '工厂', '货品编码']

# 清理数据
df = df.dropna(subset=['波次号', '工厂', '货品编码'])
df['波次号'] = df['波次号'].astype(str).str.strip()
df['工厂'] = df['工厂'].astype(str).str.strip()
df['货品编码'] = df['货品编码'].astype(str).str.strip()
df = df[(df['波次号'] != '') & (df['工厂'] != '') & (df['货品编码'] != '')]

print(f"  有效记录：{len(df)} 条")

# 统计工厂
factories = df['工厂'].value_counts()
print(f"  工厂数量：{len(factories)} 个")
print(f"  前 5 个工厂:")
for factory, count in factories.head(5).items():
    print(f"    {factory}: {count} 条")

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
print("  清空 product_batches 表...")
cursor.execute("TRUNCATE TABLE product_batches")

# 批量插入
batch_size = 500
total_inserted = 0

print(f"  开始导入 {len(df)} 条记录...")

for i in range(0, len(df), batch_size):
    batch_df = df.iloc[i:i+batch_size]
    values = []
    for _, row in batch_df.iterrows():
        batch_no = row['波次号']
        factory = row['工厂']
        goods_no = row['货品编码']
        values.append(f"('{batch_no}', '{factory}', '{goods_no}')")
    
    sql = "INSERT INTO product_batches (batch_no, factory_name, goods_no) VALUES " + ",\n".join(values)
    cursor.execute(sql)
    conn.commit()
    total_inserted += len(batch_df)
    if total_inserted % 2500 == 0 or total_inserted == len(df):
        print(f"    已导入 {total_inserted}/{len(df)} 条")

print(f"\n[OK] 导入完成！共 {total_inserted} 条记录")

# 验证
cursor.execute("SELECT COUNT(*) FROM product_batches")
count = cursor.fetchone()[0]
print(f"[验证] 表中共有 {count} 条记录")

# 检查浩茂
cursor.execute("SELECT COUNT(*) FROM product_batches WHERE factory_name = '浩茂'")
haomao_count = cursor.fetchone()[0]
if haomao_count > 0:
    print(f"[验证] ✅ 浩茂工厂：{haomao_count} 条")
else:
    print(f"[验证] ❌ 浩茂工厂：0 条")

# 统计工厂
cursor.execute("SELECT factory_name, COUNT(*) as count FROM product_batches GROUP BY factory_name ORDER BY count DESC LIMIT 10")
print(f"\n前 10 个工厂:")
for factory, count in cursor.fetchall():
    print(f"  {factory}: {count} 条")

cursor.close()
conn.close()

print("\n[OK] 导入完成！")
print("="*70)
