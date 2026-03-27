#!/usr/bin/env python3
"""
检测所有页面的乱码和排版问题
"""
import os
import re
from pathlib import Path

mobile_dir = Path("C:/Users/Administrator/.openclaw/workspace/qc-system/mobile")

print("="*70)
print("移动端页面 - 乱码和排版检测")
print("="*70)

issues = []

for html_file in sorted(mobile_dir.glob("*.html")):
    print(f"\n{html_file.name}")
    print("-" * 60)
    
    # 读取文件
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_issues = []
    
    # 1. 检查 meta charset
    if '<meta charset="UTF-8">' in content:
        print("  ✅ UTF-8 编码声明")
    else:
        msg = "❌ 缺少 UTF-8 编码声明"
        print(f"  {msg}")
        file_issues.append(msg)
    
    # 2. 检查 viewport
    if 'viewport' in content:
        print("  ✅ Viewport 设置")
    else:
        msg = "⚠️ 缺少 viewport 设置"
        print(f"  {msg}")
        file_issues.append(msg)
    
    # 3. 检查标题
    title_match = re.search(r'<title>([^<]+)</title>', content)
    if title_match:
        title = title_match.group(1)
        # 检查标题是否乱码
        if 'Ã' in title or 'ã€' in title or 'ï' in title:
            msg = f"❌ 标题可能乱码：{title[:50]}"
            print(f"  {msg}")
            file_issues.append(msg)
        else:
            print(f"  ✅ 标题：{title}")
    else:
        msg = "❌ 缺少标题"
        print(f"  {msg}")
        file_issues.append(msg)
    
    # 4. 检查未闭合标签
    tags = ['div', 'span', 'script', 'style', 'head', 'body']
    for tag in tags:
        open_count = len(re.findall(f'<{tag}\\b', content, re.IGNORECASE))
        close_count = len(re.findall(f'</{tag}>', content, re.IGNORECASE))
        if open_count != close_count:
            msg = f"⚠️ {tag} 标签不匹配：开={open_count} 闭={close_count}"
            print(f"  {msg}")
            file_issues.append(msg)
    
    # 5. 检查内联样式问题
    if 'style="' in content:
        inline_styles = len(re.findall(r'style="[^"]*"', content))
        if inline_styles > 20:
            msg = f"⚠️ 大量内联样式：{inline_styles} 处（建议提取到 CSS）"
            print(f"  {msg}")
            file_issues.append(msg)
        else:
            print(f"  ℹ️ 内联样式：{inline_styles} 处")
    
    # 6. 检查 JavaScript 错误风险
    if 'onclick="' in content:
        onclick_count = content.count('onclick="')
        if onclick_count > 10:
            msg = f"⚠️ 大量 onclick 处理器：{onclick_count} 处（建议使用事件监听）"
            print(f"  {msg}")
            file_issues.append(msg)
    
    # 7. 检查空链接
    if 'href="#"' in content:
        hash_links = content.count('href="#"')
        msg = f"⚠️ 空链接：{hash_links} 处"
        print(f"  {msg}")
        file_issues.append(msg)
    
    # 8. 检查图片 alt 属性
    imgs = re.findall(r'<img\b[^>]*>', content)
    imgs_without_alt = [img for img in imgs if 'alt=' not in img]
    if imgs_without_alt:
        msg = f"⚠️ 图片缺少 alt 属性：{len(imgs_without_alt)} 张"
        print(f"  {msg}")
        file_issues.append(msg)
    else:
        print(f"  ✅ 所有图片都有 alt 属性")
    
    # 9. 检查中文内容
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', content))
    print(f"  ℹ️ 中文字符：{chinese_chars} 个")
    
    # 10. 检查文件大小
    size_kb = html_file.stat().st_size / 1024
    if size_kb > 100:
        msg = f"⚠️ 文件过大：{size_kb:.1f}KB（建议拆分或压缩）"
        print(f"  {msg}")
        file_issues.append(msg)
    else:
        print(f"  ℹ️ 文件大小：{size_kb:.1f}KB")
    
    # 11. 检查常见乱码模式
    mojibake_patterns = [
        (r'Ã', 'UTF-8 被误认为 Latin-1'),
        (r'ã€', '日文假名乱码'),
        (r'ï¿½', '替换字符'),
        (r'â€"', '引号乱码'),
    ]
    
    for pattern, desc in mojibake_patterns:
        if re.search(pattern, content):
            msg = f"❌ 发现乱码模式：{desc}"
            print(f"  {msg}")
            file_issues.append(msg)
    
    # 保存问题
    if file_issues:
        issues.append({
            'file': html_file.name,
            'issues': file_issues
        })
    
    # 状态总结
    if file_issues:
        critical = [i for i in file_issues if '❌' in i]
        warning = [i for i in file_issues if '⚠️' in i]
        print(f"\n  总结：{len(critical)} 个严重问题，{len(warning)} 个警告")
    else:
        print(f"\n  ✅ 无明显问题")

# 总体报告
print("\n" + "="*70)
print("总体报告")
print("="*70)

total_issues = sum(len(item['issues']) for item in issues)
critical_count = sum(
    len([i for i in item['issues'] if '❌' in i])
    for item in issues
)
warning_count = sum(
    len([i for i in item['issues'] if '⚠️' in i])
    for item in issues
)

print(f"\n检测文件数：{len(list(mobile_dir.glob('*.html')))}")
print(f"发现问题的文件：{len(issues)}")
print(f"总问题数：{total_issues}")
print(f"  - 严重问题：{critical_count}")
print(f"  - 警告：{warning_count}")

if critical_count == 0 and warning_count < 10:
    print("\n✅ 页面质量良好！")
else:
    print("\n⚠️ 建议修复以下问题：")
    for item in issues:
        critical_issues = [i for i in item['issues'] if '❌' in i]
        if critical_issues:
            print(f"\n  {item['file']}:")
            for issue in critical_issues:
                print(f"    - {issue}")

print("\n" + "="*70)
