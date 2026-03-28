# QC 系统部署到 Windows Server 2025

## 📋 系统要求

- **操作系统**：Windows Server 2025
- **内存**：至少 8GB（推荐 16GB）
- **磁盘**：至少 50GB 可用空间
- **CPU**：至少 4 核（推荐 8 核）

---

## 🚀 快速部署（3 步完成）

### 第 1 步：安装必要软件

#### 1.1 安装 Docker Desktop

1. **下载**：
   ```
   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
   ```

2. **运行安装程序**
   - 勾选 ✅ "Use WSL 2 instead of Hyper-V"
   - 点击 **Install**

3. **重启服务器**

#### 1.2 安装 Git

1. **下载**：
   ```
   https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe
   ```

2. **运行安装程序**
   - 全部使用默认选项

---

### 第 2 步：运行一键部署脚本

1. **下载部署脚本**（从 GitHub）：
   ```powershell
   cd C:\
   git clone https://github.com/wonderfulchen-design/qc-system.git
   cd qc-system
   ```

2. **以管理员身份运行脚本**：
   - 找到 `deploy-windows-server.bat`
   - **右键** → **以管理员身份运行**

3. **等待部署完成**

---

### 第 3 步：配置防火墙

**以管理员身份打开 PowerShell**：

```powershell
# 允许 HTTP
New-NetFirewallRule -DisplayName "QC HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# 允许 HTTPS
New-NetFirewallRule -DisplayName "QC HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow

# 允许 API
New-NetFirewallRule -DisplayName "QC API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

---

## ✅ 完成！

**访问地址**：
```
http://121.196.166.162/qc-mobile/index.html
```

**登录信息**：
- 用户名：`admin`
- 密码：`admin123`

---

## 🔧 手动部署（详细步骤）

### 步骤 1：创建部署目录

```powershell
mkdir C:\qc-system
cd C:\qc-system
```

### 步骤 2：克隆代码

```powershell
git clone https://github.com/wonderfulchen-design/qc-system.git
cd qc-system\docker
```

### 步骤 3：配置环境变量

用记事本编辑 `.env` 文件：

```powershell
notepad .env
```

修改内容：

```env
# MySQL 配置
MYSQL_ROOT_PASSWORD=QcSystem2025
MYSQL_PASSWORD=QcUser2025
MYSQL_PORT=3306
MYSQL_DATABASE=qc_system
MYSQL_USER=qc_user

# JWT 配置
JWT_SECRET_KEY=qc-system-super-secret-jwt-key-2025
ACCESS_TOKEN_EXPIRE_DAYS=1

# 七牛云配置
QINIU_ACCESS_KEY=IapaWm5AODDduh4YR_MpLh4irSWwRobKZ0YfJVy5
QINIU_SECRET_KEY=CpNr64VnpSU8Hx_ESLGMOZxSCKoVyuHfmmutHh-I
QINIU_BUCKET=lswsampleimg
QINIU_DOMAIN=https://sample.yoursecret.ltd/
QINIU_PREFIX=qcImg/

# 企业微信配置
WECHAT_CORP_ID=ww8a4a238a216465e8
WECHAT_AGENT_ID=1000002
WECHAT_SECRET=W16ZiYxOHX1Ja67UupOKc_xK9P12sPm4T6BM415xAtw
WECHAT_REDIRECT_URI=http://121.196.166.162
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f5db137b-d14f-4e71-927c-e6f6d9b10ca7

# 端口配置
API_PORT=8000
HTTP_PORT=80
HTTPS_PORT=443
```

保存并关闭（`Ctrl + S`，然后 `Alt + F4`）

### 步骤 4：启动服务

```powershell
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤 5：配置阿里云安全组

在阿里云控制台：
1. **云服务器 ECS** → 找到实例
2. **安全组** → **配置规则**
3. **添加规则**：
   - 端口：`80`，协议：`TCP`，授权对象：`0.0.0.0/0`
   - 端口：`443`，协议：`TCP`，授权对象：`0.0.0.0/0`
