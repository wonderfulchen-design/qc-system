# 问题录入提交 QC 信息问题分析报告

## 📅 分析时间
2026-03-26 22:05

---

## 🔍 问题分析

### 用户反馈
ChatGPT 提示：在问题录入页面提交时加了 QC 信息，导致获取 token 不成功产生的异常

---

## 🔧 代码检查

### 1. 前端提交代码
```javascript
async function submitIssue() {
  const token = localStorage.getItem('token');
  
  const formData = {
    goods_no: goodsNo,
    factory_name: factory,
    batch_no: batchNo,
    issue_type: selectedTypes.join(','),
    issue_desc: issueDesc,
    solution_type: selectedSolution,
    compensation_amount: 0,
    product_image: imageUrls['product'] || null,
    issue_images: [...]
  };
  
  const response = await fetch(`${API_BASE}/api/issues`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(formData)
  });
}
```

**检查结果**: ✅ 前端代码正确
- ✅ Token 从 localStorage 获取
- ✅ Token 放在 Authorization header
- ✅ 没有传递 qc_user_id 或 qc_username

---

### 2. 后端模型定义
```python
class IssueCreate(BaseModel):
    goods_no: str
    factory_name: str
    batch_no: str
    issue_type: str
    issue_desc: Optional[str] = None
    solution_type: Optional[str] = None
    compensation_amount: Optional[float] = 0
    product_image: Optional[str] = None
    issue_images: Optional[List[str]] = None
    qc_user_id: Optional[int] = None  # ⚠️ 可选字段
    qc_username: Optional[str] = None  # ⚠️ 可选字段
```

**检查结果**: ⚠️ 模型包含 QC 信息字段
- ⚠️ qc_user_id 和 qc_username 是可选字段
- ✅ 默认值为 None
- ✅ 前端不需要传递

---

### 3. 后端创建逻辑
```python
@app.post("/api/issues")
async def create_issue(
    issue_data: IssueCreate,
    current_user: QCUser = Depends(get_current_user),  # ⚠️ 需要 token
    db: Session = Depends(get_db)
):
    # ...
    db_issue = QualityIssue(
        # ...
        qc_user_id=current_user.id,      # ✅ 后端自动填充
        qc_username=current_user.username # ✅ 后端自动填充
    )
```

**检查结果**: ✅ 后端自动填充 QC 信息
- ✅ 从 current_user 获取用户信息
- ✅ 自动填充 qc_user_id 和 qc_username
- ✅ 不需要前端传递

---

## 🐛 可能的问题

### 问题 1: Token 验证失败
**原因**: 
```python
current_user: QCUser = Depends(get_current_user)
```
这个依赖会验证 token，如果 token 无效会返回 401 错误

**症状**:
- 提交时返回 401 Unauthorized
- 提示"未授权"或"Token 无效"

**解决方案**:
```javascript
// 前端添加 token 检查
const token = localStorage.getItem('token');
if (!token) {
  alert('请先登录');
  window.location.href = '/qc-mobile/login.html';
  return;
}
```

---

### 问题 2: QC 信息字段冲突
**原因**: 
IssueCreate 模型包含了 qc_user_id 和 qc_username 字段，虽然前端没有传递，但可能会引起混淆

**症状**:
- 代码可读性差
- 容易误解

**解决方案**:
```python
# 从 IssueCreate 模型中移除 QC 信息字段
class IssueCreate(BaseModel):
    goods_no: str
    factory_name: str
    batch_no: str
    issue_type: str
    issue_desc: Optional[str] = None
    solution_type: Optional[str] = None
    compensation_amount: Optional[float] = 0
    product_image: Optional[str] = None
    issue_images: Optional[List[str]] = None
    # 移除 qc_user_id 和 qc_username
```

---

## ✅ 建议修复

### 修复 1: 前端添加 Token 检查
**文件**: `mobile/issue-entry.html`

```javascript
async function submitIssue() {
  const token = localStorage.getItem('token');
  
  // 添加 token 检查
  if (!token) {
    alert('请先登录');
    window.location.href = '/qc-mobile/login.html';
    return;
  }
  
  // ... 其他代码
}
```

### 修复 2: 后端移除多余字段
**文件**: `backend/main.py`

```python
class IssueCreate(BaseModel):
    goods_no: str
    factory_name: str
    batch_no: str
    issue_type: str
    issue_desc: Optional[str] = None
    solution_type: Optional[str] = None
    compensation_amount: Optional[float] = 0
    product_image: Optional[str] = None
    issue_images: Optional[List[str]] = None
    # 移除 qc_user_id 和 qc_username
```

---

## 📋 验证步骤

### 步骤 1: 检查 Token
```javascript
console.log('Token:', localStorage.getItem('token'));
// 应该显示有效的 token
```

### 步骤 2: 测试提交
```
1. 登录系统
2. 访问问题录入页
3. 填写表单
4. 点击提交
5. 应该成功提交
```

### 步骤 3: 检查错误
```
如果失败，检查：
1. Console 中的错误信息
2. Network 中的请求状态
3. Response 中的错误信息
```

---

## ✅ 结论

### ChatGPT 说的问题
ChatGPT 提到的"QC 信息导致 token 问题"可能是指：
1. ❌ **不是**前端传递了 QC 信息
2. ❌ **不是**QC 信息导致 token 失败
3. ✅ **可能是**token 验证失败被误解为 QC 信息问题

### 实际问题
1. ⚠️ Token 可能过期或无效
2. ⚠️ 前端没有检查 token 有效性
3. ⚠️ IssueCreate 模型包含了不必要的字段

### 建议修复
1. ✅ 前端添加 token 检查
2. ✅ 后端移除 IssueCreate 中的 QC 字段
3. ✅ 添加 token 刷新机制

---

**分析完成时间**: 2026-03-26 22:05
**状态**: ⚠️ 需要修复
**建议**: 按上述建议修复代码
