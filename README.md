# 海洋設備 QR Code 管理系統

海洋調查設備資產管理系統，透過 QR Code 實現設備快速識別、狀態追蹤、校正管理等功能。

**版本**: 1.2
**狀態**: ✅ 可投入使用
**GitHub**: https://github.com/CHC1978/DG_Workshop

---

## 專案狀態

✅ **v1.0 完成** - 核心功能已全部實作並測試（85 commits）

**最新進度**:
- ✅ 認證系統 + 2FA + 記住裝置（7天）
- ✅ 設備管理（CRUD + 檔案上傳 + 狀態操作）
- ✅ **Calibration 管理**（完整工作流程）
- ✅ **ActivityLog 附件系統**
- ✅ Dashboard（時效性警報 + 最近活動）
- ✅ QR Code 管理（環境變數配置 + 掃描入口）
- ✅ 響應式 UI（Desktop/Tablet/Mobile）
- ✅ Network Mode（同網域訪問）
- ✅ **Week 2 安全強化**（httpOnly Cookies + 2FA 管理增強）
- ✅ **Week 3 安全強化**（檔案驗證 + XSS 防護 + 100MB 上傳）

---

## 技術棧

### 後端
- Python 3.12+ / FastAPI / SQLAlchemy 2.0 / SQLite (WAL mode) / Alembic
- JWT + TOTP 2FA（Google/Microsoft Authenticator）
- 57+ API Endpoints / 8 個資料表

### 前端
- Bun / Vue 3 (Composition API) / Vite / TailwindCSS / Pinia
- 13 個頁面 / 響應式設計 / PWA 支援

### 特色功能
- 🔐 雙因素認證 + 記住裝置（7天免 2FA）
- 📱 響應式設計（手機/平板友善）
- 🌐 Network Mode（同 WiFi/VPN 訪問）
- 📊 Calibration 管理（到期提醒 + 報告上傳）
- 📎 ActivityLog 附件（多種類型）
- 🏷️ QR Code 自動生成（環境變數配置）

---

## 快速開始

### 前置需求

- Python 3.12+
- Bun 1.1+
- Git
- Windows 10/11

### 🚀 一鍵啟動

#### 方式 1: 互動式控制面板（推薦）

```cmd
manage.bat
```

**選項說明**:
- `[1]` Start All - Localhost Mode（本機開發）
- `[N]` Start All - Network Mode（手機測試，選擇 IP）
- `[3]` Restart All（重新啟動）
- `[6]` Restart Backend Only（後端代碼修改後）
- `[7]` Restart Frontend Only（前端配置修改後）
- `[S]` Check Status（檢查服務狀態）
- `[0]` Exit（停止所有服務並退出）

#### 方式 2: 首次設定（僅第一次）

如果是全新環境，先執行：
```cmd
setup_first_time.bat
```

此腳本會：
- 建立 Python 虛擬環境
- 安裝所有依賴套件
- 初始化資料庫
- 建立管理員帳號（admin/admin123）

### 訪問系統

**Localhost 模式**:
```
Frontend: http://localhost:5173
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs
```

**Network 模式**（手機/平板）:
```
Frontend: http://[您的IP]:5173
Backend:  http://[您的IP]:8000
```

### 預設帳號

```
帳號: admin
密碼: admin123
```

**⚠️ 首次登入後請**:
1. 立即修改密碼
2. 設定 2FA（系統會引導）
3. 記錄 2FA 備用碼

---

## 核心功能

### 1. 設備管理
- **資產編號自動生成**（格式：MBES-2025-001）
- **8 種設備狀態**（Ordering, In Stock, Deployed, Rented, Repair, **Calibrating**, Disposed, Lost）
- **檔案管理**（照片、手冊、校正報告）
- **維護記錄**（上次/下次維護日期 + 備註）
- **狀態操作**（Deploy, Return, Repair, Send to Calibration）
- **QR Code 標籤**（自動生成 + 下載）

### 2. Calibration 管理
- **完整校正工作流程**:
  1. Send to Calibration（設備狀態 → CALIBRATING）
  2. Add Calibration（建立校正記錄）
  3. Edit Calibration（上傳校正報告 PDF）
  4. 查看報告（直接在列表點擊下載）
- **到期提醒**（逾期=紅、緊急=橙、即將=黃）
- **篩選功能**（All, Overdue, 7 days, 30 days）
- **設備搜尋**（自動完成）

