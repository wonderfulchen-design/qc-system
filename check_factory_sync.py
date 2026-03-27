#!/usr/bin/env python3
"""
对比前端工厂列表与 product_batches 表
"""
import requests
import re
import pymysql

print("="*70)
print("前端工厂列表 vs product_batches 表 对比")
print("="*70)

# 1. 获取数据库中的工厂列表
print("\n[1/2] 获取 product_batches 表中的工厂...")
try:
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
    
    db_factories = {}
    for factory, count in cursor.fetchall():
        db_factories[factory] = count
    
    print(f"  [OK] 找到 {len(db_factories)} 个工厂")
    print(f"\n  前 10 个工厂:")
    for factory, count in sorted(db_factories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"    {factory}: {count} 条")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"  [ERROR] {e}")
    db_factories = {}

# 2. 获取前端工厂列表
print("\n[2/2] 获取前端工厂选项...")
try:
    with open('mobile/issue-entry.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 option 标签
    options = re.findall(r'<option value="([^"]+)">([^<]+)</option>', content)
    frontend_factories = {}
    for value, label in options:
        if value and value != '' and label != '请选择工厂':
            frontend_factories[value] = label
    
    print(f"  [OK] 找到 {len(frontend_factories)} 个工厂选项")
    print(f"\n  前端工厂列表:")
    for factory, label in sorted(frontend_factories.items()):
        print(f"    {factory} ({label})")
except Exception as e:
    print(f"  [ERROR] {e}")
    frontend_factories = {}

# 3. 对比分析
print("\n" + "="*70)
print("对比结果")
print("="*70)

# 数据库有但前端没有的
db_only = set(db_factories.keys()) - set(frontend_factories.keys())
if db_only:
    print(f"\n❌ 数据库有但前端没有 ({len(db_only)} 个):")
    for factory in sorted(db_only):
        count = db_factories[factory]
        print(f"  - {factory} ({count} 条)")
else:
    print(f"\n✅ 数据库中的所有工厂前端都有")

# 前端有但数据库没有的
frontend_only = set(frontend_factories.keys()) - set(db_factories.keys())
if frontend_only:
    print(f"\n⚠️ 前端有但数据库没有 ({len(frontend_only)} 个):")
    for factory in sorted(frontend_only):
        label = frontend_factories[factory]
        print(f"  - {factory} ({label})")
else:
    print(f"\n✅ 前端所有工厂都在数据库中存在")

# 都有的
common = set(frontend_factories.keys()) & set(db_factories.keys())
if common:
    print(f"\n✅ 一致的工厂 ({len(common)} 个)")

# 总结
print("\n" + "="*70)
print("总结")
print("="*70)

if not db_only and not frontend_only:
    print("\n✅ 完美匹配！前端工厂列表与 product_batches 表完全一致")
elif db_only:
    print(f"\n⚠️ 需要更新前端！数据库中有 {len(db_only)} 个工厂未在前端显示")
    print("\n建议操作:")
    print("  1. 在前端 issue-entry.html 中添加缺失的工厂选项")
    print("  2. 或者改为动态加载工厂列表")
    
    # 生成修复代码
    print("\n修复代码 (添加到 issue-entry.html):")
    print("-"*70)
    for factory in sorted(db_only):
        count = db_factories[factory]
        print(f'  <option value="{factory}">{factory}</option>  <!-- {count} 条 -->')
    print("-"*70)

if frontend_only:
    print(f"\nℹ️ 前端有 {len(frontend_only)} 个工厂在数据库中未找到")
    print("  这些工厂可能不在 product_batches 表中")
    print("  建议：移除这些选项或确认是否需要保留")

# 保存报告
with open('FACTORY_SYNC_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write("前端工厂列表 vs product_batches 表 对比报告\n")
    f.write("="*70 + "\n\n")
    
    f.write(f"数据库工厂数：{len(db_factories)}\n")
    f.write(f"前端工厂数：{len(frontend_factories)}\n\n")
    
    if db_only:
        f.write(f"数据库有但前端没有 ({len(db_only)}):\n")
        for factory in sorted(db_only):
            f.write(f"  - {factory} ({db_factories[factory]} 条)\n")
        f.write("\n")
    
    if frontend_only:
        f.write(f"前端有但数据库没有 ({len(frontend_only)}):\n")
        for factory in sorted(frontend_only):
            f.write(f"  - {factory}\n")
        f.write("\n")
    
    f.write(f"一致的工厂 ({len(common)}):\n")
    for factory in sorted(common):
        f.write(f"  ✓ {factory} ({db_factories[factory]} 条)\n")

print("\n[SAVE] 详细报告已保存：FACTORY_SYNC_REPORT.txt")
print("="*70)
