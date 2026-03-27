# 🎉 QC System 启动成功！

## ✅ 服务状态

所有服务已正常运行：

| 服务 | 状态 | 端口 |
|------|------|------|
| **MySQL** | ✅ Running (healthy) | 3306 |
| **FastAPI Backend** | ✅ Running (healthy) | 8000 |
| **Nginx** | ✅ Running | 80, 443 |
| **Crawler** | ✅ Running | - |

## 🌐 访问地址

- **API 文档**: http://localhost:8000/docs
- **前端页面**: http://localhost
- **健康检查**: http://localhost:8000/health

## 🔑 登录信息

**默认管理员账号**：
- 用户名：`admin`
- 密码：`admin123`

## 📋 新增功能 - 波次管理 API

已实现的波次工厂商品编码关系 API：

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/batches/list` | GET | 分页查询 |
| `/api/batches` | POST | 创建/更新 |
| `/api/batches/{batch_no}` | PUT | 部分更新 |
| `/api/batches/{batch_no}` | DELETE | 删除 |
| `/api/batches/batch` | POST | 批量导入 |
| `/api/batches/search` | GET | 快速搜索 |

## 🚀 快速测试

使用 PowerShell 测试创建波次：

```powershell
# 1. 登录获取 token
$login = Invoke-RestMethod -Uri "http://localhost:8000/token" -Method Post -Body "username=admin&password=admin123"
$token = $login.access_token
$headers = @{ Authorization = "Bearer $token" }

# 2. 创建波次关系
Invoke-RestMethod -Uri "http://localhost:8000/api/batches" -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"batch_no":"TEST001","factory_name":"广州制衣厂","goods_no":"SKU123456"}'

# 3. 查询列表
Invoke-RestMethod -Uri "http://localhost:8000/api/batches/list" -Headers $headers
```

## 📖 管理命令

```bash
# 查看服务状态
cd qc-system\docker
docker-compose ps

# 查看日志
docker-compose logs -f api

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 完全重置（删除所有数据）
docker-compose down -v
```

## 📁 重要文件

- `START_GUIDE.md` - 完整启动指南
- `BATCH_API_GUIDE.md` - 波次 API 使用文档
- `test_batch_api.py` - API 测试脚本
- `simple_test.py` - 简单测试脚本

## ⚠️ 注意事项

1. **首次启动**：数据库会自动初始化，包含 admin 账号
2. **数据持久化**：数据存储在 Docker volumes 中，重启不会丢失
3. **端口占用**：如果 80/3306/8000 端口被占用，修改 `docker/.env` 文件

## 🎯 下一步

1. 访问 http://localhost:8000/docs 查看完整 API 文档
2. 测试新增的波次管理功能
3. 配置前端页面（如果需要）

---

**需要帮助？** 查看 `qc-system/docs/` 或运行 `docker-compose logs -f`
