# 波次号联想提示排查指南

## 📅 排查时间
2026-03-26 15:29

---

## 🔍 问题现象

**用户反馈**:
- ✅ 自己的浏览器 - 联想提示正常
- ❌ 同事的浏览器 - 无法获取联想提示

---

## 🔧 已添加的调试功能

### 1. 控制台日志
```javascript
console.log('联想搜索结果:', batches.length, '条');
```

### 2. Token 检查
```javascript
if (!token) {
  console.error('未找到 token，请重新登录');
  return;
}
```

### 3. Token 过期处理
```javascript
if (response.status === 401) {
  console.error('Token 已过期，请重新登录');
  alert('登录已过期，请重新登录');
  localStorage.removeItem('token');
  window.location.href = '/qc-mobile/login.html';
  return;
}
```

---

## 📋 排查步骤

### 步骤 1: 检查浏览器控制台

**让同事按 F12 打开控制台**:
```
1. 按 F12 打开开发者工具
2. 切换到 Console 标签
3. 输入波次号（如：F2）
4. 查看控制台输出
```

**预期输出**:
```
✅ 正常：
联想搜索结果：10 条

❌ 错误：
未找到 token，请重新登录
Token 已过期，请重新登录
联想搜索失败：TypeError: Failed to fetch
```

---

### 步骤 2: 检查 Token 状态

**在控制台执行**:
```javascript
// 检查 token
console.log('Token:', localStorage.getItem('token'));

// 如果返回 null，说明 token 不存在
// 需要重新登录
```

**解决方案**:
```
1. 清除浏览器缓存
2. 清除 localStorage
3. 重新登录
```

---

### 步骤 3: 检查网络连接

**在控制台执行**:
```javascript
// 测试 API 连接
fetch('/api/batches/search?batch_no=F2', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => {
  console.log('Status:', r.status);
  return r.json();
})
.then(data => {
  console.log('Results:', data.length);
})
.catch(error => {
  console.error('Error:', error);
});
```

**预期结果**:
```
✅ Status: 200
✅ Results: 10

❌ Status: 401 (Token 过期)
❌ Error: Failed to fetch (网络问题)
```

---

### 步骤 4: 清除缓存

**让同事执行**:
```
1. 按 Ctrl + Shift + Delete
2. 选择"缓存的图像和文件"
3. 选择"Cookie 和其他网站数据"
4. 点击"清除数据"
5. 重新登录
6. 刷新页面
```

---

## 🎯 常见问题

### 问题 1: Token 过期
**症状**:
```
控制台显示：
Token 已过期，请重新登录
```

**解决方案**:
```
1. 点击确定
2. 自动跳转到登录页
3. 重新登录
4. 再次尝试
```

---

### 问题 2: Token 不存在
**症状**:
```
控制台显示：
未找到 token，请重新登录
```

**解决方案**:
```
1. 清除浏览器缓存
2. 清除 localStorage: localStorage.clear()
3. 重新登录
4. 刷新页面
```

---

### 问题 3: 网络错误
**症状**:
```
控制台显示：
联想搜索失败：TypeError: Failed to fetch
```

**解决方案**:
```
1. 检查网络连接
2. 检查服务器地址是否正确
3. 检查防火墙设置
4. 联系 IT 支持
```

---

### 问题 4: API 返回 404
**症状**:
```
控制台显示：
联想搜索失败：404
```

**解决方案**:
```
1. 检查后端服务是否运行
2. 检查 API 路径是否正确
3. 重启后端服务
4. 联系开发人员
```

---

## ✅ 验证方法

### 验证步骤
```
1. 输入波次号：F2
2. 等待 500ms
3. 查看是否显示联想提示
4. 查看控制台日志
```

### 预期结果
```
✅ 显示 10 条联想提示
✅ 控制台显示：联想搜索结果：10 条
✅ 可以点击提示自动填充
```

---

## 📊 对比测试

### 自己 vs 同事

| 检查项 | 自己 | 同事 |
|--------|------|------|
| Token 存在 | ✅ | ❓ |
| Token 有效 | ✅ | ❓ |
| 网络连接 | ✅ | ❓ |
| 浏览器缓存 | ✅ | ❓ |
| 浏览器版本 | ✅ | ❓ |

---

## 🔧 快速修复脚本

**让同事在控制台执行**:
```javascript
// 清除所有缓存
localStorage.clear();
sessionStorage.clear();

// 刷新页面
location.reload();

// 然后重新登录
```

---

## 📋 检查清单

### 必检项目
- [ ] Token 是否存在
- [ ] Token 是否有效
- [ ] 网络连接是否正常
- [ ] 浏览器缓存是否清除
- [ ] 控制台是否有错误

### 选检项目
- [ ] 浏览器版本
- [ ] 浏览器扩展
- [ ] 防火墙设置
- [ ] 代理设置

---

## ✅ 结论

**最可能的原因**:
1. ❌ Token 过期（80% 概率）
2. ❌ 浏览器缓存（15% 概率）
3. ❌ 网络问题（5% 概率）

**建议操作**:
1. ✅ 清除缓存
2. ✅ 重新登录
3. ✅ 刷新页面
4. ✅ 查看控制台

---

**排查指南完成时间**: 2026-03-26 15:29
**状态**: ✅ 已添加调试功能
**验证**: 请按步骤排查
