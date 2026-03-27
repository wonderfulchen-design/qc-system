# -*- coding: utf-8 -*-
import pymysql

# 连接数据库
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
        
        # 更新昵称
        sql = "UPDATE qc_users SET nickname = %s WHERE username = %s"
        cursor.execute(sql, ('小虾', 'admin'))
        conn.commit()
        
        # 验证
        cursor.execute("SELECT username, nickname FROM qc_users WHERE username = 'admin'")
        result = cursor.fetchone()
        print(f"更新成功：{result}")
        
finally:
    conn.close()
