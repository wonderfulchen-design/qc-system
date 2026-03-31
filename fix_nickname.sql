-- 查看当前用户昵称
SELECT id, username, nickname, real_name FROM qc_users;

-- 方案 1: 如果 real_name 有值，将昵称更新为 real_name
UPDATE qc_users 
SET nickname = real_name 
WHERE real_name IS NOT NULL AND real_name != '';

-- 方案 2: 手动指定特定用户的昵称
-- UPDATE qc_users SET nickname = '陈荣松' WHERE username = 'chenrongsong';

-- 验证更新结果
SELECT id, username, nickname, real_name FROM qc_users;
