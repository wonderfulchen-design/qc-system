# -*- coding: utf-8 -*-
"""
批量导入波次号工厂货品编码到数据库
"""

import csv
import pymysql
from datetime import datetime

# 数据库连接
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='qc_user',
    password='QcUser2025',
    database='qc_system',
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        # 设置 UTF-8 编码
        cursor.execute("SET NAMES utf8mb4")
        
        # 读取 CSV 文件
        csv_file = 'C:/Users/Administrator/.openclaw/qqbot/downloads/波次号工厂货品编码_1774587473150.csv'
        
        insert_count = 0
        update_count = 0
        error_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    batch_no = row['波次号'].strip()
                    factory_name = row['工厂'].strip()
                    goods_no = row['货品编码'].strip()
                    
                    # 检查是否已存在
                    cursor.execute("SELECT id FROM product_batches WHERE batch_no = %s", (batch_no,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有记录
                        cursor.execute("""
                            UPDATE product_batches 
                            SET factory_name = %s, goods_no = %s 
                            WHERE batch_no = %s
                        """, (factory_name, goods_no, batch_no))
                        update_count += 1
                    else:
                        # 插入新记录
                        cursor.execute("""
                            INSERT INTO product_batches (batch_no, factory_name, goods_no)
                            VALUES (%s, %s, %s)
                        """, (batch_no, factory_name, goods_no))
                        insert_count += 1
                    
                    # 每 100 条提交一次
                    if (insert_count + update_count) % 100 == 0:
                        conn.commit()
                        
                except Exception as e:
                    error_count += 1
                    print(f"错误：{batch_no} - {e}")
        
        # 最后提交
        conn.commit()
        
        print(f"\n导入完成！")
        print(f"新增：{insert_count} 条")
        print(f"更新：{update_count} 条")
        print(f"错误：{error_count} 条")
        print(f"总计：{insert_count + update_count + error_count} 条")
        
finally:
    conn.close()
