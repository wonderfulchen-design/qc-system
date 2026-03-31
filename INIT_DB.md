# QC System 数据库初始化脚本

## 在 Railway 上初始化数据库

### 步骤 1: 添加 MySQL 插件

1. 登录 Railway: https://railway.app
2. 进入你的项目
3. 点击 **New** → **Database** → **MySQL**
4. 等待 MySQL 创建完成（约 1 分钟）

### 步骤 2: 复制 DATABASE_URL

1. 进入 MySQL 插件页面
2. 点击 **Variables** 标签
3. 复制 `DATABASE_URL` 的值

### 步骤 3: 配置到主服务

1. 返回项目主页
2. 进入你的主服务（miqin）
3. 点击 **Variables** 标签
4. 点击 **Edit Variables**
5. 添加/更新 `DATABASE_URL` 变量：
   ```
   DATABASE_URL=mysql+pymysql://user:password@host:port/railway
   ```
6. 点击 **Save**

### 步骤 4: 初始化数据库表

在 Railway 主服务的 **Deployments** 页面，点击 **Deploy** 重新部署。

应用启动时会自动创建所有表。

---

## 手动初始化（可选）

如果自动创建失败，可以手动执行 SQL：

```sql
-- 创建用户表
CREATE TABLE IF NOT EXISTS qc_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(32) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    real_name VARCHAR(32),
    nickname VARCHAR(32),
    phone VARCHAR(16),
    email VARCHAR(64),
    department VARCHAR(32),
    role VARCHAR(16) DEFAULT 'qc',
    status INT DEFAULT 1,
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建波次表
CREATE TABLE IF NOT EXISTS product_batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_no VARCHAR(32) UNIQUE NOT NULL,
    factory_name VARCHAR(64),
    goods_no VARCHAR(32),
    merchandiser VARCHAR(32),
    designer VARCHAR(32)
);

-- 创建质量问题表
CREATE TABLE IF NOT EXISTS quality_issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_no VARCHAR(32) UNIQUE NOT NULL,
    order_no VARCHAR(64),
    goods_no VARCHAR(32),
    platform VARCHAR(16),
    buyer_wangwang VARCHAR(64),
    issue_type VARCHAR(32),
    issue_desc TEXT,
    solution_type VARCHAR(32),
    compensation_amount DECIMAL(10,2) DEFAULT 0,
    factory_name VARCHAR(64),
    batch_no VARCHAR(32),
    pattern_batch VARCHAR(32),
    merchandiser VARCHAR(32),
    designer VARCHAR(32),
    handler VARCHAR(32),
    batch_source VARCHAR(32),
    status VARCHAR(16) DEFAULT 'pending',
    qc_user_id INT,
    qc_username VARCHAR(32),
    product_image VARCHAR(255),
    issue_images JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    imported_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建评论表
CREATE TABLE IF NOT EXISTS issue_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT,
    user_id INT,
    username VARCHAR(32),
    nickname VARCHAR(32),
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_department ON qc_users(department);
CREATE INDEX idx_batches_batch_no ON product_batches(batch_no);
CREATE INDEX idx_batches_factory ON product_batches(factory_name);
CREATE INDEX idx_issues_issue_no ON quality_issues(issue_no);
CREATE INDEX idx_issues_batch_no ON quality_issues(batch_no);
CREATE INDEX idx_issues_created ON quality_issues(created_at);
CREATE INDEX idx_comments_issue_id ON issue_comments(issue_id);
```

---

## 验证

部署完成后，访问系统：

1. 打开浏览器访问你的 Railway 域名
2. 应该能看到登录页面
3. 点击企业微信登录
4. 登录后查看问题列表

---

**创建时间**: 2026-03-31
**状态**: 待执行
