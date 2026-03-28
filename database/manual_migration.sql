-- ====================================
-- QC System 数据库迁移脚本
-- 执行时间：2026-03-28
-- ====================================

-- 添加 merchandiser 字段（订单跟单员）
ALTER TABLE quality_issues 
ADD COLUMN merchandiser VARCHAR(32) COMMENT '订单跟单员' AFTER batch_no;

-- 添加 designer 字段（设计师）
ALTER TABLE quality_issues 
ADD COLUMN designer VARCHAR(32) COMMENT '设计师' AFTER merchandiser;

-- 验证字段已添加
DESCRIBE quality_issues;

-- 查看结果
SELECT 
    COLUMN_NAME AS '字段名',
    DATA_TYPE AS '类型',
    CHARACTER_MAXIMUM_LENGTH AS '长度',
    COLUMN_COMMENT AS '注释'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'railway' 
  AND TABLE_NAME = 'quality_issues'
  AND COLUMN_NAME IN ('merchandiser', 'designer');

-- 完成
SELECT '✅ 数据库迁移完成！' AS '状态';
