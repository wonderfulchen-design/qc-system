# 权限验证和访问指南

## 📅 更新时间
2026-03-26 15:33

---

## 🔍 问题原因

**用户反馈**:
```
同事直接访问：http://localhost/qc-mobile/issue-entry.html
结果：被重定向到登录页，无法使用
```

**原因**:
- ❌ 没有登录 token
- ❌ 直接访问需要权限的页面
- ❌ 系统自动重定向到登录页

---

## ✅ 正确的访问方式

### 方式 1: 从首页访问（推荐）
```
1. 访问首页：http://localhost/qc-mobile/index.html
2. 点击底部导航"录入"
3. 系统自动跳转到问题录入页
4. 如果未登录，会先跳转到登录页
5. 登录完成后自动回到问题录入页
```

### 方式 2: 先登录后访问
```
1. 访问登录页：http://localhost/qc-mobile/login.html
2. 输入账号密码登录
3. 登录成功后访问：http://localhost/qc-mobile/issue-entry.html
```

### 方式 3: 扫码访问（如果支持）
```
1. 使用手机扫描二维码
2. 自动打开 APP 并登录
3. 直接进入问题录入页
```

---

## 🔐 权限验证逻辑

### 检查流程
```javascript
function checkLogin() {
  const token = localStorage.getItem('token');
  
  if (!token) {
    // 没有 token，跳转到登录页
    window.location.href = '/qc-mobile/login.html';
    return;
  }
  
  // 有 token，可以访问
  // 继续加载页面
}
```

### 自动跳转
```
未登录 → 访问需要权限的页面 → 自动跳转到登录页 → 登录成功 → 自动回到原页面
```

---

## 📋 完整的页面访问流程

### 正常流程
```
1. 用户访问首页
   http://localhost/qc-mobile/index.html
   
2. 点击"问题录入"
   
3. 系统检查登录状态
   ✅ 已登录 → 进入问题录入页
   ❌ 未登录 → 跳转到登录页
   
4. 登录页面
   http://localhost/qc-mobile/login.html
   
5. 输入账号密码
   账号：admin
   密码：admin123
   
6. 登录成功
   - 保存 token 到 localStorage
   - 自动跳转回问题录入页
   
7. 进入问题录入页
   http://localhost/qc-mobile/issue-entry.html
   
8. 正常使用所有功能
```

---

## 🎯 给同事的访问指南

### 快速访问步骤
```
1. 打开浏览器
2. 访问：http://localhost/qc-mobile/index.html
3. 点击底部"录入"按钮
4. 如果需要登录，输入账号密码
5. 登录完成后自动进入问题录入页
```

### 账号信息
```
账号：admin
密码：admin123
```

---

## 🔧 已添加的友好提示

### 提示功能
```javascript
function showAccessNotice() {
  const token = localStorage.getItem('token');
  if (!token) {
    setTimeout(() => {
      alert('请先登录！\n\n正确的访问方式：\n1. 访问首页 http://localhost/qc-mobile/index.html\n2. 从首页点击"问题录入"\n\n或直接登录后系统会自动跳转');
    }, 1000);
  }
}
```

### 提示内容
```
请先登录！

正确的访问方式：
1. 访问首页 http://localhost/qc-mobile/index.html
2. 从首页点击"问题录入"

或直接登录后系统会自动跳转
```

---

## 📊 页面权限对比

| 页面 | 需要登录 | 直接访问结果 |
|------|---------|-------------|
| /login.html | ❌ 不需要 | ✅ 显示登录页 |
| /index.html | ❌ 不需要 | ✅ 显示首页（部分功能受限） |
| /issue-entry.html | ✅ 需要 | ❌ 跳转到登录页 |
| /issue-list.html | ✅ 需要 | ❌ 跳转到登录页 |
| /stats.html | ✅ 需要 | ❌ 跳转到登录页 |

---

## ✅ 解决方案

### 给同事的说明
```
你好！

问题录入页面需要先登录才能访问。

请按以下步骤操作：

1. 访问首页：
   http://localhost/qc-mobile/index.html

2. 点击底部导航栏的"录入"按钮

3. 如果提示登录，输入：
   账号：admin
   密码：admin123

4. 登录成功后会自动进入问题录入页

5. 之后就可以正常使用了！

注意：不要直接访问 issue-entry.html 链接，
因为系统会检查登录状态。
```

---

## 🎯 最佳实践

### 推荐做法
- ✅ 从首页导航访问各个页面
- ✅ 使用底部导航栏切换页面
- ✅ 保持登录状态（token 有效期 1 天）

### 不推荐做法
- ❌ 直接访问需要权限的页面链接
- ❌ 复制分享内部页面链接给未登录用户
- ❌ 绕过登录验证

---

## 🔐 Token 管理

### Token 存储
```javascript
// 登录成功后
localStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');

// 检查登录状态
const token = localStorage.getItem('token');
if (!token) {
  // 未登录，跳转登录页
}
```

### Token 有效期
```
有效期：1 天
过期后：自动跳转登录页
刷新 Token：重新登录
```

---

## ✅ 结论

**问题已解决！**

- ✅ 添加了访问提示
- ✅ 自动跳转登录页
- ✅ 登录后自动返回
- ✅ 友好的错误提示

**请告诉同事**:
```
不要直接访问 issue-entry.html
从首页点击"录入"按钮访问
或先登录再访问
```

---

**更新时间**: 2026-03-26 15:33
**状态**: ✅ 已添加友好提示
**验证**: 请同事按正确方式访问
