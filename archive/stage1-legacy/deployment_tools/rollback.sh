#!/bin/bash
# 資料庫回滾腳本
# 用於在部署失敗時快速回滾到之前版本

set -e  # 遇到錯誤立即退出

# 配置變數
APP_NAME="prompt-scribe-app"
DB_PATH="/var/lib/prompt-scribe/tags.db"
BACKUP_PATH="/var/lib/prompt-scribe/tags_backup.db"
LOG_FILE="/var/log/prompt-scribe-rollback.log"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日誌函數
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# 檢查權限
check_permissions() {
    log "檢查權限..."
    
    if [ ! -w "$(dirname "$DB_PATH")" ]; then
        log_error "沒有寫入權限: $(dirname "$DB_PATH")"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_PATH" ]; then
        log_error "找不到備份文件: $BACKUP_PATH"
        exit 1
    fi
    
    log_success "權限檢查通過"
}

# 停止應用服務
stop_service() {
    log "停止應用服務..."
    
    if systemctl is-active --quiet "$APP_NAME"; then
        systemctl stop "$APP_NAME"
        log_success "服務已停止"
    else
        log_warning "服務未運行"
    fi
}

# 執行回滾
perform_rollback() {
    log "開始回滾資料庫..."
    
    # 備份當前資料庫（以防萬一）
    if [ -f "$DB_PATH" ]; then
        cp "$DB_PATH" "${DB_PATH}.failed.$(date +%Y%m%d_%H%M%S)"
        log "當前資料庫已備份"
    fi
    
    # 恢復備份
    cp "$BACKUP_PATH" "$DB_PATH"
    log_success "資料庫回滾完成"
    
    # 設置正確的權限
    chown prompt-scribe:prompt-scribe "$DB_PATH" 2>/dev/null || true
    chmod 644 "$DB_PATH"
    log "權限設置完成"
}

# 啟動應用服務
start_service() {
    log "啟動應用服務..."
    
    systemctl start "$APP_NAME"
    
    # 等待服務啟動
    sleep 5
    
    if systemctl is-active --quiet "$APP_NAME"; then
        log_success "服務啟動成功"
    else
        log_error "服務啟動失敗"
        exit 1
    fi
}

# 驗證回滾
verify_rollback() {
    log "驗證回滾結果..."
    
    # 檢查資料庫文件
    if [ ! -f "$DB_PATH" ]; then
        log_error "資料庫文件不存在"
        return 1
    fi
    
    # 檢查服務狀態
    if ! systemctl is-active --quiet "$APP_NAME"; then
        log_error "服務未運行"
        return 1
    fi
    
    # 運行健康檢查
    if command -v python3 >/dev/null 2>&1; then
        if [ -f "stage1/deployment_tools/quick_health_check.py" ]; then
            log "運行健康檢查..."
            if python3 stage1/deployment_tools/quick_health_check.py --exit-code; then
                log_success "健康檢查通過"
            else
                log_warning "健康檢查失敗，但回滾完成"
            fi
        fi
    fi
    
    return 0
}

# 顯示回滾資訊
show_rollback_info() {
    echo
    echo "==============================================="
    echo "回滾完成"
    echo "==============================================="
    echo "資料庫路徑: $DB_PATH"
    echo "備份路徑: $BACKUP_PATH"
    echo "服務名稱: $APP_NAME"
    echo "日誌文件: $LOG_FILE"
    echo "==============================================="
    echo
    echo "請檢查以下項目："
    echo "1. 應用服務是否正常運行"
    echo "2. 資料庫功能是否正常"
    echo "3. 用戶是否可以正常使用"
    echo
}

# 主函數
main() {
    echo "==============================================="
    echo "資料庫回滾腳本"
    echo "==============================================="
    echo "開始時間: $(date)"
    echo "==============================================="
    
    # 檢查是否為 root 用戶或具有 sudo 權限
    if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
        log_error "需要 root 權限或 sudo 權限來執行此腳本"
        exit 1
    fi
    
    # 執行回滾步驟
    check_permissions
    stop_service
    perform_rollback
    start_service
    
    if verify_rollback; then
        log_success "回滾驗證成功"
        show_rollback_info
        exit 0
    else
        log_error "回滾驗證失敗"
        exit 1
    fi
}

# 錯誤處理
trap 'log_error "腳本執行失敗，請檢查日誌: $LOG_FILE"' ERR

# 執行主函數
main "$@"
