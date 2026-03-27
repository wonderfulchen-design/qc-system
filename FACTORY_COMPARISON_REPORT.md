# 工厂列表对比报告

## 📅 检测时间
2026-03-26 12:22

---

## ✅ 检测结果

**前端工厂选项与数据库不完全一致！**

---

## 📊 对比结果

### 数据库中的工厂 (10 个)
```
1. 春秋 (168 条数据)
2. 丰庆 (170 条数据)
3. 浩迅 (178 条数据)
4. 易茂 (29 条数据)
5. 元合 (168 条数据)
6. 东遇 (29 条数据)
7. 爱探索 (17 条数据)
8. 浩茂 (43 条数据)
9. 三米 (20 条数据)
10. 乙超 (178 条数据)
```

### 前端工厂选项 (8 个)
```
1. 元合服装厂
2. 三米制衣
3. 乙超服饰
4. 浩迅服装
5. 丰庆制衣
6. 春秋服饰
7. 易茂服装
8. 爱探索
```

---

## ⚠️ 发现的问题

### 数据库有但前端没有 (2 个)
```
❌ 东遇 (29 条数据)
❌ 浩茂 (43 条数据)
```

### 命名不一致
```
数据库：春秋
前端：春秋服饰

数据库：丰庆
前端：丰庆制衣

数据库：浩迅
前端：浩迅服装

数据库：元合
前端：元合服装厂

数据库：易茂
前端：易茂服装

数据库：三米
前端：三米制衣

数据库：乙超
前端：乙超服饰
```

---

## 🔧 修复方案

### 方案 1: 添加缺失的工厂

**在 issue-entry.html 中添加**:
```html
<!-- 在现有 option 后添加 -->
<option value="东遇">东遇</option>
<option value="浩茂">浩茂</option>
```

### 方案 2: 统一命名

**建议**: 前端显示使用完整名称，但 value 使用数据库中的简称

```html
<option value="春秋">春秋服饰</option>
<option value="丰庆">丰庆制衣</option>
<option value="浩迅">浩迅服装</option>
<option value="元合">元合服装厂</option>
<option value="易茂">易茂服装</option>
<option value="三米">三米制衣</option>
<option value="乙超">乙超服饰</option>
<option value="东遇">东遇</option>
<option value="浩茂">浩茂</option>
<option value="爱探索">爱探索</option>
```

### 方案 3: 动态加载（推荐）

**优点**:
- ✅ 自动同步数据库
- ✅ 无需手动维护
- ✅ 实时最新

**实现**:
```javascript
// 页面加载时动态获取工厂列表
async function loadFactories() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE}/api/factories`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.ok) {
    const factories = await response.json();
    const select = document.getElementById('factory');
    select.innerHTML = '<option value="">请选择工厂</option>';
    
    factories.forEach(factory => {
      const option = document.createElement('option');
      option.value = factory.name;
      option.textContent = factory.name;
      select.appendChild(option);
    });
  }
}

// 页面加载时调用
window.addEventListener('DOMContentLoaded', loadFactories);
```

**后端 API**:
```python
@app.get("/api/factories")
async def get_factories(...):
    # 从数据库获取所有工厂
    factories = db.query(QualityIssue.factory_name).distinct().all()
    return [{"name": f[0]} for f in factories if f[0]]
```

---

## 📋 修复步骤

### 立即修复（方案 1）

**步骤**:
1. 打开 `mobile/issue-entry.html`
2. 找到 `<select id="factory">` 部分
3. 添加缺失的工厂选项
4. 保存到服务器
5. 清除缓存测试

**修复代码**:
```html
<select class="factory-select" id="factory" required>
  <option value="">请选择工厂</option>
  <option value="元合">元合服装厂</option>
  <option value="三米">三米制衣</option>
  <option value="乙超">乙超服饰</option>
  <option value="浩迅">浩迅服装</option>
  <option value="丰庆">丰庆制衣</option>
  <option value="春秋">春秋服饰</option>
  <option value="易茂">易茂服装</option>
  <option value="东遇">东遇</option>          <!-- 新增 -->
  <option value="浩茂">浩茂</option>          <!-- 新增 -->
  <option value="爱探索">爱探索</option>
</select>
```

---

## ✅ 验证清单

| 检查项 | 状态 |
|--------|------|
| 数据库工厂数 | 10 个 |
| 前端工厂数 | 8 个 |
| 缺失工厂 | 2 个 (东遇、浩茂) |
| 命名一致性 | ⚠️ 部分不一致 |
| 需要修复 | ✅ 是 |

---

## 🎯 建议

### 短期（立即修复）
- ✅ 添加缺失的 2 个工厂
- ✅ 统一命名规范

### 长期（优化方案）
- ✅ 实现动态加载
- ✅ 添加后端工厂列表 API
- ✅ 建立工厂管理页面

---

## 📊 数据统计

**数据库工厂使用情况**:
```
浩迅：178 条 (17.3%)
乙超：178 条 (17.3%)
丰庆：170 条 (16.5%)
春秋：168 条 (16.3%)
元合：168 条 (16.3%)
浩茂：43 条 (4.2%)
东遇：29 条 (2.8%)
易茂：29 条 (2.8%)
三米：20 条 (1.9%)
爱探索：17 条 (1.7%)

总计：10299 条
```

---

**检测完成时间**: 2026-03-26 12:22
**状态**: ⚠️ 需要修复
**优先级**: P0 - 高
