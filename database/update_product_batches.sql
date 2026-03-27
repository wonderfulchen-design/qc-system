-- 在 product_batches 表中添加订单跟单员和设计师字段
ALTER TABLE `product_batches` 
ADD COLUMN `merchandiser` VARCHAR(32) DEFAULT NULL COMMENT '订单跟单员' 
AFTER `goods_no`,
ADD COLUMN `designer` VARCHAR(32) DEFAULT NULL COMMENT '设计师' 
AFTER `merchandiser`;

-- 确保使用 UTF-8 编码
ALTER TABLE `product_batches` 
CONVERT TO CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
