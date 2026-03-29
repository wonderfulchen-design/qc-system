# 企业微信登录配置说明

## 📋 功能说明

支持用户通过企业微信快捷登录 QC 系统，无需输入用户名和密码。

## 🔧 配置步骤

### 1️⃣ 企业微信管理后台配置

1. 登录 **企业微信管理后台** (https://work.weixin.qq.com)

2. 进入 **应用管理** → **自建应用**

3. 创建或选择一个应用（如：QC 系统）

4. 配置 **网页授权及 JS-SDK**：
   - 点击"网页授权及 JS-SDK"
   - 设置可信域名：`miqin.up.railway.app` 或你的自定义域名
   - 无需备案（企业微信支持未备案域名）

5. 记录以下信息：
   - **企业 ID (Corp ID)**: `ww8a4a238a216465e8`
   - **AgentId**: `1000002`
   - **Secret**: `W16ZiYxOHX1Ja67UupOKc_xK9P12sPm4T6BM415xAtw`

### 2️⃣ Railway 环境变量配置

确保以下环境变量已配置：

```bash
# 企业微信配置
WECHAT_CORP_ID=ww8a4a238a216465e8
WECHAT_AGENT_ID=1000002
WECHAT_SECRET=W16ZiYxOHX1Ja67UupOKc_xK9P12sPm4T6BM415xAtw
WECHAT_REDIRECT_URI=http://121.196.166.162
```

**注意：** `WECHAT_REDIRECT_URI` 应该是你的系统访问地址，用于回调。

### 3️⃣ 成员管理

在企业微信管理后台：
1. 进入 **通讯录**
2. 添加需要使用 QC 系统的成员
3. 成员的"账号"字段将作为登录后的用户名

## 🚀 使用流程

### 用户登录流程

1. 打开登录页面
   ```
   https://miqin.up.railway.app/qc-mobile/login.html
   ```

2. 点击 **"企业微信快捷登录"** 按钮

3. 跳转到企业微信授权页面

4. 用户同意授权

5. 自动登录并跳转到系统首页

### 后端处理流程

```
用户点击登录
  ↓
跳转到 /auth/wechat/login
  ↓
重定向到企业微信 OAuth2 页面
  ↓
用户同意授权
  ↓
企业微信回调 /auth/wechat/callback?code=xxx
  ↓
后端用 code 换取用户信息
  ↓
自动创建/更新用户
  ↓
生成 JWT token
  ↓
跳转到首页（带 token 参数）
  ↓
前端保存 token，完成登录
```

## 📊 用户数据同步

### 首次登录
- 自动创建用户
- 用户名 = 企业微信 UserID
- 同步姓名、部门、手机、邮箱

### 再次登录
- 自动更新用户信息
- 保持原有角色和权限

## 🔍 测试步骤

### 1. 检查企业微信配置

```bash
# 测试 access_token
curl "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ww8a4a238a216465e8&corpsecret=W16ZiYxOHX1Ja67UupOKc_xK9P12sPm4T6BM415xAtw"
```

**期望返回：**
```json
{
  "errcode": 0,
  "errmsg": "ok",
  "access_token": "xxx",
  "expires_in": 7200
}
```

### 2. 测试登录流程

1. 打开登录页面
2. 点击"企业微信快捷登录"
3. 确认跳转 URL 包含企业微信域名
4. 完成授权
5. 检查是否成功登录

### 3. 检查用户创建

登录系统后，查看用户列表：
- 用户名应该是企业微信 UserID
- 姓名、部门等信息已同步

## ⚠️ 常见问题

### 1. 回调域名不匹配

**错误：** `redirect_uri 参数错误`

**解决：** 
- 检查企业微信后台配置的可信域名
- 确保 `WECHAT_REDIRECT_URI` 与实际访问地址一致

### 2. 获取用户信息失败

**错误：** `获取用户信息失败：invalid code`

**解决：**
- code 只能使用一次，不能重复提交
- 检查网络是否通畅

### 3. 成员不在企业微信通讯录

**错误：** `用户不在应用可见范围内`

**解决：**
- 在企业微信后台将成员添加到应用可见范围
- 或者先将成员添加到企业微信通讯录

### 4. 权限不足

**错误：** `获取用户详细信息失败`

**解决：**
- 这是正常的，系统会自动降级处理
- 只使用 UserID 作为用户名

## 📝 技术细节

### OAuth2 授权模式
- **scope**: `snsapi_base`（静默授权，只获取 UserID）
- **授权 URL**: https://open.weixin.qq.com/connect/oauth2/authorize
- **Token 获取**: https://qyapi.weixin.qq.com/cgi-bin/gettoken
- **用户信息**: https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo

### 安全机制
- **state 参数**: 防止 CSRF 攻击
- **JWT Token**: 登录凭证，有效期 1 天
- **自动创建用户**: 首次登录自动注册

## 🔗 相关链接

- [企业微信 OAuth2 文档](https://developer.work.weixin.qq.com/document/path/91022)
- [企业微信 API 文档](https://developer.work.weixin.qq.com/document/path/91039)
- [Railway 部署文档](./docs/railway-deployment.md)

---

**配置时间：** 2026-03-29  
**配置人：** AI Assistant
