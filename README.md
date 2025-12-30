# 海洋設備 QR Code 管理系統

海洋調查設備資產管理系統，透過 QR Code 實現設備快速識別、狀態追蹤、租賃管理等功能。

## 專案狀態

🚧 **開發中** - 目前處於環境建置階段

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
