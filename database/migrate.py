#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
在应用启动时自动执行数据库迁移
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

def migrate_database():
    """执行数据库迁移"""
    
    # 获取数据库连接 URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ 错误：DATABASE_URL 环境变量未设置")
        return False
    
    try:
        # 创建数据库引擎
        engine = create_engine(database_url)
        
        # 检查 quality_issues 表是否存在 merchandiser 字段
        inspector = inspect(engine)
        
        if not inspector.has_table('quality_issues'):
            print("⚠️ quality_issues 表不存在，跳过迁移")
            return True
        
        # 获取表列信息
        columns = [col['name'] for col in inspector.get_columns('quality_issues')]
        
        # 检查是否需要添加 merchandiser 字段
        if 'merchandiser' not in columns:
            print("📝 添加 merchandiser 字段...")
            with engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE quality_issues "
                    "ADD COLUMN merchandiser VARCHAR(32) COMMENT '订单跟单员' AFTER batch_no"
                ))
                conn.commit()
            print("✅ merchandiser 字段添加成功")
        else:
            print("✅ merchandiser 字段已存在")
        
        # 检查是否需要添加 designer 字段
        if 'designer' not in columns:
            print("📝 添加 designer 字段...")
            with engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE quality_issues "
                    "ADD COLUMN designer VARCHAR(32) COMMENT '设计师' AFTER merchandiser"
                ))
                conn.commit()
            print("✅ designer 字段添加成功")
        else:
            print("✅ designer 字段已存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        return False


if __name__ == "__main__":
    print("🚀 开始数据库迁移...")
    success = migrate_database()
    
    if success:
        print("✅ 数据库迁移完成")
        sys.exit(0)
    else:
        print("❌ 数据库迁移失败")
        sys.exit(1)
