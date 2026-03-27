import requests

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

print('='*80)
print('波次号模糊查询测试 - 输入"2114"')
print('='*80)
print()

# 测试模糊查询
batch_input = '2114'
print(f'用户输入：{batch_input}')
print()

r = requests.get(f'http://localhost:8000/api/batches/search?batch_no={batch_input}', headers=headers)

if r.status_code == 200:
    data = r.json()
    print(f'API 返回 {len(data)} 条结果:')
    print()
    
    # 只显示前 5 个（前端也会这样显示）
    for i, item in enumerate(data[:5], 1):
        print(f'{i}. {item["batch_no"]} [工厂] {item["factory_name"]}')
    
    if len(data) > 5:
        print(f'   ... 还有 {len(data)-5} 条结果')
    
    print()
    print('='*80)
    if len(data) > 0:
        print('[PASS] 测试通过 - 可以快速找到正确波次号')
        print(f'       用户只需输入"{batch_input}"，点击即可自动填充')
    else:
        print('[FAIL] 测试失败 - 未找到匹配结果')
    print('='*80)
else:
    print(f'API 错误：{r.status_code}')
    print(r.text[:200])
