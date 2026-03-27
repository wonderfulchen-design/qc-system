# SKU 到 goodsNo 字段清理报告

## 📅 修复时间
2026-03-26 15:48

---

## 🔍 问题发现

**用户反馈**:
```
源代码里还有很多 sku
我们不是把 sku 改成 goodsNo 了吗？
```

---

## 🔧 修复内容

### 修改 1: URL 参数读取

**修改前**:
```javascript
const urlParams = new URLSearchParams(window.location.search);
const sku = urlParams.get('sku');
if (sku) {
  document.getElementById('goodsNo').value = sku;
}
```

**修改后**:
```javascript
const urlParams = new URLSearchParams(window.location.search);
const goodsNo = urlParams.get('goodsNo');
if (goodsNo) {
  const goodsNoDisplay = document.getElementById('goodsNoDisplay');
  if (goodsNoDisplay) goodsNoDisplay.textContent = goodsNo;
}
```

---

### 修改 2: 扫码 fallback

**修改前**:
```javascript
function fallbackScan() {
  const sku = prompt('请输入 SKU 编码:');
  if (sku) document.getElementById('goodsNo').value = sku;
}
```

**修改后**:
```javascript
function fallbackScan() {
  const goodsNo = prompt('请输入货品编码:');
  if (goodsNo) {
    const goodsNoDisplay = document.getElementById('goodsNoDisplay');
    if (goodsNoDisplay) goodsNoDisplay.textContent = goodsNo;
  }
}
```

---

## 📊 字段对比

### 旧字段（已废弃）
| 字段名 | 用途 | 状态 |
|--------|------|------|
| sku | 货品编码 | ❌ 已废弃 |
| SKU | 货品编码 | ❌ 已废弃 |
| skuNo | 货品编码 input ID | ❌ 已废弃 |

### 新字段（使用中）
| 字段名 | 用途 | 状态 |
|--------|------|------|
| goodsNo | 货品编码 | ✅ 使用中 |
| goods_no | 后端字段名 | ✅ 使用中 |
| goodsNoDisplay | 货品编码显示 span ID | ✅ 使用中 |

---

## ✅ 修复效果

### 修改前
```
❌ 代码中混用 sku 和 goodsNo
❌ URL 参数读取 sku
❌ fallbackScan 使用 sku
❌ 赋值给 goodsNo.value（已删除的 input）
```

### 修改后
```
✅ 统一使用 goodsNo
✅ URL 参数读取 goodsNo
✅ fallbackScan 使用 goodsNo
✅ 赋值给 goodsNoDisplay.textContent
```

---

## 📋 完整清理清单

### 已修复
- [x] URL 参数读取
- [x] fallbackScan 函数
- [x] 变量名从 sku 改为 goodsNo
- [x] 赋值目标从 value 改为 textContent

### 无需修复
- [x] 后端 API 字段（已是 goods_no）
- [x] 数据库字段（已是 goods_no）
- [x] 提交数据字段（已是 goods_no）

---

## 🎯 验证方法

### 测试 1: URL 参数
```
访问：http://localhost/qc-mobile/issue-entry.html?goodsNo=23181802105
预期：货品编码显示为 23181802105
```

### 测试 2: 扫码 fallback
```
1. 点击扫码按钮
2. 选择"手动输入"
3. 输入货品编码
4. 预期：货品编码显示在只读区域
```

---

## ✅ 结论

**修复完成！**

- ✅ 清理所有 sku 相关代码
- ✅ 统一使用 goodsNo
- ✅ 统一使用 goodsNoDisplay
- ✅ 代码更清晰易维护

---

**修复完成时间**: 2026-03-26 15:48
**状态**: ✅ 已完成
**验证**: 请刷新页面后测试
