# Docker 部署指南 - Synology DS223

本指南說明如何將 Marine Equipment QR System 部署至 Synology DS223 NAS。

## 前置需求

### Windows 開發環境

1. **安裝 Docker Desktop**
   - 下載: https://www.docker.com/products/docker-desktop/
   - 安裝時啟用 WSL2 後端
   - 安裝完成後重新啟動電腦

2. **驗證安裝**
   ```powershell
   docker --version
   docker buildx version
   ```

### Synology NAS

- Container Manager 套件已安裝
- 有足夠的儲存空間（建議 1GB+）

---

## 步驟 1: 構建 ARM64 映像

在專案根目錄執行：

```powershell
# 執行構建腳本
.\scripts\build-arm64.ps1
```

構建完成後，會在 `docker-images/` 目錄產生：
- `backend-arm64.tar` (~200-300 MB)
- `frontend-arm64.tar` (~50-100 MB)

### 構建選項

```powershell
# 只構建後端
.\scripts\build-arm64.ps1 -SkipFrontend

# 只構建前端
.\scripts\build-arm64.ps1 -SkipBackend

# 指定輸出目錄
.\scripts\build-arm64.ps1 -OutputDir "my-output"

# 構建完成後清理 builder
.\scripts\build-arm64.ps1 -CleanBuilder
```

---

## 步驟 2: 準備部署檔案

需要上傳至 NAS 的檔案：

| 本地路徑                                   | 說明 |
|----------|------|
| `docker-images/backend-arm64.tar` | 後端 Docker 映像 |
| `docker-images/frontend-arm64.tar` | 前端 Docker 映像 |
| `docker-compose.yml` | 服務編排配置 |
| `.env` | 環境變數（從 .env.example 複製並修改） |
| `backend/data/marine_equipment.db` | 資料庫（如需遷移現有資料） |
| `backend/uploads/*` | 上傳的檔案（如需遷移） |

---

## 步驟 3: 建立 .env 檔案

複製 `.env.example` 為 `.env` 並修改：

```bash
# 必須更換的設定
SECRET_KEY=<使用以下指令產生>
# python -c "import secrets; print(secrets.token_urlsafe(32))"

# 根據 NAS IP 修改
BACKEND_CORS_ORIGINS=["http://192.168.x.x:8080"]
QR_CODE_DOMAIN=192.168.x.x:8080
```

---

## 步驟 4: 在 NAS 建立目錄

透過 DSM File Station 建立：

```
/docker/marine-equipment/
├── data/                 # 資料庫存放
├── uploads/              # 上傳檔案存放
├── images/               # Docker 映像檔
├── docker-compose.yml
└── .env
```

---

## 步驟 5: 上傳檔案

透過 File Station 拖放上傳：

1. 將 `*.tar` 檔案上傳至 `/docker/marine-equipment/images/`
2. 將 `docker-compose.yml` 上傳至 `/docker/marine-equipment/`
3. 將 `.env` 上傳至 `/docker/marine-equipment/`
4. 將資料庫和上傳檔案（如有）上傳至對應目錄

---

## 步驟 6: 匯入 Docker 映像

1. 開啟 **Container Manager** > **映像**
2. 點擊 **新增** > **從檔案新增**
3. 選擇 `/docker/marine-equipment/images/backend-arm64.tar`
4. 等待匯入完成（可能需要幾分鐘）
5. 重複步驟匯入 `frontend-arm64.tar`

匯入後應看到：
- `marine-equipment-backend:arm64`
- `marine-equipment-frontend:arm64`

---

## 步驟 7: 建立並啟動專案

1. 開啟 **Container Manager** > **專案**
2. 點擊 **建立**
3. 設定：
   - 專案名稱：`marine-equipment`
   - 路徑：選擇 `/docker/marine-equipment`
   - 來源：選擇 **使用現有的 docker-compose.yml**
4. 點擊 **下一步** 確認設定
5. 點擊 **建置並啟動**

---

## 步驟 8: 驗證部署

等待容器啟動後：

- **前端**: `http://<NAS_IP>:8080`
- **API 文件**: `http://<NAS_IP>:8080/api/docs`
- **健康檢查**: `http://<NAS_IP>:8080/api/health`

---

## 疑難排解

### 查看容器日誌

在 Container Manager > 專案 > marine-equipment，點擊容器查看日誌。

### 常見問題

**Q: 容器無法啟動**
- 確認 `.env` 中的 `SECRET_KEY` 已設定
- 檢查 Volume 掛載路徑是否正確

**Q: 前端無法連接後端**
- 確認後端容器健康狀態
- 檢查 CORS 設定是否包含前端 URL

**Q: 資料庫錯誤**
- 確認 `/docker/marine-equipment/data/` 目錄有寫入權限
- 如遷移現有資料庫，確認檔案完整

---

## 更新部署

1. 重新執行構建腳本產生新映像
2. 上傳新的 tar 檔案至 NAS
3. 在 Container Manager 匯入新映像
4. 停止專案 > 重新建置並啟動

---

## 資源使用

| 服務 | 記憶體限制 | 預計使用 |
|------|-----------|---------|
| Backend | 512 MB | ~200 MB |
| Frontend | 128 MB | ~30 MB |
| **總計** | 640 MB | ~230 MB |

DS223 (2GB RAM) 完全足夠運行此系統。
