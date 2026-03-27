# 测试问题详情 API
$ErrorActionPreference = "Stop"

try {
    # 1. 登录
    Write-Host "1. 登录..." -ForegroundColor Cyan
    $login = Invoke-RestMethod -Uri "http://localhost:8000/token" -Method Post -Body "username=admin&password=admin123"
    $token = $login.access_token
    Write-Host "   登录成功！" -ForegroundColor Green
    $headers = @{ Authorization = "Bearer $token" }

    # 2. 获取问题列表
    Write-Host "`n2. 获取问题列表..." -ForegroundColor Cyan
    $issues = Invoke-RestMethod -Uri "http://localhost:8000/api/issues?page=1&page_size=5" -Headers $headers
    Write-Host "   总数：$($issues.total)" -ForegroundColor Green
    
    if ($issues.data.Count -gt 0) {
        $firstIssue = $issues.data[0]
        Write-Host "   第一个问题：$($firstIssue.issue_no)" -ForegroundColor Yellow
        
        # 3. 尝试获取问题详情（使用 issue_no）
        Write-Host "`n3. 获取问题详情 (通过 issue_no)..." -ForegroundColor Cyan
        try {
            $detail = Invoke-RestMethod -Uri "http://localhost:8000/api/issues-by-no/$($firstIssue.issue_no)" -Headers $headers
            Write-Host "   ✅ 成功获取详情！" -ForegroundColor Green
            Write-Host "   问题编号：$($detail.issue_no)" -ForegroundColor White
            Write-Host "   状态：$($detail.status)" -ForegroundColor White
            Write-Host "   工厂：$($detail.factory_name)" -ForegroundColor White
        } catch {
            Write-Host "   ❌ 失败：$($_.Exception.Message)" -ForegroundColor Red
            Write-Host "   响应：$($_.ErrorDetails.Message)" -ForegroundColor Red
        }
        
        # 4. 尝试获取问题详情（使用数字 ID - 旧方式）
        Write-Host "`n4. 获取问题详情 (通过数字 ID - 可能不兼容)..." -ForegroundColor Cyan
        try {
            $detailById = Invoke-RestMethod -Uri "http://localhost:8000/api/issues/$($firstIssue.id)" -Headers $headers
            Write-Host "   ✅ 成功获取详情！" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ 失败：$($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "   没有数据" -ForegroundColor Yellow
    }
} catch {
    Write-Host "错误：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host "详情：$($_.ErrorDetails.Message)" -ForegroundColor Red
}
