# Phase 2 開發完成 - 設備與位置管理 API

**日期**: 2025-12-30
**階段**: Phase 2 - 設備與位置管理
**狀態**: ✅ 完成

---

## 📋 本階段目標

實作完整的設備管理 API，包含自動資產編號生成、QR Code 功能、設備狀態流轉、異動歷程記錄，以及位置管理功能。

## ✅ 已完成功能

### 1. 設備管理 API (Equipment Management)

#### 基本 CRUD 操作
```
GET    /api/equipment              # 設備列表 (支援篩選、搜尋、分頁)
POST   /api/equipment              # 新增設備 (Manager+)
GET    /api/equipment/{id}         # 設備詳情
PUT    /api/equipment/{id}         # 更新設備 (Manager+)
DELETE /api/equipment/{id}         # 軟刪除設備 (Admin)
```

**篩選參數**:
- `category` - 設備類別 (MBES, GNSS, SVP, etc.)
- `status` - 設備狀態 (IN_STOCK, DEPLOYED, RENTED, etc.)
- `location_id` - 當前位置 ID
- `search` - 搜尋關鍵字 (asset_code, manufacturer, model, serial_number)
- `skip`, `limit` - 分頁參數

#### QR Code 掃描
```
GET /api/equipment/by-qr/{asset_code}
```
- 透過資產編號快速查詢設備
- 手機掃碼後使用
- 返回設備完整資訊

#### 設備狀態操作
```
POST /api/equipment/{id}/deploy    # 部署設備 (Operator+)
POST /api/equipment/{id}/return    # 回收設備 (Operator+)
POST /api/equipment/{id}/repair    # 送修設備 (Operator+)
POST /api/equipment/{id}/note      # 新增備註
```

**狀態流轉規則**:
```
ORDERING → IN_STOCK → DEPLOYED
                  ↓
              RENTED
                  ↓
              REPAIR → 回到 IN_STOCK
                  ↓
         DISPOSED / LOST
```

#### 設備異動歷程
```
GET /api/equipment/{id}/logs
```
- 記錄所有設備變更
- 包含狀態變更、位置變更、維護記錄、備註等
- 支援地理位置記錄 (latitude, longitude)
- 追蹤操作使用者

**Log 類型**:
- `STATUS_CHANGE` - 狀態變更
- `LOCATION_CHANGE` - 位置變更
- `RENTAL_START` - 租賃開始
- `RENTAL_END` - 租賃結束
- `CALIBRATION` - 校驗記錄
- `MAINTENANCE` - 維護記錄
- `NOTE` - 一般備註
- `CREATED` - 建立記錄
- `UPDATED` - 更新記錄

### 2. 位置管理 API (Location Management)

#### 基本 CRUD 操作
```
GET    /api/locations              # 位置列表 (支援類型篩選)
POST   /api/locations              # 新增位置 (Manager+)
GET    /api/locations/{id}         # 位置詳情 (含設備數量)
PUT    /api/locations/{id}         # 更新位置 (Manager+)
DELETE /api/locations/{id}         # 軟刪除位置 (Admin)
```

**位置類型**:
- `WAREHOUSE` - 倉庫
- `VESSEL` - 船舶
- `PLATFORM` - 平台
- `VEHICLE` - 車輛
- `EXTERNAL` - 外部 (租賃客戶處)

#### 位置設備清單
```
GET /api/locations/{id}/equipment
```
- 查詢某位置的所有設備
- 僅顯示啟用中的設備
- 依資產編號排序

**安全限制**:
- 不能刪除有設備的位置
- 必須先移除所有設備才能刪除位置

### 3. QR Code 功能

#### QR Code 端點
```
GET /api/qrcode/{equipment_id}                # QR code 資訊 (base64)
GET /api/qrcode/{equipment_id}/image          # 下載 QR code 圖片
GET /api/qrcode/by-asset/{asset_code}/image   # 依資產編號下載
```

**QR Code 規格**:
- 格式: PNG
- 尺寸: 可調整 (預設 box_size=10)
- 容錯級別: L (低)
- 邊框: 4 個單位
- 顏色: 黑白

**QR Code 內容格式**:
```
https://localhost:5173/e/{asset_code}
例如: https://localhost:5173/e/MBES-2025-001
```

### 4. 資產編號自動生成

#### 生成邏輯 (`app/utils/asset_code.py`)
```python
格式: {CATEGORY}-{YEAR}-{SEQUENCE}

規則:
- 類別代碼大寫 (MBES, GNSS, SVP, etc.)
- 年份: 4 位數 (預設當年)
- 序號: 3 位數，從 001 開始
- 每年每類別獨立計數

範例:
MBES-2025-001  # 第一台 2025 年的多音束測深儀
MBES-2025-002  # 第二台
GNSS-2025-001  # 第一台 2025 年的 GNSS
MBES-2024-100  # 2024 年的第 100 台多音束
```

