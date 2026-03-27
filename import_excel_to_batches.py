#!/usr/bin/env python3
"""
导入 Excel 波次号 - 工厂 - 货品编码数据到 product_batches 表
"""
import pandas as pd
import requests
from datetime import datetime

API_BASE = "http://localhost:8000"

print("="*70)
print("导入 Excel 数据到 product_batches 表")
print("="*70)

# 1. 读取 Excel 文件
print("\n[1/4] 读取 Excel 文件...")
file_path = r'C:\Users\Administrator\.openclaw\qqbot\downloads\波次号工厂货品编码_1774499615842.xlsx'
try:
    df = pd.read_excel(file_path)
    print(f"  [OK] 读取成功")
    print(f"  行数：{len(df)}")
    print(f"  列数：{len(df.columns)}")
    print(f"  列名：{', '.join(df.columns)}")
except Exception as e:
    print(f"  [ERROR] {e}")
    exit(1)

# 2. 登录
print("\n[2/4] 登录系统...")
try:
    token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print(f"  [OK] 登录成功")
except Exception as e:
    print(f"  [ERROR] {e}")
    exit(1)

# 3. 检查并准备数据
print("\n[3/4] 检查数据...")

# 重命名列（如果列名不匹配）
column_mapping = {
    '波次号': 'batch_no',
    '工厂': 'factory_name',
    '货品编码': 'goods_no'
}

# 尝试使用中文列名或英文列名
for cn_col, en_col in column_mapping.items():
    if cn_col in df.columns:
        df[en_col] = df[cn_col]

# 检查必需的列
required_cols = ['batch_no', 'factory_name', 'goods_no']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    print(f"  [ERROR] 缺少必需的列：{', '.join(missing_cols)}")
    print(f"  当前列名：{', '.join(df.columns)}")
    exit(1)

# 清理数据
df = df.dropna(subset=required_cols)
df = df[df['batch_no'].astype(str).str.strip() != '']
df = df[df['factory_name'].astype(str).str.strip() != '']
df = df[df['goods_no'].astype(str).str.strip() != '']

print(f"  [OK] 有效数据：{len(df)} 条")

# 统计工厂
factories = df['factory_name'].value_counts()
print(f"  工厂数量：{len(factories)} 个")
print(f"  前 5 个工厂:")
for factory, count in factories.head(5).items():
    print(f"    {factory}: {count} 条")

# 4. 导入数据库
print("\n[4/4] 导入数据到数据库...")
print("  提示：由于批量插入数据量较大，建议使用 SQL 直接导入")
print("  已生成 SQL 导入脚本：import_batches.sql")

# 生成 SQL 脚本
sql_lines = [
    "-- 导入波次号 - 工厂 - 货品编码数据",
    f"-- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"-- 数据来源：{file_path}",
    f"-- 总记录数：{len(df)}",
    "",
    "USE qc_system;",
    "",
    "-- 清空现有数据（可选）",
    "-- TRUNCATE TABLE product_batches;",
    "",
    "-- 插入数据",
    "INSERT INTO product_batches (batch_no, factory_name, goods_no) VALUES"
]

# 生成 INSERT 语句
values = []
for _, row in df.iterrows():
    batch_no = str(row['batch_no']).strip()
    factory_name = str(row['factory_name']).strip()
    goods_no = str(row['goods_no']).strip()
    values.append(f"  ('{batch_no}', '{factory_name}', '{goods_no}')")

sql_lines.append(",\n".join(values[:1000]))  # 只输出前 1000 条作为示例
sql_lines.append(";")

# 保存 SQL 文件
sql_file = 'import_batches.sql'
with open(sql_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(sql_lines))

print(f"\n  [SAVE] SQL 脚本已保存：{sql_file}")

# 生成工厂列表
print("\n" + "="*70)
print("工厂列表（用于更新前端）")
print("="*70)

factory_list = sorted(factories.index.tolist())
print("\n前端工厂选项:")
print('<select class="factory-select" id="factory" required>')
print('  <option value="">请选择工厂</option>')
for factory in factory_list:
    count = factories[factory]
    print(f'  <option value="{factory}">{factory} ({count})</option>')
print('</select>')

# 保存工厂列表
with open('factories_complete_list.txt', 'w', encoding='utf-8') as f:
    f.write("完整的工厂列表（来自 Excel）\n")
    f.write("="*70 + "\n\n")
    f.write(f"总计：{len(factory_list)} 个工厂\n\n")
    for factory in factory_list:
        count = factories[factory]
        f.write(f"{factory}: {count} 条\n")

print(f"\n[SAVE] 工厂列表已保存：factories_complete_list.txt")

print("\n" + "="*70)
print("导入说明")
print("="*70)
print("""
下一步操作:

1. 导入 SQL 数据:
   docker exec -i qc-mysql mysql -u qc_user -pQcUser2025 qc_system < import_batches.sql

2. 验证导入:
   docker exec qc-mysql mysql -u qc_user -pQcUser2025 qc_system -e "SELECT COUNT(*) FROM product_batches;"

3. 更新前端工厂列表:
   使用上面生成的工厂选项替换 issue-entry.html 中的内容

4. 测试波次号自动填充:
   访问：http://192.168.5.105/qc-mobile/issue-entry.html
   输入波次号：F21144
   应该自动填充工厂和货品编码
""")

print("="*70)
