import requests
import json

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

# 获取首页数据（问题列表）
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=5', headers=headers)
if r.status_code == 200:
    api_data = r.json()
    print('='*70)
    print('API 返回数据')
    print('='*70)
    print('总记录数:', api_data.get('total', 0))
    print('当前页:', api_data.get('page', 0))
    print()
    print('最新 5 条记录:')
    for i, issue in enumerate(api_data.get('data', [])[:5], 1):
        print(f'{i}. {issue.get("issue_no")}')
        print(f'   工厂：{issue.get("factory_name")}')
        print(f'   货品：{issue.get("goods_no")}')
        print(f'   问题：{issue.get("issue_type")}')
        product_img = issue.get('product_image', '无')
        print(f'   商品图：{product_img[:50] if product_img else "无"}...')
        print(f'   时间：{issue.get("created_at", "无")}')
        print()
    
    # 保存完整数据用于对比
    with open('/tmp/api_data.json', 'w', encoding='utf-8') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    print('完整数据已保存到 /tmp/api_data.json')
else:
    print('API 错误:', r.status_code)
    print(r.text[:200])
