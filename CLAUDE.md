# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

海洋調查設備資產管理系統，透過 QR Code 實現設備快速識別、狀態追蹤、租賃管理等功能。支援 Web 及 PWA 行動裝置存取。

**專案狀態**: 規劃階段 - 詳細計畫參見 `plan/marine-equipment-qr-system-plan.md`

## 技術棧

- **後端**: Python 3.12+ / FastAPI / SQLAlchemy 2.0 / SQLite (WAL mode) / Alembic
- **前端**: Bun / Vue 3 / Vite / TailwindCSS / Headless UI / PWA
- **認證**: JWT + TOTP 2FA (Google/Microsoft Authenticator)

## 開發指令

### 後端
```bash
cd backend
python -m venv venv
venv\Scripts\activate                    # Windows (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt

# 資料庫 Migration
alembic revision --autogenerate -m "描述變更"  # 建立新的 migration
alembic upgrade head                           # 執行所有待處理的 migration
alembic downgrade -1                           # 回退上一個 migration
alembic history                                # 查看 migration 歷史

# 啟動開發伺服器
uvicorn app.main:app --reload --port 8000

# 執行測試
pytest                                   # 執行所有測試
pytest tests/test_auth.py               # 執行單一測試檔案
pytest -v                               # 詳細輸出
pytest --cov=app                        # 測試覆蓋率
```

### 前端
```bash
cd frontend
bun install
bun dev                                  # 開發伺服器 (port 5173)
bun run build                            # 生產建置
bun run preview                          # 預覽生產建置

# 測試
bun test                                 # 執行測試
bun run type-check                       # TypeScript 型別檢查
bun run lint                             # ESLint 檢查
```

### API 文件
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 專案結構

```
marine-equipment-qr/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── api/                 # API endpoints
│   │   ├── core/                # config, database, security, deps
│   │   ├── models/              # SQLAlchemy models
│   │   └── schemas/             # Pydantic schemas
│   ├── alembic/                 # DB migrations
│   └── data/                    # SQLite 檔案
└── frontend/
    └── src/
        ├── api/                 # Axios API 封裝
        ├── stores/              # Pinia stores
        ├── composables/         # Vue composables
        ├── components/          # 共用元件
        ├── views/               # 頁面
        └── router/              # Vue Router
```

## 資料模型

核心 Models: User, Equipment, Location, Deployment, Rental, Customer, Calibration, EquipmentLog

### 設備類別代碼
| 代碼 | 說明 |
|------|------|
| MBES | 多音束測深儀 (Multibeam Echosounder) |
| GNSS | 衛星定位系統 (GNSS Receiver) |
| SVP | 聲速剖面儀 (Sound Velocity Profiler) |
| SBP | 淺層剖面儀 (Sub-bottom Profiler) |
| USBL | 水下定位系統 (Ultra-Short Baseline) |
| ROV | 水下無人載具 (Remotely Operated Vehicle) |
| INS | 慣性導航系統 (Inertial Navigation System) |
| MAG | 磁力儀 (Magnetometer) |

### 資產編號格式
```
{類別}-{年份}-{序號}
範例: MBES-2024-001, GNSS-2023-015
```

**產生規則**:
- 序號為 3 位數,從 001 開始
- 每年每類別獨立計數
- 系統自動產生,確保唯一性
- QR Code 內容格式: `https://{domain}/e/{asset_code}`

## 命名慣例

- Python: snake_case
- TypeScript/Vue: camelCase (變數), PascalCase (元件)
- API endpoints: kebab-case
- 資料庫表: 複數形式 (equipments, calibrations)

## 常見任務

### 新增 API endpoint
1. 在 `app/schemas/` 建立 Pydantic schema
2. 在 `app/api/` 建立 router
3. 在 `app/api/router.py` 註冊路由

### 新增資料庫表
1. 在 `app/models/` 建立 model
2. 在 `app/models/__init__.py` 匯出
3. 執行 `alembic revision --autogenerate -m "描述"`
4. 執行 `alembic upgrade head`

### 新增前端頁面
1. 在 `src/views/` 建立 Vue 元件
2. 在 `src/router/index.ts` 新增路由
3. 如需 API，在 `src/api/` 建立封裝函式

## 環境變數

建立 `backend/.env`:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/marine_equipment.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
TEMP_TOKEN_EXPIRE_MINUTES=5
```

## 認證流程

系統採用兩階段登入:
1. POST `/api/auth/login/step1` - 帳密驗證，返回臨時 token
2. POST `/api/auth/login/step2` - TOTP 驗證，返回 JWT access token

首次登入需設定 2FA，使用 Google/Microsoft Authenticator 掃描 QR Code。

## 權限角色

Admin > Manager > Operator > Viewer

詳細權限矩陣參見 `plan/marine-equipment-qr-system-plan.md`

## 核心業務邏輯

### 設備狀態流轉
```
新設備 (ORDERING) → 入庫 (IN_STOCK) → 部署/租賃 (DEPLOYED/RENTED)
                                    ↓
                               維修 (REPAIR) → 回到 IN_STOCK
                                    ↓
                               報廢/遺失 (DISPOSED/LOST)
```

### 兩階段認證登入
1. **Step 1**: POST `/api/auth/login/step1` - 驗證帳號密碼,返回臨時 token
2. **Step 2**: POST `/api/auth/login/step2` - 驗證 TOTP 碼,返回 JWT access token

首次登入強制設定 2FA,使用 Google/Microsoft Authenticator 掃描 QR Code。

### PWA 離線支援
- Service Worker 快取靜態資源
- 掃碼功能可離線使用
- 資料同步策略: Network First with Cache Fallback
- 離線時顯示提示並快取操作,待連線後同步

## 資料庫注意事項

- SQLite 使用 WAL (Write-Ahead Logging) 模式提升並發效能
- 資料庫檔案位於 `backend/data/marine_equipment.db`
- 自動記錄所有設備異動至 `EquipmentLog` 表
- 軟刪除策略: 設備不實際刪除,僅標記 `is_active=false`

## 環境注意事項
- 目前開發環境是Windows 11 , PowerShell 命令下.
- **⚠️ 重要：絕對不要使用 Bash 工具自行啟動後端或前端服務**
  - **禁止執行**: `uvicorn`, `python -m uvicorn`, `bun dev` 等啟動指令
  - **禁止執行**: 任何會在背景啟動服務的命令
  - 所有前端與後端的啟動、重啟、停止操作都由使用者手動執行
  - Claude 只能診斷問題、修改程式碼，不能控制服務的生命週期