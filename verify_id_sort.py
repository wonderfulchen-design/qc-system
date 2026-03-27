import requests

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

print('='*80)
print('ID 排序验证 - ID 越大越新（新到旧排序）')
print('='*80)
print()

# 获取问题列表（前 10 条）
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=10', headers=headers)
if r.status_code == 200:
    data = r.json()
    issues = data.get('data', [])
    
    print('API 返回的前 10 条记录（按 ID 降序排序）:')
    print()
    
    prev_id = None
    is_sorted = True
    
    for i, issue in enumerate(issues, 1):
        issue_id = issue.get('id', 0)
        issue_no = issue.get('issue_no', '无')
        created_at = issue.get('created_at', '无')
        
        # 检查是否降序
        if prev_id and issue_id > prev_id:
            is_sorted = False
            print(f'{i}. ID={issue_id} {issue_no} - {created_at} [ERROR] 顺序错误！')
        else:
            print(f'{i}. ID={issue_id} {issue_no} - {created_at} [OK]')
        
        prev_id = issue_id
    
    print()
    print('='*80)
    if is_sorted:
        print('[PASS] 排序验证：正确 - ID 降序（新到旧）')
    else:
        print('[FAIL] 排序验证：错误 - 不是 ID 降序')
    print('='*80)
else:
    print('API 错误:', r.status_code)
