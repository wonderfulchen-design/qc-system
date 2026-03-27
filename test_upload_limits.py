#!/usr/bin/env python3
"""
测试图片上传限制
"""
import requests
import io

API_BASE = "http://localhost:8000"

# 登录
token = requests.post(f"{API_BASE}/token", data={'username':'admin','password':'admin123'}).json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*70)
print("图片上传限制测试")
print("="*70)

# 测试 1: 正常图片（小文件）
print("\n[测试 1] 正常图片 (1KB)")
small_img = b"FAKE_JPEG_DATA"  # 14 bytes
files = {'file': ('test_small.jpg', small_img, 'image/jpeg')}
r = requests.post(f"{API_BASE}/uploads", headers=headers, files=files)
print(f"  状态码：{r.status_code}")
if r.status_code == 200:
    print(f"  [OK] 上传成功")
    print(f"  返回：{r.json()}")
else:
    print(f"  [ERR] {r.json()}")

# 测试 2: 超大图片（超过 5MB）
print("\n[测试 2] 超大图片 (6MB)")
large_img = b"X" * (6 * 1024 * 1024)  # 6MB
files = {'file': ('test_large.jpg', large_img, 'image/jpeg')}
r = requests.post(f"{API_BASE}/uploads", headers=headers, files=files)
print(f"  状态码：{r.status_code}")
if r.status_code == 413:
    print(f"  [OK] 正确拒绝 (Payload Too Large)")
    print(f"  错误信息：{r.json().get('detail')}")
else:
    print(f"  [WARN] 应该返回 413")

# 测试 3: 不支持的文件类型
print("\n[测试 3] 不支持的文件类型 (.exe)")
fake_exe = b"MZ" + b"\x00" * 100
files = {'file': ('test.exe', fake_exe, 'application/x-msdownload')}
r = requests.post(f"{API_BASE}/uploads", headers=headers, files=files)
print(f"  状态码：{r.status_code}")
if r.status_code == 400:
    print(f"  [OK] 正确拒绝")
    print(f"  错误信息：{r.json().get('detail')}")
else:
    print(f"  [WARN] 应该返回 400")

# 测试 4: 空文件
print("\n[测试 4] 空文件")
files = {'file': ('empty.jpg', b"", 'image/jpeg')}
r = requests.post(f"{API_BASE}/uploads", headers=headers, files=files)
print(f"  状态码：{r.status_code}")
if r.status_code == 400:
    print(f"  [OK] 正确拒绝")
    print(f"  错误信息：{r.json().get('detail')}")
else:
    print(f"  [WARN] 应该返回 400")

print("\n" + "="*70)
print("测试完成")
print("="*70)

print("\n限制说明:")
print("  - 文件大小：最大 5MB")
print("  - 文件类型：JPEG, PNG, GIF, WebP")
print("  - 分辨率：最大 4096x4096")
print("  - Nginx 限制：50MB")
