with open('/app/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 只添加图片字段，移除 qc_user_id 和 qc_username
old_text = '''"product_image": i.product_image,
                "issue_images": i.issue_images,
                "qc_user_id": i.qc_user_id,
                "qc_username": i.qc_username,
                "created_at": i.created_at.isoformat() if i.created_at else None'''

new_text = '''"product_image": i.product_image,
                "issue_images": i.issue_images,
                "created_at": i.created_at.isoformat() if i.created_at else None'''

if old_text in content:
    content = content.replace(old_text, new_text)
    with open('/app/backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Code fixed - removed qc_user_id/qc_username, kept image fields')
else:
    print('❌ Text not found')
