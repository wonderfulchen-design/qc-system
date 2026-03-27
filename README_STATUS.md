# QC System 启动状态

## ✅ 已完成

1. **代码已实现** - 波次 CRUD API 已添加到 `backend/main.py`
2. **依赖已安装** - FastAPI, Uvicorn, SQLAlchemy 等
3. **配置文件** - `.env` 已创建
4. **启动脚本** - `start.bat` 已创建

## ⚠️ 需要的前置条件

### 选项 1：使用 Docker（推荐）
1. **启动 Docker Desktop**
   - 双击桌面上的 Docker Desktop 图标
   - 等待状态变为 "Docker is running"
   
2. **启动服务**
   ```bash
   cd qc-system\docker
   docker-compose up -d
   ```

### 选项 2：本地 MySQL
1. **安装 MySQL 8.0+**
2. **启动 MySQL 服务**
3. **初始化数据库**
   ```bash
   mysql -u root -p < qc-system/database/init_with_admin.sql
   ```

## 🚀 快速启动（如果已有 MySQL）

直接运行：
```bash
cd qc-system
start.bat
```

或手动启动：
```bash
cd qc-system\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 详细文档

查看 `qc-system/START_GUIDE.md` 获取完整启动指南。

## 🎯 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 🔗 访问地址

- API 文档：http://localhost:8000/docs
- 后端接口：http://localhost:8000
