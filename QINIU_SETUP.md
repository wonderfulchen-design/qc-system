# 七牛云配置说明

## 问题原因

昨天推送的图片看不到，是因为：
1. 前端上传图片到 Railway 容器本地 `/uploads` 目录
2. Railway 是容器化部署，文件系统不持久化，重启后图片丢失
3. 推送的图片 URL 是相对路径 `/uploads/xxx.jpg`，外网访问不了

## 解决方案

### ✅ 已修改代码

1. **前端**：`issue-entry-fixed.html` 已改为七牛云直传
2. **后端**：七牛云 token API 已有 (`/api/qiniu/upload-token`)
3. **推送**：企业微信通知直接使用七牛云 CDN URL

### 🔧 需要配置 Railway 环境变量

登录 Railway Dashboard，添加以下环境变量：

```bash
# 七牛云配置（必须）
# 华南区（z2）配置 - HTTPS
QINIU_ACCESS_KEY=你的七牛云 AccessKey
QINIU_SECRET_KEY=你的七牛云 SecretKey
QINIU_BUCKET=lswsampleimg
QINIU_DOMAIN=https://lswsampleimg.qiniudn.com
QINIU_PREFIX=qcImg/
QINIU_REGION=z2

# 企业微信配置（可选，如果需要推送）
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi/webhook/send?key=xxx
WECHAT_REDIRECT_URI=https://miqin.up.railway.app
```

### 📝 七牛云密钥获取

1. 登录 https://portal.qiniu.com
2. 进入 个人中心 → 密钥管理
3. 复制 AccessKey 和 SecretKey

### ✅ 验证步骤

1. **检查环境变量**：
   ```bash
   # 在 Railway 控制台查看是否配置了 QINIU_* 变量
   ```

2. **测试上传**：
   - 打开 https://miqin.up.railway.app/qc-mobile/issue-entry.html
   - 上传一张图片
   - 检查返回的 URL 是否是 `http://qp2bc4f1j.hn-bkt.clouddn.com/qcImg/xxx`

3. **测试推送**：
   - 提交一个问题
   - 检查企业微信收到的消息图片是否能正常显示

### 🚀 部署

代码已修改，提交后 Railway 会自动重新部署：

```bash
cd qc-system
git add .
git commit -m "fix: 前端图片上传改用七牛云直传"
git push
```

---

## 技术说明

### 前端上传流程

```javascript
// 1. 获取七牛云 token
const tokenResp = await fetch('/api/qiniu/upload-token')
const { token, domain, prefix } = await tokenResp.json()

// 2. 直传七牛云（华南区用 upload-z2.qiniup.com）
const formData = new FormData()
formData.append('token', token)
formData.append('file', file)
await fetch('https://up-z2.qiniup.com', { method: 'POST', body: formData })

// 3. 构建 CDN URL（HTTPS）
const cdnUrl = `${domain}${prefix}${fileHash}`
// 例如：https://lswsampleimg.qiniudn.com/qcImg/abc123.jpg
```

### 后端通知

```python
# 直接使用前端传来的完整 URL
first_issue_image = issue_images[0]  # http://qp2bc4f1j.hn-bkt.clouddn.com/qcImg/xxx

# 推送到企业微信
{
    "picurl": first_issue_image  # 企业微信直接从这个 URL 加载图片
}
```

---

**修改时间：** 2026-03-29  
**修改人：** AI Assistant