4. **保存**

---

## 📊 常用命令

### 查看服务状态
```powershell
docker-compose ps
```

### 查看日志
```powershell
# 查看所有服务
docker-compose logs -f

# 查看后端
docker-compose logs -f api

# 查看数据库
docker-compose logs -f mysql

# 查看 Nginx
docker-compose logs -f nginx
```

### 重启服务
```powershell
# 重启所有
docker-compose restart

# 重启单个
docker-compose restart api
```

### 停止服务
```powershell
docker-compose down
```

### 更新代码
```powershell
# 拉取最新代码
cd C:\qc-system\qc-system
git pull

# 重新构建
cd docker
docker-compose down
docker-compose build api
docker-compose up -d
```

---

## ⚠️ 常见问题

### 1. Docker 无法启动

**错误**：`Docker Desktop requires Hyper-V or WSL 2`

**解决**：
```powershell
# 启用 WSL 2
wsl --install

# 重启服务器
shutdown /r /t 0
```

### 2. 端口被占用

**错误**：`Bind for 0.0.0.0:80 failed: port is already allocated`

**解决**：
```powershell
# 查看端口占用
netstat -ano | findstr :80

# 停止占用端口的服务
# 或使用其他端口，修改 .env 文件
HTTP_PORT=8080
```

### 3. 防火墙阻止访问

**解决**：
```powershell
# 以管理员身份运行 PowerShell
# 添加防火墙规则
New-NetFirewallRule -DisplayName "QC HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
```

### 4. Docker 容器反复重启

**查看日志**：
```powershell
docker-compose logs api
```

**常见原因**：
- 数据库连接失败 → 检查 `.env` 中的数据库配置
- 端口冲突 → 修改端口
- 内存不足 → 增加服务器内存

### 5. 无法访问外网

**解决**：
```powershell
# 检查网络
ping www.baidu.com

# 配置 DNS
# 网络适配器 → 属性 → IPv4 → 使用以下 DNS
# 首选：8.8.8.8
# 备用：114.114.114.114
```

---

## 📈 性能优化

### 1. 增加 Docker 资源

1. 打开 **Docker Desktop**
2. 点击 **设置**（齿轮图标）
3. **Resources** → 调整：
   - CPUs: 4-6 核
   - Memory: 8-12 GB
   - Swap: 2 GB
4. 点击 **Apply & Restart**

### 2. 数据库优化

编辑 `docker-compose.yml`，增加 MySQL 内存限制：

```yaml
services:
  mysql:
    deploy:
      resources:
        limits:
          memory: 4G
```

### 3. 定期清理

```powershell
# 清理未使用的容器
docker container prune

# 清理未使用的镜像
docker image prune

# 清理未使用的卷
docker volume prune
```

---

## 💾 数据备份

### 备份数据库

```powershell
# 创建备份目录
mkdir C:\qc-system\backup

# 备份数据库
docker exec qc-mysql mysqldump -uroot -pQcSystem2025 qc_system > C:\qc-system\backup\qc_$(Get-Date -Format "yyyyMMdd").sql
```

### 恢复数据库

```powershell
docker exec -i qc-mysql mysql -uroot -pQcSystem2025 qc_system < C:\qc-system\backup\qc_20260329.sql
```

---

## 🎉 部署完成！

现在你的 QC 系统已经运行在 Windows Server 2025 上了！

**优势**：
- ✅ Windows 图形界面，管理方便
- ✅ 8 核 16G 强大性能
- ✅ 国内访问速度快
- ✅ 24 小时稳定运行
- ✅ 无需额外费用

**访问地址**：
```
http://121.196.166.162/qc-mobile/index.html
```

---

## 📞 需要帮助？

如果遇到任何问题，请提供：
1. 错误截图
2. 执行的命令
3. 日志内容

我会帮你解决！🔧
