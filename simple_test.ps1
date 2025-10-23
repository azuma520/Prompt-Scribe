# Simple latency test
Write-Host "Testing /start endpoint..."

$headers = @{"Content-Type" = "application/json"}
$body = '{"message": "cherry blossom girl", "user_access_level": "all-ages"}'

$startTime = Get-Date
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/inspire/start" -Method POST -Headers $headers -Body $body
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    Write-Host "SUCCESS! Duration: $duration seconds"
    Write-Host "Status: $($response.StatusCode)"
    
    $json = $response.Content | ConvertFrom-Json
    Write-Host "Session ID: $($json.session_id)"
    Write-Host "Phase: $($json.phase)"
    Write-Host "Tool Calls: $($json.metadata.total_tool_calls)"
    
    if ($duration -lt 5) {
        Write-Host "LATENCY OPTIMIZATION SUCCESS! < 5 seconds"
    } else {
        Write-Host "Still needs optimization"
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
}
