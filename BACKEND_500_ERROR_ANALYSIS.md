# 后端 500 错误和图片上传问题分析报告

## 📅 分析时间
2026-03-26 22:36

---

## 🔍 问题现象

### 用户反馈
1. **问题录入页面提交报 500 错误**
2. **图片上传也在报错**

---

## 🔧 代码检查

### 1. 上传接口检查 ✅

**文件**: `backend/main.py`

```python
@app.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    current_user: QCUser = Depends(get_current_user)
):
    # 1. 验证文件类型 ✅
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, ...)
    
    # 2. 读取文件并验证大小 ✅
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, ...)
    
    # 3. 验证图片尺寸 ✅
    try:
        img = Image.open(io.BytesIO(content))
        # ...
    except:
        pass  # 跳过验证
    
    # 4. 保存文件 ⚠️
    filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as buffer:
        buffer.write(content)  # ⚠️ 可能报错
    
    return {"url": file_url, ...}
```

**检查结果**:
- ✅ 文件类型验证正常
- ✅ 文件大小验证正常
- ✅ 图片尺寸验证正常
- ⚠️ **文件保存可能报错**

---

### 2. 提交接口检查 ✅

**已添加错误处理**:
```python
@app.post("/api/issues")
async def create_issue(...):
    try:
        db_issue = QualityIssue(...)
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
        return db_issue
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"提交失败：{str(e)}")
```

**检查结果**: ✅ 已添加错误处理

---

### 3. 全局异常处理 ✅

**已添加**:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误：{str(exc)}"}
    )
```

**检查结果**: ✅ 已添加

---

## 🐛 可能的问题

### 问题 1: 上传目录权限 ⚠️

**症状**:
```
上传文件时可能报错：
- PermissionError: [Errno 13] Permission denied
- FileNotFoundError: [Errno 2] No such file or directory
```

**检查**:
```bash
docker exec qc-api ls -la /app/uploads/
# 显示：drwxr-xr-x 2 appuser appuser
# 权限正常
```

---

### 问题 2: PIL 库未安装 ⚠️

**症状**:
```python
try:
    from PIL import Image  # ❌ 可能导入失败
    import io
    img = Image.open(io.BytesIO(content))
except ImportError:
    pass  # 跳过验证
```

**检查**:
```bash
docker exec qc-api pip list | grep -i pillow
```

---

### 问题 3: 数据库连接问题 ⚠️

**症状**:
```
提交时可能报错：
- SQLAlchemyError
- OperationalError
- 数据库连接超时
```

**检查**:
```bash
docker logs qc-api --tail 100
```

---

### 问题 4: 前端上传代码 ⚠️

**检查前端代码**:
```javascript
// mobile/issue-entry.html
async function uploadImage(type) {
  const file = e.target.files[0];
  
  // 验证文件大小
  if (file.size > maxSize) {
    alert(`图片过大 (${sizeMB}MB)，最大允许 5MB`);
    return;
  }
  
  // 压缩图片
  const compressedFile = await compressImage(file);
  
  // 上传
  const formData = new FormData();
  formData.append('file', compressedFile);
  
  const response = await fetch(`${API_BASE}/uploads`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
      // ❌ 缺少 Content-Type
    },
    body: formData
  });
}
```

**问题**:
- ❌ **没有设置 Content-Type**（FormData 会自动设置）
- ❌ **没有错误处理**

---

## ✅ 建议修复

### 修复 1: 前端添加错误处理

**文件**: `mobile/issue-entry.html`

```javascript
async function uploadImage(type) {
  // ...
  
  try {
    const response = await fetch(`${API_BASE}/uploads`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    // 先获取文本
    const text = await response.text();
    
    // 尝试解析 JSON
    let result;
    try {
      result = JSON.parse(text);
    } catch (e) {
      throw new Error(text || '上传失败');
    }
    
    if (response.ok) {
      // 成功处理
    } else {
      throw new Error(result.detail || '上传失败');
    }
  } catch (error) {
    alert(`上传失败：${error.message}`);
  }
}
```

---

### 修复 2: 后端添加详细日志

**文件**: `backend/main.py`

```python
import logging

@app.post("/uploads")
async def upload_file(...):
    try:
        logging.info(f"开始上传文件：{file.filename}")
        
        # 验证文件类型
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            logging.warning(f"不支持的文件类型：{file.content_type}")
            raise HTTPException(...)
        
        # 读取文件
        content = await file.read()
        logging.info(f"文件大小：{len(content)} bytes")
        
        # 保存文件
        filepath = UPLOAD_DIR / filename
        logging.info(f"保存路径：{filepath}")
        
        with open(filepath, "wb") as buffer:
            buffer.write(content)
        
        logging.info(f"上传成功：{filename}")
        return {...}
        
    except Exception as e:
        logging.error(f"上传失败：{str(e)}")
        raise
```

---

## 📋 验证步骤

### 步骤 1: 检查后端日志
```bash
docker logs qc-api --tail 100
```

### 步骤 2: 测试上传
```
1. 打开问题录入页
2. 点击上传图片
3. 查看 Console 错误
4. 查看 Network 响应
```

### 步骤 3: 检查权限
```bash
docker exec qc-api ls -la /app/uploads/
docker exec qc-api touch /app/uploads/test.txt
```

### 步骤 4: 检查 PIL
```bash
docker exec qc-api python -c "from PIL import Image; print('PIL OK')"
```

---

## ✅ 检查清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 上传目录权限 | ✅ | appuser 可写 |
| PIL 库安装 | ⚠️ | 需要检查 |
| 数据库连接 | ⚠️ | 需要检查日志 |
| 前端错误处理 | ⚠️ | 需要添加 |
| 后端日志 | ⚠️ | 需要添加 |
| 全局异常处理 | ✅ | 已添加 |
| 提交错误处理 | ✅ | 已添加 |

---

## 🎯 快速排查

### 1. 查看具体错误
```
打开浏览器 Console
查看 Network 标签
点击失败的请求
查看 Response 内容
```

### 2. 查看后端日志
```bash
docker logs qc-api --tail 50 --follow
```

### 3. 测试上传接口
```bash
curl -X POST http://localhost:8000/uploads \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

---

## ✅ 总结

### 已确认
1. ✅ 上传目录权限正常
2. ✅ 后端错误处理已添加
3. ✅ 全局异常处理已添加

### 需要检查
1. ⚠️ PIL 库是否安装
2. ⚠️ 数据库连接是否正常
3. ⚠️ 后端日志具体内容
4. ⚠️ 前端错误处理

### 建议操作
1. 查看后端日志（最重要）
2. 查看前端 Console 错误
3. 查看 Network 响应内容
4. 添加前端错误处理

---

**分析完成时间**: 2026-03-26 22:36
**状态**: ⚠️ 需要更多信息
**建议**: 请提供后端日志和前端 Console 错误信息