**特性**:
- 自動查詢資料庫確保唯一性
- 避免編號衝突
- 支援跨年度計數

### 5. 異動歷程系統

#### EquipmentLog Model
```python
欄位:
- equipment_id: 設備 ID (FK)
- log_type: 異動類型 (Enum)
- old_value: 舊值
- new_value: 新值
- description: 描述
- latitude: 緯度 (選填)
- longitude: 經度 (選填)
- created_by: 操作使用者 (FK)
- created_at: 建立時間
```

**自動記錄**:
- 設備建立
- 設備更新 (追蹤欄位變更)
- 狀態變更 (部署、回收、送修)
- 位置變更
- 備註新增
- 軟刪除

---

## 📂 新增檔案

```
backend/app/
├── api/
│   ├── equipment.py          # 設備管理 API (265 行)
│   ├── locations.py          # 位置管理 API (220 行)
│   ├── qrcode.py             # QR Code API (135 行)
│   └── router.py             # 更新: 註冊新路由
├── models/
│   ├── equipment_log.py      # 異動歷程模型
│   ├── equipment.py          # 更新: 新增 logs relationship
│   └── __init__.py           # 更新: 匯出 EquipmentLog
├── schemas/
│   ├── equipment.py          # 設備 schemas
│   ├── location.py           # 位置 schemas
│   └── __init__.py           # 更新: 匯出新 schemas
├── utils/
│   ├── __init__.py
│   └── asset_code.py         # 資產編號生成工具
└── alembic/
    └── versions/
        └── 20251230_104912_add_equipmentlog_*.py  # 新 migration
```

---

## 🔧 技術實作細節

### 1. 資產編號生成演算法

```python
async def generate_asset_code(category, db, year=None):
    # 1. 取得類別前綴 (大寫)
    category_prefix = category.value.upper()  # "MBES"

    # 2. 取得年份 (預設當年)
    year = year or datetime.now().year  # 2025

    # 3. 查詢該類別該年度的設備數量
    pattern = f"{category_prefix}-{year}-%"
    count = await db.query(Equipment).filter(
        Equipment.asset_code.like(pattern)
    ).count()

    # 4. 計算下一個序號
    next_sequence = count + 1  # 1, 2, 3, ...

    # 5. 格式化為 3 位數
    asset_code = f"{category_prefix}-{year}-{next_sequence:03d}"

    return asset_code  # "MBES-2025-001"
```

### 2. 異動記錄機制

**自動觸發時機**:
1. **建立設備**: 記錄 `CREATED` log
2. **更新設備**: 記錄 `UPDATED` log，包含變更欄位清單
3. **狀態變更**: 記錄舊狀態 → 新狀態
4. **部署/回收**: 記錄位置變更和狀態變更
5. **新增備註**: 記錄 `NOTE` log

**記錄內容**:
```json
{
  "log_type": "STATUS_CHANGE",
  "old_value": "Status: IN_STOCK, Location: 1",
  "new_value": "Status: DEPLOYED, Location: 5",
  "description": "Equipment deployed to vessel",
  "latitude": 25.0330,
  "longitude": 121.5654,
  "created_by": 1,
  "created_at": "2025-12-30T10:30:00"
}
```

### 3. 軟刪除策略

**設備刪除**:
- 設定 `is_active = False`
- 保留所有歷史記錄
- 仍可查詢但不會出現在一般列表
- 僅 Admin 可執行

**位置刪除**:
- 檢查是否有設備在該位置
- 若有設備則拒絕刪除
- 必須先移除設備才能刪除
- 設定 `is_active = False`

### 4. 權限控制

| 操作 | Admin | Manager | Operator | Viewer |
|------|:-----:|:-------:|:--------:|:------:|
| 檢視設備 | ✅ | ✅ | ✅ | ✅ |
| 掃碼查詢 | ✅ | ✅ | ✅ | ✅ |
| 新增/編輯設備 | ✅ | ✅ | ❌ | ❌ |
| 刪除設備 | ✅ | ❌ | ❌ | ❌ |
| 部署/回收操作 | ✅ | ✅ | ✅ | ❌ |
| 新增備註 | ✅ | ✅ | ✅ | ✅ |
| 新增/編輯位置 | ✅ | ✅ | ❌ | ❌ |
| 刪除位置 | ✅ | ❌ | ❌ | ❌ |
| 下載 QR Code | ✅ | ✅ | ✅ | ✅ |

---

## 📊 API 端點總覽

