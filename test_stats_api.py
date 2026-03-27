import requests

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

print('='*80)
print('全量统计 API 测试')
print('='*80)
print()

# 1. 测试总览统计
print('1. 测试 /api/stats/summary')
r = requests.get('http://localhost:8000/api/stats/summary', headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f'   [OK] 总记录数：{data.get("total", 0)}')
    print(f'   [OK] 工厂数量：{len(data.get("by_factory", []))}')
    print(f'   [OK] 问题类型数量：{len(data.get("by_type", []))}')
    print(f'   [OK] 解决方式数量：{len(data.get("by_solution", []))}')
    
    print()
    print('   工厂统计（前 5）:')
    for f in data.get('by_factory', [])[:5]:
        print(f'      {f["factory"]}: {f["count"]} 条')
    
    print()
    print('   问题类型统计（前 5）:')
    for t in data.get('by_type', [])[:5]:
        print(f'      {t["type"]}: {t["count"]} 条')
else:
    print(f'   ❌ API 错误：{r.status_code}')
    print(f'   {r.text[:200]}')

print()

# 2. 测试按工厂统计
print('2. 测试 /api/stats/by-factory')
r = requests.get('http://localhost:8000/api/stats/by-factory', headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f'   [OK] 返回 {len(data)} 个工厂统计')
    if len(data) > 0:
        print(f'   第 1 个工厂：{data[0]["factory"]} ({data[0]["count"]} 条)')
else:
    print(f'   [ERROR] API 错误：{r.status_code}')

print()

# 3. 测试按问题类型统计
print('3. 测试 /api/stats/by-type')
r = requests.get('http://localhost:8000/api/stats/by-type', headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f'   [OK] 返回 {len(data)} 个问题类型统计')
    if len(data) > 0:
        print(f'   第 1 个问题类型：{data[0]["type"]} ({data[0]["count"]} 条)')
else:
    print(f'   [ERROR] API 错误：{r.status_code}')

print()
print('='*80)
print('测试完成')
print('='*80)
