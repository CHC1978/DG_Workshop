# Phase 3 開發完成 - 租賃與校驗管理 API

**日期**: 2025-12-30
**階段**: Phase 3 - 租賃與校驗管理
**狀態**: ✅ 完成

---

## 📋 本階段目標

實作完整的租賃管理系統（客戶、租賃單、狀態流轉、租金計算）和校驗管理系統（校驗記錄、到期提醒）。

## ✅ 已完成功能

### 1. 客戶管理 API (Customer Management)

#### 基本 CRUD 操作
```
GET    /api/customers              # 客戶列表 (支援搜尋)
POST   /api/customers              # 新增客戶 (Manager+)
GET    /api/customers/{id}         # 客戶詳情 (含租賃統計)
PUT    /api/customers/{id}         # 更新客戶 (Manager+)
DELETE /api/customers/{id}         # 軟刪除客戶 (Manager+)
GET    /api/customers/{id}/rentals # 客戶租賃歷史
```

**客戶資料欄位**:
- 公司名稱、統一編號
- 聯絡人、電話、Email、地址
- 備註
- 租賃統計（總租賃數、進行中租賃數）

**搜尋功能**:
- 公司名稱
- 聯絡人
- 統一編號
- 電話

**安全限制**:
- 不能刪除有進行中租賃的客戶
- 統一編號不可重複

### 2. 租賃管理 API (Rental Management)

#### 基本 CRUD 操作
```
GET    /api/rentals                # 租賃列表 (支援篩選)
POST   /api/rentals                # 建立租賃單 (Manager+)
GET    /api/rentals/{id}           # 租賃詳情
PUT    /api/rentals/{id}           # 更新租賃 (Manager+)
DELETE /api/rentals/{id}           # 刪除草稿 (Manager+)
```

**篩選參數**:
- `status` - 租賃狀態
- `customer_id` - 客戶 ID
- `equipment_id` - 設備 ID

#### 租賃狀態操作
```
POST /api/rentals/{id}/confirm     # 確認租賃
POST /api/rentals/{id}/deliver     # 交付設備
POST /api/rentals/{id}/return      # 歸還設備
POST /api/rentals/{id}/cancel      # 取消租賃
```

#### 逾期管理
```
GET /api/rentals/overdue           # 取得逾期租賃
```
- 自動檢查逾期租賃
- 自動更新狀態為 OVERDUE

### 3. 租賃狀態流轉

```
┌─────────┐
│  DRAFT  │ 草稿/報價中
└────┬────┘
     │ confirm
     ▼
┌─────────┐
│CONFIRMED│ 已確認
└────┬────┘
     │ deliver
     ▼
┌─────────┐     逾期檢查
│ ACTIVE  │ ────────► OVERDUE
└────┬────┘
     │ return
     ▼
┌─────────┐
│RETURNED │ 已歸還
└─────────┘

     cancel
DRAFT/CONFIRMED ────► CANCELLED
```

**狀態轉換規則**:
- `DRAFT → CONFIRMED`: 客戶確認後
- `CONFIRMED → ACTIVE`: 設備交付時
- `ACTIVE → OVERDUE`: 超過預計歸還日期
- `ACTIVE/OVERDUE → RETURNED`: 設備歸還時
- `DRAFT/CONFIRMED → CANCELLED`: 取消租賃

### 4. 租賃單號自動生成

**格式**: `R-{YEAR}-{SEQUENCE}`

**規則**:
- 年份: 4 位數（預設當年）
- 序號: 3 位數，從 001 開始
- 每年獨立計數

**範例**:
```
R-2025-001  # 2025 年第 1 筆租賃
R-2025-002  # 2025 年第 2 筆租賃
R-2025-015  # 2025 年第 15 筆租賃
R-2024-150  # 2024 年的第 150 筆
```

### 5. 租金計算

**計算邏輯**:
```python
def calculate_rental_amount(daily_rate, start_date, end_date):
    days = (end_date - start_date).days + 1  # 含頭尾
    return daily_rate * days
```

**重新計算時機**:
- 建立租賃時：依預計歸還日計算
- 交付設備時：計算總金額
- 歸還設備時：依實際歸還日重新計算

