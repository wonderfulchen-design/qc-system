#!/usr/bin/env python3
"""
检测问题录入页面工厂列表与 product_batches 表是否一致
"""
import pymysql
import re

print("="*70)
print("问题录入页面工厂列表 vs product_batches 表 对比")
print("="*70)

# 1. 获取数据库中的工厂
print("\n[1/2] 获取 product_batches 表中的工厂...")
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='qc_user',
    password='QcUser2025',
    database='qc_system',
    charset='utf8mb4'
)
cursor = conn.cursor()

cursor.execute("""
    SELECT factory_name, COUNT(*) as count 
    FROM product_batches 
    WHERE factory_name IS NOT NULL AND factory_name != '' 
    GROUP BY factory_name 
    ORDER BY count DESC
""")

db_factories = {row[0]: row[1] for row in cursor.fetchall()}
print(f"  [OK] 数据库中有 {len(db_factories)} 个工厂")

cursor.close()
conn.close()

# 2. 获取前端工厂列表
print("\n[2/2] 获取问题录入页面的工厂选项...")
with open('mobile/issue-entry.html', 'r', encoding='utf-8') as f:
    content = f.read()

options = re.findall(r'<option value="([^"]+)">([^<]+)</option>', content)
frontend_factories = {}
for value, label in options:
    if value and value != '' and '请选择' not in label:
        frontend_factories[value] = label

print(f"  [OK] 前端有 {len(frontend_factories)} 个工厂选项")

# 3. 对比
print("\n" + "="*70)
print("对比结果")
print("="*70)

# 数据库有但前端没有
db_only = set(db_factories.keys()) - set(frontend_factories.keys())
if db_only:
    print(f"\n❌ 数据库有但前端没有 ({len(db_only)} 个):")
    for factory in sorted(db_only, key=lambda x: db_factories[x], reverse=True):
        print(f"  - {factory} ({db_factories[factory]} 条)")
else:
    print(f"\n✅ 数据库的所有工厂前端都有")

# 前端有但数据库没有
frontend_only = set(frontend_factories.keys()) - set(db_factories.keys())
if frontend_only:
    print(f"\n⚠️ 前端有但数据库没有 ({len(frontend_only)} 个):")
    for factory in sorted(frontend_only):
        print(f"  - {factory} ({frontend_factories[factory]})")
else:
    print(f"\n✅ 前端的所有工厂都在数据库中存在")

# 总结
print("\n" + "="*70)
if not db_only and not frontend_only:
    print("✅ 完美匹配！工厂列表完全一致")
elif frontend_only:
    print(f"⚠️ 前端有 {len(frontend_only)} 个无效工厂，需要移除")
    print("\n建议移除的工厂:")
    for factory in sorted(frontend_only):
        print(f"  - {factory}")
elif db_only:
    print(f"⚠️ 前端缺少 {len(db_only)} 个工厂，需要添加")

print("="*70)
