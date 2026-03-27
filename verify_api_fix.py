import requests
import json

# 登录
r = requests.post('http://localhost:8000/token', data={'username':'admin','password':'admin123'})
token = r.json()['access_token']
headers = {'Authorization': 'Bearer ' + token}

# 获取问题列表
r = requests.get('http://localhost:8000/api/issues?page=1&page_size=3', headers=headers)
if r.status_code == 200:
    data = r.json()
    print('='*70)
    print('API 返回数据验证')
    print('='*70)
    print(f'总记录数：{data.get("total", 0)}')
    print(f'当前页：{data.get("page", 0)}')
    print()
    print('最新 3 条记录:')
    print('-'*70)
    for i, issue in enumerate(data.get('data', [])[:3], 1):
        print(f'{i}. Issue No: {issue.get("issue_no")}')
        print(f'   描述：{issue.get("issue_desc", "")}')
        print(f'   商品图：{issue.get("product_image", "无")}')
        print(f'   问题图：{issue.get("issue_images", "无")}')
        print(f'   时间：{issue.get("created_at", "无")}')
        print(f'   QC ID: {issue.get("qc_user_id", "无")}')
        print(f'   QC 名：{issue.get("qc_username", "无")}')
        print()
    
    # 检查是否有图片字段
    first_issue = data['data'][0]
    print('='*70)
    print('字段检查:')
    print('='*70)
    print(f'product_image 字段：{"✅ 存在" if "product_image" in first_issue else "❌ 不存在"}')
    print(f'issue_images 字段：{"✅ 存在" if "issue_images" in first_issue else "❌ 不存在"}')
    print(f'qc_user_id 字段：{"✅ 存在" if "qc_user_id" in first_issue else "❌ 不存在"}')
    print(f'qc_username 字段：{"✅ 存在" if "qc_username" in first_issue else "❌ 不存在"}')
    print(f'created_at 字段：{"✅ 存在" if "created_at" in first_issue else "❌ 不存在"}')
    print()
    print('完整 JSON:')
    print(json.dumps(first_issue, indent=2, ensure_ascii=False))
else:
    print('API 错误:', r.status_code)
    print(r.text[:200])
