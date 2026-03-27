# 后端 JSON 解析问题分析报告

## 📅 分析时间
2026-03-26 22:14

---

## 🔍 问题分析

### 用户反馈
ChatGPT 提示：后端错误导致 JSON 无法解析

---

## 🔧 代码检查

### 1. IssueResponse 模型
```python
class IssueResponse(BaseModel):
    id: int
    issue_no: str
    goods_no: Optional[str]
    factory_name: Optional[str]
    issue_type: str
    issue_desc: Optional[str]
    solution_type: Optional[str]
    compensation_amount: Optional[float]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True  # ✅ 正确配置
```

**检查结果**: ✅ 模型定义正确

---

### 2. create_issue 返回
```python
@app.post("/api/issues", response_model=IssueResponse)
async def create_issue(...):
    db_issue = QualityIssue(...)
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    
    return db_issue  # ✅ 返回 ORM 对象
```

**检查结果**: ✅ 返回正确

---

### 3. 可能的问题

#### 问题 1: datetime 序列化
**原因**: 
```python
created_at: Optional[datetime]
```
datetime 对象可能需要特殊处理

**症状**:
- JSON 序列化失败
- 返回 500 错误

**解决方案**:
```python
class IssueResponse(BaseModel):
    # ...
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
```

---

#### 问题 2: QC 字段移除
**当前 IssueCreate 模型**:
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
    # QC 信息由后端自动填充，不需要前端传递
```

**检查结果**: ✅ 已修复

---

## ✅ 建议修复

### 修复 1: 添加 datetime 编码器
**文件**: `backend/main.py`

```python
from pydantic import BaseModel
from datetime import datetime

class IssueResponse(BaseModel):
    id: int
    issue_no: str
    goods_no: Optional[str]
    factory_name: Optional[str]
    issue_type: str
    issue_desc: Optional[str]
    solution_type: Optional[str]
    compensation_amount: Optional[float]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
```

### 修复 2: 添加错误处理
**文件**: `backend/main.py`

```python
@app.post("/api/issues", response_model=IssueResponse)
async def create_issue(...):
    try:
        db_issue = QualityIssue(...)
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
        return db_issue
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📋 验证步骤

### 步骤 1: 测试 API
```bash
curl -X POST http://localhost:8000/api/issues \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "goods_no": "23181802105",
    "factory_name": "三米",
    "batch_no": "F21139",
    "issue_type": "污渍",
    "issue_desc": "测试描述",
    "solution_type": "返工"
  }'
```

### 步骤 2: 检查响应
```
应该返回 JSON:
{
  "id": 123,
  "issue_no": "Q20260326...",
  "goods_no": "23181802105",
  ...
}
```

### 步骤 3: 检查错误
```
如果失败，检查：
1. 后端日志
2. 返回的 status code
3. 返回的 error detail
```

---

## ✅ 结论

### 当前状态
1. ✅ IssueCreate 模型已修复（移除 QC 字段）
2. ✅ IssueResponse 模型正确
3. ⚠️ 可能需要添加 datetime 编码器
4. ⚠️ 可能需要添加错误处理

### 建议修复
1. ✅ 前端添加 token 检查（已完成）
2. ✅ 后端移除 QC 字段（已完成）
3. ⚠️ 添加 datetime 编码器（建议）
4. ⚠️ 添加错误处理（建议）

---

**分析完成时间**: 2026-03-26 22:14
**状态**: ⚠️ 建议优化
**建议**: 按上述建议添加编码器和错误处理
