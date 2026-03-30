# -*- coding: utf-8 -*-
with open('mobile/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改显示逻辑：优先显示 real_name，没有则显示 username
old_code = "document.getElementById('userName').textContent = user.username;"
new_code = "document.getElementById('userName').textContent = user.real_name || user.username;"

content = content.replace(old_code, new_code)

with open('mobile/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - fixed username display to show real_name')
