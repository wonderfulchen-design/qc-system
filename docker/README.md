# Docker 部署指南

## 📦 项目结构

```
qc-system/
├── docker/
│   ├── Dockerfile              # API 服务镜像
│   ├── docker-compose.yml      # Docker Compose 配置
│   ├── .env.example            # 环境变量示例
│   ├── nginx/
│   │   └── nginx.conf          # Nginx 配置
│   └── ssl/                    # SSL 证书目录 (生产环境)
├── backend/
│   └── main.py                 # FastAPI 后端
├── mobile/
│   └── login.html              # 移动端登录页
├── database/
│   └── init_with_admin.sql     # 数据库初始化 (含管理员)
└── crawler.py                  # 数据爬虫
```

---

## 🚀 快速部署

### 1. 准备环境

```bash
# 安装 Docker 和 Docker Compose
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# 安装 Docker Compose 插件
apt install docker-compose-plugin
```

### 2. 配置环境变量

```bash
cd qc-system/docker

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，修改密码和密钥
nano .env
```

**重要：生产环境必须修改！**
- `JWT_SECRET_KEY` - 生成随机字符串
- `MYSQL_ROOT_PASSWORD` - MySQL root 密码
- `MYSQL_PASSWORD` - 数据库用户密码

### 3. 启动服务

```bash
# 构建并启动所有服务
docker compose up -d --build

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f api
docker compose logs -f mysql
```

### 4. 验证部署

```bash
# 访问 API 文档
http://localhost/docs

# 访问移动端登录页
http://localhost/qc-mobile/login.html

# 健康检查
curl http://localhost/health
```

---

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker compose up -d

# 停止所有服务
docker compose down

# 重启服务
docker compose restart

# 重启单个服务
docker compose restart api

# 查看日志
docker compose logs -f
docker compose logs -f api
docker compose logs -f mysql

# 查看实时日志 (带时间戳)
docker compose logs -f --tail=100
```

### 数据库操作

```bash
# 进入 MySQL 容器
docker exec -it qc-mysql mysql -u root -p

# 备份数据库
docker exec qc-mysql mysqldump -u root -pQcSystem2025!@# qc_system > backup.sql

# 恢复数据库
docker exec -i qc-mysql mysql -u root -pQcSystem2025!@# qc_system < backup.sql

# 查看数据库大小
docker exec qc-mysql mysql -u root -pQcSystem2025!@# -e "SELECT table_schema, SUM(data_length + index_length) / 1024 / 1024 AS 'Size (MB)' FROM information_schema.tables WHERE table_schema = 'qc_system' GROUP BY table_schema;"
```

### 应用管理

```bash
# 进入 API 容器
docker exec -it qc-api bash

# 运行爬虫
docker exec qc-api python crawler.py

# 运行数据分析
docker exec qc-api python analyzer.py

# 查看上传文件
docker exec qc-api ls -la /app/uploads

# 查看应用日志
docker exec qc-api cat /app/logs/app.log
```

---

## 🔐 默认账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | admin | 系统管理员 |
| qc_manager | admin123 | manager | 质检经理 |
| qc_user | admin123 | qc | 质检员 |

**⚠️ 首次登录后请立即修改密码！**

---

## 📱 移动端访问

### 局域网访问

```
http://<服务器 IP>/qc-mobile/login.html
```

### 企业微信配置

1. 登录企业微信管理后台
2. 应用管理 → 自建应用 → 创建应用
3. 配置应用主页：`http://<服务器 IP>/qc-mobile/`
4. 获取 AgentId 和 Secret
5. 修改 `.env` 文件配置企业微信参数
6. 重新部署：`docker compose up -d`

---

## 🔒 HTTPS 配置 (生产环境)

### 1. 申请 SSL 证书

```bash
# 使用 Let's Encrypt (免费)
apt install certbot
certbot certonly --standalone -d your-domain.com
```

### 2. 配置证书

```bash
# 复制证书到 nginx/ssl 目录
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/
```

### 3. 启用 HTTPS

编辑 `nginx/nginx.conf`，取消 HTTPS server 块注释

### 4. 重启 Nginx

```bash
docker compose restart nginx
```

---

## 📊 数据爬取

### 手动爬取

```bash
# 执行一次爬取
docker exec qc-api python crawler.py

# 查看爬取日志
docker compose logs -f crawler
```

### 自动爬取

Crawler 服务已配置为每天凌晨 2 点自动运行

修改爬取频率：编辑 `docker-compose.yml` 中的 `sleep 86400` (秒)

---

## 🛠️ 故障排查

### API 无法启动

```bash
# 查看 API 日志
docker compose logs api

# 检查数据库连接
docker exec qc-api curl -v http://mysql:3306

# 进入容器调试
docker exec -it qc-api bash
```

### 数据库连接失败

```bash
# 检查 MySQL 状态
docker compose ps mysql

# 查看 MySQL 日志
docker compose logs mysql

# 重启 MySQL
docker compose restart mysql
```

### 端口冲突

```bash
# 查看端口占用
netstat -tlnp | grep :8000
netstat -tlnp | grep :3306

# 修改 .env 中的端口配置
API_PORT=8001
MYSQL_PORT=33060
```

---

## 📈 性能优化

### 1. 增加数据库连接池

编辑 `backend/main.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600
)
```

### 2. 启用 Redis 缓存

```yaml
# docker-compose.yml 添加 Redis 服务
redis:
  image: redis:7-alpine
  container_name: qc-redis
  restart: always
  volumes:
    - redis_data:/data
```

### 3. 图片存储优化

使用对象存储 (阿里云 OSS/MinIO) 替代本地存储

---

## 💾 数据备份

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/qc-system"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker exec qc-mysql mysqldump -u root -pQcSystem2025!@# qc_system > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
docker run --rm -v qc-system_uploads_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/uploads_$DATE.tar.gz /data

# 删除 30 天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 定时备份

```bash
# 添加到 crontab
0 3 * * * /path/to/backup.sh
```

---

## 🎯 生产环境检查清单

- [ ] 修改所有默认密码
- [ ] 配置 HTTPS
- [ ] 配置防火墙 (仅开放 80/443)
- [ ] 设置日志轮转
- [ ] 配置监控告警
- [ ] 设置自动备份
- [ ] 压力测试
- [ ] 安全扫描

---

**部署完成！开始使用 QC 质量管理系统吧！** 🎉
