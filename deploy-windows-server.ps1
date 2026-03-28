# QC 系统部署到 Windows Server 2025 - PowerShell 脚本
# 以管理员身份运行 PowerShell 后执行此脚本

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "QC 系统部署到 Windows Server 2025" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键点击 PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/8] 检查 Docker 安装..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker 已安装：$dockerVersion" -ForegroundColor Green
    } else {
        throw "Docker 未安装"
    }
} catch {
    Write-Host "Docker 未安装！" -ForegroundColor Red
    Write-Host "正在安装 Docker Desktop..." -ForegroundColor Yellow
    $dockerInstaller = "$env:TEMP\DockerInstaller.exe"
    Invoke-WebRequest -Uri "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -OutFile $dockerInstaller
    Start-Process -FilePath $dockerInstaller -ArgumentList "install", "--quiet" -Wait
    Write-Host "Docker 安装完成！请重启服务器后重新运行此脚本" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "[2/8] 检查 Git 安装..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Git 已安装：$gitVersion" -ForegroundColor Green
    } else {
        throw "Git 未安装"
    }
} catch {
    Write-Host "Git 未安装！" -ForegroundColor Red
    Write-Host "正在安装 Git..." -ForegroundColor Yellow
    $gitInstaller = "$env:TEMP\GitInstaller.exe"
    Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe" -OutFile $gitInstaller
    Start-Process -FilePath $gitInstaller -ArgumentList "/VERYSILENT", "/NORESTART" -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "Git 安装完成！" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/8] 创建部署目录..." -ForegroundColor Yellow
$deployPath = "C:\qc-system"
if (-not (Test-Path $deployPath)) {
    New-Item -ItemType Directory -Path $deployPath | Out-Null
    Write-Host "✓ 创建目录：$deployPath" -ForegroundColor Green
} else {
    Write-Host "✓ 目录已存在：$deployPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/8] 克隆代码..." -ForegroundColor Yellow
Set-Location $deployPath
if (Test-Path "qc-system") {
    Write-Host "✓ 代码已存在，跳过克隆" -ForegroundColor Green
} else {
    git clone https://github.com/wonderfulchen-design/qc-system.git
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 代码克隆成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 代码克隆失败！请检查网络连接" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[5/8] 进入部署目录..." -ForegroundColor Yellow
Set-Location "$deployPath\qc-system\docker"
Write-Host "✓ 当前目录：$(Get-Location)" -ForegroundColor Green

Write-Host ""
Write-Host "[6/8] 配置环境变量..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env 文件已存在" -ForegroundColor Green
    Write-Host "提示：如需修改配置，请编辑 .env 文件" -ForegroundColor Cyan
} else {
    Write-Host "✗ .env 文件不存在，创建示例配置..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ 已创建 .env 文件，请编辑配置" -ForegroundColor Green
        notepad .env
    } else {
        # 创建默认配置
        $envContent = @"
# MySQL 配置
MYSQL_ROOT_PASSWORD=QcSystem2025
MYSQL_PASSWORD=QcUser2025
MYSQL_PORT=3306
MYSQL_DATABASE=qc_system
MYSQL_USER=qc_user

# JWT 配置
JWT_SECRET_KEY=qc-system-super-secret-jwt-key-2025
ACCESS_TOKEN_EXPIRE_DAYS=1

# 七牛云配置
QINIU_ACCESS_KEY=IapaWm5AODDduh4YR_MpLh4irSWwRobKZ0YfJVy5
QINIU_SECRET_KEY=CpNr64VnpSU8Hx_ESLGMOZxSCKoVyuHfmmutHh-I
QINIU_BUCKET=lswsampleimg
QINIU_DOMAIN=https://sample.yoursecret.ltd/
QINIU_PREFIX=qcImg/

# 企业微信配置
WECHAT_CORP_ID=ww8a4a238a216465e8
WECHAT_AGENT_ID=1000002
WECHAT_SECRET=W16ZiYxOHX1Ja67UupOKc_xK9P12sPm4T6BM415xAtw
WECHAT_REDIRECT_URI=http://121.196.166.162
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f5db137b-d14f-4e71-927c-e6f6d9b10ca7

# 端口配置
API_PORT=8000
HTTP_PORT=80
HTTPS_PORT=443
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✓ 已创建 .env 文件" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[7/8] 启动 Docker 服务..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 服务启动成功" -ForegroundColor Green
} else {
    Write-Host "✗ 服务启动失败！" -ForegroundColor Red
    Write-Host "请检查 Docker 是否运行" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[8/8] 配置防火墙..." -ForegroundColor Yellow
try {
    # 检查防火墙规则是否已存在
    $rules = Get-NetFirewallRule -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "QC *" }
    if ($rules) {
        Write-Host "✓ 防火墙规则已存在" -ForegroundColor Green
    } else {
        # 添加防火墙规则
        New-NetFirewallRule -DisplayName "QC HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "QC HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName "QC API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue
        Write-Host "✓ 防火墙规则已添加" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ 防火墙配置失败，请手动配置" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 等待服务启动
Write-Host "等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 查看服务状态
Write-Host "服务状态：" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "访问地址：" -ForegroundColor Green
Write-Host "  本地：http://localhost/qc-mobile/index.html" -ForegroundColor White
Write-Host "  服务器：http://121.196.166.162/qc-mobile/index.html" -ForegroundColor White
Write-Host ""
Write-Host "登录信息：" -ForegroundColor Green
Write-Host "  用户名：admin" -ForegroundColor White
Write-Host "  密码：admin123" -ForegroundColor White
Write-Host ""
Write-Host "常用命令：" -ForegroundColor Cyan
Write-Host "  查看状态：docker-compose ps" -ForegroundColor White
Write-Host "  查看日志：docker-compose logs -f" -ForegroundColor White
Write-Host "  重启服务：docker-compose restart" -ForegroundColor White
Write-Host "  停止服务：docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
