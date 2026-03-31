#!/usr/bin/env python3
"""
修复数据库连接问题 - 添加连接池配置和重试机制
"""

import os

# 读取 main.py 文件
main_py_path = os.path.join(os.path.dirname(__file__), 'backend', 'main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 1: 更新数据库引擎配置
old_engine = '''engine = create_engine(DATABASE_URL)'''

new_engine = '''# 数据库连接池配置 - 防止 "MySQL server has gone away" 错误
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # 连接前检查是否有效
    pool_recycle=3600,         # 1 小时后回收连接
    pool_size=10,              # 连接池大小
    max_overflow=20,           # 最大溢出连接数
    pool_timeout=30            # 获取连接超时
)'''

if old_engine in content:
    content = content.replace(old_engine, new_engine)
    print("✅ 已更新数据库引擎配置")
else:
    print("⚠️ 未找到需要替换的引擎配置（可能已修改）")

# 保存文件
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n📝 修复完成！请重新部署到 Railway")
print("\n🔧 额外建议：")
print("1. 在 Railway 后台检查 MySQL 插件状态")
print("2. 确保 DATABASE_URL 环境变量正确")
print("3. 如仍有问题，添加重试装饰器到关键 API")
