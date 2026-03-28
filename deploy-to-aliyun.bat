@echo off
chcp 65001 >nul
echo ====================================
echo QC 系统部署到阿里云 ECS
echo ====================================
echo.

:: 配置阿里云服务器信息
set ALIYUN_HOST=121.196.166.162
set ALIYUN_USER=root
set ALIYUN_PASSWORD=

echo 正在连接阿里云服务器...
echo.

:: 使用 PowerShell 执行 SSH 命令
powershell -Command "Write-Host '提示：请使用 SSH 工具连接服务器后执行以下命令：' -ForegroundColor Green; Write-Host ''; Write-Host '1. 安装 Docker:' -ForegroundColor Yellow; Write-Host 'curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun' -ForegroundColor White; Write-Host ''; Write-Host '2. 上传代码后执行:' -ForegroundColor Yellow; Write-Host 'cd qc-system/docker' -ForegroundColor White; Write-Host 'docker-compose up -d' -ForegroundColor White; Write-Host ''; Write-Host '访问地址：http://%ALIYUN_HOST%/qc-mobile/index.html' -ForegroundColor Green"

echo.
echo ====================================
echo 部署说明
echo ====================================
echo.
echo 请按以下步骤操作：
echo.
echo 1. 使用 PuTTY 或 PowerShell 连接服务器
echo    SSH 命令：ssh root@121.196.166.162
echo.
echo 2. 安装 Docker（首次部署）
echo    curl -fsSL https://get.docker.com ^| bash -s docker --mirror Aliyun
echo.
echo 3. 上传项目代码（使用 Git 或 FTP）
echo    git clone https://github.com/wonderfulchen-design/qc-system.git
echo.
echo 4. 进入部署目录
echo    cd qc-system/docker
echo.
echo 5. 启动服务
echo    docker-compose up -d
echo.
echo 6. 查看日志
echo    docker-compose logs -f
echo.
echo 7. 访问系统
echo    http://121.196.166.162/qc-mobile/index.html
echo.
echo ====================================
echo 按任意键退出...
pause >nul
