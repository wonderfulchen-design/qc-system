# QC System 快速启动脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  QC Quality Management System" -ForegroundColor Cyan
Write-Host "  快速启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$WORKSPACE = "C:\Users\Administrator\.openclaw\workspace"
$BACKEND_DIR = "$WORKSPACE\qc-system\backend"
$DB_INIT = "$WORKSPACE\qc-system\database\init_with_admin.sql"

# 1. 检查 MySQL
Write-Host "[1/4] 检查 MySQL 服务..." -ForegroundColor Yellow
$mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue
if ($mysqlService) {
    Write-Host "  MySQL 服务：$($mysqlService.Name) - $($mysqlService.Status)" -ForegroundColor Green
    if ($mysqlService.Status -eq "Stopped") {
        Write-Host "  启动 MySQL 服务..." -ForegroundColor Yellow
        Start-Service $mysqlService.Name
        Start-Sleep -Seconds 3
    }
} else {
    Write-Host "  未找到 MySQL 服务！" -ForegroundColor Red
    Write-Host "  请先安装 MySQL 或启动 Docker" -ForegroundColor Red
    exit 1
}

# 2. 初始化数据库（如果不存在）
Write-Host ""
Write-Host "[2/4] 检查数据库..." -ForegroundColor Yellow
$checkDb = mysql -u root -e "SHOW DATABASES LIKE 'qc_system';" 2>$null
if ($checkDb) {
    Write-Host "  数据库 qc_system 已存在" -ForegroundColor Green
} else {
    Write-Host "  初始化数据库..." -ForegroundColor Yellow
    mysql -u root -p < $DB_INIT 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  数据库初始化成功！" -ForegroundColor Green
    } else {
        Write-Host "  数据库初始化失败，请手动执行：mysql -u root -p < $DB_INIT" -ForegroundColor Red
    }
}

# 3. 创建上传目录
Write-Host ""
Write-Host "[3/4] 创建上传目录..." -ForegroundColor Yellow
$uploadDir = "$BACKEND_DIR\uploads"
if (!(Test-Path $uploadDir)) {
    New-Item -ItemType Directory -Path $uploadDir -Force | Out-Null
    Write-Host "  目录已创建：$uploadDir" -ForegroundColor Green
} else {
    Write-Host "  目录已存在：$uploadDir" -ForegroundColor Green
}

# 4. 启动后端服务
Write-Host ""
Write-Host "[4/4] 启动后端服务..." -ForegroundColor Yellow
Write-Host "  工作目录：$BACKEND_DIR" -ForegroundColor Cyan
Write-Host "  访问地址：http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API 文档：http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $BACKEND_DIR
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
