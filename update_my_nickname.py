#!/usr/bin/env python3
"""
手动更新特定用户的昵称为中文名
用法：python update_my_nickname.py <username> <chinese_nickname>
"""

import os
import sys
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'qc_user'),
    'password': os.getenv('DB_PASSWORD', 'QcUser2025'),
    'database': os.getenv('DB_NAME', 'qc_system')
}

def update_nickname(username, chinese_nickname):
    """更新指定用户的昵称"""
    
    try:
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG, charset='utf8mb4')
        cursor = conn.cursor()
        
        # 更新昵称
        sql = "UPDATE qc_users SET nickname = %s WHERE username = %s"
        affected = cursor.execute(sql, (chinese_nickname, username))
        
        conn.commit()
        
        if affected > 0:
            print(f"✅ 成功更新用户 '{username}' 的昵称为 '{chinese_nickname}'")
        else:
            print(f"⚠️  未找到用户 '{username}'")
        
        # 验证更新
        cursor.execute("SELECT username, nickname, real_name FROM qc_users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            print(f"   当前状态：username={result[0]}, nickname={result[1]}, real_name={result[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误：{e}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        nickname = sys.argv[2]
        update_nickname(username, nickname)
    else:
        print("用法：python update_my_nickname.py <username> <chinese_nickname>")
        print("示例：python update_my_nickname.py chenrongsong 陈荣松")
