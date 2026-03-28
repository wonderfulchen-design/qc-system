@echo off
chcp 65001 >nul
echo ====================================
echo QC 系统部署到 Windows Server 2025
echo ====================================
echo.

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误：请以管理员身份运行此脚本！
    echo 右键点击脚本，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [1/6] 检查 Docker 安装...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Docker 未安装！
    echo 请先安装 Docker Desktop: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
    pause
    exit /b 1
)
echo Docker 已安装 ✓
echo.

echo [2/6] 检查 Git 安装...
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Git 未安装！
    echo 请先安装 Git: https://github.com/git-for-windows/git/releases
    pause
    exit /b 1
)
echo Git 已安装 ✓
echo.

echo [3/6] 克隆代码...
if exist "qc-system" (
    echo 代码已存在，跳过克隆
) else (
    git clone https://github.com/wonderfulchen-design/qc-system.git
    if %errorLevel% neq 0 (
        echo 克隆失败！请检查网络连接
        pause
        exit /b 1
    )
)
echo 代码准备完成 ✓
echo.

echo [4/6] 进入部署目录...
cd qc-system\docker
echo.

echo [5/6] 配置环境变量...
if exist ".env" (
    echo .env 文件已存在
) else (
    echo 创建 .env 文件...
    copy .env.example .env >nul 2>&1
    echo 请编辑 .env 文件配置环境变量
    notepad .env
)
echo.

echo [6/6] 启动 Docker 服务...
docker-compose up -d
if %errorLevel% neq 0 (
    echo 启动失败！请检查 Docker 是否运行
    pause
    exit /b 1
)
echo 服务启动成功 ✓
echo.

echo ====================================
echo 部署完成！
echo ====================================
echo.
echo 访问地址：http://localhost/qc-mobile/index.html
echo 服务器地址：http://121.196.166.162/qc-mobile/index.html
echo.
echo 登录信息：
echo 用户名：admin
echo 密码：admin123
echo.
echo 常用命令：
echo 查看状态：docker-compose ps
echo 查看日志：docker-compose logs -f
echo 重启服务：docker-compose restart
echo 停止服务：docker-compose down
echo.
echo 按任意键退出...
pause >nul