### 3. ActivityLog 附件
- **點擊 log 查看附件**
- **上傳多種類型**（校正報告、受損照片、維修文件等）
- **描述與分類**
- **下載/刪除管理**
- **操作人員追蹤**
- **GPS 位置記錄**

### 4. Dashboard
- **時效性警報**:
  - 🔧 Maintenance Due（需維護）
  - 📊 Calibration Due（需校正）
  - ⏰ Overdue Rentals（逾期租賃）
- **Recent Activities**（最近 10 筆設備異動）
- **響應式設計**（手機卡片 + 桌面表格）

### 5. QR Code 系統
- **環境變數配置**（固定 IP）
- **手機相機掃描**（直接開啟連結）
- **公開資訊頁面**（/e/:assetCode）
- **GPS 掃描記錄**
- **更新工具**（update_qr_codes.py）

### 6. 安全與權限
- **雙因素認證**（TOTP）
- **httpOnly Cookies**（Token 安全儲存，防 XSS）
- **記住裝置**（7 天免 2FA）
- **2FA 管理**（Admin 可 Reset/Enable/Disable）
- **4 種角色**（Admin, Manager, Operator, Viewer）
- **操作追蹤**（誰在何時做了什麼）

#### 2FA 操作說明

| 操作 | 說明 | 效果 |
|------|------|------|
| **Disable 2FA** | 暫時停用 2FA | 保留 secret，可直接重新啟用 |
| **Enable 2FA** | 重新啟用 2FA | 使用原有 secret，無需掃描 QR |
| **Reset 2FA** | 重設 2FA | 清除 secret，需重新設定 |

---

## 專案結構

```
DG_workshop/
├── backend/                    # Python FastAPI 後端
│   ├── app/
│   │   ├── api/               # 12 個 API 檔案（57+ endpoints）
│   │   ├── core/              # config, database, security, deps
│   │   ├── models/            # 9 個資料模型（8 個資料表）
│   │   ├── schemas/           # Pydantic schemas
│   │   └── utils/             # 工具函數
│   ├── alembic/               # 11 個 migrations
│   ├── data/                  # SQLite 資料庫
│   ├── uploads/               # 檔案儲存
│   └── *.py                   # 管理工具腳本
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── api/               # 8 個 API 封裝
│       ├── components/common/ # 共用元件
│       ├── layouts/           # 版面配置
│       ├── router/            # Vue Router
│       ├── stores/            # Pinia stores
│       ├── types/             # TypeScript 型別
│       ├── utils/             # 工具函數
│       └── views/             # 13 個頁面
├── docs/                       # 11 份文件
├── manage.bat                  # 主控制面板
└── README.md                   # 本文件
```

---

## 開發指令

### 日常使用（推薦）

```cmd
manage.bat
```

選擇對應選項即可。

### 手動啟動（如需要）

#### 後端
```bash
cd backend
venv\Scripts\activate                    # Windows
python -m uvicorn app.main:app --reload --port 8000

# Network Mode (同網域訪問)
python -m uvicorn app.main:app --host 0.0.0.0 --reload --port 8000
```

#### 前端
```bash
cd frontend
bun dev                                  # Localhost
bun dev --host 0.0.0.0                  # Network Mode
```

### 資料庫管理

```bash
cd backend
venv\Scripts\activate

# Migration
alembic revision --autogenerate -m "描述"
alembic upgrade head
alembic history

# 資料管理
python list_equipment.py                 # 列出所有設備
python delete_equipment.py MBES-2025-001 # 刪除設備
python clean_and_recreate_data.py        # 清理測試資料
python update_qr_codes.py                # 更新 QR code URL
```

---

## 使用手冊

**完整使用手冊**: `docs/20251230_192855_User_Manual_v1.0.md`

**快速指南**:

### 校正工作流程
1. **送出**: Equipment 詳情 → "Send to Calibration"
2. **記錄**: Calibrations → "+ Add Calibration"
3. **報告**: Edit → 上傳 PDF
4. **查看**: Report 欄位 → 📄 View

### ActivityLog 附件
1. **查看**: 點擊 log 行或 📎 View
2. **上傳**: Modal 底部選擇檔案類型 → 上傳
3. **管理**: 下載/刪除附件

