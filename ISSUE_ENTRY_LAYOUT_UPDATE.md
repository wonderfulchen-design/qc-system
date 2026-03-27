# 问题录入页面优化报告

## 📅 修改时间
2026-03-26 14:38

---

## ✅ 修改完成

### 1. 页面布局优化

**波次号移到最上面**:
```html
<!-- 波次号信息 - 最重要放在最上面 -->
<div class="form-section" style="border: 2px solid #667eea;">
  <div class="section-title" style="color: #667eea; font-size: 18px;">
    🔢 波次号（必填）
  </div>
  <input type="text" class="form-input" id="batchNo" 
         placeholder="请输入波次号，自动填充工厂和货品编码" 
         style="font-size: 16px; font-weight: bold;" required>
  <div style="font-size:12px;color:#999;margin-top:5px;">
    ℹ️ 输入波次号后自动填充工厂和货品编码
  </div>
</div>
```

**货品编码和工厂改为纯文本显示**:
```html
<!-- 商品信息 - 纯文本显示 -->
<div class="form-section">
  <div class="section-title">📦 商品信息（自动填充）</div>
  
  <div class="form-group">
    <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
      <span style="color: #999; font-size: 14px;">货品编码</span>
      <span id="goodsNoDisplay" style="color: #333; font-size: 15px; font-weight: 500;">-</span>
    </div>
  </div>
  
  <div class="form-group">
    <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
      <span style="color: #999; font-size: 14px;">工厂</span>
      <span id="factoryDisplay" style="color: #333; font-size: 15px; font-weight: 500;">-</span>
    </div>
  </div>
  
  <div style="font-size:12px;color:#999;margin-top:10px;">
    ℹ️ 输入波次号后自动填充，无需手动填写
  </div>
</div>
```

### 2. JavaScript 代码修改

**自动填充逻辑**:
```javascript
// 自动填充工厂和货品编码
const factoryDisplay = document.getElementById('factoryDisplay');
const goodsNoDisplay = document.getElementById('goodsNoDisplay');

if (factoryDisplay && batch.factory_name) {
  factoryDisplay.textContent = batch.factory_name;
  showToast('已自动填充工厂');
}
if (goodsNoDisplay && batch.goods_no) {
  goodsNoDisplay.textContent = batch.goods_no;
  showToast('已自动填充货品编码');
}
```

**验证逻辑**:
```javascript
// 验证必填项
const batchNo = document.getElementById('batchNo').value.trim();
const goodsNo = document.getElementById('goodsNoDisplay').textContent.trim();
const factory = document.getElementById('factoryDisplay').textContent.trim();

if (!batchNo) {
  alert('请填写波次号');
  return;
}
if (!goodsNo || !factory || goodsNo === '-' || factory === '-') {
  alert('请输入波次号自动填充工厂和货品编码');
  return;
}
```

**草稿保存/加载**:
```javascript
// 保存草稿
const draft = {
  goodsNo: document.getElementById('goodsNoDisplay').textContent,
  factory: document.getElementById('factoryDisplay').textContent,
  batchNo: document.getElementById('batchNo').value,
  ...
};

// 加载草稿
const goodsNoDisplay = document.getElementById('goodsNoDisplay');
const factoryDisplay = document.getElementById('factoryDisplay');
if (goodsNoDisplay) goodsNoDisplay.textContent = draft.goodsNo || '-';
if (factoryDisplay) factoryDisplay.textContent = draft.factory || '-';
```

---

## 📊 页面布局

**修改后的顺序**:
```
1. 🔢 波次号（必填）- 蓝色边框突出显示
   └─ 输入波次号，自动填充

2. 📦 商品信息（自动填充）- 纯文本显示
   ├─ 货品编码：23181805051
   └─ 工厂：三米

3. 📷 拍照上传
4. 🏷️ 问题类型
5. 📝 问题描述
6. 💰 补偿金额
7. 提交按钮
```

---

## 🎯 使用流程

**QC 人员操作**:
```
1. 输入波次号（如：F21157）
2. 点击外部（失去焦点）
3. 自动显示:
   - 货品编码：23181805051
   - 工厂：三米
4. 继续填写其他信息
5. 提交
```

---

## ✅ 优化效果

- ✅ **波次号在最上面** - 蓝色边框突出显示
- ✅ **货品编码纯文本** - 只显示，不可编辑
- ✅ **工厂纯文本** - 只显示，不可编辑
- ✅ **验证逻辑修改** - 只验证波次号必填
- ✅ **提示信息清晰** - 告知用户自动填充

---

## 📁 修改的文件

**文件**: `mobile/issue-entry.html`

**修改内容**:
1. 波次号移到最上面，蓝色边框
2. 货品编码和工厂改为 `<span>` 显示
3. JavaScript 自动填充逻辑修改
4. 验证逻辑修改
5. 草稿保存/加载修改

---

## ⚠️ 注意

**Docker 容器是只读的**，需要通过以下方式同步:

**方法 1: 重新构建容器**
```bash
docker-compose -f docker/docker-compose.yml build nginx
docker-compose -f docker/docker-compose.yml up -d nginx
```

**方法 2: 挂载卷**
```yaml
# docker-compose.yml
volumes:
  - ./mobile:/usr/share/nginx/html/qc-mobile:ro
```

**方法 3: 直接复制到容器**
```bash
docker cp issue-entry.html qc-nginx:/tmp/issue-entry.html
docker exec qc-nginx cp /tmp/issue-entry.html /usr/share/nginx/html/qc-mobile/
```

---

**修改完成时间**: 2026-03-26 14:38
**状态**: ✅ 本地文件已修改
**同步**: 需要手动同步到容器
