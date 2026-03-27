# 波次工厂商品编码关系 - 实时更新 API 使用指南

## 概述

QC 系统现已支持波次号 (batch_no)、工厂名称 (factory_name)、商品编码 (goods_no) 关系的实时增删改查。

## API 端点

### 1. 分页查询列表
```
GET /api/batches/list
```

**查询参数：**
- `page` (可选，默认 1): 页码
- `page_size` (可选，默认 20): 每页数量
- `batch_no` (可选): 波次号模糊搜索
- `factory_name` (可选): 工厂名称模糊搜索
- `goods_no` (可选): 商品编码模糊搜索

**响应示例：**
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "data": [
    {
      "batch_no": "B20260327001",
      "factory_name": "广州制衣厂",
      "goods_no": "SKU123456"
    }
  ]
}
```

---

### 2. 创建或更新单个波次关系
```
POST /api/batches
```

**请求体：**
```json
{
  "batch_no": "B20260327001",
  "factory_name": "广州制衣厂",
  "goods_no": "SKU123456"
}
```

**说明：**
- 波次号唯一，如果已存在则更新，否则创建
- 需要认证 token

**响应示例：**
```json
{
  "batch_no": "B20260327001",
  "factory_name": "广州制衣厂",
  "goods_no": "SKU123456"
}
```

---

### 3. 部分更新波次关系
```
PUT /api/batches/{batch_no}
```

**请求体（可选字段）：**
```json
{
  "factory_name": "新的工厂名称",
  "goods_no": "新的商品编码"
}
```

**说明：**
- 只更新提供的字段
- 波次号不能修改

**响应示例：**
```json
{
  "batch_no": "B20260327001",
  "factory_name": "新的工厂名称",
  "goods_no": "SKU123456"
}
```

---

### 4. 删除波次关系
```
DELETE /api/batches/{batch_no}
```

**响应示例：**
```json
{
  "message": "Batch deleted successfully",
  "batch_no": "B20260327001"
}
```

---

### 5. 批量导入/更新
```
POST /api/batches/batch
```

**请求体：**
```json
[
  {
    "batch_no": "B20260327001",
    "factory_name": "广州制衣厂",
    "goods_no": "SKU123456"
  },
  {
    "batch_no": "B20260327002",
    "factory_name": "深圳制衣厂",
    "goods_no": "SKU123457"
  }
]
```

**响应示例：**
```json
{
  "message": "Batch import completed",
  "success_count": 2,
  "error_count": 0,
  "errors": []
}
```

---

### 6. 快速查询（已有接口）
```
GET /api/batches/search?batch_no=xxx&goods_no=xxx
GET /api/batches/{batch_no}
```

---

## 认证方式

所有接口需要 JWT Token 认证，在请求头中添加：
```
Authorization: Bearer <your_token>
```

获取 Token：
```
POST /token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

---

## 使用示例 (Python)

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 登录获取 token
login_response = requests.post(f"{BASE_URL}/token", data={
    "username": "admin",
    "password": "your_password"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 创建波次关系
create_response = requests.post(f"{BASE_URL}/api/batches", json={
    "batch_no": "B20260327001",
    "factory_name": "广州制衣厂",
    "goods_no": "SKU123456"
}, headers=headers)
print(create_response.json())

# 3. 批量导入
batch_data = [
    {"batch_no": "B20260327001", "factory_name": "广州制衣厂", "goods_no": "SKU123456"},
    {"batch_no": "B20260327002", "factory_name": "深圳制衣厂", "goods_no": "SKU123457"},
]
batch_response = requests.post(f"{BASE_URL}/api/batches/batch", json=batch_data, headers=headers)
print(batch_response.json())

# 4. 分页查询
list_response = requests.get(f"{BASE_URL}/api/batches/list", params={
    "page": 1,
    "page_size": 20,
    "factory_name": "广州"
}, headers=headers)
print(list_response.json())

# 5. 更新
update_response = requests.put(f"{BASE_URL}/api/batches/B20260327001", json={
    "factory_name": "新的工厂名称"
}, headers=headers)
print(update_response.json())

# 6. 删除
delete_response = requests.delete(f"{BASE_URL}/api/batches/B20260327001", headers=headers)
print(delete_response.json())
```

---

## 数据库表结构

```sql
CREATE TABLE `product_batches` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `batch_no` VARCHAR(32) NOT NULL COMMENT '波次号',
  `factory_name` VARCHAR(64) DEFAULT NULL COMMENT '工厂名称',
  `goods_no` VARCHAR(32) DEFAULT NULL COMMENT '商品编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_batch_no` (`batch_no`),
  KEY `idx_factory` (`factory_name`),
  KEY `idx_goods` (`goods_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='波次工厂商品编码关系表';
```

---

## 注意事项

1. **波次号唯一**: `batch_no` 是唯一键，不能重复
2. **实时生效**: 所有修改立即生效，无需重启服务
3. **权限控制**: 所有接口需要登录认证
4. **批量导入**: 建议单次不超过 1000 条，超大批量请分批处理
5. **错误处理**: 批量导入会返回成功/失败计数和详细错误信息

---

## 重启后端服务

修改代码后，重启后端服务：

```bash
# 如果使用 Docker
docker-compose restart backend

# 如果直接运行
cd qc-system/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