### QR Code 掃描
1. 手機相機對準 QR code
2. 點擊連結通知
3. 開啟設備資訊頁面
4. 已登入 → 完整資訊 + GPS 記錄

---

## API 文件

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

**主要 API 模組**:
- `/api/auth` - 認證（6 endpoints）
- `/api/users` - 使用者（7 endpoints）
- `/api/equipment` - 設備（11 endpoints）
- `/api/calibrations` - 校正（6 endpoints）
- `/api/uploads` - 檔案上傳（9 endpoints）
- `/api/dashboard` - 儀表板（3 endpoints）

---

## 環境變數

建立 `backend/.env`:
```env
# 應用程式
APP_NAME=Marine Equipment QR System
DEBUG=True

# 安全性
SECRET_KEY=（至少 32 字元的隨機字串）
ALGORITHM=HS256

# JWT Token
ACCESS_TOKEN_EXPIRE_MINUTES=30
TEMP_TOKEN_EXPIRE_MINUTES=5

# 資料庫
DATABASE_URL=sqlite+aiosqlite:///./data/marine_equipment.db

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# QR Code（重要！）
QR_CODE_DOMAIN=192.168.1.100:5173
QR_CODE_PROTOCOL=http
```

**⚠️ 部署時務必修改**:
- `SECRET_KEY`: 使用強密碼
- `QR_CODE_DOMAIN`: 設定實際 IP
- `DEBUG`: 生產環境改為 False

---

## 系統需求

### 軟體需求
- Python 3.12+
- Bun 1.1+
- 瀏覽器：Chrome, Edge, Firefox
- 作業系統：Windows 10/11

### 硬體建議
- RAM: 4GB+
- 硬碟: 10GB+（含檔案儲存空間）
- 網路: WiFi 或有線網路

### 瀏覽器支援
- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+（Mac/iOS）
- ✅ 手機瀏覽器（Chrome Mobile, Safari Mobile）

---

## 角色權限

| 功能 | Admin | Manager | Operator | Viewer |
|------|:-----:|:-------:|:--------:|:------:|
| 查看所有資料 | ✅ | ✅ | ✅ | ✅ |
| 新增/編輯設備 | ✅ | ✅ | ❌ | ❌ |
| 刪除設備 | ✅ | ❌ | ❌ | ❌ |
| 設備狀態操作 | ✅ | ✅ | ✅ | ❌ |
| 新增/編輯 Calibration | ✅ | ✅ | ❌ | ❌ |
| 上傳檔案 | ✅ | ✅ | ✅ | ❌ |
| 管理使用者 | ✅ | ❌ | ❌ | ❌ |
| 重設 2FA | ✅ | ❌ | ❌ | ❌ |

---

## 常見使用情境

### 情境 1: 新設備入庫
```
1. Equipment → + Add Equipment
2. 填寫基本資訊 → Create
3. 自動生成資產編號（MBES-2025-001）
4. Download QR → 列印標籤 → 貼在設備上
```

### 情境 2: 設備送校正
```
1. Equipment 詳情 → Send to Calibration
2. 設備狀態 → CALIBRATING
3. Calibrations → + Add Calibration
4. 填寫校正資訊 → Create
5. Edit → 上傳校正報告 PDF
6. 完成後改回 In Stock
```

### 情境 3: 手機查看設備
```
1. 啟動 Network Mode (manage.bat → [N])
2. 手機連同 WiFi
3. 手機相機掃描設備 QR code
4. 自動開啟設備資訊頁面
5. 登入查看完整資訊
```

### 情境 4: 記錄維修事件
```
1. Equipment 詳情 → Send to Repair
2. ActivityLog 自動記錄
3. 點擊 log 行 → 開啟附件 Modal
4. 上傳受損照片、維修報告
5. 選擇附件類型 + 描述
```

---

## 檔案上傳

### 支援的檔案類型

| 位置 | 類型 | 格式 | 大小限制 |
|------|------|------|---------|
| Equipment Photo | 圖片 | JPG, PNG, GIF, WebP | 100MB |
| Equipment Manual | 文件 | PDF, DOC, DOCX | 100MB |
| Calibration Report | PDF | PDF | 100MB |
| Log Attachments | 任意 | 所有常見格式 | 100MB |

