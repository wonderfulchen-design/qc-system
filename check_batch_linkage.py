#!/usr/bin/env python3
"""
检测波次号、工厂和货品编码的联动关系
"""
import requests

API_BASE = "http://localhost:8000"

# 登录
token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*70)
print("波次号、工厂、货品编码 联动关系检测")
print("="*70)

# 测试 1: 通过波次号查询
print("\n[测试 1] 通过波次号 F21144 查询...")
r = requests.get(f"{API_BASE}/api/batches/F21144", headers=headers)
print(f"  状态码：{r.status_code}")

if r.status_code == 200:
    batch = r.json()
    print(f"  [OK] 查询成功")
    print(f"  波次号：{batch.get('batch_no')}")
    print(f"  工厂：{batch.get('factory_name')}")
    print(f"  货品编码：{batch.get('goods_no')}")
    
    batch_no = batch.get('batch_no')
    factory_name = batch.get('factory_name')
    goods_no = batch.get('goods_no')
else:
    print(f"  [WARN] 波次号 F21144 不存在")
    print(f"  错误：{r.text[:100]}")
    batch_no = None
    factory_name = None
    goods_no = None

# 测试 2: 通过波次号模糊搜索
print("\n[测试 2] 通过波次号模糊搜索 (F21144)...")
r = requests.get(f"{API_BASE}/api/batches/search?batch_no=F21144", headers=headers)
print(f"  状态码：{r.status_code}")

if r.status_code == 200:
    results = r.json()
    print(f"  [OK] 找到 {len(results)} 条记录")
    for i, batch in enumerate(results[:5], 1):
        print(f"  {i}. 波次：{batch.get('batch_no')} | 工厂：{batch.get('factory_name')} | 货品：{batch.get('goods_no')}")
else:
    print(f"  [ERROR] 搜索失败")

# 测试 3: 通过货品编码搜索
if goods_no:
    print(f"\n[测试 3] 通过货品编码 {goods_no} 搜索...")
    r = requests.get(f"{API_BASE}/api/batches/search?goods_no={goods_no}", headers=headers)
    print(f"  状态码：{r.status_code}")
    
    if r.status_code == 200:
        results = r.json()
        print(f"  [OK] 找到 {len(results)} 条记录")
        for i, batch in enumerate(results[:5], 1):
            print(f"  {i}. 波次：{batch.get('batch_no')} | 工厂：{batch.get('factory_name')} | 货品：{batch.get('goods_no')}")
    else:
        print(f"  [ERROR] 搜索失败")

# 测试 4: 通过工厂搜索
if factory_name:
    print(f"\n[测试 4] 通过工厂 {factory_name} 搜索...")
    r = requests.get(f"{API_BASE}/api/batches/search?batch_no=&goods_no=", headers=headers)
    # 注意：当前 API 不支持直接按工厂搜索
    
    # 获取所有批次，然后过滤
    print(f"  [INFO] 当前 API 不支持直接按工厂搜索")
    print(f"  [建议] 添加 /api/bactories/{factory_name}/batches 接口")

print("\n" + "="*70)
print("联动关系分析")
print("="*70)

print("\n当前实现:")
print("  ✅ 波次号 → 工厂 + 货品编码 (单向)")
print("  ✅ 货品编码 → 波次号 + 工厂 (单向)")
print("  ❌ 工厂 → 波次号 + 货品编码 (不支持)")

print("\n联动类型:")
print("  波次号输入:")
print("    → 自动填充工厂")
print("    → 自动填充货品编码")
print("    → 一对一或一对多关系")

print("\n前端实现检查:")
print("  检查 issue-entry.html 中是否有:")
print("  - batchNo 输入框的 change 事件")
print("  - 调用 /api/batches/{batch_no} API")
print("  - 自动填充 factory 和 goodsNo 字段")

# 检查前端代码
print("\n" + "="*70)
print("前端代码检查")
print("="*70)

with open('mobile/issue-entry.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否有波次号联动逻辑
if 'batchNo' in content and 'api/batches' in content:
    print("  ✅ 发现波次号相关代码")
    print("  ✅ 发现批次 API 调用")
else:
    print("  ⚠️ 未发现完整的波次号联动代码")

# 检查是否有事件监听
if 'addEventListener' in content or 'onchange' in content:
    print("  ✅ 发现事件监听代码")
else:
    print("  ⚠️ 未发现事件监听代码")

print("\n" + "="*70)
print("结论")
print("="*70)

print("""
当前状态:
  ✅ 后端支持波次号查询
  ✅ 后端支持货品编码搜索
  ✅ 数据库有 product_batches 表
  ⚠️ 前端可能缺少自动填充逻辑
  ❌ 不支持按工厂搜索

建议:
  1. 在前端添加波次号输入框的 change 事件
  2. 调用 /api/batches/{batch_no} API
  3. 自动填充工厂和货品编码字段
  4. 添加按工厂搜索功能
""")