### 設備端點 (11 個)
```
GET    /api/equipment                   # 列表
POST   /api/equipment                   # 新增
GET    /api/equipment/by-qr/{code}      # QR 掃描
GET    /api/equipment/{id}              # 詳情
PUT    /api/equipment/{id}              # 更新
DELETE /api/equipment/{id}              # 刪除
GET    /api/equipment/{id}/logs         # 歷程
POST   /api/equipment/{id}/deploy       # 部署
POST   /api/equipment/{id}/return       # 回收
POST   /api/equipment/{id}/repair       # 送修
POST   /api/equipment/{id}/note         # 備註
```

### 位置端點 (6 個)
```
GET    /api/locations                   # 列表
POST   /api/locations                   # 新增
GET    /api/locations/{id}              # 詳情
PUT    /api/locations/{id}              # 更新
DELETE /api/locations/{id}              # 刪除
GET    /api/locations/{id}/equipment    # 位置設備
```

### QR Code 端點 (3 個)
```
GET /api/qrcode/{id}                    # QR 資訊 (base64)
GET /api/qrcode/{id}/image              # 下載圖片
GET /api/qrcode/by-asset/{code}/image   # 依編號下載
```

**總計**: 20 個新端點 (加上 Phase 1 的 13 個 = 33 個端點)

---

## 🗄️ 資料庫變更

### 新增資料表

#### equipment_logs
```sql
CREATE TABLE equipment_logs (
    id INTEGER PRIMARY KEY,
    equipment_id INTEGER NOT NULL,        -- FK to equipments
    log_type VARCHAR NOT NULL,            -- Enum: status_change, note, etc.
    old_value TEXT,
    new_value TEXT,
    description TEXT,
    latitude FLOAT,
    longitude FLOAT,
    created_by INTEGER,                   -- FK to users
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    FOREIGN KEY (equipment_id) REFERENCES equipments(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
)

-- Indexes
CREATE INDEX ix_equipment_logs_id ON equipment_logs(id)
CREATE INDEX ix_equipment_logs_equipment_id ON equipment_logs(equipment_id)
CREATE INDEX ix_equipment_logs_log_type ON equipment_logs(log_type)
```

### Migration 版本
- 第 1 版: `20251230_095709_initial_migration_*.py` (User, Equipment, Location)
- 第 2 版: `20251230_104912_add_equipmentlog_*.py` (EquipmentLog)

---

## 🧪 測試方式

### 1. 啟動後端
```powershell
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 2. 訪問 API 文件
http://localhost:8000/docs

### 3. 測試設備管理流程

#### Step 1: 建立位置
```bash
curl -X POST "http://localhost:8000/api/locations" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Warehouse",
    "location_type": "warehouse",
    "code": "WH-001"
  }'
```

#### Step 2: 建立設備
```bash
curl -X POST "http://localhost:8000/api/equipment" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "mbes",
    "manufacturer": "Kongsberg",
    "model": "EM2040C",
    "serial_number": "12345678",
    "purchase_date": "2025-01-15",
    "purchase_price": 1500000,
    "rental_daily_rate": 5000,
    "current_location_id": 1
  }'
```

**返回結果**:
```json
{
  "id": 1,
  "asset_code": "MBES-2025-001",  // 自動生成
  "qr_code": "https://localhost:5173/e/MBES-2025-001",
  "category": "mbes",
  "manufacturer": "Kongsberg",
  "model": "EM2040C",
  "status": "ordering",
  ...
}
```

#### Step 3: 部署設備
```bash
curl -X POST "http://localhost:8000/api/equipment/1/deploy" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 2,
    "notes": "Deployed to R/V Ocean Explorer",
    "latitude": 25.0330,
    "longitude": 121.5654
  }'
```

#### Step 4: 查看異動歷程
```bash
curl -X GET "http://localhost:8000/api/equipment/1/logs" \
  -H "Authorization: Bearer <token>"
```

#### Step 5: 下載 QR Code
```bash
# 方式 1: 依設備 ID
curl -X GET "http://localhost:8000/api/qrcode/1/image" \
  -H "Authorization: Bearer <token>" \
  -o MBES-2025-001.png

# 方式 2: 依資產編號
curl -X GET "http://localhost:8000/api/qrcode/by-asset/MBES-2025-001/image" \
  -H "Authorization: Bearer <token>" \
  -o MBES-2025-001.png
```

#### Step 6: 掃碼查詢 (模擬手機掃碼)
```bash
curl -X GET "http://localhost:8000/api/equipment/by-qr/MBES-2025-001" \
  -H "Authorization: Bearer <token>"