**範例**:
```
日租金: $5,000
租賃期間: 2025-01-10 ~ 2025-01-20 (11 天)
總金額: $5,000 × 11 = $55,000

實際歸還: 2025-01-25 (延長 5 天)
重新計算: $5,000 × 16 = $80,000
```

### 6. 設備狀態同步

**租賃交付時**:
- 租賃狀態: `CONFIRMED → ACTIVE`
- 設備狀態: `IN_STOCK → RENTED`
- 記錄異動 log (RENTAL_START)

**租賃歸還時**:
- 租賃狀態: `ACTIVE/OVERDUE → RETURNED`
- 設備狀態: `RENTED → IN_STOCK`
- 記錄異動 log (RENTAL_END)
- 重新計算租金

### 7. 校驗管理 API (Calibration Management)

#### 基本 CRUD 操作
```
GET    /api/calibrations           # 校驗記錄列表
POST   /api/calibrations           # 新增校驗記錄 (Manager+)
GET    /api/calibrations/{id}      # 校驗詳情
PUT    /api/calibrations/{id}      # 更新校驗 (Manager+)
DELETE /api/calibrations/{id}      # 刪除校驗 (Manager+)
```

#### 校驗到期管理
```
GET /api/calibrations/due-soon?days=30
```
- 查詢即將到期的校驗（預設 30 天內）
- 標示逾期狀態
- 計算剩餘天數
- 包含設備資訊

#### 設備校驗歷史
```
GET /api/calibrations/equipment/{equipment_id}
```
- 查詢設備的所有校驗記錄
- 依校驗日期降序排列

### 8. 校驗資料欄位

**校驗記錄**:
- 設備 ID
- 校驗日期
- 下次到期日期
- 校驗提供商
- 證書編號
- 費用
- 備註

**自動記錄**:
- 新增校驗時自動記錄到設備異動歷程
- 包含校驗提供商、證書編號、到期日期

---

## 📂 新增檔案總覽

### Models (3 個)
```
backend/app/models/
├── customer.py          # 客戶模型
├── rental.py            # 租賃模型 (含狀態流轉)
└── calibration.py       # 校驗模型
```

### Schemas (3 個)
```
backend/app/schemas/
├── customer.py          # 客戶 schemas
├── rental.py            # 租賃 schemas (含操作 requests)
└── calibration.py       # 校驗 schemas
```

### API Endpoints (3 個)
```
backend/app/api/
├── customers.py         # 客戶管理 API (220 行)
├── rentals.py           # 租賃管理 API (310 行)
└── calibrations.py      # 校驗管理 API (230 行)
```

### Utilities (1 個)
```
backend/app/utils/
└── rental_number.py     # 租賃單號生成
```

### Database Migration
```
backend/alembic/versions/
└── 20251230_110532_add_customer_rental_and_calibration_.py
```

---

## 🗄️ 資料庫結構

### 資料表總覽 (7 個)

```sql
users              -- 使用者 (Phase 1)
equipments         -- 設備 (Phase 1)
locations          -- 位置/船舶 (Phase 1)
equipment_logs     -- 設備異動歷程 (Phase 2)
customers          -- 客戶 (Phase 3) ✨
rentals            -- 租賃 (Phase 3) ✨
calibrations       -- 校驗 (Phase 3) ✨
```

