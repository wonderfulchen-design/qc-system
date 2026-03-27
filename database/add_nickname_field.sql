-- 添加昵称字段到用户表
ALTER TABLE `qc_users` 
ADD COLUMN `nickname` VARCHAR(32) DEFAULT NULL COMMENT '用户昵称，用于评论显示' 
AFTER `real_name`;

-- 更新现有用户的昵称为用户名（可选）
-- UPDATE `qc_users` SET `nickname` = `username` WHERE `nickname` IS NULL;