### 檔案儲存結構
```
uploads/
  MBES-2025-001/
    photo.jpg                    # 設備照片
    manual.pdf                   # 操作手冊
    calibration_1.pdf           # 校正報告
    logs/
      5/
        1735567890_damage.jpg   # Log 附件
```

---

## 開發與部署

### 開發環境
```cmd
manage.bat → [1] Localhost Mode
```

### 測試環境（手機/平板）
```cmd
manage.bat → [N] Network Mode
```

### 部署檢查清單
- [ ] 修改 admin 密碼
- [ ] 設定正確的 `QR_CODE_DOMAIN`（實際固定 IP）
- [ ] 執行 `python update_qr_codes.py`
- [ ] 設定 Windows Firewall（port 5173, 8000）
- [ ] 備份資料庫
- [ ] 列印 QR code 標籤
- [ ] 使用者培訓

---

## 文件

### 使用文件
- [**使用手冊 v1.0**](./docs/20251230_192855_User_Manual_v1.0.md) - 完整操作指南
- [**開發總結**](./docs/20251230_193000_Development_Summary.md) - 開發歷程
- [CLAUDE.md](./CLAUDE.md) - Claude Code 專案指南
- [SETUP.md](./SETUP.md) - 環境設定詳細步驟

### 技術文件
- [**開發者指南**](./docs/260103_Developer_Guide_zh-TW.md) - 技術棧、共用元件、開發慣例（繁體中文）
- [SYSTEM_REQUIREMENTS.md](./SYSTEM_REQUIREMENTS.md) - 系統需求與規範
- [BATCH_FILES_README.md](./docs/BATCH_FILES_README.md) - 批次檔使用說明
- Phase 1-3 完成報告（docs/）
- API 文件：http://localhost:8000/docs

---

## 開發規劃

### ✅ 已完成（v1.0）
- Phase 1: 認證系統
- Phase 2: 設備管理
- Phase 3: 租賃校正
- Phase 4: 前端開發
- Calibration 完善
- ActivityLog 附件

### ✅ 已完成（v1.1 安全強化）
- **httpOnly Cookies**：Token 改用 httpOnly cookie 儲存，防止 XSS 攻擊
- **2FA 管理增強**：Admin 可執行 Reset/Enable/Disable 2FA
- **Disable/Enable 分離**：Disable 保留 secret，Enable 可直接重啟用
- **Reset 2FA 流程**：強制用戶重新掃描 QR code 設定

### ✅ 已完成（v1.2 檔案安全 + 前端防護）
- **Magic Number 驗證**：檔案簽名驗證，防止偽造副檔名
- **PDF 安全掃描**：檢測 JavaScript、自動執行、嵌入檔案等危險內容
- **圖片重新編碼**：移除 EXIF metadata 和隱藏 payload
- **DOMPurify XSS 防護**：前端 HTML 內容清理
- **前端安全審計日誌**：追蹤認證失敗、權限拒絕等安全事件
- **檔案大小提升**：單檔上傳限制提升至 100MB
- **PWA 圖示**：新增 192x192 和 512x512 應用程式圖示

### 🔜 下次開發
- Phase 5: SubEquipment 管理（設備組件追蹤）
- Phase 6: Category 動態管理（需謹慎測試）

---

## 故障排除

### 問題 1: 後端無法啟動
```
檢查: backend/.env 檔案是否存在
解決: 複製 .env.example 為 .env
```

### 問題 2: 前端無法載入頁面
```
檢查: Node modules 是否安裝
解決: cd frontend && bun install
```

### 問題 3: manage.bat 執行錯誤
```
檢查: 是否使用純英文路徑
解決: 確保專案路徑無中文字元
```

### 問題 4: QR code 掃描無法開啟
```
檢查: QR_CODE_DOMAIN 設定
解決: 執行 update_qr_codes.py 更新
```


### 問題 5: Docker 建立 admin 
init_db() 只建立資料表，不會自動建立 admin 帳號。

  需要手動執行 create_admin.py 腳本。
    解決方案：在容器內建立 admin
  在 NAS 任務排程器執行：

        
  #!/bin/bash
        docker exec marine-equipment-backend python -m app.scripts.create_admin

---

## 授權

內部專案 - 部門使用

---

## 聯絡

**專案維護**: CHC Team
**技術支援**: GitHub Issues
**Email**: jin_chang@me.com

---

**最後更新**: 2026-01-03
**版本**: 1.2
**狀態**: ✅ Production Ready
