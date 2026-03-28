# QC 系统部署到阿里云 ECS（Windows 版）

## 📋 准备工作

### 1. 下载工具

#### 方式 1：使用 PowerShell（推荐，Win10/11 自带）
- 按 `Win + X` → 选择 **Windows PowerShell** 或 **终端**

#### 方式 2：下载 PuTTY
- 下载地址：https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
- 下载 `putty.exe` 即可

### 2. 获取服务器信息

- **服务器 IP**：`121.196.166.162`
- **用户名**：`root`
- **密码**：（在阿里云控制台重置或查看）

---

## 🚀 部署步骤

### 步骤 1：连接服务器

#### 使用 PowerShell：
```powershell
ssh root@121.196.166.162
```
输入密码（输入时不显示），按回车

#### 使用 PuTTY：
1. 打开 `putty.exe`
2. **Host Name**: `121.196.166.162`
3. **Port**: `22`
4. 点击 **Open**
5. 输入用户名：`root`
6. 输入密码

---

### 步骤 2：安装 Docker（首次部署）

```bash
# 使用阿里云镜像源安装 Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 启动 Docker
systemctl start docker

# 设置开机自启
systemctl enable docker

# 验证安装
docker --version
docker-compose --version
```

---

### 步骤 3：上传代码

#### 方式 1：使用 Git（推荐）
```bash
# 克隆代码
cd /root
git clone https://github.com/wonderfulchen-design/qc-system.git

# 进入部署目录
cd qc-system/docker
```

#### 方式 2：使用 FTP 上传
1. 下载 FileZilla：https://filezilla-project.org/
2. 连接服务器（IP: 121.196.166.162, 用户：root）
3. 上传整个 `qc-system` 文件夹到 `/root/`

---

### 步骤 4：配置环境变量

```bash
# 编辑配置文件
cd /root/qc-system/docker
vi .env
```

按 `i` 进入编辑模式，修改以下内容：

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

按 `ESC`，输入 `:wq` 保存退出

---

### 步骤 5：启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

---

### 步骤 6：配置阿里云安全组

1. 登录阿里云控制台：https://console.aliyun.com/
2. 进入 **云服务器 ECS**
3. 找到你的实例（杭州）
4. 点击 **安全组** → **配置规则**
5. 点击 **手动添加**
6. 添加以下规则：

| 优先级 | 协议 | 端口 | 授权对象 | 描述 |
|--------|------|------|----------|------|
| 1 | TCP | 80 | 0.0.0.0/0 | HTTP |
| 2 | TCP | 443 | 0.0.0.0/0 | HTTPS（可选） |
| 3 | TCP | 22 | 0.0.0.0/0 | SSH |
| 4 | TCP | 8000 | 0.0.0.0/0 | API（可选） |

7. 点击 **保存**

---

### 步骤 7：访问测试

浏览器访问：
```
http://121.196.166.162/qc-mobile/index.html
```

**登录信息**：
- 用户名：`admin`
- 密码：`admin123`

---

## 🔧 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f api

# 查看数据库日志
docker-compose logs -f mysql

# 查看 Nginx 日志
docker-compose logs -f nginx
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart api
```

### 更新代码
```bash
# 进入项目目录
cd /root/qc-system

# 拉取最新代码
git pull

# 重新构建并启动
docker-compose down
docker-compose build api
docker-compose up -d
```

### 数据库备份
```bash
# 备份数据库
docker exec qc-mysql mysqldump -uroot -pQcSystem2025 qc_system > /root/backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i qc-mysql mysql -uroot -pQcSystem2025 qc_system < /root/backup_20260329.sql
```

---

## ⚠️ 常见问题

### 1. Docker 安装失败
```bash
# 手动安装
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install docker-ce docker-ce-cli containerd.io
```

### 2. 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :80

# 停止占用端口的服务
systemctl stop nginx
```

### 3. 无法访问
- 检查安全组规则是否添加
- 检查防火墙状态：`systemctl status firewalld`
- 关闭防火墙：`systemctl stop firewalld`

### 4. 数据库连接失败
```bash
# 查看数据库日志
docker-compose logs mysql

# 重启数据库
docker-compose restart mysql
```

---

## 📊 性能监控

### 查看服务器资源
```bash
# CPU 和内存
top

# 磁盘空间
df -h

# Docker 资源占用
docker stats
```

### 设置监控（可选）
```bash
# 安装宝塔面板（可视化管理）
curl -o setup.sh http://download.bt.cn/install/install_6.0.sh && sh setup.sh
```

---

## 🎉 部署完成！

现在你的 QC 系统已经运行在阿里云 ECS 上了！

**访问地址**：
```
http://121.196.166.162/qc-mobile/index.html
```

**优势**：
- ✅ 8 核 16G 强大性能
- ✅ 国内访问速度快
- ✅ 24 小时稳定运行
- ✅ 无需额外费用

---

## 📞 需要帮助？

如果遇到任何问题，请提供：
1. 错误截图
2. 执行的命令
3. 日志内容

我会帮你解决！🔧
