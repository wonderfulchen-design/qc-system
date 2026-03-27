SET NAMES utf8mb4;
USE qc_system;
UPDATE qc_users SET nickname = '小虾' WHERE username = 'admin';
SELECT username, nickname FROM qc_users WHERE username = 'admin';
