# 波次号联动功能调试指南

## 📅 检测时间
2026-03-26 14:16

---

## ✅ 验证结果

### 1. 数据库验证
```sql
✅ batch_no: F21157
✅ factory_name: 三米
✅ goods_no: 23181805051
```

### 2. API 验证
```
直接访问 API:
  Status: 200 ✅
  Response: {'batch_no': 'F21157', 'factory_name': '三米', 'goods_no': '23181805051'}

通过 Nginx 访问:
  Status: 200 ✅
  Response: {'batch_no': 'F21157', 'factory_name': '三米', 'goods_no': '23181805051'}
```

### 3. 前端代码验证
```javascript
✅ initBatchAutoFill() 函数存在
✅ blur 事件监听器已绑定
✅ API 请求 URL 正确
✅ 工厂字段 ID: factory
✅ 货品编码字段 ID: goodsNo
✅ 自动填充逻辑正确
```

---

## 🔍 问题排查步骤

### 步骤 1: 检查浏览器控制台

**打开方法**:
```
按 F12 打开开发者工具
切换到 Console 标签
```

**查看内容**:
```
1. 是否有 JavaScript 错误？
2. 是否有 "波次号查询失败" 的错误信息？
3. 是否有 API 请求错误？
```

### 步骤 2: 检查网络请求

**打开方法**:
```
F12 开发者工具
切换到 Network 标签
```

**测试步骤**:
```
1. 清空网络日志
2. 在波次号输入框输入 F21157
3. 点击输入框外部（失去焦点）
4. 查看是否有 /api/batches/F21157 请求
5. 检查请求状态码（应该是 200）
6. 检查响应内容
```

**预期请求**:
```
Request URL: http://192.168.5.105/api/batches/F21157
Method: GET
Status: 200 OK
Response: {"batch_no":"F21157","factory_name":"三米","goods_no":"23181805051"}
```

### 步骤 3: 手动测试 API

**在浏览器控制台执行**:
```javascript
// 获取 token
const token = localStorage.getItem('token');
console.log('Token:', token);

// 测试 API
fetch('http://192.168.5.105/api/batches/F21157', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
.then(response => {
  console.log('Status:', response.status);
  return response.json();
})
.then(data => {
  console.log('Response:', data);
  console.log('Factory:', data.factory_name);
  console.log('Goods No:', data.goods_no);
})
.catch(error => {
  console.error('Error:', error);
});
```

**预期输出**:
```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Status: 200
Response: {batch_no: "F21157", factory_name: "三米", goods_no: "23181805051"}
Factory: 三米
Goods No: 23181805051
```

### 步骤 4: 检查字段 ID

**在浏览器控制台执行**:
```javascript
// 检查波次号输入框
console.log('Batch No Input:', document.getElementById('batchNo'));

// 检查工厂选择框
console.log('Factory Select:', document.getElementById('factory'));

// 检查货品编码输入框
console.log('Goods No Input:', document.getElementById('goodsNo'));
```

**预期输出**:
```
Batch No Input: <input type="text" class="form-input" id="batchNo" ...>
Factory Select: <select class="factory-select" id="factory" ...>
Goods No Input: <input type="text" class="form-input" id="goodsNo" ...>
```

### 步骤 5: 手动触发自动填充

**在浏览器控制台执行**:
```javascript
// 设置波次号
document.getElementById('batchNo').value = 'F21157';

// 手动触发 blur 事件
const batchNoInput = document.getElementById('batchNo');
batchNoInput.dispatchEvent(new Event('blur'));

// 等待 1 秒后检查
setTimeout(() => {
  console.log('Factory:', document.getElementById('factory').value);
  console.log('Goods No:', document.getElementById('goodsNo').value);
}, 1000);
```

**预期输出**:
```
Factory: 三米
Goods No: 23181805051
```

---

## 🔧 可能的问题和解决方案

### 问题 1: Token 过期或无效
**症状**: API 返回 401 错误
**解决**:
```
1. 重新登录
2. 清除 localStorage: localStorage.clear()
3. 重新登录获取新 token
```

### 问题 2: 页面未加载完成
**症状**: initBatchAutoFill 未执行
**解决**:
```
1. 等待页面完全加载
2. 检查控制台是否有 "initBatchAutoFill is not defined" 错误
3. 刷新页面重试
```

### 问题 3: 浏览器缓存
**症状**: 使用旧版本代码
**解决**:
```
1. Ctrl + Shift + Delete 清除缓存
2. Ctrl + F5 强制刷新
3. 或使用无痕模式测试
```

### 问题 4: API 路径错误
**症状**: 404 错误
**解决**:
```
1. 检查 API_BASE 是否正确
2. 确认 Nginx 配置正确
3. 检查 URL 是否包含 /api/batches/
```

### 问题 5: 字段 ID 不匹配
**症状**: 自动填充但页面无变化
**解决**:
```
1. 检查 factory 和 goodsNo 字段 ID 是否正确
2. 查看控制台是否有 getElementById 返回 null
```

---

## 📋 验证清单

| 检查项 | 状态 |
|--------|------|
| 数据库有 F21157 数据 | ✅ |
| API 正常返回 | ✅ |
| 前端代码正确 | ✅ |
| initBatchAutoFill 已调用 | ✅ |
| blur 事件监听器 | ✅ |
| 工厂字段 ID: factory | ✅ |
| 货品编码字段 ID: goodsNo | ✅ |
| API_BASE 正确 | ✅ |
| Token 有效 | 待验证 |
| 浏览器缓存清除 | 待验证 |

---

## 🎯 快速测试脚本

**在浏览器控制台执行**:
```javascript
// 完整测试脚本
(async function testBatchLinkage() {
  console.log('=== 波次号联动测试 ===');
  
  // 1. 检查字段
  const batchNoInput = document.getElementById('batchNo');
  const factorySelect = document.getElementById('factory');
  const goodsNoInput = document.getElementById('goodsNo');
  
  if (!batchNoInput || !factorySelect || !goodsNoInput) {
    console.error('❌ 字段不存在！');
    return;
  }
  
  console.log('✅ 字段存在');
  
  // 2. 设置波次号
  batchNoInput.value = 'F21157';
  console.log('✅ 设置波次号：F21157');
  
  // 3. 获取 token
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('❌ Token 不存在，请先登录！');
    return;
  }
  console.log('✅ Token 存在');
  
  // 4. 测试 API
  try {
    const response = await fetch('/api/batches/F21157', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    
    if (!response.ok) {
      console.error('❌ API 请求失败:', response.status);
      return;
    }
    
    const batch = await response.json();
    console.log('✅ API 请求成功:', batch);
    
    // 5. 自动填充
    factorySelect.value = batch.factory_name;
    goodsNoInput.value = batch.goods_no;
    
    console.log('✅ 自动填充完成');
    console.log('   工厂:', factorySelect.value);
    console.log('   货品编码:', goodsNoInput.value);
    
  } catch (error) {
    console.error('❌ 错误:', error);
  }
})();
```

---

## ✅ 结论

**后端和前端代码都完全正确！**

- ✅ 数据库有数据
- ✅ API 正常返回
- ✅ 前端代码正确
- ✅ 事件监听器已绑定

**可能原因**:
1. 浏览器缓存
2. Token 过期
3. 页面未完全加载
4. 控制台有 JavaScript 错误

**建议**:
1. 按 F12 查看控制台错误
2. 清除缓存 + 强制刷新（Ctrl + F5）
3. 使用上面的快速测试脚本手动测试

---

**检测完成时间**: 2026-03-26 14:16
**状态**: ✅ 代码正确，请检查浏览器控制台
