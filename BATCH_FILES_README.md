# 批次檔使用說明

## 📁 批次檔清單

### 🎮 主控制面板

#### `manage.bat` ⭐ 推薦
互動式控制面板，提供完整的系統管理功能。

**功能選單**：
```
[1] Start All              - 啟動所有服務
[2] Stop All               - 停止所有服務
[3] Restart All            - 重新啟動
[4] Start Backend Only     - 僅啟動後端
[5] Start Frontend Only    - 僅啟動前端
[6] Stop Backend Only      - 僅停止後端
[7] Stop Frontend Only     - 僅停止前端
[8] Check Status           - 檢查服務狀態
[9] First Time Setup       - 首次環境設定
[0] Exit                   - 退出
```

**使用方式**：雙擊執行，選擇數字選項

---

### 🚀 快速啟動

#### `快速啟動.bat` ⭐ 推薦（中文介面）
一鍵啟動系統，中文友善介面。

**功能**：
- 自動停止舊程序
- 啟動後端和前端（視窗自動最小化）
- 顯示登入資訊
- 顯示系統 URL

**使用時機**：日常啟動系統

#### `start_all.bat`
英文版快速啟動（功能相同）

---

### 🔄 重新啟動

#### `restart_all.bat`
完整重新啟動流程。

**執行步驟**：
1. 停止所有舊程序
2. 等待 2 秒
3. 啟動新的服務（視窗自動最小化）

**使用時機**：
- 修改後端代碼後需要重載
- 系統出現異常需要重啟
- 更新配置檔案後

---

### 🛑 停止服務

#### `stop_all.bat`
停止所有運行中的服務。

**停止的程序**：
- Python/Uvicorn (後端)
- Bun/Node (前端)

**使用時機**：
- 不需要系統運行時
- 切換專案時
- 關機前

---

### ⚙️ 單獨控制

#### `start_backend.bat`
僅啟動後端伺服器。

**檢查項目**：
- 虛擬環境是否存在
- .env 檔案是否存在
- 自動啟動 uvicorn

**URL**: http://localhost:8000

#### `start_frontend.bat`
僅啟動前端伺服器。

**檢查項目**：
- node_modules 是否存在
- 自動安裝依賴（如缺失）
- 啟動 Vite 開發伺服器

**URL**: http://localhost:5173

---

### 🎬 首次設定

#### `setup_first_time.bat`
首次使用時執行，自動完成所有設定。

**執行步驟**：
1. 檢查 Python 和 Bun
2. 建立 Python 虛擬環境
3. 安裝後端依賴套件
4. 安裝前端依賴套件
5. 建立 .env 檔案
6. 執行資料庫 migration
7. 建立管理員帳號

**僅需執行一次**！

---

## 📖 使用情境

### 情境 1: 首次使用專案
```cmd
1. setup_first_time.bat      (一次性設定)
2. manage.bat → [1]          (啟動系統)
3. 訪問 http://localhost:5173
```

### 情境 2: 日常開發
```cmd
快速啟動.bat
或
manage.bat → [1]
```

### 情境 3: 修改後端代碼後
```cmd
restart_all.bat
或
manage.bat → [3]
```

### 情境 4: 只需要測試後端 API
```cmd
manage.bat → [4]
訪問 http://localhost:8000/docs
```

### 情境 5: 只需要開發前端
```cmd
manage.bat → [5]
```

### 情境 6: 檢查服務是否運行
```cmd
manage.bat → [8]
```

### 情境 7: 結束工作
```cmd
stop_all.bat
或
manage.bat → [2]
或
直接關閉伺服器視窗
```

---

## 💡 特殊功能

### 🔽 視窗自動最小化
所有啟動腳本都會將伺服器視窗自動最小化到工作列。

**優點**：
- 桌面更整潔
- 不干擾工作
- 需要時可從工作列開啟查看 log

**查看 Log**：
- 點擊工作列的「後端伺服器」或「前端伺服器」視窗
- 可以看到即時的運行記錄

### 🔍 狀態檢查
使用 `manage.bat → [8]` 檢查服務狀態。

**顯示內容**：
```
Backend (Python/Uvicorn):
  [RUNNING] Backend server is running

Frontend (Bun/Node):
  [RUNNING] Frontend server is running

URLs:
  Backend:  http://localhost:8000
  Frontend: http://localhost:5173
  API Docs: http://localhost:8000/docs
```

---

## ⚠️ 注意事項

### 關於最小化視窗
- 視窗最小化但程序仍在運行
- 關閉最小化的視窗會停止對應的服務
- 可從工作列恢復視窗查看 log

### 關於停止服務
- `stop_all.bat` 會強制終止所有 Python 和 Bun 程序
- 如果有其他 Python/Node 程式在運行，也會被停止
- 建議使用前確認沒有其他重要程式運行

### 關於重新啟動
- `restart_all.bat` 會完全停止並重啟服務
- 後端修改代碼後必須重啟才生效
- 前端 Vite 有 HMR，通常不需要重啟

---

## 🎯 推薦工作流程

### 早上開始工作
```cmd
快速啟動.bat
```
或
```cmd
manage.bat → [1] Start All
```

### 中途需要重啟
```cmd
manage.bat → [3] Restart All
```

### 需要查看運行狀態
```cmd
manage.bat → [8] Check Status
```

### 下班關閉系統
```cmd
manage.bat → [2] Stop All
```
或
```cmd
stop_all.bat
```

---

## 📞 快捷鍵建議

可以為常用批次檔建立桌面捷徑：

1. **右鍵批次檔** → 傳送到 → 桌面（建立捷徑）
2. **右鍵捷徑** → 內容 → 快速鍵
3. 設定快捷鍵（例如：Ctrl+Alt+M for manage.bat）

**推薦建立捷徑**：
- `manage.bat` - 主控制面板
- `快速啟動.bat` - 快速啟動
- `stop_all.bat` - 快速停止

---

**版本**: 2.0
**最後更新**: 2025-12-30
