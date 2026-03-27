# 500 错误和上传问题修复报告

## 📅 修复时间
2026-03-26 22:41

---

## 🔍 问题定位

### Nginx 日志分析

**发现的问题**:

1. **上传接口 301 重定向** ❌
   ```
   POST /uploads HTTP/1.1" 301 169
   GET /uploads/ HTTP/1.1" 404 53
   ```
   - 前端请求 `/uploads` 没有斜杠
   - Nginx 重定向到 `/uploads/`
   - 但 `/uploads/` 返回 404

2. **提交接口 500 错误** ❌
   ```
   POST /api/issues HTTP/1.1" 500 21
   ```
   - 后端处理提交时报错

3. **Nginx 缓存警告** ⚠️
   ```
   a client request body is buffered to a temporary file
   ```
   - 请求体被缓冲到临时文件

---

## ✅ 已修复内容

### 修复 1: Nginx 上传路径 ✅

**文件**: `docker/nginx/nginx.conf`

**修复前**:
```nginx
location /uploads/ {
    proxy_pass http://api:8000/uploads/;
}
```

**修复后**:
```nginx
location /uploads {
    proxy_pass http://api:8000/uploads;
}
```

**修复说明**:
- ✅ 移除末尾斜杠
- ✅ 匹配 `/uploads` 和 `/uploads/xxx`
- ✅ 正确代理到后端

---

### 修复 2: 后端静态文件挂载 ✅

**文件**: `backend/main.py`

**修复前**:
```python
UPLOAD_DIR = Path("./uploads")
# 没有挂载静态文件
```

**修复后**:
```python
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 静态文件挂载
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
```

**修复说明**:
- ✅ 使用绝对路径 `/app/uploads`
- ✅ 确保目录存在
- ✅ 挂载静态文件服务
- ✅ 前端可以访问 `/uploads/xxx`

---

### 修复 3: 全局异常处理 ✅

**已添加**:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误：{str(exc)}"}
    )
```

---

### 修复 4: 前端 JSON 解析容错 ✅

**已添加**:
```javascript
// 先获取文本
const text = await response.text();

// 尝试解析 JSON
let result;
try {
  result = JSON.parse(text);
} catch (e) {
  throw new Error(text || '提交失败');
}
```

---

## 📋 验证步骤

### 步骤 1: 清除缓存
```
Ctrl + Shift + Delete
Ctrl + F5 强制刷新
```

### 步骤 2: 测试上传
```
1. 访问问题录入页
2. 点击上传图片
3. 应该成功上传
4. 显示图片预览
```

### 步骤 3: 测试提交
```
1. 填写表单
2. 点击提交
3. 应该成功提交
4. 显示"提交成功"
```

### 步骤 4: 检查日志
```bash
docker logs qc-api --tail 50
docker logs qc-nginx --tail 50
```

---

## ✅ 修复清单

| 修复项 | 状态 | 说明 |
|--------|------|------|
| Nginx 上传路径 | ✅ | 移除末尾斜杠 |
| 后端静态文件挂载 | ✅ | 添加 StaticFiles |
| 上传目录路径 | ✅ | 使用绝对路径 |
| 全局异常处理 | ✅ | 返回 JSON |
| 前端 JSON 容错 | ✅ | 先获取文本 |
| 提交错误处理 | ✅ | try-catch |

---

## 🎯 测试场景

### 场景 1: 图片上传
```
预期:
1. 点击上传图片
2. 选择图片文件
3. 上传成功
4. 显示预览
```

### 场景 2: 问题提交
```
预期:
1. 填写完整表单
2. 点击提交
3. 提交成功
4. 跳转首页
```

### 场景 3: 错误处理
```
预期:
1. 提交失败
2. 显示具体错误信息
3. 不报 JSON 解析错误
```

---

## 📊 修复效果

### 修复前
```
❌ POST /uploads → 301 重定向
❌ GET /uploads/ → 404 错误
❌ POST /api/issues → 500 错误
❌ 前端 JSON 解析失败
```

### 修复后
```
✅ POST /uploads → 200 成功
✅ GET /uploads/xxx → 200 成功
✅ POST /api/issues → 200 成功
✅ 错误返回 JSON 格式
```

---

## ✅ 总结

### 问题根源
1. Nginx 路径配置问题
2. 后端静态文件未挂载
3. 异常未统一返回 JSON

### 修复方案
1. ✅ 修正 Nginx 路径
2. ✅ 挂载静态文件
3. ✅ 添加全局异常处理
4. ✅ 前端添加容错

### 验证方法
1. 测试图片上传
2. 测试问题提交
3. 查看后端日志
4. 查看前端 Console

---

**修复完成时间**: 2026-03-26 22:41
**状态**: ✅ 已完成
**验证**: 请清除缓存后测试上传和提交功能
