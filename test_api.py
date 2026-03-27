# -*- coding: utf-8 -*-
"""测试 API 返回"""
import sys
sys.path.insert(0, '/app/backend')
from main import SessionLocal, ProductBatch, BatchResponse
from pydantic import ConfigDict

db = SessionLocal()
batch = db.query(ProductBatch).filter(ProductBatch.batch_no == 'FY21098').first()

if batch:
    # 使用 from_attributes
    response = BatchResponse.model_validate(batch)
    print(f"batch_no: {response.batch_no}")
    print(f"merchandiser: {response.merchandiser}")
    print(f"designer: {response.designer}")

db.close()
