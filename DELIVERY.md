# QC 质量控制系统 - 项目交付清单

## ✅ 已完成内容

### 📱 移动端页面 (4 个)

| 文件 | 说明 | 大小 |
|------|------|------|
| `mobile/login.html` | 登录页面 - 精美渐变设计，支持企业微信登录 | 10.8KB |
| `mobile/index.html` | 首页 - 数据概览/快捷入口/预警/待办 | 13.5KB |
| `mobile/issue-entry.html` | 问题录入 - 扫码/拍照/语音/问题类型选择 | 11.2KB |
| `mobile/issue-list.html` | 问题列表 (待创建) | - |

### 🔧 后端服务

| 文件 | 说明 | 大小 |
|------|------|------|
| `backend/main.py` | FastAPI 完整 API 服务 | 22KB |
| `requirements.txt` | Python 依赖清单 | 0.8KB |

### 🗄️ 数据库

| 文件 | 说明 | 大小 |
|------|------|------|
| `database/init_with_admin.sql` | 独立数据库初始化 (含默认管理员) | 14.2KB |
| `database/init.sql` | 基础版表结构 | 13.4KB |

### 🐳 Docker 部署

| 文件 | 说明 |
|------|------|
| `docker/Dockerfile` | Python 3.10 镜像构建 |
| `docker/docker-compose.yml` | 4 服务编排 (MySQL/API/Nginx/Crawler) |
| `docker/nginx/nginx.conf` | Nginx 反向代理配置 |
| `docker/.env.example` | 环境变量模板 |
| `docker/README.md` | 详细部署文档 |

### 📚 文档

| 文件 | 说明 |
|------|------|
| `README.md` | 项目方案 (系统架构/功能模块/考核体系) |
| `STARTUP.md` | 启动指南 |
| `docs/mobile-prototype.md` | 移动端原型设计 (7 个页面线框图) |
| `docs/wecom-deployment.md` | 企业微信部署指南 |
| `crawler.py` | 数据爬虫脚本 |
| `analyzer.py` | 数据分析脚本 |

---

## 📊 项目统计

- **总文件数**: 20+
- **代码总量**: 约 100KB+
- **API 接口**: 15+
- **数据库表**: 10 张
- **移动端页面**: 4 个 (已创建 3 个)

---

## 🚀 快速部署

```bash
# 1. 进入 docker 目录
cd qc-system/docker

# 2. 配置环境变量
cp .env.example .env
nano .env

# 3. 一键启动
docker compose up -d --build

# 4. 访问系统
# 登录页：http://localhost/qc-mobile/login.html
# API 文档：http://localhost/docs
```

---

## 🔐 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 系统管理员 |
| qc_manager | admin123 | 质检经理 |
| qc_user | admin123 | 质检员 |

---

## 📋 待创建页面 (可选)

如需继续创建以下页面，请告知：

1. **问题列表页** (`issue-list.html`) - 数据浏览/筛选/分页
2. **问题详情页** (`issue-detail.html`) - 完整信息/图片/处理记录
3. **统计分析页** (`stats.html`) - 图表/趋势/排行榜
4. **个人考核页** (`performance.html`) - 考核得分/排名/历史

---

**项目已可正常运行！需要继续创建其他页面吗？** 🎉
