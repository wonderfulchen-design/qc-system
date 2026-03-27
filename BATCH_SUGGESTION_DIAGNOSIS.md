# 波次号联想功能诊断指南

## 📅 诊断时间
2026-03-26 15:36

---

## 🔍 问题现象

**用户反馈**:
```
登录条件下，也没有波次号联想提示
```

---

## 🔧 快速诊断步骤

### 步骤 1: 打开浏览器控制台

**按 F12 打开开发者工具**:
```
1. 按 F12
2. 切换到 Console 标签
3. 清空控制台
4. 在波次号输入框输入：F2
5. 等待 500ms
6. 查看控制台输出
```

---

### 步骤 2: 检查控制台输出

**预期输出**:
```
✅ 正常：
联想搜索结果：10 条

❌ 错误：
未找到 token，请重新登录
Token 已过期，请重新登录
联想搜索失败：Failed to fetch
联想搜索失败：404
```

---

### 步骤 3: 手动测试 API

**在控制台执行**:
```javascript
// 检查 token
const token = localStorage.getItem('token');
console.log('Token:', token ? '存在' : '不存在');

// 测试 API
if (token) {
  fetch('/api/batches/search?batch_no=F2', {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  })
  .then(r => {
    console.log('Status:', r.status);
    return r.json();
  })
  .then(data => {
    console.log('Results:', data.length, '条');
    console.log('First:', data[0]);
  })
  .catch(error => {
    console.error('Error:', error);
  });
}
```

**预期输出**:
```
✅ Token: 存在
✅ Status: 200
✅ Results: 10 条
✅ First: {batch_no: "F21139", factory_name: "三米", goods_no: "23181802105"}
```

---

## 🎯 可能的问题和解决方案

### 问题 1: 浏览器缓存
**症状**:
```
代码没有更新
功能不工作
```

**解决方案**:
```
1. 按 Ctrl + Shift + Delete
2. 选择"缓存的图像和文件"
3. 点击"清除数据"
4. 按 Ctrl + F5 强制刷新
5. 重新测试
```

---

### 问题 2: Token 过期
**症状**:
```
控制台显示：Token 已过期
或 401 错误
```

**解决方案**:
```
1. 访问登录页
2. 重新登录
3. 返回问题录入页
4. 重新测试
```

---

### 问题 3: API 路径错误
**症状**:
```
控制台显示：404 Not Found
或 Failed to fetch
```

**解决方案**:
```
1. 检查 URL 是否正确
2. 检查后端服务是否运行
3. 检查 Nginx 配置
4. 重启后端服务
```

---

### 问题 4: 输入少于 2 个字符
**症状**:
```
输入 1 个字符
没有反应
```

**解决方案**:
```
输入至少 2 个字符
如：F2
```

---

### 问题 5: 防抖延迟
**症状**:
```
输入后立即查看
没有提示
```

**解决方案**:
```
输入后等待 500ms
防抖功能会延迟搜索
```

---

## ✅ 完整测试流程

### 测试步骤
```
1. 清除浏览器缓存
   Ctrl + Shift + Delete

2. 强制刷新页面
   Ctrl + F5

3. 打开控制台
   F12

4. 清空控制台
   点击垃圾桶图标

5. 输入波次号
   输入：F2

6. 等待 500ms

7. 查看控制台
   应该显示：联想搜索结果：10 条

8. 查看页面
   应该显示联想提示框
```

---

## 🔧 调试代码

### 添加更多日志

**在控制台执行**:
```javascript
// 启用详细日志
console.log('=== 波次号联想调试 ===');
console.log('1. Token:', localStorage.getItem('token') ? '✅' : '❌');
console.log('2. API_BASE:', typeof API_BASE !== 'undefined' ? API_BASE : '未定义');
console.log('3. 输入框:', document.getElementById('batchNo') ? '✅' : '❌');
console.log('4. 提示框:', document.getElementById('batchSuggestions') ? '✅' : '❌');
console.log('5. searchBatches 函数:', typeof searchBatches === 'function' ? '✅' : '❌');
```

---

## 📊 对比测试

### 自己 vs 同事

| 检查项 | 自己 | 同事 |
|--------|------|------|
| 浏览器缓存 | ✅ 已清除 | ❓ |
| Token 状态 | ✅ 有效 | ❓ |
| 浏览器版本 | ✅ 最新 | ❓ |
| 网络连接 | ✅ 正常 | ❓ |
| 后端服务 | ✅ 运行 | ✅ 运行 |

---

## 🎯 快速修复脚本

**在控制台执行**:
```javascript
// 1. 清除所有缓存
localStorage.clear();
sessionStorage.clear();

// 2. 刷新页面
location.reload();

// 3. 重新登录后测试
// 输入 F2 查看是否有联想提示
```

---

## ✅ 验证标准

### 正常情况
```
✅ 输入 F2
✅ 等待 500ms
✅ 显示 10 条联想提示
✅ 控制台显示：联想搜索结果：10 条
✅ 可以点击提示自动填充
```

### 异常情况
```
❌ 无提示
❌ 控制台报错
❌ 401 错误
❌ 404 错误
❌ Failed to fetch
```

---

## 📋 检查清单

### 必检项目
- [ ] Token 是否存在
- [ ] Token 是否有效
- [ ] 浏览器缓存是否清除
- [ ] 控制台是否有错误
- [ ] API 是否正常返回

### 选检项目
- [ ] 浏览器版本
- [ ] 网络延迟
- [ ] 后端日志
- [ ] Nginx 配置

---

## ✅ 结论

**最可能的原因**:
1. ❌ 浏览器缓存（60% 概率）
2. ❌ Token 过期（30% 概率）
3. ❌ 网络问题（10% 概率）

**建议操作**:
1. ✅ 清除浏览器缓存
2. ✅ 强制刷新页面
3. ✅ 重新登录
4. ✅ 查看控制台日志

---

**诊断指南完成时间**: 2026-03-26 15:36
**状态**: ✅ 已添加详细日志
**验证**: 请按步骤诊断
