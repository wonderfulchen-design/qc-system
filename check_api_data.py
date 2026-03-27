import requests

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

# 获取问题列表
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=10', headers=headers)
if r.status_code == 200:
    data = r.json()
    print('API 返回数据:')
    print('总记录数:', data.get('total', 0))
    print('当前页:', data.get('page', 0))
    print('每页数量:', data.get('page_size', 0))
    print()
    print('最新 10 条记录:')
    for i, issue in enumerate(data.get('data', [])[:10], 1):
        print(f'{i}. {issue.get("issue_no")}: {issue.get("issue_desc", "")[:30]}...')
        print(f'   商品图：{issue.get("product_image", "无")}')
        print(f'   时间：{issue.get("created_at", "无")}')
else:
    print('API 错误:', r.status_code)
    print(r.text[:200])
