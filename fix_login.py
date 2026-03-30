# -*- coding: utf-8 -*-
with open('mobile/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 隐藏用户名密码登录表单
content = content.replace('<form id="loginForm">', '<form id="loginForm" style="display:none;">')
content = content.replace('<div class="divider"><span>或</span></div>', '<!-- 隐藏普通登录 -->')

with open('mobile/login.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - hidden username/password login form')
