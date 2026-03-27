#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入 product_batches 数据到 Railway 数据库
"""

import pymysql
import csv

# Railway 数据库配置
RAILWAY_CONFIG = {
    'host': 'mysql.railway.internal',
    'port': 3306,
    'user': 'root',
    'password': 'XynEQoaeLXXTuvsatqGWUgrLgvaeqNtF',  # 从 Railway MySQL 服务复制你的密码
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
        
        # 读取 CSV 文件
        print("正在读取 CSV 文件...")
        with open('product_batches_data.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            success_count = 0
            error_count = 0
            
            for idx, row in enumerate(reader):
                try:
                    batch_no = row.get('波次号', '').strip()
                    factory_name = row.get('工厂', '').strip()
                    goods_no = row.get('货品编码', '').strip()
                    merchandiser = row.get('订单跟单员', '').strip() if row.get('订单跟单员') else None
                    designer = row.get('设计师', '').strip() if row.get('设计师') else None
                    
                    if not batch_no or not factory_name or not goods_no:
                        error_count += 1
                        continue
                    
                    # 检查是否已存在
                    cursor.execute("SELECT id FROM product_batches WHERE batch_no = %s", (batch_no,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新
                        cursor.execute("""
                            UPDATE product_batches 
                            SET factory_name=%s, goods_no=%s, merchandiser=%s, designer=%s
                            WHERE batch_no=%s
                        """, (factory_name, goods_no, merchandiser, designer, batch_no))
                    else:
                        # 插入
                        cursor.execute("""
                            INSERT INTO product_batches (batch_no, factory_name, goods_no, merchandiser, designer)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (batch_no, factory_name, goods_no, merchandiser, designer))
                    
                    success_count += 1
                    
                    if (idx + 1) % 100 == 0:
                        conn.commit()
                        print(f"已处理 {idx + 1} 条记录...")
                    
                except Exception as e:
                    error_count += 1
                    print(f"第 {idx + 1} 行错误：{e}")
            
            conn.commit()
            
            print(f"\n✅ 导入完成！")
            print(f"成功：{success_count} 条")
            print(f"失败：{error_count} 条")
            
            # 验证
            cursor.execute("SELECT COUNT(*) FROM product_batches")
            count = cursor.fetchone()[0]
            print(f"数据库中共有 {count} 条记录")
            
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"❌ 导入失败：{e}")
        import sys
        sys.exit(1)

if __name__ == '__main__':
    import_data()
