# 服装 QC 质量控制系统 - 项目方案

## 项目概述

基于现有售后反馈数据，构建一套适合服装外发质量控制人员 (QC) 使用的移动端质量管理系统，实现快速浏览、记录反馈信息和考核质检人员工作情况。

## 数据来源分析

### 现有系统字段
- **买家旺旺** - 客户 ID
- **商家编号** - 商品 SKU
- **问题来源** - 天猫/淘宝/小店/抖音
- **交易单号** - 订单号
- **商品图/问题图** - 质量问题的视觉证据
- **问题描述** - 污渍、扣子、拉链、尺码不符、掉色、印花问题、做工开线等、破洞、起球勾线掉毛、过敏、洗唛和吊牌不符、有味道、面料硬不舒服、色差、松紧坏、长短不一、发错、少发、其他
- **解决方式** - 退货/补偿/现金补偿等
- **补偿金额** - 经济损失
- **车缝工厂** - 责任工厂
- **波次号/版型波次** - 生产批次
- **设计师** - 设计责任人
- **处理人** - 客服处理人员
- **添加时间** - 问题发现时间

### 数据规模
- 总数据量：约 99,566 条
- 分页：6,638 页
- 时间范围：2025 年至今

---

## 系统设计方案

### 一、系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      移动端 (H5/小程序)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 问题录入  │  │ 数据浏览  │  │ 统计分析  │  │ 考核报表  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 网关层                               │
│            认证授权 / 限流 / 日志 / 数据校验                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      后端服务                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 数据采集  │  │ 质量管理  │  │ 人员考核  │  │ 报表分析  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据存储                                │
│     MySQL(业务数据) + Redis(缓存) + MinIO(图片存储)          │
└─────────────────────────────────────────────────────────────┘
```

### 二、核心功能模块

#### 1. 数据采集模块
- 定时爬取现有售后反馈系统
- 数据清洗与标准化
- 问题分类自动打标
- 图片下载与存储

#### 2. 移动端 QC 工作台
- **快速录入**: 扫码/拍照 + 语音输入问题描述
- **问题分类**: 预设 20+ 种质量问题类型
- **图片上传**: 支持多图上传，自动压缩
- **工厂选择**: 关联外发工厂数据库
- **批次追踪**: 关联生产波次号

#### 3. 数据浏览与搜索
- 按工厂/问题类型/时间范围筛选
- 质量问题趋势图表
- 高频问题 TOP10 排行
- 工厂质量排名

#### 4. 质检人员考核系统
- **工作量统计**: 每人检验批次/件数
- **漏检率**: 售后问题/检验总量
- **问题发现率**: 发现问题数/检验数
- **响应时效**: 问题处理平均时长
- **质量评分**: 综合考核得分

#### 5. 预警与通知
- 工厂质量问题超阈值预警
- 同类问题高频出现预警
- 考核不达标通知
- 日报/周报自动推送

### 三、数据库设计

#### 核心表结构

```sql
-- 质量问题记录表
CREATE TABLE quality_issues (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    issue_no VARCHAR(32) UNIQUE,          -- 问题编号
    sku_no VARCHAR(32),                    -- 商家编号
    order_no VARCHAR(64),                  -- 交易单号
    platform VARCHAR(16),                  -- 问题来源平台
    issue_type VARCHAR(32),                -- 问题类型
    issue_desc TEXT,                       -- 问题描述
    solution_type VARCHAR(32),             -- 解决方式
    compensation_amount DECIMAL(10,2),     -- 补偿金额
    factory_name VARCHAR(64),              -- 车缝工厂
    batch_no VARCHAR(32),                  -- 波次号
    pattern_batch VARCHAR(32),             -- 版型波次
    designer VARCHAR(32),                  -- 设计师
    handler VARCHAR(32),                   -- 处理人
    product_image VARCHAR(255),            -- 商品图
    issue_images JSON,                     -- 问题图数组
    created_at DATETIME,                   -- 添加时间
    INDEX idx_factory (factory_name),
    INDEX idx_type (issue_type),
    INDEX idx_created (created_at)
);

-- QC 检验记录表
CREATE TABLE qc_inspections (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    qc_user_id BIGINT,                     -- 质检员 ID
    factory_name VARCHAR(64),              -- 工厂名称
    batch_no VARCHAR(32),                  -- 波次号
    inspect_date DATE,                     -- 检验日期
    total_pieces INT,                      -- 检验件数
    passed_pieces INT,                     -- 合格件数
    failed_pieces INT,                     -- 不合格件数
    issues_found JSON,                     -- 发现问题列表
    inspect_images JSON,                   -- 检验照片
    status VARCHAR(16),                    -- 状态
    created_at DATETIME,
    INDEX idx_qc_user (qc_user_id),
    INDEX idx_factory (factory_name),
    INDEX idx_date (inspect_date)
);

-- 质检人员表
CREATE TABLE qc_users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(32) UNIQUE,
    real_name VARCHAR(32),
    phone VARCHAR(16),
    department VARCHAR(32),
    status TINYINT DEFAULT 1,
    created_at DATETIME
);

-- 考核统计表 (按月)
CREATE TABLE qc_monthly_stats (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    qc_user_id BIGINT,
    stat_month DATE,                       -- 统计月份
    total_inspections INT,                 -- 总检验次数
    total_pieces INT,                      -- 总检验件数
    issues_found INT,                      -- 发现问题数
    missed_issues INT,                     -- 漏检问题数 (售后反馈)
    miss_rate DECIMAL(5,2),                -- 漏检率
    avg_response_hours DECIMAL(6,2),       -- 平均响应时长
    quality_score DECIMAL(5,2),            -- 质量评分
    rank INT,                              -- 排名
    created_at DATETIME
);

