# 測試 Inspire Agent 延遲
Write-Host "開始測試 Inspire Agent 延遲..." -ForegroundColor Green

# 測試 /start 端點
Write-Host "`n測試 /start 端點..." -ForegroundColor Yellow
$headers = @{"Content-Type" = "application/json"}
$body = '{"message": "櫻花樹下的和服少女，溫柔寧靜的氛圍", "user_access_level": "all-ages"}'

$startTime = Get-Date
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/inspire/start" -Method POST -Headers $headers -Body $body
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    Write-Host "/start 成功" -ForegroundColor Green
    Write-Host "延遲: $([math]::Round($duration, 2)) 秒" -ForegroundColor Cyan
    Write-Host "狀態碼: $($response.StatusCode)" -ForegroundColor Cyan
    
    $json = $response.Content | ConvertFrom-Json
    Write-Host "Session ID: $($json.session_id)" -ForegroundColor Cyan
    Write-Host "Phase: $($json.phase)" -ForegroundColor Cyan
    Write-Host "Tool Calls: $($json.metadata.total_tool_calls)" -ForegroundColor Cyan
    
    $sessionId = $json.session_id
    
    # 測試 /continue 端點
    Write-Host "`n測試 /continue 端點..." -ForegroundColor Yellow
    $continueBody = '{"session_id": "' + $sessionId + '", "message": "choose direction 2"}'
    
    $startTime2 = Get-Date
    try {
        $response2 = Invoke-WebRequest -Uri "http://localhost:8000/api/inspire/continue" -Method POST -Headers $headers -Body $continueBody
        $endTime2 = Get-Date
        $duration2 = ($endTime2 - $startTime2).TotalSeconds
        
        Write-Host "/continue 成功" -ForegroundColor Green
        Write-Host "延遲: $([math]::Round($duration2, 2)) 秒" -ForegroundColor Cyan
        Write-Host "狀態碼: $($response2.StatusCode)" -ForegroundColor Cyan
        
        $json2 = $response2.Content | ConvertFrom-Json
        Write-Host "📝 Phase: $($json2.phase)" -ForegroundColor Cyan
        Write-Host "🔧 Tool Calls: $($json2.metadata.total_tool_calls)" -ForegroundColor Cyan
        
        # 總結
        Write-Host "`n測試總結:" -ForegroundColor Green
        Write-Host "  /start:  $([math]::Round($duration, 2)) 秒" -ForegroundColor White
        Write-Host "  /continue: $([math]::Round($duration2, 2)) 秒" -ForegroundColor White
        Write-Host "  總計: $([math]::Round($duration + $duration2, 2)) 秒" -ForegroundColor White
        
        if ($duration -lt 5 -and $duration2 -lt 5) {
            Write-Host "延遲優化成功：兩個端點都 < 5 秒" -ForegroundColor Green
        } else {
            Write-Host "延遲仍需優化" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "❌ /continue 錯誤: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "/start 錯誤: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n測試完成" -ForegroundColor Green
