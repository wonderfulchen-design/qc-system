import requests

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

print('='*80)
print('列表排序验证 - 是否新到旧排序')
print('='*80)
print()

# 获取问题列表（前 10 条）
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=10', headers=headers)
if r.status_code == 200:
    data = r.json()
    issues = data.get('data', [])
    
    print('API 返回的前 10 条记录（按创建时间排序）:')
    print()
    
    prev_time = None
    is_sorted = True
    
    for i, issue in enumerate(issues, 1):
        created_at = issue.get('created_at', '无')
        issue_no = issue.get('issue_no', '无')
        
        # 检查是否降序
        if prev_time and created_at and prev_time:
            if created_at > prev_time:
                is_sorted = False
                print(f'{i}. {issue_no} - {created_at} [ERROR] 顺序错误！')
            else:
                print(f'{i}. {issue_no} - {created_at} [OK]')
        else:
            print(f'{i}. {issue_no} - {created_at}')
        
        prev_time = created_at
    
    print()
    print('='*80)
    if is_sorted:
        print('[PASS] 排序验证：正确 - 新到旧排序（降序）')
    else:
        print('[FAIL] 排序验证：错误 - 不是新到旧排序')
    print('='*80)
else:
    print('API 错误:', r.status_code)