```

---

## 📊 開發統計

### Git Commits
```
6 commits total (Phase 1 + Phase 2)
- eee26b5: Initial commit - 專案環境架構完成
- 9cd3a2d: Setup - 依賴安裝與測試
- 05bae90: Feature - 認證 API 與 2FA
- 985628f: Docs - Phase 1 完成報告
- ada9990: Merge - 解決 README 衝突
- 44c429f: Feature - 設備與位置管理 API ✨ NEW
```

### 程式碼統計
- **新增檔案**: 15 個 (Phase 2)
- **新增程式碼**: ~1,328 行 (Phase 2)
- **API 端點**: 33 個 (Phase 1: 13 + Phase 2: 20)
- **資料表**: 4 個 (users, equipments, locations, equipment_logs)

### 累計開發
- **總檔案數**: 50+ 個
- **總程式碼**: ~4,500+ 行
- **Python 套件**: 48 個
- **JavaScript 套件**: 497 個

---

## 🎯 使用情境示例

### 情境 1: 新設備入庫
```
1. Manager 在系統中新增設備
   → 系統自動生成資產編號: MBES-2025-001
   → 系統自動生成 QR Code URL
   → 記錄建立 log

2. Manager 列印 QR Code 標籤
   → 訪問 /api/qrcode/1/image
   → 下載 PNG 圖片
   → 列印並貼在設備上

3. Manager 將設備入庫到倉庫
   → 設備狀態: ORDERING → IN_STOCK
   → 記錄狀態變更 log
```

### 情境 2: 設備部署到船舶
```
1. Operator 掃描設備 QR Code
   → 讀取資產編號: MBES-2025-001
   → 系統顯示設備詳情

2. Operator 執行部署操作
   → POST /api/equipment/1/deploy
   → 指定目標位置: R/V Ocean Explorer
   → 記錄 GPS 位置

3. 系統自動記錄
   → 狀態: IN_STOCK → DEPLOYED
   → 位置: Warehouse → Vessel
   → 時間、操作人員、GPS 座標
```

### 情境 3: 查詢船舶上的設備
```
1. Manager 選擇船舶: R/V Ocean Explorer
   → GET /api/locations/2

2. 查看該船的所有設備
   → GET /api/locations/2/equipment
   → 顯示設備列表
   → 顯示設備數量

3. 點選設備查看詳情
   → GET /api/equipment/{id}
   → 顯示完整規格、狀態、歷程
```

---

## 🔄 設備狀態流轉實例

```
時間軸範例:

2025-01-15  建立設備 MBES-2025-001
            狀態: ORDERING
            Log: "Equipment created"

2025-02-01  設備到貨入庫
            狀態: ORDERING → IN_STOCK
            位置: → Main Warehouse
            Log: "Equipment received and stored"

2025-03-10  部署到船舶
            狀態: IN_STOCK → DEPLOYED
            位置: Main Warehouse → R/V Ocean Explorer
            Log: "Deployed for Project ABC"

2025-04-20  回收入庫
            狀態: DEPLOYED → IN_STOCK
            位置: R/V Ocean Explorer → Main Warehouse
            Log: "Project completed, returned to warehouse"

2025-05-01  發現故障送修
            狀態: IN_STOCK → REPAIR
            Log: "Sensor malfunction, sent to repair"

2025-06-01  維修完成
            狀態: REPAIR → IN_STOCK
            Log: "Repair completed, sensor replaced"
```

---

## 📝 下一階段計畫 (Phase 3)

### 1. 租賃管理 API
- [ ] Customer model 與 API
- [ ] Rental model 與 API
- [ ] 租賃單 CRUD
- [ ] 租金計算
- [ ] 租賃狀態流轉
- [ ] 逾期檢查

### 2. 校驗管理 API
- [ ] Calibration model 與 API
- [ ] 校驗記錄 CRUD
- [ ] 到期提醒
- [ ] 證書管理

### 3. 前端開發
- [ ] 登入頁面
- [ ] 2FA 設定頁面
- [ ] 設備列表頁
- [ ] 設備詳情頁
- [ ] QR 掃描頁
- [ ] 儀表板

### 4. 統計與報表
- [ ] Dashboard 統計 API
- [ ] 設備使用率報表
- [ ] 租賃營收報表

---

## ✅ 檢查清單

- [x] EquipmentLog model 建立
- [x] 資產編號自動生成
- [x] 設備 CRUD API
- [x] 位置 CRUD API
- [x] QR Code 生成功能
- [x] 設備狀態操作 (deploy, return, repair)
- [x] 異動歷程記錄
- [x] Migration 執行成功
- [x] API 測試通過
- [x] 代碼推送到 GitHub
- [x] 文件撰寫完成
- [ ] 前端頁面開發

---

**文件版本**: 1.0
**最後更新**: 2025-12-30 10:50
**作者**: CHC
**GitHub**: https://github.com/CHC1978/DG_Workshop
