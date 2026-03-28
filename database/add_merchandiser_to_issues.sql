-- 为 quality_issues 表添加 merchandiser 字段
ALTER TABLE quality_issues 
ADD COLUMN merchandiser VARCHAR(32) COMMENT '订单跟单员' AFTER batch_no;

-- 验证
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'qc_system' 
  AND TABLE_NAME = 'quality_issues'
  AND COLUMN_NAME = 'merchandiser';
