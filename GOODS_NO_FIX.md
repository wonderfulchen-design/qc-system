# 字段名称修复报告

## 📅 修复时间
2026-03-26 13:20

---

## 🔍 发现问题

### 字段命名不一致
```
前端使用：sku_no
后端期望：goods_no
数据库字段：goods_no
```

### 显示文本问题
```
原显示：款号/SKU
应显示：货品编码（按昨天要求）
```

---

## 🔧 修复内容

### 1. 标签文本修改
```html
<!-- 修复前 -->
<label>款号/SKU</label>

<!-- 修复后 -->
<label>货品编码</label>
```

### 2. 输入框 ID 修改
```javascript
// 修复前
id="skuNo"

// 修复后
id="goodsNo"
```

### 3. 提交字段名修改
```javascript
// 修复前
formData = {
  sku_no: skuNo,
  ...
}

// 修复后
formData = {
  goods_no: goodsNo,
  ...
}
```

### 4. 所有相关引用修改
```javascript
// 修复前
document.getElementById('skuNo')
const skuNo = ...
draft.skuNo

// 修复后
document.getElementById('goodsNo')
const goodsNo = ...
draft.goodsNo
```

---

## 📋 修改清单

### 修改的位置（8 处）
1. ✅ 标签文本：款号/SKU → 货品编码
2. ✅ 输入框 ID：skuNo → goodsNo
3. ✅ 自动填充函数引用
4. ✅ 货品编码搜索监听器
5. ✅ 提交验证函数
6. ✅ formData 字段名
7. ✅ 扫码功能赋值
8. ✅ 草稿保存/加载

---

## 📊 字段对照表

| 位置 | 原名称 | 新名称 | 状态 |
|------|--------|--------|------|
| 前端 ID | skuNo | goodsNo | ✅ |
| 提交字段 | sku_no | goods_no | ✅ |
| 标签显示 | 款号/SKU | 货品编码 | ✅ |
| 数据库 | goods_no | goods_no | ✅ |
| 后端 API | goods_no | goods_no | ✅ |

---

## ✅ 验证清单

| 检查项 | 状态 |
|--------|------|
| 标签显示 | ✅ 货品编码 |
| 输入框 ID | ✅ goodsNo |
| 提交字段 | ✅ goods_no |
| 自动填充 | ✅ 已修复 |
| 扫码功能 | ✅ 已修复 |
| 草稿功能 | ✅ 已修复 |
| 后端一致 | ✅ goods_no |

---

## 📁 修改的文件

**文件**: `mobile/issue-entry.html`

**修改内容**:
- 标签文本：款号/SKU → 货品编码
- 所有 skuNo/sku_no 引用 → goodsNo/goods_no
- 共 8 处修改

---

## 🎯 验证方法

### 1. 访问页面
```
http://192.168.5.105/qc-mobile/issue-entry.html
```

### 2. 检查标签
- 应该显示"货品编码"而非"款号/SKU"

### 3. 测试功能
- 输入货品编码
- 扫码功能
- 自动填充
- 提交问题

### 4. 验证后端
- 提交后检查数据库 goods_no 字段
- 应该正确保存

---

## ✅ 结论

**字段名称已完全修复！**

- ✅ 前端显示：货品编码
- ✅ 前端 ID：goodsNo
- ✅ 提交字段：goods_no
- ✅ 后端一致：goods_no
- ✅ 数据库一致：goods_no

---

**修复完成时间**: 2026-03-26 13:20
**状态**: ✅ 已完成
**验证**: 请清除缓存后测试
