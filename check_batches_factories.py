#!/usr/bin/env python3
"""
检查 product_batches 表中的工厂
"""
import requests

API_BASE = "http://localhost:8000"

# 登录
token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*70)
print("检查 product_batches 表中的工厂")
print("="*70)

# 获取所有批次
print("\n获取所有批次数据...")
all_batches = []
page = 1
while True:
    r = requests.get(f"{API_BASE}/api/batches/search?page={page}&page_size=100", headers=headers)
    if r.status_code == 200:
        batches = r.json()
        if not batches:
            break
        all_batches.extend(batches)
        page += 1
    else:
        break

print(f"  找到 {len(all_batches)} 个批次")

# 统计工厂
factories_in_batches = {}
for batch in all_batches:
    factory = batch.get('factory_name')
    batch_no = batch.get('batch_no')
    goods_no = batch.get('goods_no')
    if factory:
        if factory not in factories_in_batches:
            factories_in_batches[factory] = []
        factories_in_batches[factory].append({
            'batch_no': batch_no,
            'goods_no': goods_no
        })

print(f"\nproduct_batches 表中的工厂 ({len(factories_in_batches)} 个):")
for factory in sorted(factories_in_batches.keys()):
    count = len(factories_in_batches[factory])
    print(f"  {factory}: {count} 个批次")

# 检查特定工厂
print("\n" + "="*70)
print("特定工厂检查:")
print("="*70)

target_factories = ['浩茂', '东遇', '元合', '春秋', '浩迅']
for factory in target_factories:
    if factory in factories_in_batches:
        count = len(factories_in_batches[factory])
        print(f"  ✅ {factory}: 在表中 ({count} 个批次)")
    else:
        print(f"  ❌ {factory}: 不在表中")

# 生成前端代码
print("\n" + "="*70)
print("建议的前端工厂选项:")
print("="*70)
print('<select class="factory-select" id="factory" required>')
print('  <option value="">请选择工厂</option>')
for factory in sorted(factories_in_batches.keys()):
    print(f'  <option value="{factory}">{factory}</option>')
print('</select>')

# 保存结果
with open('batches_factories.txt', 'w', encoding='utf-8') as f:
    f.write("product_batches 表中的工厂列表\n")
    f.write("="*70 + "\n\n")
    f.write(f"总计：{len(factories_in_batches)} 个工厂\n\n")
    for factory in sorted(factories_in_batches.keys()):
        count = len(factories_in_batches[factory])
        f.write(f"{factory}: {count} 个批次\n")

print("\n[SAVE] 详细列表已保存：batches_factories.txt")
print("="*70)
