-- 创建评论表
DROP TABLE IF EXISTS `issue_comments`;
CREATE TABLE `issue_comments` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `issue_id` BIGINT NOT NULL COMMENT '问题 ID',
  `user_id` BIGINT NOT NULL COMMENT '用户 ID',
  `username` VARCHAR(32) NOT NULL COMMENT '用户名',
  `nickname` VARCHAR(32) COMMENT '昵称',
  `content` TEXT NOT NULL COMMENT '评论内容',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
  PRIMARY KEY (`id`),
  KEY `idx_issue_id` (`issue_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问题评论表';
