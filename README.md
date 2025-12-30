# 海洋設備 QR Code 管理系統

海洋調查設備資產管理系統，透過 QR Code 實現設備快速識別、狀態追蹤、租賃管理等功能。

## 專案狀態

✅ **Phase 1-3 完成** - 後端 API 完整實作 (54 endpoints)
🔄 **前端開發中** - 基礎介面完成，持續擴充功能

**最新進度**:
- ✅ 認證系統 + 2FA
- ✅ 設備管理 API
- ✅ 租賃管理 API
- ✅ 校驗管理 API
- ✅ 前端登入介面
- ✅ Dashboard 儀表板
- ✅ 設備列表頁面

## 技術棧

### 後端
- Python 3.12+
- FastAPI 0.115+
- SQLAlchemy 2.0 (Async)
- SQLite (WAL mode)
- Alembic (Migration)
- JWT + TOTP 2FA

### 前端
- Bun 1.1+
- Vue 3.5+ (Composition API)
- Vite 6.0+
- TailwindCSS 3.4+
- Pinia 2.2+ (狀態管理)
- PWA 支援

## 快速開始

### 前置需求

- Python 3.12+
- Bun 1.1+
- Git

### 🚀 一鍵啟動 (Windows)

#### 方式 1: 互動式控制面板（推薦）
```cmd
manage.bat
```
提供互動式選單：
- [1] Start All
- [2] Stop All
- [3] Restart All
- [4] Start Backend Only
- [5] Start Frontend Only
- [6] Restart Backend Only ⭐ NEW
- [7] Restart Frontend Only ⭐ NEW
- [8] Stop Backend Only
- [9] Stop Frontend Only
- [S] Check Status
- [H] First Time Setup
- [0] Exit

#### 方式 2: 直接執行批次檔

**首次使用**:
```cmd
setup_first_time.bat
```
自動完成環境設定、資料庫初始化、建立管理員帳號

**快速啟動**:
```cmd
quick_start.bat
或
start_all.bat
```
同時啟動後端和前端服務（視窗自動最小化）

**重新啟動**:
```cmd
restart_all.bat
```
停止並重新啟動所有服務

**停止系統**:
```cmd
stop_all.bat
```
停止所有運行中的服務

**單獨控制**:
- `start_backend.bat` - 僅啟動後端
- `start_frontend.bat` - 僅啟動前端

**開發建議**:
- 修改後端代碼後：`manage.bat → [6] Restart Backend Only`
- 修改前端配置後：`manage.bat → [7] Restart Frontend Only`
- 檢查服務狀態：`manage.bat → [S] Check Status`

> ⚠️ **系統需求**: 所有 Windows 批次檔 (.bat) 必須使用純英文/ASCII 字元。
> 詳見 [SYSTEM_REQUIREMENTS.md](./SYSTEM_REQUIREMENTS.md)

### 後端設定

```bash
cd backend

# 建立虛擬環境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 安裝依賴
pip install -r requirements.txt

# 複製環境變數範例
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS

# 編輯 .env 設定 SECRET_KEY

# 初始化資料庫 (首次執行)
alembic upgrade head

# 啟動開發伺服器
uvicorn app.main:app --reload --port 8000
```

訪問 http://localhost:8000/docs 查看 API 文件

### 前端設定

```bash
cd frontend

# 安裝依賴
bun install

# 啟動開發伺服器
bun dev
```

訪問 http://localhost:5173

## 專案結構

```
DG_workshop/
├── backend/              # Python FastAPI 後端
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # 核心模組 (config, database, security)
│   │   ├── models/      # SQLAlchemy models
│   │   └── schemas/     # Pydantic schemas
│   ├── alembic/         # 資料庫 migrations
│   └── tests/           # 測試
├── frontend/            # Vue 3 前端
│   └── src/
│       ├── api/         # API 封裝
│       ├── components/  # Vue 元件
│       ├── stores/      # Pinia stores
│       └── views/       # 頁面
├── plan/                # 專案計畫文件
└── CLAUDE.md            # Claude Code 專案說明
```

## 開發指令

詳細開發指令請參考 [CLAUDE.md](./CLAUDE.md)

## 文件

- [專案計畫書](./plan/marine-equipment-qr-system-plan.md)
- [Claude Code 指南](./CLAUDE.md)
- API 文件: http://localhost:8000/docs

## 授權

內部專案

## 聯絡

專案維護者: DG Team
