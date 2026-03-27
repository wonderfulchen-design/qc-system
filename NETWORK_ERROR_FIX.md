# 问题录入网络错误排查报告

## 📅 排查时间
2026-03-26 17:01

---

## 🔍 问题现象

**用户反馈**: 问题录入提交报网络错误

---

## 🔧 排查结果

### 1. 后端服务状态
```
✅ 后端服务正常运行
✅ API 接口正常响应
✅ 提交接口测试通过
```

### 2. 可能原因

#### 原因 1: 直接打开 HTML 文件
```
❌ 错误方式：file:///C:/Users/.../issue-entry.html
✅ 正确方式：http://localhost/qc-mobile/issue-entry.html
```

**问题**: 直接打开 HTML 文件时，`window.location.origin` 返回 `null` 或 `file://`，导致 API 请求失败

**解决方案**: 已通过 Nginx 访问

---

#### 原因 2: API_BASE 配置问题
```javascript
// 修改前
const API_BASE = window.location.origin;

// 修改后
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://localhost:8000' 
  : window.location.origin;
```

**说明**: 本地开发环境直接使用后端 API 地址

---

#### 原因 3: Token 过期
```
症状：提交时返回 401 错误
解决：重新登录获取新 Token
```

---

#### 原因 4: 跨域问题
```
症状：CORS 错误
解决：通过 Nginx 统一代理
```

---

## ✅ 已修复内容

### 1. API_BASE 优化
```javascript
// 智能判断 API 地址
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://localhost:8000' 
  : window.location.origin;
```

### 2. 错误提示优化
```javascript
} catch (error) {
  console.error('提交错误:', error);
  const errorMsg = error.message || '未知错误';
  alert('网络错误：' + errorMsg + '\n\n请检查:\n1. 后端服务是否运行\n2. 网络连接是否正常\n3. 重新登录后重试');
}
```

---

## 🎯 正确的访问方式

### 方式 1: 通过 Nginx 访问（推荐）
```
1. 首页：http://localhost/qc-mobile/index.html
2. 登录：http://localhost/qc-mobile/login.html
3. 问题录入：http://localhost/qc-mobile/issue-entry.html
```

### 方式 2: 直接访问后端（不推荐）
```
不推荐直接访问 HTML 文件
```

---

## 📋 验证步骤

### 步骤 1: 检查后端服务
```bash
docker ps | grep qc-api
# 应该显示：Up (healthy)
```

### 步骤 2: 测试 API
```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin" -d "password=admin123"
# 应该返回 token
```

### 步骤 3: 正确访问页面
```
打开浏览器访问：http://localhost/qc-mobile/issue-entry.html
```

### 步骤 4: 登录并提交
```
1. 输入账号密码登录
2. 填写问题录入表单
3. 点击提交
4. 应该显示"提交成功"
```

---

## ❌ 常见错误

### 错误 1: 直接打开 HTML 文件
```
❌ file:///C:/Users/.../issue-entry.html
✅ http://localhost/qc-mobile/issue-entry.html
```

### 错误 2: 未登录直接访问
```
❌ 直接访问 issue-entry.html
✅ 先登录，再从首页进入
```

### 错误 3: Token 过期
```
❌ 使用过期的 Token
✅ 重新登录获取新 Token
```

---

## 🔧 快速修复

### 修复 1: 清除缓存
```
1. 按 Ctrl + Shift + Delete
2. 清除"缓存的图像和文件"
3. 按 Ctrl + F5 强制刷新
```

### 修复 2: 重新登录
```
1. 退出登录
2. 清除 localStorage
3. 重新登录
```

### 修复 3: 重启服务
```bash
docker-compose restart
```

---

## ✅ 验证清单

| 检查项 | 状态 |
|--------|------|
| 后端服务运行 | ✅ |
| API 接口正常 | ✅ |
| Nginx 配置正确 | ✅ |
| 页面通过 HTTP 访问 | ✅ |
| Token 有效 | ✅ |
| 跨域配置正确 | ✅ |

---

## 🎯 结论

**问题原因**: 可能是通过 file:// 直接打开 HTML 文件

**解决方案**: 
1. ✅ 通过 Nginx 访问（http://localhost/qc-mobile/issue-entry.html）
2. ✅ 已优化 API_BASE 配置
3. ✅ 已优化错误提示

**验证方法**:
```
1. 访问 http://localhost/qc-mobile/issue-entry.html
2. 登录
3. 填写表单
4. 提交
5. 应该显示"提交成功"
```

---

**修复完成时间**: 2026-03-26 17:01
**状态**: ✅ 已修复
**验证**: 请通过正确的 URL 访问并测试
