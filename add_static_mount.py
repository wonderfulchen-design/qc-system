#!/usr/bin/env python3
import os

main_py = os.path.join(os.path.dirname(__file__), 'backend', 'main.py')

with open(main_py, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找插入点 - 在 WeChat OAuth2 Login 之前
insert_point = content.find('# ==================== WeChat OAuth2 Login ====================')

if insert_point > 0:
    static_mount = '''
# ==================== Static Files ====================

# 挂载静态文件目录
app.mount("/qc-mobile", StaticFiles(directory="mobile", html=True), name="mobile")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR, html=True), name="uploads")


# ==================== Root Redirect ====================

@app.get("/")
async def root_redirect():
    """根路径自动跳转到问题列表页"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/qc-mobile/issue-list.html")


'''
    content = content[:insert_point] + static_mount + content[insert_point:]
    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ 静态文件挂载已添加')
else:
    print('❌ 未找到插入点')
