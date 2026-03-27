# 波次号、工厂、货品编码联动关系检测报告

## 📅 检测时间
2026-03-26 12:18

---

## ✅ 检测结果

**波次号 F21144 存在联动关系！**

---

## 📊 实际数据

### 波次号 F21144
```
波次号：F21144
工厂：春秋
货品编码：23181813015
关系：一对一
```

### 货品编码 23181813015
```
找到 6 条记录:
1. F21144  | 春秋 | 23181813015
2. FY21526 | 春秋 | 23181813015
3. FY22296 | 春秋 | 23181813015
4. FY25897 | 春秋 | 23181813015
5. FY28140 | 春秋 | 23181813015
6. ...     | ...  | 23181813015

关系：一对多 (一个货品编码对应多个波次)
```

---

## 🔧 联动关系类型

### 当前实现

| 输入 | 输出 | 状态 | API |
|------|------|------|-----|
| **波次号** | 工厂 + 货品编码 | ✅ 支持 | `/api/batches/{batch_no}` |
| **货品编码** | 波次号列表 + 工厂 | ✅ 支持 | `/api/batches/search?goods_no=xxx` |
| **工厂** | 波次号 + 货品编码 | ❌ 不支持 | - |

### 关系说明

**1. 波次号 → 工厂 + 货品编码 (单向)**
```
输入：F21144
↓
查询：/api/batches/F21144
↓
返回：{
  "batch_no": "F21144",
  "factory_name": "春秋",
  "goods_no": "23181813015"
}
```

**2. 货品编码 → 波次号列表 (一对多)**
```
输入：23181813015
↓
查询：/api/batches/search?goods_no=23181813015
↓
返回：[
  {"batch_no": "F21144", "factory_name": "春秋"},
  {"batch_no": "FY21526", "factory_name": "春秋"},
  ...
]
```

**3. 工厂 → 波次号 + 货品编码**
```
❌ 当前不支持
建议添加：/api/factories/{factory_name}/batches
```

---

## 📱 前端实现检查

### issue-entry.html 检查

**当前状态**: ⚠️ **缺少自动填充逻辑**

**检查项**:
| 功能 | 状态 | 说明 |
|------|------|------|
| 波次号输入框 | ✅ 存在 | `<input id="batchNo">` |
| 工厂选择框 | ✅ 存在 | `<select id="factory">` |
| 货品编码输入框 | ✅ 存在 | `<input id="skuNo">` |
| 波次号 change 事件 | ❌ 未发现 | 缺少自动填充 |
| API 调用 | ❌ 未发现 | 未调用批次查询 API |
| 自动填充逻辑 | ❌ 未发现 | 需要添加 |

---

## 🔧 需要添加的功能

### 前端自动填充逻辑

**1. 波次号输入后自动填充**
```javascript
// 在 issue-entry.html 中添加
document.getElementById('batchNo').addEventListener('blur', async function() {
  const batchNo = this.value.trim();
  if (!batchNo) return;
  
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`${API_BASE}/api/batches/${batchNo}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      const batch = await response.json();
      // 自动填充工厂
      document.getElementById('factory').value = batch.factory_name;
      // 自动填充货品编码
      document.getElementById('skuNo').value = batch.goods_no;
      showToast('已自动填充');
    }
  } catch (error) {
    console.error('查询失败:', error);
  }
});
```

**2. 货品编码输入后搜索**
```javascript
// 可选：货品编码输入后提示相关波次
document.getElementById('skuNo').addEventListener('blur', async function() {
  const goodsNo = this.value.trim();
  if (goodsNo.length < 5) return;
  
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`${API_BASE}/api/batches/search?goods_no=${goodsNo}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      const batches = await response.json();
      if (batches.length === 1) {
        // 只有一个匹配，自动填充
        document.getElementById('batchNo').value = batches[0].batch_no;
        document.getElementById('factory').value = batches[0].factory_name;
      } else if (batches.length > 1) {
        // 多个匹配，提示用户选择
        showToast(`找到${batches.length}个匹配，请手动选择波次`);
      }
    }
  } catch (error) {
    console.error('搜索失败:', error);
  }
});
```

---

## 📋 完整联动流程

### 场景 1: 输入波次号
```
1. 用户输入：F21144
2. 失去焦点/回车
3. 调用：GET /api/batches/F21144
4. 返回：{ batch_no: "F21144", factory_name: "春秋", goods_no: "23181813015" }
5. 自动填充：
   - 工厂：春秋
   - 货品编码：23181813015
```

### 场景 2: 输入货品编码
```
1. 用户输入：23181813015
2. 失去焦点/回车
3. 调用：GET /api/batches/search?goods_no=23181813015
4. 返回：[{ batch_no: "F21144", factory_name: "春秋" }, ...]
5. 如果只有 1 个匹配：
   - 自动填充波次号：F21144
   - 自动填充工厂：春秋
6. 如果有多个匹配：
   - 提示用户手动选择
```

### 场景 3: 选择工厂
```
当前：❌ 不支持
建议：
1. 用户选择工厂
2. 调用：GET /api/factories/{factory_name}/batches
3. 显示相关波次和货品编码列表
4. 用户选择
```

---

## ✅ 验证清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| **后端 API** | ✅ | `/api/batches/{batch_no}` 正常 |
| **后端 API** | ✅ | `/api/batches/search` 正常 |
| **数据库** | ✅ | product_batches 表正常 |
| **数据存在** | ✅ | F21144 存在 |
| **联动关系** | ✅ | 波次→工厂→货品 |
| **前端输入框** | ✅ | 3 个字段都存在 |
| **前端自动填充** | ❌ | 需要添加 |
| **前端事件监听** | ❌ | 需要添加 |

---

## 🔧 修复建议

### P0 - 必须添加
1. **波次号自动填充**
   - 添加 blur 事件监听
   - 调用批次查询 API
   - 填充工厂和货品编码

### P1 - 建议添加
2. **货品编码搜索提示**
   - 添加输入提示
   - 多个匹配时提示用户

3. **工厂筛选功能**
   - 添加按工厂搜索 API
   - 前端支持下拉选择

---

## 📊 测试数据

### 波次号 F21144
```
✅ 存在
✅ 工厂：春秋
✅ 货品编码：23181813015
✅ 关系：一对一
```

### 货品编码 23181813015
```
✅ 存在
✅ 对应 6 个波次
✅ 都是春秋工厂
✅ 关系：一对多
```

---

## ✅ 结论

**波次号 F21144 存在单向联动关系！**

### 已实现
- ✅ 后端 API 完整
- ✅ 数据库关系正确
- ✅ 波次号可查询工厂 + 货品编码
- ✅ 货品编码可查询波次列表

### 待实现
- ❌ 前端自动填充逻辑
- ❌ 前端事件监听
- ❌ 按工厂搜索功能

### 联动类型
```
波次号 → 工厂 + 货品编码  (✅ 支持)
货品编码 → 波次号列表    (✅ 支持)
工厂 → 波次号 + 货品编码  (❌ 不支持)
```

---

**检测完成时间**: 2026-03-26 12:18
**状态**: ✅ 后端联动正常，⚠️ 前端需添加自动填充
