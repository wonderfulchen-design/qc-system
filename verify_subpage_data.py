import requests
import json

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

# 获取问题列表（前 10 条）
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=10', headers=headers)
if r.status_code == 200:
    api_data = r.json()
    
    print('='*80)
    print('子页面数据校验 - API vs 数据库')
    print('='*80)
    print()
    
    # 校验前 10 条数据
    for i, issue in enumerate(api_data.get('data', [])[:10], 1):
        print(f'{i}. Issue No: {issue.get("issue_no")}')
        print(f'   工厂：{issue.get("factory_name")}')
        print(f'   货品：{issue.get("goods_no")}')
        print(f'   问题：{issue.get("issue_type")}')
        print(f'   解决：{issue.get("solution_type")}')
        print(f'   补偿：{issue.get("compensation_amount")}')
        print(f'   商品图：{issue.get("product_image", "无")}')
        print(f'   问题图：{issue.get("issue_images", "无")}')
        print(f'   时间：{issue.get("created_at", "无")}')
        print()
    
    # 保存完整数据
    with open('C:\\Users\\Administrator\\.openclaw\\workspace\\qc-system\\subpage_api_data.json', 'w', encoding='utf-8') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    print('完整数据已保存到 subpage_api_data.json')
else:
    print('API 错误:', r.status_code)
    print(r.text[:200])
