# QC System 启动指南

## 方法一：使用 Docker（推荐）⭐

### 1. 启动 Docker Desktop
确保 Docker Desktop 已安装并运行：
- 打开 Docker Desktop 应用程序
- 等待状态显示为 "Docker is running"

### 2. 启动所有服务
```bash
cd C:\Users\Administrator\.openclaw\workspace\qc-system\docker
docker-compose up -d
```

### 3. 查看服务状态
```bash
docker-compose ps
```

### 4. 访问系统
- **API 文档**: http://localhost:8000/docs
- **前端页面**: http://localhost
- **MySQL**: localhost:3306

### 5. 停止服务
```bash
docker-compose down
```

### 6. 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f mysql
```

---

## 方法二：本地 Python 环境

### 前置条件
1. **MySQL 8.0+** 已安装并运行
2. **Python 3.8+** 已安装

### 1. 安装依赖
```bash
cd C:\Users\Administrator\.openclaw\workspace\qc-system\backend
pip install fastapi uvicorn sqlalchemy pymysql python-jose python-dotenv python-multipart pillow
```

### 2. 初始化数据库
```bash
# 使用 root 用户登录 MySQL
mysql -u root -p

# 执行初始化脚本
source C:\Users\Administrator\.openclaw\workspace\qc-system\database\init_with_admin.sql
```

或者使用 MySQL Workbench 执行 `init_with_admin.sql` 文件。

### 3. 配置环境变量
创建 `backend/.env` 文件：
```env
DATABASE_URL=mysql+pymysql://qc_user:QcUser2025@localhost:3306/qc_system
JWT_SECRET_KEY=qc-system-super-secret-jwt-key-2025
ACCESS_TOKEN_EXPIRE_DAYS=1
UPLOAD_DIR=./uploads
```

### 4. 创建上传目录
```bash
cd C:\Users\Administrator\.openclaw\workspace\qc-system\backend
mkdir uploads
```

### 5. 启动后端服务
```bash
cd C:\Users\Administrator\.openclaw\workspace\qc-system\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问 API 文档
打开浏览器访问：http://localhost:8000/docs

---

## 默认账号

**管理员账号**（初始化后）：
- 用户名：`admin`
- 密码：`admin123`

**普通用户**：
- 用户名：`qc_user`
- 密码：`qc123456`

---

## 常见问题

### Q: Docker 无法启动？
A: 
1. 确保 Docker Desktop 已启动
2. 检查 Windows 功能中是否启用了"容器"
3. 重启 Docker Desktop：`Docker Desktop > Settings > Restart`

### Q: MySQL 连接失败？
A:
1. 检查 MySQL 服务是否运行：`Get-Service MySQL*`
2. 检查端口是否被占用：`netstat -ano | findstr :3306`
3. 检查数据库用户权限

### Q: API 启动失败？
A:
1. 检查端口 8000 是否被占用
2. 查看错误日志
3. 确保 `.env` 文件配置正确

### Q: 如何重置数据库？
A:
```bash
# Docker 方式
docker-compose down -v  # 删除所有数据卷
docker-compose up -d    # 重新启动

# 本地方式
mysql -u root -p -e "DROP DATABASE qc_system; CREATE DATABASE qc_system;"
mysql -u root -p qc_system < database/init_with_admin.sql
```

---

## 服务架构

```
┌─────────────┐
│   Nginx     │ :80 (前端 + 反向代理)
│             │ :443 (HTTPS)
└──────┬──────┘
       │
       ├──────────────┐
       │              │
┌──────▼──────┐  ┌────▼────────┐
│  FastAPI    │  │   MySQL     │
│  Backend    │  │  Database   │
│  :8000      │  │  :3306      │
└─────────────┘  └─────────────┘
```

---

## 下一步

1. **测试 API**: 访问 http://localhost:8000/docs
2. **登录系统**: 使用 admin/admin123 登录
3. **配置前端**: 修改 `mobile/` 目录下的前端配置
4. **部署生产**: 参考 `docker/README.md`

---

**需要帮助？** 查看完整文档：`qc-system/docs/`
