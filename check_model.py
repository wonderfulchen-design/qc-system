with open('/app/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查 QualityIssue 模型
if 'class QualityIssue(Base):' in content:
    start = content.find('class QualityIssue(Base):')
    end = content.find('\n\nclass', start + 10)
    model_def = content[start:end]
    print('Current QualityIssue model:')
    print(model_def[:1000])
    
    # 检查是否有 qc_user_id 字段
    if 'qc_user_id' in model_def:
        print('\n✅ qc_user_id field exists')
    else:
        print('\n❌ qc_user_id field NOT found, need to add')
