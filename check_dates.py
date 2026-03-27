import json
import os

files = sorted([f for f in os.listdir('data') if f.endswith('.json')])
data = []
for f in files:
    with open(os.path.join('data', f), 'r', encoding='utf-8') as file:
        data.extend(json.load(file))

dates = [d['created_at'] for d in data if d.get('created_at')]
print(f'数据条数：{len(data)}')
print(f'最早日期：{min(dates) if dates else "N/A"}')
print(f'最新日期：{max(dates) if dates else "N/A"}')
print(f'文件数：{len(files)}')
