# 七牛云 OSS 集成指南

## ✅ 已完成配置

### 1. 后端配置 (`.env`)
```env
QINIU_ACCESS_KEY=IapaWm5AODDduh4YR_MpLh4irSWwRobKZ0YfJVy5
QINIU_SECRET_KEY=CpNr64VnpSU8Hx_ESLGMOZxSCKoVyuHfmmutHh-I
QINIU_BUCKET=lswsampleimg
QINIU_DOMAIN=http://qp2bc4f1j.hn-bkt.clouddn.com
QINIU_PREFIX=qcImg/
```

### 2. 新增 API 端点
- `GET /api/qiniu/upload-token` - 获取七牛云上传凭证

### 3. 前端改动
- `mobile/issue-entry.html` - 图片上传改为直传七牛云
- 9 张图片（1 张商品图 + 8 张问题图）全部上传到七牛云
- 返回 CDN 链接保存到数据库

---

## 📦 安装依赖

```bash
cd qc-system
pip install qiniu>=7.9.0
```

或使用 requirements.txt：
```bash
pip install -r requirements.txt
```

---

## 🔄 上传流程

### 前端直传模式（推荐）

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   前端 H5    │ ────▶│  后端 API     │      │   七牛云     │
│             │      │              │      │             │
│ 1. 请求 token│─────▶│ 2. 返回凭证   │      │             │
│             │◀─────│              │      │             │
│             │      │              │      │             │
│ 3. 直传文件 │─────────────────────────────▶│ 4. 返回 CDN 链接 │
│             │      │              │      │             │
│ 5. 保存 CDN  │─────▶│ 6. 存入数据库 │      │             │
│   链接到 DB  │      │              │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
```

---

## 🔑 七牛云后台配置

### 1. 上传凭证策略
后端生成的上传凭证包含以下限制：
- **Bucket**: `lswsampleimg`
- **目录前缀**: `qcImg/`（只能上传到此目录）
- **有效期**: 3600 秒（1 小时）
- **文件名**: 使用文件 hash（etag）避免重复

### 2. CORS 设置（如需要）
如果前端遇到 CORS 问题，在七牛云后台设置：
- 进入 Bucket → 空间设置 → CORS 设置
- 添加规则允许你的域名访问

### 3. CDN 域名
- 当前配置：`http://qp2bc4f1j.hn-bkt.clouddn.com`
- 建议配置 HTTPS 域名（生产环境）

---

## 🧪 测试步骤

### 1. 启动后端
```bash
cd qc-system/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试上传凭证 API
```bash
curl -X GET http://localhost:8000/api/qiniu/upload-token \
  -H "Authorization: Bearer YOUR_TOKEN"
```

返回示例：
```json
{
  "token": "xxx:yyy:zzz",
  "bucket": "lswsampleimg",
  "domain": "http://qp2bc4f1j.hn-bkt.clouddn.com",
  "prefix": "qcImg/",
  "expire": 3600
}
```

### 3. 前端测试
1. 打开质检录入页面
2. 点击任意图片上传位
3. 选择图片上传
4. 检查七牛云后台是否收到文件（在 `qcImg/` 目录下）

---

## 📁 文件命名规则

上传到七牛云的文件名格式：
```
qcImg/{timestamp}_{random}.{ext}
```

示例：
```
qcImg/1711605600000_a1b2c3.jpg
qcImg/1711605600123_d4e5f6.png
```

---

## 🔒 安全说明

1. **AK/SK 只保存在后端**，前端永远拿不到
2. 前端只能拿到临时上传凭证（1 小时过期）
3. 上传凭证限制了只能传到指定 Bucket 和目录
4. 文件名使用 hash 避免覆盖和冲突

---

## 🐛 常见问题

### Q: 上传失败 "401 Unauthorized"
A: 检查后端 `.env` 中的 AK/SK 是否正确，确认七牛云账号状态正常

### Q: 上传失败 "CORS error"
A: 在七牛云后台配置 CORS，允许前端域名访问

### Q: 图片无法显示
A: 检查 CDN 域名是否正确，确认七牛云 Bucket 是公开读或配置了 CDN

### Q: 上传凭证过期
A: 凭证有效期 1 小时，过期后前端需要重新请求 token

---

## 📊 数据库字段

图片链接保存到 `quality_issues` 表：
- `product_image` - 商品图（VARCHAR 255）
- `issue_images` - 问题图数组（JSON）

示例：
```json
{
  "product_image": "http://qp2bc4f1j.hn-bkt.clouddn.com/qcImg/1711605600000_a1b2c3.jpg",
  "issue_images": [
    "http://qp2bc4f1j.hn-bkt.clouddn.com/qcImg/1711605600001_d4e5f6.jpg",
    "http://qp2bc4f1j.hn-bkt.clouddn.com/qcImg/1711605600002_g7h8i9.jpg"
  ]
}
```

---

## ✅ 验收清单

- [ ] 安装七牛云 SDK (`pip install qiniu`)
- [ ] 后端重启，加载新配置
- [ ] 测试获取上传凭证 API
- [ ] 前端上传 9 张图片测试
- [ ] 检查七牛云后台文件是否在 `qcImg/` 目录
- [ ] 检查数据库是否保存了正确的 CDN 链接
- [ ] 检查图片是否能正常显示

---

**完成时间**: 2026-03-28  
**版本**: v1.0
