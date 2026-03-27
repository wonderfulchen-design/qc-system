# QC System Railway 部署脚本
# 在 PowerShell 中执行：powershell -ExecutionPolicy Bypass -File deploy-railway.ps1

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  QC System Railway 部署助手" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 git
Write-Host "[1/5] 检查 Git..." -ForegroundColor Yellow
try {
    git --version | Out-Null
    Write-Host "  ✓ Git 已安装" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 未安装 Git，请先安装：https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# 2. 初始化仓库
Write-Host ""
Write-Host "[2/5] 初始化 Git 仓库..." -ForegroundColor Yellow
Set-Location "C:\Users\Administrator\.openclaw\workspace\qc-system"

if (!(Test-Path ".git")) {
    git init
    Write-Host "  ✓ Git 仓库已初始化" -ForegroundColor Green
} else {
    Write-Host "  ✓ Git 仓库已存在" -ForegroundColor Green
}

# 3. 添加文件
Write-Host ""
Write-Host "[3/5] 添加文件..." -ForegroundColor Yellow
git add .
git commit -m "Ready for Railway deployment"
Write-Host "  ✓ 文件已提交" -ForegroundColor Green

# 4. 提示创建 GitHub 仓库
Write-Host ""
Write-Host "[4/5] 创建 GitHub 仓库" -ForegroundColor Yellow
Write-Host ""
Write-Host "  请在浏览器打开：" -ForegroundColor Cyan
Write-Host "  https://github.com/new" -ForegroundColor White
Write-Host ""
Write-Host "  填写：" -ForegroundColor Cyan
Write-Host "  Repository name: qc-system" -ForegroundColor White
Write-Host "  选择：Public 或 Private" -ForegroundColor White
Write-Host "  点击：Create repository" -ForegroundColor White
Write-Host ""

$githubUser = Read-Host "  输入你的 GitHub 用户名"

if ($githubUser) {
    Write-Host ""
    Write-Host "[5/5] 推送代码到 GitHub..." -ForegroundColor Yellow
    
    # 检查是否已有 remote
    $remote = git remote get-url origin 2>$null
    if (!$remote) {
        git remote add origin "https://github.com/$githubUser/qc-system.git"
    }
    
    git branch -M main
    git push -u origin main
    
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "  ✓ 代码已推送到 GitHub！" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  仓库地址：" -ForegroundColor Cyan
    Write-Host "  https://github.com/$githubUser/qc-system" -ForegroundColor White
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "  下一步：" -ForegroundColor Cyan
    Write-Host "  1. 返回 Railway 页面" -ForegroundColor White
    Write-Host "  2. 点击 'Deploy from GitHub repo'" -ForegroundColor White
    Write-Host "  3. 选择 'qc-system' 仓库" -ForegroundColor White
    Write-Host "  4. 点击 'Deploy'" -ForegroundColor White
    Write-Host "====================================" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "按回车键退出"
