#!/usr/bin/env python3
"""
对比前端工厂选项与数据库工厂列表
"""
import requests
import re

API_BASE = "http://localhost:8000"

# 登录
token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*70)
print("前端工厂选项 vs 数据库工厂列表 对比")
print("="*70)

# 1. 获取数据库工厂列表
print("\n[1/3] 获取数据库工厂列表...")
r = requests.get(f"{API_BASE}/api/issues?page=1&page_size=1000", headers=headers)
if r.status_code == 200:
    data = r.json()
    db_factories = {}
    for issue in data['data']:
        factory = issue.get('factory_name')
        if factory:
            db_factories[factory] = db_factories.get(factory, 0) + 1
    
    print(f"  [OK] 找到 {len(db_factories)} 个工厂")
else:
    print(f"  [ERROR] 获取失败")
    db_factories = {}

# 2. 获取前端工厂选项
print("\n[2/3] 获取前端工厂选项...")
with open('mobile/issue-entry.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 option 标签
options = re.findall(r'<option value="([^"]+)">([^<]+)</option>', content)
frontend_factories = {}
for value, label in options:
    if value and value != '':  # 排除空选项
        frontend_factories[value] = label

print(f"  [OK] 找到 {len(frontend_factories)} 个工厂选项")

# 3. 对比分析
print("\n[3/3] 对比分析...")
print("="*70)

# 数据库有但前端没有的
db_only = set(db_factories.keys()) - set(frontend_factories.keys())
if db_only:
    print(f"\n❌ 数据库有但前端没有 ({len(db_only)} 个):")
    for factory in sorted(db_only):
        count = db_factories[factory]
        print(f"  - {factory} ({count} 条数据)")

# 前端有但数据库没有的
frontend_only = set(frontend_factories.keys()) - set(db_factories.keys())
if frontend_only:
    print(f"\n⚠️ 前端有但数据库没有 ({len(frontend_only)} 个):")
    for factory in sorted(frontend_only):
        label = frontend_factories[factory]
        print(f"  - {factory} ({label})")

# 都有的
common = set(frontend_factories.keys()) & set(db_factories.keys())
if common:
    print(f"\n✅ 一致的工厂 ({len(common)} 个):")
    for factory in sorted(common):
        count = db_factories[factory]
        print(f"  ✓ {factory} ({count} 条数据)")

# 总结
print("\n" + "="*70)
print("总结")
print("="*70)

if not db_only and not frontend_only:
    print("\n✅ 完美匹配！前端工厂选项与数据库完全一致")
elif db_only:
    print(f"\n⚠️ 需要更新前端！数据库中有 {len(db_only)} 个工厂未在前端显示")
    print("\n建议操作:")
    print("  1. 在前端 issue-entry.html 中添加缺失的工厂选项")
    print("  2. 或者改为动态加载工厂列表")
    
    # 生成修复代码
    print("\n修复代码 (添加到 issue-entry.html):")
    print("-"*70)
    for factory in sorted(db_only):
        print(f'  <option value="{factory}">{factory}</option>')
    print("-"*70)

if frontend_only:
    print(f"\nℹ️ 前端有 {len(frontend_only)} 个工厂在数据库中未找到")
    print("  可能是历史数据或已删除的工厂")

# 保存报告
with open('FACTORY_COMPARISON_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write("前端工厂选项 vs 数据库工厂列表 对比报告\n")
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

print("\n[SAVE] 详细报告已保存：FACTORY_COMPARISON_REPORT.txt")
print("="*70)
