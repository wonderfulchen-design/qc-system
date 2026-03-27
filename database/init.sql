-- ============================================
-- 服装 QC 质量控制系统 - 数据库初始化脚本
-- ============================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 质检人员表
-- ============================================
DROP TABLE IF EXISTS `qc_users`;
CREATE TABLE `qc_users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(32) NOT NULL COMMENT '用户名',
  `password_hash` VARCHAR(128) NOT NULL COMMENT '密码哈希',
  `real_name` VARCHAR(32) DEFAULT NULL COMMENT '真实姓名',
  `phone` VARCHAR(16) DEFAULT NULL COMMENT '手机号',
  `email` VARCHAR(64) DEFAULT NULL COMMENT '邮箱',
  `department` VARCHAR(32) DEFAULT NULL COMMENT '部门',
  `role` VARCHAR(16) DEFAULT 'qc' COMMENT '角色：qc/manager/admin',
  `status` TINYINT DEFAULT 1 COMMENT '状态：1 启用 0 禁用',
  `avatar_url` VARCHAR(255) DEFAULT NULL COMMENT '头像 URL',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_department` (`department`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='质检人员表';

-- ============================================
-- 2. 工厂信息表
-- ============================================
DROP TABLE IF EXISTS `factories`;
CREATE TABLE `factories` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `factory_code` VARCHAR(32) NOT NULL COMMENT '工厂编码',
  `factory_name` VARCHAR(64) NOT NULL COMMENT '工厂名称',
  `contact_person` VARCHAR(32) DEFAULT NULL COMMENT '联系人',
  `contact_phone` VARCHAR(16) DEFAULT NULL COMMENT '联系电话',
  `address` VARCHAR(255) DEFAULT NULL COMMENT '地址',
  `quality_level` VARCHAR(8) DEFAULT 'C' COMMENT '质量等级：A/B/C/D',
  `cooperation_status` TINYINT DEFAULT 1 COMMENT '合作状态：1 正常 0 暂停',
  `total_orders` INT DEFAULT 0 COMMENT '总订单数',
  `total_issues` INT DEFAULT 0 COMMENT '总问题数',
  `total_compensation` DECIMAL(12,2) DEFAULT 0 COMMENT '总补偿金额',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_factory_code` (`factory_code`),
  KEY `idx_quality_level` (`quality_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工厂信息表';

-- ============================================
-- 3. 售后质量问题记录表
-- ============================================
DROP TABLE IF EXISTS `quality_issues`;
CREATE TABLE `quality_issues` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `issue_no` VARCHAR(32) NOT NULL COMMENT '问题编号',
  `source_system` VARCHAR(32) DEFAULT 'after_sales' COMMENT '来源系统',
  
  -- 订单信息
  `order_no` VARCHAR(64) DEFAULT NULL COMMENT '交易单号',
  `sku_no` VARCHAR(32) DEFAULT NULL COMMENT '商家编号/SKU',
  `platform` VARCHAR(16) DEFAULT NULL COMMENT '销售平台：天猫/淘宝/抖音/小店',
  `buyer_wangwang` VARCHAR(64) DEFAULT NULL COMMENT '买家旺旺 ID',
  
  -- 问题信息
  `issue_type` VARCHAR(32) NOT NULL COMMENT '问题类型',
  `issue_desc` TEXT COMMENT '问题描述',
  `solution_type` VARCHAR(32) DEFAULT NULL COMMENT '解决方式',
  `compensation_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '补偿金额',
  
  -- 生产信息
  `factory_id` BIGINT DEFAULT NULL COMMENT '工厂 ID',
  `factory_name` VARCHAR(64) DEFAULT NULL COMMENT '工厂名称',
  `batch_no` VARCHAR(32) DEFAULT NULL COMMENT '波次号',
  `pattern_batch` VARCHAR(32) DEFAULT NULL COMMENT '版型波次',
  `designer` VARCHAR(32) DEFAULT NULL COMMENT '设计师',
  
  -- 处理信息
  `handler` VARCHAR(32) DEFAULT NULL COMMENT '处理人',
  `batch_source` VARCHAR(32) DEFAULT NULL COMMENT '波次来源：客服添加/同步波次',
  `status` VARCHAR(16) DEFAULT 'pending' COMMENT '状态：pending/processing/resolved/closed',
  
  -- 图片
  `product_image` VARCHAR(255) DEFAULT NULL COMMENT '商品图 URL',
  `issue_images` JSON DEFAULT NULL COMMENT '问题图数组',
  
  -- 时间
  `created_at` DATETIME DEFAULT NULL COMMENT '添加时间 (原始)',
  `imported_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '导入时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_issue_no` (`issue_no`),
  KEY `idx_factory` (`factory_name`),
  KEY `idx_issue_type` (`issue_type`),
  KEY `idx_platform` (`platform`),
  KEY `idx_created` (`created_at`),
  KEY `idx_status` (`status`),
  KEY `idx_batch` (`batch_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='售后质量问题记录表';

-- ============================================
-- 4. QC 检验记录表
-- ============================================
DROP TABLE IF EXISTS `qc_inspections`;
CREATE TABLE `qc_inspections` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `inspection_no` VARCHAR(32) NOT NULL COMMENT '检验单号',
  
  -- 检验人员
  `qc_user_id` BIGINT NOT NULL COMMENT '质检员 ID',
  `qc_user_name` VARCHAR(32) DEFAULT NULL COMMENT '质检员姓名',
  
  -- 检验对象
  `factory_id` BIGINT DEFAULT NULL COMMENT '工厂 ID',
  `factory_name` VARCHAR(64) DEFAULT NULL COMMENT '工厂名称',
  `batch_no` VARCHAR(32) DEFAULT NULL COMMENT '波次号',
  `sku_no` VARCHAR(32) DEFAULT NULL COMMENT '款号',
  
  -- 检验信息
  `inspect_date` DATE NOT NULL COMMENT '检验日期',
  `inspect_location` VARCHAR(128) DEFAULT NULL COMMENT '检验地点',
  `total_pieces` INT DEFAULT 0 COMMENT '检验总件数',
  `passed_pieces` INT DEFAULT 0 COMMENT '合格件数',
  `failed_pieces` INT DEFAULT 0 COMMENT '不合格件数',
  `pass_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '合格率',
  
  -- 发现问题
  `issues_found` JSON DEFAULT NULL COMMENT '发现问题列表',
  `issue_summary` TEXT COMMENT '问题摘要',
  
  -- 图片证据
  `inspect_images` JSON DEFAULT NULL COMMENT '检验照片',
  
  -- 状态
  `status` VARCHAR(16) DEFAULT 'completed' COMMENT '状态：draft/completed/submitted',
  `remark` TEXT COMMENT '备注',
  
  -- 时间
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_inspection_no` (`inspection_no`),
  KEY `idx_qc_user` (`qc_user_id`),
  KEY `idx_factory` (`factory_name`),
  KEY `idx_date` (`inspect_date`),
  KEY `idx_batch` (`batch_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='QC 检验记录表';

-- ============================================
-- 5. 检验问题明细表
-- ============================================
DROP TABLE IF EXISTS `qc_inspection_details`;
CREATE TABLE `qc_inspection_details` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `inspection_id` BIGINT NOT NULL COMMENT '检验单 ID',
  
  `issue_type` VARCHAR(32) NOT NULL COMMENT '问题类型',
  `issue_desc` VARCHAR(255) DEFAULT NULL COMMENT '问题描述',
  `severity` VARCHAR(8) DEFAULT 'minor' COMMENT '严重程度：critical/major/minor',
  `piece_count` INT DEFAULT 1 COMMENT '涉及件数',
  `image_url` VARCHAR(255) DEFAULT NULL COMMENT '问题图片',
  
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  KEY `idx_inspection` (`inspection_id`),
  KEY `idx_issue_type` (`issue_type`),
  CONSTRAINT `fk_inspection_detail` FOREIGN KEY (`inspection_id`) REFERENCES `qc_inspections` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验问题明细表';

-- ============================================
-- 6. QC 月度考核统计表
-- ============================================
DROP TABLE IF EXISTS `qc_monthly_stats`;
CREATE TABLE `qc_monthly_stats` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  
  -- 人员信息
  `qc_user_id` BIGINT NOT NULL COMMENT '质检员 ID',
  `qc_user_name` VARCHAR(32) DEFAULT NULL COMMENT '质检员姓名',
  `stat_month` DATE NOT NULL COMMENT '统计月份 (第一天)',
  
  -- 工作量
  `total_inspections` INT DEFAULT 0 COMMENT '总检验次数',
  `total_pieces` INT DEFAULT 0 COMMENT '总检验件数',
  `avg_pieces_per_day` DECIMAL(8,2) DEFAULT 0 COMMENT '日均检验件数',
  
  -- 质量指标
  `issues_found` INT DEFAULT 0 COMMENT '发现问题数',
  `issue_discovery_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '问题发现率',
  `missed_issues` INT DEFAULT 0 COMMENT '漏检问题数',
  `miss_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '漏检率',
  
  -- 时效指标
  `avg_response_hours` DECIMAL(6,2) DEFAULT 0 COMMENT '平均响应时长 (小时)',
  `on_time_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '及时率',
  
  -- 数据质量
  `data_completeness` DECIMAL(5,2) DEFAULT 0 COMMENT '数据完整率',
  
  -- 综合评分
  `quality_score` DECIMAL(5,2) DEFAULT 0 COMMENT '质量评分',
  `rank` INT DEFAULT 0 COMMENT '排名',
  `rank_total` INT DEFAULT 0 COMMENT '参与排名人数',
  
  -- 绩效等级
  `performance_level` VARCHAR(8) DEFAULT 'C' COMMENT '绩效等级：S/A/B/C/D',
  
  -- 时间
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_month` (`qc_user_id`, `stat_month`),
  KEY `idx_month` (`stat_month`),
  KEY `idx_score` (`quality_score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='QC 月度考核统计表';

-- ============================================
-- 7. 工厂质量档案表
-- ============================================
DROP TABLE IF EXISTS `factory_quality_profiles`;
CREATE TABLE `factory_quality_profiles` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `factory_id` BIGINT DEFAULT NULL COMMENT '工厂 ID',
  `factory_name` VARCHAR(64) NOT NULL COMMENT '工厂名称',
  `stat_month` DATE NOT NULL COMMENT '统计月份',
  
  -- 订单数据
  `total_orders` INT DEFAULT 0 COMMENT '总订单数',
  `total_pieces` INT DEFAULT 0 COMMENT '总件数',
  
  -- 质量数据
  `total_issues` INT DEFAULT 0 COMMENT '总问题数',
  `issue_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '问题率',
  `total_compensation` DECIMAL(12,2) DEFAULT 0 COMMENT '总补偿金额',
  
  -- 问题类型分布
  `issue_type_distribution` JSON DEFAULT NULL COMMENT '问题类型分布',
  
  -- 主要问题
  `top_issues` JSON DEFAULT NULL COMMENT 'TOP 问题列表',
  
  -- 质量等级
  `quality_level` VARCHAR(8) DEFAULT 'C' COMMENT '质量等级：A/B/C/D',
  `level_change` VARCHAR(8) DEFAULT '-' COMMENT '等级变化：+/=/-',
  
  -- 时间
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_factory_month` (`factory_name`, `stat_month`),
  KEY `idx_month` (`stat_month`),
  KEY `idx_quality_level` (`quality_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工厂质量档案表';

-- ============================================
-- 8. 系统配置表
-- ============================================
DROP TABLE IF EXISTS `system_configs`;
CREATE TABLE `system_configs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `config_key` VARCHAR(64) NOT NULL COMMENT '配置键',
  `config_value` TEXT COMMENT '配置值',
  `config_type` VARCHAR(16) DEFAULT 'string' COMMENT '配置类型',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '描述',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- ============================================
-- 9. 操作日志表
-- ============================================
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT DEFAULT NULL COMMENT '操作人 ID',
  `user_name` VARCHAR(32) DEFAULT NULL COMMENT '操作人姓名',
  `action` VARCHAR(64) NOT NULL COMMENT '操作类型',
  `module` VARCHAR(32) DEFAULT NULL COMMENT '模块',
  `target_id` BIGINT DEFAULT NULL COMMENT '目标 ID',
  `target_type` VARCHAR(32) DEFAULT NULL COMMENT '目标类型',
  `old_value` JSON DEFAULT NULL COMMENT '旧值',
  `new_value` JSON DEFAULT NULL COMMENT '新值',
  `ip_address` VARCHAR(45) DEFAULT NULL COMMENT 'IP 地址',
  `user_agent` VARCHAR(255) DEFAULT NULL COMMENT '用户代理',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_action` (`action`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- ============================================
-- 初始化数据
-- ============================================

-- 默认管理员账号 (密码需要哈希，这里仅为示例)
INSERT INTO `qc_users` (`username`, `password_hash`, `real_name`, `role`, `status`) 
VALUES ('admin', '$2b$12$placeholder_hash', '系统管理员', 'admin', 1);

-- 系统配置
INSERT INTO `system_configs` (`config_key`, `config_value`, `description`) VALUES
('qc.miss_rate_threshold', '2.0', '漏检率阈值 (%)'),
('qc.issue_discovery_target', '5.0', '问题发现率目标 (%)'),
('qc.response_time_target', '4.0', '响应时效目标 (小时)'),
('factory.issue_rate_a', '1.0', 'A 级工厂问题率上限 (%)'),
('factory.issue_rate_b', '3.0', 'B 级工厂问题率上限 (%)'),
('factory.issue_rate_c', '5.0', 'C 级工厂问题率上限 (%)'),
('crawler.source_url', 'http://114.55.34.212:8080/afterSalesFeedback.html', '数据源 URL'),
('crawler.enabled', 'true', '爬虫开关');

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 视图：QC 考核实时统计
-- ============================================
DROP VIEW IF EXISTS `v_qc_performance`;
CREATE VIEW `v_qc_performance` AS
SELECT 
    u.id AS qc_user_id,
    u.real_name AS qc_user_name,
    u.department,
    COUNT(DISTINCT i.id) AS total_inspections,
    SUM(i.total_pieces) AS total_pieces,
    SUM(i.failed_pieces) AS total_failed,
    AVG(i.pass_rate) AS avg_pass_rate,
    COUNT(DISTINCT d.id) AS issues_found
FROM qc_users u
LEFT JOIN qc_inspections i ON u.id = i.qc_user_id
LEFT JOIN qc_inspection_details d ON i.id = d.inspection_id
WHERE u.status = 1
GROUP BY u.id, u.real_name, u.department;

-- ============================================
-- 视图：工厂质量实时统计
-- ============================================
DROP VIEW IF EXISTS `v_factory_quality`;
CREATE VIEW `v_factory_quality` AS
SELECT 
    f.id AS factory_id,
    f.factory_name,
    f.quality_level,
    COUNT(DISTINCT qi.id) AS total_issues,
    SUM(qi.compensation_amount) AS total_compensation,
    GROUP_CONCAT(DISTINCT qi.issue_type) AS issue_types
FROM factories f
LEFT JOIN quality_issues qi ON f.factory_name = qi.factory_name
WHERE f.cooperation_status = 1
GROUP BY f.id, f.factory_name, f.quality_level;
