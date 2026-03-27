# 🚀 项目启动指南

## 项目概述

本项目为**服装 QC 质量控制系统**，用于爬取和分析现有售后反馈数据，并提供一套适合 QC 人员使用的移动端系统，实现快速浏览、记录反馈信息和考核质检人员工作情况。

---

## 📁 项目结构

```
qc-system/
├── README.md                 # 项目方案文档
├── STARTUP.md               # 本文件 - 启动指南
├── requirements.txt         # Python 依赖
├── crawler.py               # 数据爬虫脚本
├── analyzer.py              # 数据分析脚本
├── database/
│   └── init.sql            # 数据库初始化脚本
├── docs/
│   └── mobile-prototype.md # 移动端原型设计
├── data/                    # 爬取的数据 (运行后生成)
│   ├── quality_issues.csv
│   ├── quality_issues.json
│   └── images/
└── reports/                 # 分析报告 (运行后生成)
```

---

## 🔧 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库初始化

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE qc_system DEFAULT CHARSET=utf8mb4;

# 导入表结构
use qc_system;
source database/init.sql;
```

### 3. 数据爬取

```bash
# 测试爬取 (前 10 页)
python crawler.py

# 完整爬取 (编辑 crawler.py 取消注释)
# crawler.crawl(max_pages=None, download_images=True)
```

**注意事项:**
- 首次运行建议先测试爬取前 10 页
- 确认数据正常后再进行完整爬取
- 完整爬取约需 2-3 小时 (6638 页)
- 图片下载会消耗较多时间和存储空间

### 4. 数据分析

```bash
# 运行分析脚本
python analyzer.py

# 查看生成的报告
# reports/quality_analysis_report_YYYYMMDD_HHMMSS.txt
# reports/summary_stats.json
```

---

## 📊 数据字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| buyer_wangwang | 买家旺旺 ID | 260314-512890059130354 |
| merchant_no | 商家编号/SKU | 24181814145 |
| platform | 销售平台 | 天猫/淘宝/抖音/小店 |
| order_no | 交易单号 | (空) |
| issue_type | 问题类型 | 污渍/扣子/做工开线等 |
| solution | 解决方式 | 退货/补偿/现金补偿 |
| compensation | 补偿金额 | 5/20 |
| factory | 车缝工厂 | 元合/三米/乙超 |
| batch_no | 波次号 | FY27157 |
| pattern_batch | 版型波次 | WB44942 |
| designer | 设计师 | 刘小落/陈丹 |
| handler | 处理人 | 舟舟/贝贝 |
| created_at | 添加时间 | 2025-03-24 23:36:52 |

---

## 📱 移动端开发

### 技术栈推荐

```
Uni-app + uView UI + Pinia
```

### 开发步骤

1. **创建项目**
```bash
npx degit dcloudio/uni-preset-vue#vite qc-mobile
cd qc-mobile
npm install
```

2. **安装 UI 库**
```bash
npm install uview-ui
```

3. **参考原型设计**
- 查看 `docs/mobile-prototype.md`
- 实现 6 个核心页面

### 核心页面

| 页面 | 路径 | 优先级 |
|------|------|--------|
| 首页 | /pages/index/index | P0 |
| 问题录入 | /pages/issue/entry | P0 |
| 数据浏览 | /pages/issue/list | P0 |
| 问题详情 | /pages/issue/detail | P0 |
| 统计分析 | /pages/stats/overview | P1 |
| 我的考核 | /pages/performance/my | P1 |

---

## 🔌 API 接口设计

### 后端框架

```
FastAPI + SQLAlchemy + MySQL
```

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/issues | GET | 获取问题列表 |
| /api/issues/{id} | GET | 获取问题详情 |
| /api/issues | POST | 创建问题记录 |
| /api/factories | GET | 获取工厂列表 |
| /api/factories/{name}/stats | GET | 工厂质量统计 |
| /api/qc/inspections | POST | 提交检验记录 |
| /api/qc/performance | GET | 获取考核数据 |
| /api/stats/overview | GET | 整体统计 |
| /api/stats/trend | GET | 趋势分析 |

---

## 📈 考核指标体系

### QC 人员考核 (100 分)

| 指标 | 权重 | 计算方式 | 目标值 |
|------|------|----------|--------|
| 检验工作量 | 25 分 | 检验件数/团队平均×25 | ≥100% |
| 漏检率 | 30 分 | (1-漏检率/2%)×30 | ≤2% |
| 问题发现率 | 20 分 | 发现率/5%×20 | ≥5% |
| 响应时效 | 15 分 | (1-超时率)×15 | ≤4h |
| 数据完整性 | 10 分 | 完整率×10 | ≥98% |

### 工厂质量评级

| 等级 | 问题率 | 月补偿金额 | 措施 |
|------|--------|------------|------|
| A | ≤1% | ≤5000 | 优秀，优先合作 |
| B | 1-3% | 5000-20000 | 良好，正常合作 |
| C | 3-5% | 20000-50000 | 需改进，减少订单 |
| D | ≥5% | ≥50000 | 不合格，暂停合作 |

---

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=qc_system

# 爬虫
CRAWLER_BASE_URL=http://114.55.34.212:8080
CRAWLER_DELAY=1  # 请求间隔 (秒)
CRAWLER_MAX_PAGES=  # 空表示全部

# 文件存储
STORAGE_TYPE=local  # local/minio/oss
STORAGE_PATH=./data/images

# OSS (如使用)
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_ACCESS_KEY=your_key
OSS_SECRET_KEY=your_secret
OSS_BUCKET=qc-images
```

---

## 🚨 注意事项

### 数据安全
1. 生产环境请使用 HTTPS
2. 数据库密码使用环境变量
3. 敏感操作记录日志
4. 定期备份数据

### 爬虫合规
1. 确认爬取权限
2. 控制请求频率 (避免影响生产系统)
3. 仅用于内部质量管理
4. 不对外公开原始数据

### 性能优化
1. 大数据量分页查询
2. 图片使用 CDN 加速
3. 统计数据缓存 (Redis)
4. 异步处理耗时任务

---

## 📞 下一步行动

### 立即可做
- [ ] 运行爬虫测试 (前 10 页)
- [ ] 确认数据字段完整性
- [ ] 分析现有数据质量

### 短期 (1-2 周)
- [ ] 完成数据库初始化
- [ ] 实现基础 API 接口
- [ ] 开发移动端核心页面

### 中期 (3-4 周)
- [ ] 完善考核统计功能
- [ ] 实现图片上传功能
- [ ] 部署测试环境

### 长期 (5-10 周)
- [ ] 全量数据导入
- [ ] 用户培训
- [ ] 正式上线

---

## 📚 相关文档

- [项目方案](README.md) - 完整设计方案
- [移动端原型](docs/mobile-prototype.md) - 页面设计稿
- [数据库脚本](database/init.sql) - 表结构定义

---

## 💡 常见问题

**Q: 爬虫无法连接服务器？**
A: 检查网络连通性，确认目标服务器可访问。如需登录，修改 `crawler.py` 的 `login()` 方法。

**Q: 数据量太大爬取太慢？**
A: 可以设置 `max_pages` 参数分批爬取，或增加时间范围筛选。

**Q: 移动端选择什么框架？**
A: 推荐 Uni-app，一套代码可编译为 H5、小程序、APP。

**Q: 如何计算漏检率？**
A: 漏检率 = 该 QC 检验批次的售后问题数 / 检验总件数

---

**祝项目顺利！如有问题请随时联系。** 🎉