### Customers Table
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    tax_id VARCHAR(50) UNIQUE,
    contact_person VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    address TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
)
```

### Rentals Table
```sql
CREATE TABLE rentals (
    id INTEGER PRIMARY KEY,
    rental_number VARCHAR(50) UNIQUE NOT NULL,
    equipment_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    expected_end_date DATE NOT NULL,
    actual_end_date DATE,
    daily_rate NUMERIC(10,2) NOT NULL,
    deposit_amount NUMERIC(10,2),
    total_amount NUMERIC(10,2),
    status VARCHAR NOT NULL DEFAULT 'draft',
    notes TEXT,
    delivery_notes TEXT,
    return_notes TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    FOREIGN KEY (equipment_id) REFERENCES equipments(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
```

### Calibrations Table
```sql
CREATE TABLE calibrations (
    id INTEGER PRIMARY KEY,
    equipment_id INTEGER NOT NULL,
    calibration_date DATE NOT NULL,
    next_due_date DATE NOT NULL,
    provider VARCHAR(200) NOT NULL,
    certificate_number VARCHAR(100),
    cost FLOAT,
    notes TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    FOREIGN KEY (equipment_id) REFERENCES equipments(id)
)
```

---

## 🔧 業務邏輯實作

### 1. 租賃建立流程

```python
# Step 1: 建立租賃單 (DRAFT 狀態)
POST /api/rentals
{
  "equipment_id": 1,
  "customer_id": 1,
  "start_date": "2025-02-01",
  "expected_end_date": "2025-02-10",
  "daily_rate": 5000,
  "deposit_amount": 50000
}

# 系統檢查:
✓ 設備是否存在且可用 (IN_STOCK 或 ORDERING)
✓ 客戶是否存在且啟用
✓ 日期是否合理 (結束日 >= 開始日)
✓ 自動生成租賃單號: R-2025-001

# Step 2: 確認租賃
POST /api/rentals/1/confirm
# DRAFT → CONFIRMED

# Step 3: 交付設備
POST /api/rentals/1/deliver
{
  "delivery_notes": "Delivered to customer site",
  "latitude": 25.0330,
  "longitude": 121.5654
}

# 系統處理:
✓ 租賃狀態: CONFIRMED → ACTIVE
✓ 設備狀態: IN_STOCK → RENTED
✓ 計算總金額 (日租金 × 天數)
✓ 記錄異動 log (RENTAL_START)

# Step 4: 歸還設備
POST /api/rentals/1/return
{
  "actual_end_date": "2025-02-12",  # 延長 2 天
  "return_notes": "Equipment returned in good condition"
}

# 系統處理:
✓ 租賃狀態: ACTIVE → RETURNED
✓ 設備狀態: RENTED → IN_STOCK
✓ 重新計算總金額 (實際日期)
✓ 記錄異動 log (RENTAL_END)
```

### 2. 租金計算範例

**範例 1: 正常歸還**
```
日租金: $5,000
預計: 2025-02-01 ~ 2025-02-10 (10 天)
預計金額: $50,000

實際: 2025-02-10 (準時)
實際金額: $50,000
```

**範例 2: 延期歸還**
```
日租金: $5,000
預計: 2025-02-01 ~ 2025-02-10 (10 天)
預計金額: $50,000

實際: 2025-02-15 (延長 5 天)
實際金額: $5,000 × 15 = $75,000
```

**範例 3: 提前歸還**
```
日租金: $5,000
預計: 2025-02-01 ~ 2025-02-10 (10 天)
預計金額: $50,000

實際: 2025-02-07 (提前 3 天)
實際金額: $5,000 × 7 = $35,000
```

### 3. 逾期檢查機制

```python
# 每次查詢 /api/rentals/overdue 時自動執行

today = date.today()

# 查詢所有進行中且超過預期日期的租賃
overdue_rentals = rentals.filter(
    status == ACTIVE,
    expected_end_date < today
)

# 自動更新狀態
for rental in overdue_rentals:
    rental.status = OVERDUE
```

### 4. 校驗到期提醒

```python
# GET /api/calibrations/due-soon?days=30

today = date.today()
future_date = today + timedelta(days=30)

# 查詢 30 天內到期的校驗
calibrations = calibrations.filter(
    next_due_date <= future_date
)

# 返回資料包含:
- 校驗記錄
- 設備資產編號
- 設備名稱
- 剩餘天數 (可為負數表示逾期)
- 是否逾期標示
```

**範例輸出**:
```json
[
  {
    "calibration": {...},
    "equipment_asset_code": "MBES-2025-001",
    "equipment_name": "Kongsberg EM2040C",
    "days_until_due": 15,
    "is_overdue": false
  },
  {
    "calibration": {...},
    "equipment_asset_code": "GNSS-2024-010",
    "equipment_name": "Trimble R12",
    "days_until_due": -5,
    "is_overdue": true
  }
]
```

---

## 📊 API 端點總覽

### 客戶管理 (6 個)
```
GET    /api/customers
POST   /api/customers
GET    /api/customers/{id}
PUT    /api/customers/{id}
DELETE /api/customers/{id}
GET    /api/customers/{id}/rentals
```

### 租賃管理 (10 個)
```
GET    /api/rentals
POST   /api/rentals
GET    /api/rentals/{id}
PUT    /api/rentals/{id}
DELETE /api/rentals/{id}
POST   /api/rentals/{id}/confirm
POST   /api/rentals/{id}/deliver
POST   /api/rentals/{id}/return
POST   /api/rentals/{id}/cancel
GET    /api/rentals/overdue
```

### 校驗管理 (6 個)
```
GET    /api/calibrations
POST   /api/calibrations
GET    /api/calibrations/{id}
PUT    /api/calibrations/{id}
DELETE /api/calibrations/{id}
GET    /api/calibrations/due-soon
GET    /api/calibrations/equipment/{id}
```

**Phase 3 新增**: 21 個端點
**累計總數**: 54 個端點

---

## 🎯 使用情境範例

### 情境 1: 租賃設備給客戶

```
1. 建立客戶資料
   POST /api/customers
   {
     "company_name": "Ocean Survey Co.",
     "tax_id": "12345678",
     "contact_person": "John Wang",
     "phone": "0912-345-678",
     "email": "john@oceansurvey.com"
   }
   → 客戶 ID: 1

2. 建立租賃單 (草稿)
   POST /api/rentals
   {
     "equipment_id": 1,          # MBES-2025-001
     "customer_id": 1,
     "start_date": "2025-02-01",
     "expected_end_date": "2025-02-10",
     "daily_rate": 5000,
     "deposit_amount": 50000
   }
   → 租賃單號: R-2025-001
   → 狀態: DRAFT

3. 確認租賃
   POST /api/rentals/1/confirm
   → 狀態: DRAFT → CONFIRMED

4. 交付設備
   POST /api/rentals/1/deliver
   {
     "delivery_notes": "Delivered to Keelung Port",
     "latitude": 25.1326,
     "longitude": 121.7390
   }
   → 租賃狀態: CONFIRMED → ACTIVE
   → 設備狀態: IN_STOCK → RENTED
   → 總金額: $50,000

5. 歸還設備 (實際延長 2 天)
   POST /api/rentals/1/return
   {
     "actual_end_date": "2025-02-12",
     "return_notes": "Equipment returned in good condition"
   }
   → 租賃狀態: ACTIVE → RETURNED
   → 設備狀態: RENTED → IN_STOCK
   → 重新計算金額: $60,000 (12 天)
```

### 情境 2: 校驗管理

```
1. 設備送校驗
   POST /api/calibrations
   {
     "equipment_id": 1,
     "calibration_date": "2025-01-15",
     "next_due_date": "2026-01-15",
     "provider": "National Measurement Laboratory",
     "certificate_number": "CAL-2025-0123",
     "cost": 15000,
     "notes": "Annual calibration completed"
   }
   → 自動記錄到設備異動歷程

2. 查詢即將到期的校驗
   GET /api/calibrations/due-soon?days=60
   → 返回 60 天內到期的校驗清單
   → 標示逾期狀態
   → 顯示剩餘天數

3. 查詢設備校驗歷史
   GET /api/calibrations/equipment/1
   → 顯示該設備的所有校驗記錄
   → 追蹤校驗週期
```

### 情境 3: 逾期管理

```
1. 系統自動檢查逾期租賃
   GET /api/rentals/overdue

2. 系統處理:
   - 查詢所有 ACTIVE 狀態且超過預期日期的租賃
   - 自動更新狀態: ACTIVE → OVERDUE
   - 返回逾期清單

3. Manager 聯絡客戶催還

4. 客戶歸還設備
   POST /api/rentals/{id}/return
   → 計算實際金額（包含逾期費用）
```

---

## 📊 開發統計

### Git Commits
```
8 commits total (Phase 1-3)
- eee26b5: Initial commit
- 9cd3a2d: Setup
- 05bae90: Phase 1 - Authentication
- 985628f: Phase 1 docs
- ada9990: Merge
- 44c429f: Phase 2 - Equipment Management
- 04a98ec: Phase 2 docs
- 2163cc4: Phase 3 - Rental & Calibration ✨ NEW
```

### 程式碼統計 (Phase 3)
- **新增檔案**: 16 個
- **新增程式碼**: ~1,743 行
- **API 端點**: 21 個新端點
- **資料表**: 3 個新表

### 累計統計 (Phase 1-3)
| 項目 | Phase 1 | Phase 2 | Phase 3 | 總計 |
|------|---------|---------|---------|------|
| API 端點 | 13 | 20 | 21 | **54** |
| 資料表 | 3 | 1 | 3 | **7** |
| Models | 3 | 1 | 3 | **7** |
| 程式碼 | ~2,500 | ~1,328 | ~1,743 | **~5,571** |

---

## 🧪 測試範例

### 1. 啟動後端
```powershell
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 2. 訪問 Swagger UI
http://localhost:8000/docs

### 3. 測試租賃流程

**建立客戶**:
```bash
curl -X POST "http://localhost:8000/api/customers" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "contact_person": "John Doe",
    "phone": "0912-345-678",
    "email": "test@example.com"
  }'
```

**建立租賃單**:
```bash
curl -X POST "http://localhost:8000/api/rentals" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": 1,
    "customer_id": 1,
    "start_date": "2025-02-01",
    "expected_end_date": "2025-02-10",
    "daily_rate": 5000,
    "deposit_amount": 50000
  }'
```

**交付設備**:
```bash
curl -X POST "http://localhost:8000/api/rentals/1/deliver" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_notes": "Delivered successfully"
  }'
```

### 4. 測試校驗管理

**新增校驗記錄**:
```bash
curl -X POST "http://localhost:8000/api/calibrations" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": 1,
    "calibration_date": "2025-01-15",
    "next_due_date": "2026-01-15",
    "provider": "Calibration Lab",
    "certificate_number": "CAL-2025-001",
    "cost": 15000
  }'
```

**查詢即將到期**:
```bash
curl -X GET "http://localhost:8000/api/calibrations/due-soon?days=30" \
  -H "Authorization: Bearer <token>"
```

---

## 🎯 下一階段計畫 (Phase 4)

### 1. 統計報表 API
- [ ] Dashboard 統計數據
- [ ] 設備使用率報表
- [ ] 租賃營收報表
- [ ] 校驗到期統計

### 2. Deployment 管理
- [ ] Deployment model (自用部署記錄)
- [ ] 部署 CRUD API
- [ ] 專案管理功能

### 3. 前端開發 (關鍵!)
- [ ] 登入頁面 (兩階段認證)
- [ ] 2FA 設定頁面
- [ ] Dashboard 儀表板
- [ ] 設備管理頁面
- [ ] 租賃管理頁面
- [ ] 客戶管理頁面
- [ ] QR Code 掃描功能

### 4. 進階功能
- [ ] 批次 QR Code 列印
- [ ] Excel 匯出功能
- [ ] Email 通知 (到期提醒)
- [ ] 資料備份功能

---

## ✅ 檢查清單

- [x] Customer model 建立
- [x] Rental model 建立
- [x] Calibration model 建立
- [x] 客戶管理 API
- [x] 租賃管理 API
- [x] 校驗管理 API
- [x] 租賃單號自動生成
- [x] 租金自動計算
- [x] 設備狀態同步
- [x] 逾期自動檢查
- [x] 校驗到期提醒
- [x] Migration 執行成功
- [x] API 測試通過
- [x] 代碼推送到 GitHub
- [x] 文件撰寫完成
- [ ] 前端頁面開發

---

## 📈 後端 API 開發進度

```
Phase 1: 認證系統 ✅ (13 endpoints)
├─ 登入 (兩階段)
├─ 2FA 管理
└─ 使用者管理

Phase 2: 設備管理 ✅ (20 endpoints)
├─ 設備 CRUD
├─ 位置管理
├─ QR Code 功能
└─ 異動歷程

Phase 3: 租賃校驗 ✅ (21 endpoints)
├─ 客戶管理
├─ 租賃管理
├─ 租賃狀態流轉
└─ 校驗管理

Phase 4: 統計報表 (規劃中)
├─ Dashboard API
├─ 報表 API
└─ 部署管理

後端 API: 90% 完成
前端頁面: 0% 完成 (下一優先項目!)
```

---

**文件版本**: 1.0
**最後更新**: 2025-12-30 11:07
**作者**: CHC
**GitHub**: https://github.com/CHC1978/DG_Workshop
**下一步**: 建議開始前端開發，讓系統能實際使用
