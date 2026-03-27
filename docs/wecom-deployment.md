# 企业微信部署指南

## 📋 部署方案

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    企业微信移动端                         │
│  (H5 应用 / 小程序)                                      │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Nginx 反向代理                        │
│         SSL 证书 / 负载均衡 / 静态资源                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI 后端服务                      │
│     认证授权 / API 接口 / 数据校验 / 业务逻辑              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    MySQL 8.0 数据库                      │
│         业务数据 / 用户信息 / 考核统计                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 第一步：企业微信应用配置

### 1. 登录企业微信管理后台

访问：https://work.weixin.qq.com/

### 2. 创建自建应用

```
应用管理 → 应用 → 创建应用

- 应用名称：QC 质量管理系统
- 应用图标：上传 logo (建议 512x512)
- 可见范围：选择 QC 部门/相关人员
```

### 3. 获取应用凭证

```
进入应用 → 应用信息

- AgentId: 1000001 (示例)
- Secret: xxxxxxxxxxxxxxxxxxxx
- 企业 ID: wwxxxxxxxxxxxxxx
```

### 4. 配置应用主页

```
应用主页：https://your-domain.com/qc-mobile/

或

- 配置 H5 应用入口
- 配置小程序 (需额外开发)
```

### 5. 配置可信域名

```
应用管理 → 应用 → 可信域名

- 网页授权及 JS-SDK 域名：your-domain.com
- 上传校验文件到服务器根目录
```

---

## 🔐 第二步：后端服务部署

### 1. 服务器要求

| 配置 | 推荐 | 最低 |
|------|------|------|
| CPU | 4 核 | 2 核 |
| 内存 | 8GB | 4GB |
| 硬盘 | 100GB SSD | 50GB |
| 带宽 | 5Mbps | 2Mbps |

### 2. 安装依赖

```bash
# 系统环境 (Ubuntu 22.04 示例)
sudo apt update
sudo apt install -y python3.10 python3-pip mysql-server nginx git

# Python 虚拟环境
python3 -m venv /opt/qc-system/venv
source /opt/qc-system/venv/bin/activate

# 安装依赖
cd /opt/qc-system
pip install -r requirements.txt
```

### 3. 创建配置文件

```bash
# /opt/qc-system/.env
DB_HOST=localhost
DB_PORT=3306
DB_USER=qc_user
DB_PASSWORD=YourSecurePassword123!
DB_NAME=qc_system

# JWT 配置
JWT_SECRET_KEY=your-random-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 企业微信配置
CORP_ID=wwxxxxxxxxxxxxxx
AGENT_ID=1000001
AGENT_SECRET=xxxxxxxxxxxxxxxxxxxx

# 服务配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### 4. 数据库初始化

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE qc_system DEFAULT CHARSET=utf8mb4;
CREATE USER 'qc_user'@'localhost' IDENTIFIED BY 'YourSecurePassword123!';
GRANT ALL PRIVILEGES ON qc_system.* TO 'qc_user'@'localhost';
FLUSH PRIVILEGES;

# 导入表结构
use qc_system;
source /opt/qc-system/database/init.sql;
```

### 5. 创建后端服务

