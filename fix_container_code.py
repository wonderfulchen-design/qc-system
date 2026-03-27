with open('/app/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换
old_text = '"created_at": i.created_at.isoformat() if i.created_at else None\n            }\n            for i in issues'

new_text = '"product_image": i.product_image,\n                "issue_images": i.issue_images,\n                "qc_user_id": i.qc_user_id,\n                "qc_username": i.qc_username,\n                "created_at": i.created_at.isoformat() if i.created_at else None\n            }\n            for i in issues'

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('/app/backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Code updated successfully!')
else:
    print('❌ Old text not found, checking current code...')
    # 查找当前代码
    if '"product_image": i.product_image' in content:
        print('✅ Image fields already exist!')
    else:
        print('❌ Image fields not found')
