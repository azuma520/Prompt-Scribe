#!/bin/bash
# 資料庫部署腳本
# 安全地部署新版本的 tags.db 到生產環境

set -e  # 遇到錯誤立即退出

# 配置變數
APP_NAME="prompt-scribe-app"
DB_PATH="/var/lib/prompt-scribe/tags.db"
BACKUP_DIR="/var/lib/prompt-scribe/backups"
NEW_DB_PATH="output/tags.db"  # 新資料庫路徑
LOG_FILE="/var/log/prompt-scribe-deploy.log"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_info() {
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# 檢查前置條件
check_prerequisites() {
    log "檢查部署前置條件..."
    
    # 檢查新資料庫文件
    if [ ! -f "$NEW_DB_PATH" ]; then
        log_error "找不到新資料庫文件: $NEW_DB_PATH"
        exit 1
    fi
    
    # 檢查目標目錄
    if [ ! -d "$(dirname "$DB_PATH")" ]; then
        log_error "目標目錄不存在: $(dirname "$DB_PATH")"
        exit 1
    fi
    
    # 創建備份目錄
    mkdir -p "$BACKUP_DIR"
    
    # 檢查權限
    if [ ! -w "$(dirname "$DB_PATH")" ]; then
        log_error "沒有寫入權限: $(dirname "$DB_PATH")"
        exit 1
    fi
    
    log_success "前置條件檢查通過"
}

# 創建備份
create_backup() {
    log "創建資料庫備份..."
    
    local backup_file="$BACKUP_DIR/tags_backup_$(date +%Y%m%d_%H%M%S).db"
    
    if [ -f "$DB_PATH" ]; then
        cp "$DB_PATH" "$backup_file"
        log_success "備份創建成功: $backup_file"
        
        # 創建符號連結指向最新備份
        ln -sf "$backup_file" "$(dirname "$DB_PATH")/tags_backup.db"
        log_info "備份連結已更新"
    else
        log_warning "沒有找到現有資料庫文件，跳過備份"
    fi
    
    echo "$backup_file"
}

# 驗證新資料庫
validate_new_database() {
    log "驗證新資料庫..."
    
    if [ ! -f "stage1/deployment_tools/quick_health_check.py" ]; then
        log_warning "找不到健康檢查腳本，跳過驗證"
        return 0
    fi
    
    # 臨時複製新資料庫進行驗證
    local temp_db="/tmp/tags_validation.db"
    cp "$NEW_DB_PATH" "$temp_db"
    
    if python3 stage1/deployment_tools/quick_health_check.py --db-path "$temp_db" --exit-code; then
        log_success "新資料庫驗證通過"
        rm -f "$temp_db"
        return 0
    else
        log_error "新資料庫驗證失敗"
        rm -f "$temp_db"
        return 1
    fi
}

# 停止應用服務
stop_service() {
    log "停止應用服務..."
    
    if systemctl is-active --quiet "$APP_NAME"; then
        systemctl stop "$APP_NAME"
        log_success "服務已停止"
        
        # 等待服務完全停止
        sleep 3
    else
        log_warning "服務未運行"
    fi
}

# 部署新資料庫
deploy_database() {
    log "部署新資料庫..."
    
    # 複製新資料庫
    cp "$NEW_DB_PATH" "$DB_PATH"
    log_success "資料庫文件已複製"
    
    # 設置正確的權限
    chown prompt-scribe:prompt-scribe "$DB_PATH" 2>/dev/null || true
    chmod 644 "$DB_PATH"
    log_info "權限設置完成"
    
    # 驗證文件
    if [ -f "$DB_PATH" ] && [ -r "$DB_PATH" ]; then
        local db_size=$(du -h "$DB_PATH" | cut -f1)
        log_info "資料庫大小: $db_size"
    else
        log_error "資料庫文件部署失敗"
        exit 1
    fi
}

# 啟動應用服務
start_service() {
    log "啟動應用服務..."
    
    systemctl start "$APP_NAME"
    log_info "服務啟動命令已執行"
    
    # 等待服務啟動
    log "等待服務啟動..."
    sleep 5
    
    # 檢查服務狀態
    local max_attempts=12  # 最多等待 60 秒
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if systemctl is-active --quiet "$APP_NAME"; then
            log_success "服務啟動成功"
            return 0
        fi
        
        log_info "等待服務啟動... ($((attempt + 1))/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    log_error "服務啟動超時"
    return 1
}

# 部署後驗證
post_deployment_verification() {
    log "執行部署後驗證..."
    
    # 運行健康檢查
    if [ -f "stage1/deployment_tools/quick_health_check.py" ]; then
        log "運行健康檢查..."
        if python3 stage1/deployment_tools/quick_health_check.py --db-path "$DB_PATH" --exit-code; then
            log_success "健康檢查通過"
        else
            log_warning "健康檢查失敗，但部署完成"
            return 1
        fi
    fi
    
    # 檢查服務狀態
    if ! systemctl is-active --quiet "$APP_NAME"; then
        log_error "服務未正常運行"
        return 1
    fi
    
    # 檢查資料庫連接
    if [ -f "stage1/check_db_status.py" ]; then
        log "檢查資料庫狀態..."
        python3 stage1/check_db_status.py > /dev/null 2>&1 || log_warning "資料庫狀態檢查失敗"
    fi
    
    log_success "部署後驗證完成"
    return 0
}

# 顯示部署資訊
show_deployment_info() {
    echo
    echo "==============================================="
    echo "部署完成"
    echo "==============================================="
    echo "新資料庫路徑: $DB_PATH"
    echo "備份目錄: $BACKUP_DIR"
    echo "服務名稱: $APP_NAME"
    echo "日誌文件: $LOG_FILE"
    echo "部署時間: $(date)"
    echo "==============================================="
    echo
    echo "請檢查以下項目："
    echo "1. 應用服務是否正常運行"
    echo "2. 資料庫功能是否正常"
    echo "3. 用戶是否可以正常使用"
    echo "4. 監控數據是否正常"
    echo
    echo "如需回滾，請執行: ./stage1/deployment_tools/rollback.sh"
    echo
}

# 主函數
main() {
    echo "==============================================="
    echo "資料庫部署腳本"
    echo "==============================================="
    echo "開始時間: $(date)"
    echo "新資料庫: $NEW_DB_PATH"
    echo "目標路徑: $DB_PATH"
    echo "==============================================="
    
    # 檢查是否為 root 用戶或具有 sudo 權限
    if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
        log_error "需要 root 權限或 sudo 權限來執行此腳本"
        exit 1
    fi
    
    # 執行部署步驟
    check_prerequisites
    
    local backup_file
    backup_file=$(create_backup)
    
    if ! validate_new_database; then
        log_error "新資料庫驗證失敗，停止部署"
        exit 1
    fi
    
    stop_service
    deploy_database
    
    if ! start_service; then
        log_error "服務啟動失敗，開始回滾"
        if [ -f "$backup_file" ]; then
            cp "$backup_file" "$DB_PATH"
            systemctl start "$APP_NAME"
            log_warning "已回滾到備份版本"
        fi
        exit 1
    fi
    
    if post_deployment_verification; then
        log_success "部署驗證成功"
        show_deployment_info
        exit 0
    else
        log_warning "部署驗證失敗，但服務已啟動"
        show_deployment_info
        exit 1
    fi
}

# 錯誤處理
trap 'log_error "部署腳本執行失敗，請檢查日誌: $LOG_FILE"' ERR

# 執行主函數
main "$@"