```bash
# 创建 main.py (FastAPI 入口)
cat > /opt/qc-system/main.py << 'EOF'
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import hashlib

app = FastAPI(title="QC 质量管理系统 API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1

# 认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 数据模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

class UserLogin(BaseModel):
    username: str
    password: str

class QCUser(BaseModel):
    id: int
    username: str
    real_name: str
    department: Optional[str]
    role: str

# 密码哈希
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# 创建 Token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API 路由
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    """
    # TODO: 从数据库验证用户
    # 这里是示例，实际需要从 qc_users 表查询
    user_id = 1  # 示例用户 ID
    username = form_data.username
    
    # 验证密码 (示例)
    # actual_password_hash = hash_password(form_data.password)
    # if actual_password_hash != stored_password_hash:
    #     raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_access_token(
        data={"sub": user_id, "username": username},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id,
        username=username
    )

@app.get("/api/user/me", response_model=QCUser)
async def get_current_user_info(current_user_id: int = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    # TODO: 从数据库查询用户信息
    return QCUser(
        id=current_user_id,
        username="demo",
        real_name="演示用户",
        department="质检部",
        role="qc"
    )

@app.get("/api/issues")
async def get_issues(
    page: int = 1,
    page_size: int = 20,
    factory: Optional[str] = None,
    issue_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user_id: int = Depends(get_current_user)
):
    """
    获取问题列表 (支持筛选和分页)
    """
    # TODO: 实现数据库查询
    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "data": []
    }

@app.get("/api/stats/overview")
async def get_stats_overview(current_user_id: int = Depends(get_current_user)):
    """
    获取统计概览
    """
    # TODO: 实现统计查询
    return {
        "total_issues": 0,
        "total_compensation": 0,
        "factory_count": 0,
        "trend": []
    }

@app.get("/api/qc/performance")
async def get_qc_performance(
    month: Optional[str] = None,
    current_user_id: int = Depends(get_current_user)
):
    """
    获取 QC 考核数据
    """
    # TODO: 实现考核数据查询
    return {
        "score": 0,
        "rank": 0,
        "metrics": {}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

### 6. 创建 Systemd 服务

```bash
# /etc/systemd/system/qc-api.service
cat > /etc/systemd/system/qc-api.service << 'EOF'
[Unit]
Description=QC System API Service
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/qc-system
Environment="PATH=/opt/qc-system/venv/bin"
ExecStart=/opt/qc-system/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable qc-api
sudo systemctl start qc-api
sudo systemctl status qc-api
```

---

## 🌐 第三步：Nginx 配置

### 1. 配置 Nginx

```bash
# /etc/nginx/sites-available/qc-system
cat > /etc/nginx/sites-available/qc-system << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    # 强制 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 静态文件 (移动端 H5)
    location /qc-mobile/ {
        alias /opt/qc-system/mobile/;
        try_files $uri $uri/ /qc-mobile/index.html;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 文件上传
    location /uploads/ {
        alias /opt/qc-system/uploads/;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # 日志
    access_log /var/log/nginx/qc-system-access.log;
    error_log /var/log/nginx/qc-system-error.log;
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/qc-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. 申请 SSL 证书

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d your-domain.com

# 自动续期 (已自动配置 cron)
sudo certbot renew --dry-run
```

---

## 📱 第四步：移动端开发 (企业微信 H5)

### 1. 项目初始化

```bash
# 创建 Uni-app 项目
npx degit dcloudio/uni-preset-vue#vite qc-mobile
cd qc-mobile
npm install

# 安装 uView UI
npm install uview-ui
```

### 2. 配置 manifest.json

```json
{
  "h5": {
    "title": "QC 质量管理系统",
    "router": {
      "mode": "history",
      "base": "/qc-mobile/"
    },
    "devServer": {
      "port": 8080,
      "proxy": {
        "/api": {
          "target": "http://localhost:8000",
          "changeOrigin": true
        }
      }
    }
  },
  "mp-weixin": {
    "appid": "企业微信应用 AgentId",
    "setting": {
      "urlCheck": false
    }
  }
}
```

### 3. 登录页面示例

```vue
<!-- pages/login/login.vue -->
<template>
  <view class="login-container">
    <view class="logo">
      <image src="/static/logo.png" mode="aspectFit"></image>
      <text>QC 质量管理系统</text>
    </view>
    
    <view class="form">
      <u-input 
        v-model="username" 
        placeholder="请输入用户名"
        prefix-icon="account"
      ></u-input>
      
      <u-input 
        v-model="password" 
        type="password"
        placeholder="请输入密码"
        prefix-icon="lock"
      ></u-input>
      
      <u-button type="primary" @click="handleLogin">
        登录
      </u-button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
        return
      }
      
      try {
        const res = await uni.request({
          url: '/api/token',
          method: 'POST',
          data: {
            username: this.username,
            password: this.password
          }
        })
        
        // 保存 Token
        uni.setStorageSync('token', res.data.access_token)
        uni.setStorageSync('userInfo', res.data)
        
        // 跳转到首页
        uni.switchTab({ url: '/pages/index/index' })
      } catch (error) {
        uni.showToast({ title: '登录失败', icon: 'none' })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  padding: 40px;
  .logo {
    text-align: center;
    margin-bottom: 60px;
    image {
      width: 120px;
      height: 120px;
    }
    text {
      display: block;
      margin-top: 20px;
      font-size: 24px;
      font-weight: bold;
    }
  }
  .form {
    .u-input {
      margin-bottom: 20px;
    }
  }
}
</style>
```

---

## 🔒 第五步：权限管理

### 1. 角色定义

| 角色 | 权限 |
|------|------|
| admin | 系统管理、用户管理、所有数据 |
| manager | 部门管理、统计分析、考核审核 |
| qc | 问题录入、数据浏览、个人考核 |
| viewer | 只读权限 (数据浏览) |

### 2. 权限中间件

```python
# permissions.py
from functools import wraps
from fastapi import HTTPException, status

def require_role(required_roles: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if current_user.get('role') not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 使用示例
@app.get("/api/admin/users")
@require_role(['admin', 'manager'])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    pass
```

---

## 📊 第六步：数据爬取配置

### 定时任务 (Cron)

```bash
# /etc/cron.d/qc-crawler
# 每天凌晨 2 点爬取增量数据
0 2 * * * root cd /opt/qc-system && /opt/qc-system/venv/bin/python crawler.py >> /var/log/qc-crawler.log 2>&1

# 每周日凌晨 3 点生成周报
0 3 * * 0 root cd /opt/qc-system && /opt/qc-system/venv/bin/python analyzer.py >> /var/log/qc-analyzer.log 2>&1
```

---

## ✅ 第七步：验收检查清单

### 后端服务
- [ ] API 服务正常运行 (端口 8000)
- [ ] 数据库连接正常
- [ ] 用户登录接口可用
- [ ] JWT Token 生成正常
- [ ] 权限验证生效

### 前端应用
- [ ] H5 页面可访问
- [ ] 登录流程正常
- [ ] 企业微信内打开正常
- [ ] 图片上传功能正常
- [ ] 数据展示正常

### 安全配置
- [ ] HTTPS 已启用
- [ ] 密码加密存储
- [ ] API 访问需要认证
- [ ] 敏感操作有日志记录
- [ ] SQL 注入防护

### 性能优化
- [ ] 静态资源 CDN 加速
- [ ] 数据库查询有索引
- [ ] 接口响应时间 < 500ms
- [ ] 图片压缩处理
- [ ] 分页查询实现

---

## 📞 技术支持

遇到问题请检查：

1. **日志文件**
   - API 日志：`/var/log/qc-api/`
   - Nginx 日志：`/var/log/nginx/`
   - 应用日志：`/opt/qc-system/logs/`

2. **服务状态**
   ```bash
   systemctl status qc-api
   systemctl status nginx
   systemctl status mysql
   ```

3. **网络连通性**
   ```bash
   curl -I https://your-domain.com/api/
   ping your-domain.com
   ```

---

**部署完成后，企业微信用户即可通过工作台访问 QC 质量管理系统！** 🎉
