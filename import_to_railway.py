#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入 product_batches 数据到 Railway 数据库
"""

import pymysql
import sys

# Railway 数据库配置
RAILWAY_CONFIG = {
    'host': 'mysql.railway.internal',  # Railway 内部域名
    'port': 3306,
    'user': 'root',
    'password': '你的 MYSQL_ROOT_PASSWORD',  # 替换为你的密码
    'database': 'railway',
    'charset': 'utf8mb4'
}

def import_data():
    """导入数据"""
    try:
        # 连接 Railway 数据库
        print("正在连接 Railway 数据库...")
        conn = pymysql.connect(**RAILWAY_CONFIG)
        cursor = conn.cursor()
        
        # 读取 SQL 文件
        print("正在读取 SQL 文件...")
        with open('product_batches_data.sql', 'r', encoding='utf8mb4') as f:
            sql = f.read()
        
        # 执行 SQL
        print("正在导入数据...")
        cursor.execute(sql)
        conn.commit()
        
        # 验证
        cursor.execute("SELECT COUNT(*) FROM product_batches")
        count = cursor.fetchone()[0]
        print(f"✅ 导入成功！共有 {count} 条记录")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 导入失败：{e}")
        sys.exit(1)

if __name__ == '__main__':
    import_data()
