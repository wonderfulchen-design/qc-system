# Railway 部署配置

## 📦 服务架构

```
Railway
├── MySQL Database
└── FastAPI Backend (带 Nginx 静态文件服务)
```

---

## 🔧 Railway 环境变量配置

在 Railway 项目设置中添加以下环境变量：

### MySQL 配置
```env
DATABASE_URL=mysql+pymysql://qc_user:QcUser2025@mysql:3306/qc_system
MYSQL_ROOT_PASSWORD=QcSystem2025
MYSQL_PASSWORD=QcUser2025
MYSQL_DATABASE=qc_system
MYSQL_USER=qc_user
```

### JWT 配置
```env
JWT_SECRET_KEY=qc-system-super-secret-jwt-key-2025
ACCESS_TOKEN_EXPIRE_DAYS=1
```

### 七牛云配置
```env
QINIU_ACCESS_KEY=IapaWm5AODDduh4YR_MpLh4irSWwRobKZ0YfJVy5
QINIU_SECRET_KEY=CpNr64VnpSU8Hx_ESLGMOZxSCKoVyuHfmmutHh-I
QINIU_BUCKET=lswsampleimg
QINIU_DOMAIN=https://sample.yoursecret.ltd/
QINIU_PREFIX=qcImg/
```

### 企业微信配置
```env
WECHAT_CORP_ID=ww8a4a238a216465e8
WECHAT_AGENT_ID=1000002
WECHAT_SECRET=W16ZiYxOHX1Ja67UupOKc_xK9P12sPm4T6BM415xAtw
WECHAT_REDIRECT_URI=https://miqin.up.railway.app
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f5db137b-d14f-4e71-927c-e6f6d9b10ca7
```

### 上传配置
```env
UPLOAD_DIR=/app/uploads
```

---

## 🚀 Railway 部署步骤

### 1. 连接 GitHub 仓库
1. 登录 Railway
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择 `qc-system` 仓库

### 2. 添加 MySQL 服务
1. 点击 "New" → "Database" → "MySQL"
2. 等待 MySQL 部署完成
3. 复制 MySQL 连接信息

### 3. 配置后端服务
1. 在 `backend` 服务中添加环境变量（见上方）
2. 设置 `PORT=8000`
3. 设置启动命令：
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

### 4. 数据库迁移
连接 MySQL 执行：
```sql
-- 添加 merchandiser 字段
ALTER TABLE quality_issues 
ADD COLUMN merchandiser VARCHAR(32) COMMENT '订单跟单员' AFTER batch_no;

-- 验证
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'railway' 
  AND TABLE_NAME = 'quality_issues'
  AND COLUMN_NAME = 'merchandiser';
```

### 5. 生成域名
1. Railway 会自动生成域名：`miqin-production.up.railway.app`
3. 更新环境变量 `WECHAT_REDIRECT_URI` 为实际域名

---

## 📝 验证部署

### 1. 健康检查
```
https://miqin.up.railway.app/health
```

### 2. 访问前端
```
https://miqin.up.railway.app/qc-mobile/index.html
```

### 3. 测试功能
- ✅ 登录（admin / admin123）
- ✅ 波次号联想
- ✅ 图片上传（七牛云）
- ✅ 问题提交
- ✅ 企业微信推送

---

## 🔍 日志查看

在 Railway Dashboard 查看：
- Deployments 标签 → 查看部署日志
- Logs 标签 → 实时日志

---

## ⚠️ 注意事项

1. **域名更新**：Railway 会自动生成域名，需要更新环境变量中的 `WECHAT_REDIRECT_URI`
2. **数据库初始化**：首次部署需要执行数据库迁移脚本
3. **静态文件**：Nginx 配置需要调整，或使用 FastAPI 直接服务静态文件
4. **上传目录**：Railway 使用临时文件系统，建议配置持久化存储或使用七牛云

---

## 🎯 快速部署命令

```bash
# 本地测试
cd qc-system/docker
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 数据库迁移
docker exec qc-mysql mysql -uqc_user -pQcUser2025 qc_system < database/add_merchandiser_to_issues.sql
```

---

**部署地址**: https://miqin.up.railway.app
