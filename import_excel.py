#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Excel 导入波次号、工厂、货品编码数据到数据库
"""

import pandas as pd
import sys
import os

# 添加数据库配置
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "mysql+pymysql://qc_user:QcUser2025@localhost:3306/qc_system"

# 创建数据库连接
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 创建基础模型
Base = declarative_base()

# 定义数据模型
class ProductBatch(Base):
    __tablename__ = 'product_batches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_no = Column(String(32), index=True, comment='波次号')
    factory_name = Column(String(64), index=True, comment='工厂名称')
    goods_no = Column(String(32), index=True, comment='货品编码')

# 创建表
Base.metadata.create_all(engine)

def import_excel_data(file_path):
    """导入 Excel 数据"""
    print(f"正在读取文件：{file_path}")
    
    # 读取 Excel
    df = pd.read_excel(file_path)
    
    print(f"读取到 {len(df)} 行数据")
    print(f"列名：{df.columns.tolist()}")
    
    # 重命名列
    df.columns = ['batch_no', 'factory_name', 'goods_no']
    
    # 导入数据
    count = 0
    for index, row in df.iterrows():
        try:
            # 检查是否已存在
            exists = session.query(ProductBatch).filter_by(
                batch_no=str(row['batch_no']),
                factory_name=str(row['factory_name']),
                goods_no=str(row['goods_no'])
            ).first()
            
            if not exists:
                product = ProductBatch(
                    batch_no=str(row['batch_no']),
                    factory_name=str(row['factory_name']),
                    goods_no=str(row['goods_no'])
                )
                session.add(product)
                count += 1
        except Exception as e:
            print(f"第 {index+1} 行导入失败：{e}")
            continue
    
    # 提交
    session.commit()
    print(f"\n[OK] 成功导入 {count} 条新数据")
    print(f"总记录数：{session.query(ProductBatch).count()}")
    
    session.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = r"C:\Users\Administrator\.openclaw\qqbot\downloads\波次号工厂货品编码_1774429944023.xlsx"
    
    import_excel_data(file_path)
