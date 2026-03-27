import requests
import json

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

print('='*80)
print('统计 API 数据校验')
print('='*80)
print()

# 1. 获取问题列表统计
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=1', headers=headers)
if r.status_code == 200:
    data = r.json()
    print('1. 问题总数统计:')
    print('   API 返回总数:', data.get('total', 0))
    api_total = data.get('total', 0)
else:
    print('   API 错误:', r.status_code)
    api_total = 0

print()

# 2. 按工厂统计
print('2. 按工厂统计 (前 5):')
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=100', headers=headers)
if r.status_code == 200:
    data = r.json()
    factory_count = {}
    for issue in data.get('data', []):
        factory = issue.get('factory_name', '未知')
        factory_count[factory] = factory_count.get(factory, 0) + 1
    
    # 排序取前 5
    sorted_factories = sorted(factory_count.items(), key=lambda x: x[1], reverse=True)[:5]
    for factory, count in sorted_factories:
        print(f'   {factory}: {count} 条')
else:
    print('   API 错误:', r.status_code)

print()

# 3. 按问题类型统计
print('3. 按问题类型统计 (前 5):')
if r.status_code == 200:
    type_count = {}
    for issue in data.get('data', []):
        issue_type = issue.get('issue_type', '未知')
        type_count[issue_type] = type_count.get(issue_type, 0) + 1
    
    sorted_types = sorted(type_count.items(), key=lambda x: x[1], reverse=True)[:5]
    for issue_type, count in sorted_types:
        print(f'   {issue_type}: {count} 条')

print()

# 保存完整数据
with open('C:\\Users\\Administrator\\.openclaw\\workspace\\qc-system\\api_stats.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': api_total,
        'factories': dict(sorted_factories) if r.status_code == 200 else {},
        'types': dict(sorted_types) if r.status_code == 200 else {}
    }, f, indent=2, ensure_ascii=False)

print('API 统计数据已保存到 api_stats.json')
