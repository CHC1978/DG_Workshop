# 環境設定指南

## 1. 安裝後端依賴

```powershell
# 進入後端目錄
cd backend

# 建立 Python 虛擬環境
python -m venv venv

# 啟動虛擬環境 (PowerShell)
venv\Scripts\activate

# 安裝依賴套件
pip install -r requirements.txt
```

## 2. 設定環境變數

編輯 `backend/.env` 檔案，設定 SECRET_KEY：

```powershell
# 使用 EmEditor 或其他編輯器開啟
emeditor backend\.env
```

將 `SECRET_KEY` 改為隨機字串（至少 32 字元）：

```
SECRET_KEY=請改為隨機產生的長字串例如用openssl-rand-hex-32
```

產生隨機 SECRET_KEY 的方法：
```powershell
# Python 方式
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 3. 初始化資料庫

```powershell
# 確保在 backend 目錄且虛擬環境已啟動

# 初始化 Alembic
alembic init alembic

# 編輯 alembic.ini，設定 sqlalchemy.url
# 或使用 alembic/env.py 動態讀取 config

# 建立第一個 migration
alembic revision --autogenerate -m "Initial migration"

# 執行 migration
alembic upgrade head
```

## 4. 安裝前端依賴

```powershell
# 在新的 PowerShell 視窗

# 進入前端目錄
cd frontend

# 安裝依賴
bun install
```

## 5. 啟動開發伺服器

### 後端

```powershell
# 在 backend 目錄，虛擬環境已啟動
uvicorn app.main:app --reload --port 8000
```

訪問：
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端

```powershell
# 在 frontend 目錄
bun dev
```

訪問：http://localhost:5173

## 6. 開發工具建議

- **編輯器**: EmEditor (已配置)
- **API 測試**: Swagger UI (http://localhost:8000/docs)
- **資料庫查看**: DB Browser for SQLite
- **版本控制**: Git + GitHub Desktop (選配)

## 7. 常見問題

### Q: PowerShell 無法執行 activate 腳本

A: 執行以下指令允許腳本執行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: Bun 指令找不到

A: 確認 Bun 已安裝：
```powershell
bun --version
```

若未安裝，請至 https://bun.sh/ 下載安裝。

### Q: 資料庫檔案在哪裡？

A: SQLite 資料庫檔案位於 `backend/data/marine_equipment.db`

## 8. 下一步

環境架構完成後，可以開始：

1. ✅ 建立使用者認證 API (Step 1 登入)
2. ✅ 實作 2FA TOTP 功能 (Step 2 登入)
3. ✅ 建立設備管理 CRUD API
4. ✅ 建立前端登入頁面
5. ✅ 實作 QR Code 掃描功能

詳細開發計畫請參考 `plan/marine-equipment-qr-system-plan.md


 1. 清除瀏覽器數據

  在瀏覽器 Console (F12 → Console) 執行：
  localStorage.clear()
  location.reload()`