-- 工厂质量档案表
CREATE TABLE factory_quality_profile (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    factory_name VARCHAR(64) UNIQUE,
    total_orders INT,
    total_issues INT,
    issue_rate DECIMAL(5,2),               -- 问题率
    total_compensation DECIMAL(12,2),      -- 总补偿金额
    main_issue_types JSON,                 -- 主要问题类型分布
    quality_level VARCHAR(8),              -- 质量等级 A/B/C/D
    last_updated DATETIME
);
```

### 四、移动端界面设计

#### 页面结构
```
首页
├── 今日数据概览
├── 快捷入口 (录入/扫描/统计)
└── 待处理事项

问题录入页
├── 扫码/手动输入 SKU
├── 拍照上传 (商品图 + 问题图)
├── 问题类型选择 (宫格)
├── 语音输入描述
├── 工厂/批次选择
└── 提交

数据浏览页
├── 筛选条件 (工厂/类型/时间)
├── 列表展示 (缩略图 + 关键信息)
└── 详情查看

统计分析页
├── 问题趋势图
├── 工厂排名
├── 问题类型分布
└── 补偿金额统计

考核报表页
├── 个人考核得分
├── 工作量统计
├── 漏检率趋势
└── 团队排名
```

### 五、技术选型

| 模块 | 技术栈 | 说明 |
|------|--------|------|
| 移动端 | Uni-app / Taro | 一套代码编译多端 (H5/小程序/APP) |
| 后端 | Python FastAPI / Node.js | 快速开发，高性能 API |
| 数据库 | MySQL 8.0 | 主业务数据存储 |
| 缓存 | Redis | 热点数据缓存，会话管理 |
| 文件存储 | MinIO / 阿里云 OSS | 图片存储 |
| 数据采集 | Scrapy / Playwright | 定时爬取现有系统 |
| 任务调度 | Celery / APScheduler | 定时任务 |
| 图表 | ECharts | 数据可视化 |

### 六、爬虫方案设计

```python
# 核心爬取逻辑
- 登录现有系统 (如需)
- 设置时间范围：2025-01-01 至今
- 分页遍历所有数据
- 提取字段并标准化
- 下载图片到本地/OSS
- 增量更新 (避免重复)
- 异常重试机制
```

### 七、考核指标体系

#### QC 人员考核维度

| 指标 | 权重 | 计算方式 | 目标值 |
|------|------|----------|--------|
| 检验工作量 | 25% | 检验件数/团队平均 | ≥100% |
| 漏检率 | 30% | 售后问题数/检验件数 | ≤2% |
| 问题发现率 | 20% | 发现问题数/检验件数 | ≥5% |
| 响应时效 | 15% | 平均处理时长 | ≤4h |
| 数据完整性 | 10% | 记录完整率 | ≥98% |

#### 工厂质量评级

| 等级 | 问题率 | 补偿金额/月 | 说明 |
|------|--------|-------------|------|
| A | ≤1% | ≤5000 | 优秀，优先合作 |
| B | 1%-3% | 5000-20000 | 良好，正常合作 |
| C | 3%-5% | 20000-50000 | 需改进，减少订单 |
| D | ≥5% | ≥50000 | 不合格，暂停合作 |

### 八、实施计划

| 阶段 | 时间 | 任务 |
|------|------|------|
| 第一阶段 | 2 周 | 数据采集爬取 + 历史数据导入 |
| 第二阶段 | 3 周 | 后端 API 开发 + 数据库搭建 |
| 第三阶段 | 3 周 | 移动端开发 + 核心功能实现 |
| 第四阶段 | 1 周 | 考核模块 + 报表统计 |
| 第五阶段 | 1 周 | 测试优化 + 上线部署 |

**总计：约 10 周**

### 九、预期效果

1. **数据集中化**: 所有质量问题统一归集，便于分析
2. **移动化办公**: QC 人员现场快速录入，无需回办公室
3. **考核透明化**: 数据驱动考核，减少人为因素
4. **质量可追溯**: 问题 - 工厂 - 批次 - 责任人全链路追踪
5. **决策支持**: 通过数据分析优化供应商结构

---

## 下一步行动

### ✅ 已确认
- [x] 现有系统无需登录认证 (爬虫可直接访问)
- [x] 新 QC 系统需要登录权限管理
- [x] 数据库：MySQL 8.0
- [x] 移动端部署：企业微信 H5 应用

### 📋 待执行
1. 准备服务器环境 (4 核 8G/50GB/5Mbps)
2. 配置企业微信应用 (获取 AgentId/Secret)
3. 申请域名和 SSL 证书
4. 导入历史数据 (运行爬虫脚本)
5. 创建管理员账号
6. 企业微信内测试访问

---

## 📁 项目文件清单

```
qc-system/
├── README.md                      # 项目方案 (本文档)
├── STARTUP.md                     # 启动指南
├── crawler.py                     # 数据爬虫
├── analyzer.py                    # 数据分析
├── requirements.txt               # Python 依赖
│
├── backend/
│   └── main.py                    # FastAPI 后端服务 (新增)
│
├── database/
│   └── init.sql                   # 数据库初始化
│
└── docs/
    ├── mobile-prototype.md        # 移动端原型设计
    └── wecom-deployment.md        # 企业微信部署指南 (新增)
```
