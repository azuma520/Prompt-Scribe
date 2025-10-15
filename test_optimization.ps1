# 測試 API 優化效果
Write-Host "`n=== API 優化測試 ===" -ForegroundColor Cyan

# 測試 1: 標籤驗證（批量查詢優化）
Write-Host "`n1. 測試標籤驗證端點（5個標籤）" -ForegroundColor Yellow
$json = '{"tags":["1girl","solo","long_hair","breasts","looking_at_viewer"]}'

Write-Host "第一次請求（未命中快取，批量查詢）..."
$time1 = Measure-Command {
    curl.exe -s -X POST "http://127.0.0.1:8010/api/llm/validate-prompt" `
        -H "Content-Type: application/json" `
        --data-raw $json | Out-Null
}
Write-Host "耗時: $([math]::Round($time1.TotalMilliseconds, 2)) ms" -ForegroundColor Green

Write-Host "`n第二次請求（應命中快取）..."
$time2 = Measure-Command {
    curl.exe -s -X POST "http://127.0.0.1:8010/api/llm/validate-prompt" `
        -H "Content-Type: application/json" `
        --data-raw $json | Out-Null
}
Write-Host "耗時: $([math]::Round($time2.TotalMilliseconds, 2)) ms" -ForegroundColor Green

# 測試 2: 推薦端點
Write-Host "`n2. 測試推薦端點" -ForegroundColor Yellow
$json2 = '{"description":"a lonely girl in cyberpunk city","max_tags":8}'

Write-Host "第一次請求..."
$time3 = Measure-Command {
    curl.exe -s -X POST "http://127.0.0.1:8010/api/llm/recommend-tags" `
        -H "Content-Type: application/json" `
        --data-raw $json2 | Out-Null
}
Write-Host "耗時: $([math]::Round($time3.TotalMilliseconds, 2)) ms" -ForegroundColor Green

Write-Host "`n第二次請求（應命中快取）..."
$time4 = Measure-Command {
    curl.exe -s -X POST "http://127.0.0.1:8010/api/llm/recommend-tags" `
        -H "Content-Type: application/json" `
        --data-raw $json2 | Out-Null
}
Write-Host "耗時: $([math]::Round($time4.TotalMilliseconds, 2)) ms" -ForegroundColor Green

# 查看快取統計
Write-Host "`n3. 快取統計" -ForegroundColor Yellow
curl.exe -s "http://127.0.0.1:8010/cache/stats"

Write-Host "`n`n=== 優化效果總結 ===" -ForegroundColor Cyan
Write-Host "驗證端點 - 優化前: ~1,640ms (N+1 查詢)"
Write-Host "驗證端點 - 優化後: ~$([math]::Round($time1.TotalMilliseconds, 0))ms (批量查詢)"
$improvement1 = [math]::Round((1640 - $time1.TotalMilliseconds) / 1640 * 100, 1)
Write-Host "改善幅度: $improvement1%" -ForegroundColor Green

if ($time2.TotalMilliseconds -lt $time1.TotalMilliseconds) {
    $cacheImprovement = [math]::Round(($time1.TotalMilliseconds - $time2.TotalMilliseconds) / $time1.TotalMilliseconds * 100, 1)
    Write-Host "快取加速: $cacheImprovement%" -ForegroundColor Green
}

Write-Host "`n" -ForegroundColor Cyan

