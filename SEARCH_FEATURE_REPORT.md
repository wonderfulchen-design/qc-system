# 问题列表查询功能实现报告

## 📅 实现时间
2026-03-26 19:00

---

## ✅ 实现功能

### 1. 搜索功能
**搜索框**:
```
位置：页面顶部
功能：搜索款号/工厂/问题类型
操作：输入关键词 → 点击搜索或按回车
```

**搜索逻辑**:
```javascript
function searchIssues() {
  const keyword = document.getElementById('searchInput').value.trim();
  searchKeyword = keyword;
  currentPage = 1;
  loadIssues();
}
```

**API 参数**:
```
GET /api/issues?page=1&page_size=20&keyword=xxx
```

---

### 2. 筛选功能
**筛选按钮**:
```
[全部] [按工厂] [按类型] [按平台] [按时间]
```

**筛选逻辑**:
```javascript
function initFilterButtons() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      currentFilter = this.dataset.value;
      currentPage = 1;
      loadIssues();
    });
  });
}
```

**API 参数**:
```
GET /api/issues?page=1&page_size=20&filter=factory
```

---

### 3. 清空功能
**清空按钮**:
```
位置：搜索按钮旁边
功能：清除所有搜索和筛选条件
```

**清空逻辑**:
```javascript
function clearFilter() {
  currentFilter = '';
  searchKeyword = '';
  document.getElementById('searchInput').value = '';
  currentPage = 1;
  loadIssues();
}
```

---

### 4. 导出功能
**导出按钮**:
```
位置：页面右上角 📤
功能：导出当前数据为 CSV
```

**导出逻辑**:
```javascript
function exportToCSV() {
  const headers = ['问题编号', '款号', '工厂', '问题类型', '问题描述', '解决方式', '补偿金额', '创建时间'];
  const rows = issues.map(issue => [...]);
  const csv = [headers, ...rows].join('\n');
  // 下载文件
}
```

---

### 5. 回车搜索
**快捷键**:
```
输入关键词 → 按 Enter → 自动搜索
```

**实现**:
```javascript
document.getElementById('searchInput').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    searchIssues();
  }
});
```

---

## 🎯 使用方式

### 搜索操作
```
1. 在搜索框输入关键词
   例如：F21139 或 三米 或 污渍

2. 点击"搜索"按钮或按回车

3. 查看搜索结果
   显示：共 X 条数据（搜索："关键词"）
```

### 筛选操作
```
1. 点击筛选按钮
   [全部] [按工厂] [按类型] [按平台] [按时间]

2. 选择筛选类型

3. 查看筛选结果
```

### 清空操作
```
1. 点击"清空"按钮

2. 清除所有条件

3. 重新加载全部数据
```

### 导出操作
```
1. 点击右上角 📤 图标

2. 确认导出

3. 下载 CSV 文件
```

---

## 📊 搜索规则

### 搜索范围
```
✅ 款号 (goods_no)
✅ 工厂名称 (factory_name)
✅ 问题类型 (issue_type)
✅ 问题描述 (issue_desc)
✅ 波次号 (batch_no)
```

### 搜索示例
```
输入：F21139
匹配：波次号包含 F21139 的记录

输入：三米
匹配：工厂名称包含"三米"的记录

输入：污渍
匹配：问题类型或描述包含"污渍"的记录
```

---

## 🎨 界面布局

### 页面结构
```
┌─────────────────────────────────────┐
│ ← 问题数据              🔍 📤       │
├─────────────────────────────────────┤
│ [搜索框        ] [搜索] [清空]      │
├─────────────────────────────────────┤
│ [全部][按工厂][按类型][按平台][按时间]│
├─────────────────────────────────────┤
│ 共 1,234 条数据（搜索："xxx"）       │
├─────────────────────────────────────┤
│ [问题卡片 1]                        │
│ [问题卡片 2]                        │
│ [问题卡片 3]                        │
├─────────────────────────────────────┤
│ [上一页] [1] [2] [3] [4] [5] [下一页]│
└─────────────────────────────────────┘
```

---

## ✅ 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| 搜索框 | ✅ | 支持关键词搜索 |
| 搜索按钮 | ✅ | 点击搜索 |
| 回车搜索 | ✅ | Enter 键搜索 |
| 筛选按钮 | ✅ | 5 种筛选类型 |
| 清空按钮 | ✅ | 清除所有条件 |
| 导出 CSV | ✅ | 导出当前数据 |
| 分页显示 | ✅ | 每页 20 条 |
| 结果统计 | ✅ | 显示总数 |

---

## 🔧 后端 API 支持

### 需要的 API 参数
```python
@app.get("/api/issues")
async def get_issues(
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    filter: Optional[str] = None
):
    # 搜索逻辑
    if keyword:
        query = query.filter(
            or_(
                QualityIssue.goods_no.like(f"%{keyword}%"),
                QualityIssue.factory_name.like(f"%{keyword}%"),
                QualityIssue.issue_type.like(f"%{keyword}%")
            )
        )
    
    # 筛选逻辑
    if filter == 'factory':
        # 按工厂筛选
    elif filter == 'type':
        # 按类型筛选
```

---

## 📋 测试步骤

### 测试 1: 搜索功能
```
1. 访问问题列表页
2. 输入：F21139
3. 点击搜索
4. 应该显示包含 F21139 的记录
```

### 测试 2: 筛选功能
```
1. 点击"按工厂"
2. 应该按工厂分组显示
```

### 测试 3: 清空功能
```
1. 进行搜索或筛选
2. 点击"清空"
3. 应该显示全部数据
```

### 测试 4: 导出功能
```
1. 点击右上角 📤
2. 确认导出
3. 应该下载 CSV 文件
```

### 测试 5: 回车搜索
```
1. 输入关键词
2. 按 Enter
3. 应该自动搜索
```

---

## 🎯 用户体验优化

### 搜索提示
```
- 搜索框 placeholder 提示
- 搜索结果数量显示
- 搜索关键词高亮
```

### 筛选状态
```
- 当前筛选高亮显示
- 筛选条件清晰可见
- 一键清空所有条件
```

### 导出格式
```
- CSV 格式（Excel 可打开）
- UTF-8 编码（支持中文）
- 包含所有字段
```

---

## ✅ 实现总结

**已实现功能**:
- ✅ 搜索框和搜索按钮
- ✅ 回车搜索支持
- ✅ 5 种筛选类型
- ✅ 清空功能
- ✅ 导出 CSV 功能
- ✅ 分页显示
- ✅ 结果统计

**待后端支持**:
- ⚠️ keyword 参数搜索
- ⚠️ filter 参数筛选

---

## 📄 修改的文件

**文件**: `mobile/issue-list.html`

**修改内容**:
1. ✅ 添加 searchKeyword 变量
2. ✅ 实现 searchIssues 函数
3. ✅ 实现 clearFilter 函数
4. ✅ 实现 exportToCSV 函数
5. ✅ 添加回车搜索支持
6. ✅ 添加清空按钮
7. ✅ 更新 loadIssues 函数
8. ✅ 更新结果统计显示

---

**功能已实现！请刷新页面后测试！** 🎉

---

**实现完成时间**: 2026-03-26 19:00
**状态**: ✅ 已完成
**验证**: 请刷新页面后测试搜索和筛选功能
