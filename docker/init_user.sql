USE qc_system;

CREATE TABLE IF NOT EXISTS qc_users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(32) UNIQUE NOT NULL,
  password_hash VARCHAR(128) NOT NULL,
  real_name VARCHAR(32),
  role VARCHAR(16) DEFAULT 'qc',
  status TINYINT DEFAULT 1
);

DELETE FROM qc_users WHERE username='admin';

INSERT INTO qc_users (username, password_hash, real_name, role, status) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', '系统管理员', 'admin', 1);

SELECT id, username, real_name, role FROM qc_users;
