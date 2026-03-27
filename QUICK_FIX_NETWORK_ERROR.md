# 网络错误快速修复指南

## 🚨 问题
问题录入提交报网络错误

## ✅ 已修复
API_BASE 已硬编码为 `http://localhost:8000`

## 🔧 立即修复步骤

### 步骤 1: 清除浏览器缓存
```
1. 按 Ctrl + Shift + Delete
2. 选择"所有时间"
3. 勾选"缓存的图像和文件"
4. 点击"清除数据"
```

### 步骤 2: 强制刷新页面
```
按 Ctrl + F5
```

### 步骤 3: 重新登录
```
1. 退出登录
2. 重新登录
3. 再次提交
```

## 🎯 正确的访问方式

**通过 Nginx 访问**:
```
http://localhost/qc-mobile/issue-entry.html
```

**不要直接打开 HTML 文件**:
```
❌ file:///C:/Users/.../issue-entry.html
```

## ✅ 后端状态

```
✅ 后端服务：运行中 (52 分钟)
✅ 登录接口：200 OK
✅ API 接口：200 OK
```

## 📋 验证方法

### 方法 1: 测试 API
```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin" -d "password=admin123"
```

### 方法 2: 使用测试脚本
```bash
python batch_submit_with_tracking.py 1
```

## 🐛 可能的原因

1. **浏览器缓存** - 最常见
2. **Token 过期** - 重新登录
3. **跨域问题** - 通过 Nginx 访问
4. **文件缓存** - 强制刷新

## ✅ 快速解决

**一行命令清除所有**:
```javascript
// 在控制台执行
localStorage.clear(); sessionStorage.clear(); location.reload(true);
```

---

**修复后请重新测试！**
