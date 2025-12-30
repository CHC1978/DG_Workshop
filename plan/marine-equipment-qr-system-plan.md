# 海洋設備 QR Code 管理系統 - 開發計畫書

**建立日期**: 2025-12-30 (週二)  
**版本**: 1.0  
**狀態**: 規劃完成，待開發

---

## 1. 專案概述

### 1.1 專案目標

建立一套 Web-based 海洋調查設備資產管理系統，透過 QR Code 實現設備快速識別、狀態追蹤、租賃管理等功能。

### 1.2 核心功能

| 功能模組 | 說明 |
|----------|------|
| 設備資產管理 | 設備 CRUD、分類、規格、QR 標籤產生 |
| 庫存調度 | 部署出庫/回收入庫、位置追蹤（船舶/倉庫） |
| 租賃管理 | 客戶管理、租賃單、出租/歸還、租金計算 |
| 校驗維護 | 校驗排程、到期提醒、維修紀錄 |
| 使用者認證 | 帳號管理、2FA (TOTP)、角色權限 |
| 行動存取 | PWA、手機相機掃碼、離線支援 |

### 1.3 使用情境

1. **網頁登入**: 桌面瀏覽器進入系統進行完整管理操作
2. **手機掃碼**: 現場掃描設備 QR Code，快速查看/操作設備
3. **兩階段認證**: 所有登入需通過 Google/Microsoft Authenticator 驗證

---

## 2. 技術棧

### 2.1 後端

| 項目 | 選擇 | 版本 | 說明 |
|------|------|------|------|
| 語言 | Python | 3.12+ | Claude Code 支援最佳 |
| 框架 | FastAPI | 0.115+ | 高效能 async API |
| ORM | SQLAlchemy | 2.0+ | 支援 async |
| 資料庫 | SQLite | 3.45+ | 輕量、單檔案、WAL 模式 |
| Migration | Alembic | 1.13+ | 資料庫版本控制 |
| 認證 | python-jose + pyotp | - | JWT + TOTP 2FA |
| 密碼 | passlib + bcrypt | - | 安全雜湊 |

### 2.2 前端

| 項目 | 選擇 | 版本 | 說明 |
|------|------|------|------|
| Runtime | Bun | 1.1+ | 取代 Node.js |
| 框架 | Vue 3 | 3.5+ | Composition API |
| 建置 | Vite | 6.0+ | 開發/打包 |
| 狀態管理 | Pinia | 2.2+ | 含持久化 |
| 路由 | Vue Router | 4.4+ | - |
| 樣式 | TailwindCSS | 3.4+ | Utility-first CSS |
| UI 元件 | Headless UI | 2.2+ | 無樣式元件 |
| QR 掃描 | vue-qrcode-reader | 5.5+ | 相機掃碼 |
| QR 產生 | qrcode | 1.5+ | 產生 QR 圖片 |
| PWA | vite-plugin-pwa | 0.21+ | 離線支援 |
| HTTP | axios | 1.7+ | API 請求 |
| 工具 | @vueuse/core | 11+ | Composables |

### 2.3 開發環境

```
作業系統: Linux / macOS / Windows (WSL2)
編輯器: VS Code + Claude Code
版本控制: Git
容器化: Docker (選配，部署用)
```

---

## 3. 專案結構

```
marine-equipment-qr/
├── CLAUDE.md                    # Claude Code 專案說明 (重要!)
├── README.md                    # 專案說明文件
├── docker-compose.yml           # Docker 部署配置 (選配)
│
├── backend/                     # Python FastAPI 後端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 應用程式入口
│   │   ├── api/                 # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── router.py        # 路由彙整
│   │   │   ├── auth.py          # 認證 (登入/2FA)
│   │   │   ├── users.py         # 使用者管理
│   │   │   ├── equipment.py     # 設備管理
│   │   │   ├── locations.py     # 位置/船舶管理
│   │   │   ├── deployments.py   # 部署調度
│   │   │   ├── rentals.py       # 租賃管理
│   │   │   ├── customers.py     # 客戶管理
│   │   │   ├── calibrations.py  # 校驗管理
│   │   │   └── qrcode.py        # QR Code 產生
│   │   ├── core/                # 核心模組
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # 環境設定
│   │   │   ├── database.py      # 資料庫連線
│   │   │   ├── security.py      # JWT/TOTP/密碼
│   │   │   └── deps.py          # 依賴注入 (權限檢查)
│   │   ├── models/              # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Base model
│   │   │   ├── user.py          # 使用者
│   │   │   ├── equipment.py     # 設備
│   │   │   ├── location.py      # 位置/船舶
│   │   │   ├── deployment.py    # 部署紀錄
│   │   │   ├── rental.py        # 租賃
│   │   │   ├── customer.py      # 客戶
│   │   │   ├── calibration.py   # 校驗
│   │   │   └── equipment_log.py # 異動歷程
│   │   └── schemas/             # Pydantic Schemas
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── user.py
│   │       ├── equipment.py
│   │       ├── location.py
│   │       ├── deployment.py
│   │       ├── rental.py
│   │       ├── customer.py
│   │       └── calibration.py
│   ├── alembic/                 # 資料庫 Migration
│   │   ├── env.py
│   │   ├── versions/
│   │   └── alembic.ini
│   ├── tests/                   # 測試
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   └── test_equipment.py
│   ├── data/                    # SQLite 資料庫檔案
│   │   └── .gitkeep
│   ├── pyproject.toml           # Python 專案設定
│   └── requirements.txt         # 依賴清單
│
├── frontend/                    # Vue 3 前端
│   ├── index.html
│   ├── package.json
│   ├── bun.lockb
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── public/
│   │   ├── favicon.ico
│   │   └── icons/               # PWA 圖示
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       │   └── index.ts         # 路由設定
│       ├── stores/              # Pinia Stores
│       │   ├── auth.ts          # 認證狀態
│       │   ├── equipment.ts
│       │   └── ui.ts            # UI 狀態
│       ├── api/                 # API 封裝
│       │   ├── client.ts        # Axios instance
│       │   ├── auth.ts
│       │   ├── equipment.ts
│       │   └── ...
│       ├── composables/         # 可重用邏輯
│       │   ├── useAuth.ts
│       │   ├── useScanner.ts    # QR 掃描
│       │   └── usePermission.ts
│       ├── components/          # 共用元件
│       │   ├── common/
│       │   │   ├── AppHeader.vue
│       │   │   ├── AppSidebar.vue
│       │   │   ├── DataTable.vue
│       │   │   └── ConfirmDialog.vue
│       │   ├── equipment/
│       │   │   ├── EquipmentCard.vue
│       │   │   ├── EquipmentForm.vue
│       │   │   └── QRCodeLabel.vue
│       │   └── auth/
│       │       ├── LoginForm.vue
│       │       └── TotpInput.vue
│       ├── layouts/             # 版面配置
│       │   ├── MainLayout.vue
│       │   └── AuthLayout.vue
│       ├── views/               # 頁面
│       │   ├── LoginView.vue
│       │   ├── Setup2FAView.vue
│       │   ├── DashboardView.vue
│       │   ├── ScannerView.vue
│       │   ├── equipment/
│       │   │   ├── EquipmentListView.vue
│       │   │   └── EquipmentDetailView.vue
│       │   ├── rentals/
│       │   │   ├── RentalListView.vue
│       │   │   └── RentalDetailView.vue
│       │   ├── locations/
│       │   │   └── LocationListView.vue
│       │   └── admin/
│       │       ├── UserListView.vue
│       │       └── SettingsView.vue
│       ├── types/               # TypeScript 型別
│       │   ├── equipment.ts
│       │   ├── user.ts
│       │   └── api.ts
│       └── utils/               # 工具函式
│           ├── format.ts
│           └── validators.ts
│
└── docs/                        # 文件
    ├── api.md                   # API 文件
    ├── deployment.md            # 部署指南
    └── user-guide.md            # 使用手冊
```

---

## 4. 資料模型

### 4.1 ER Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     User        │     │    Equipment    │     │    Location     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ username        │     │ asset_code (UQ) │     │ name            │
│ email           │     │ qr_code (UQ)    │     │ location_type   │
│ hashed_password │     │ category        │◄────│ code (UQ)       │
│ full_name       │     │ manufacturer    │     │ imo_number      │
│ role            │     │ model           │     │ call_sign       │
│ totp_secret     │     │ serial_number   │     │ owner_company   │
│ totp_enabled    │     │ status ─────────┼──── │ is_active       │
│ is_active       │     │ purchase_date   │     └─────────────────┘
└─────────────────┘     │ purchase_price  │
                        │ rental_daily_rate│
                        │ current_location_id (FK)│
                        └────────┬────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Deployment    │     │     Rental      │     │   Calibration   │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ equipment_id(FK)│     │ rental_number   │     │ equipment_id(FK)│
│ location_id(FK) │     │ equipment_id(FK)│     │ calibration_date│
│ project_id      │     │ customer_id(FK) │     │ next_due_date   │
│ deployed_at     │     │ start_date      │     │ provider        │
│ expected_return │     │ expected_end    │     │ certificate_no  │
│ actual_return   │     │ actual_end_date │     │ notes           │
│ deployed_by(FK) │     │ daily_rate      │     └─────────────────┘
│ purpose         │     │ deposit_amount  │
└─────────────────┘     │ total_amount    │     ┌─────────────────┐
                        │ status          │     │   Customer      │
                        └────────┬────────┘     ├─────────────────┤
                                 │              │ id (PK)         │
                                 └─────────────►│ company_name    │
                                                │ tax_id          │
┌─────────────────┐                             │ contact_person  │
│  EquipmentLog   │                             │ phone           │
├─────────────────┤                             │ email           │
│ id (PK)         │                             │ address         │
│ equipment_id(FK)│                             └─────────────────┘
│ log_type        │
│ old_value       │
│ new_value       │
│ description     │
│ created_at      │
│ created_by (FK) │
│ latitude        │
│ longitude       │
└─────────────────┘
```

### 4.2 列舉型別 (Enum)

```python
# 設備狀態
class EquipmentStatus(str, Enum):
    ORDERING = "ordering"      # 採購中
    IN_STOCK = "in_stock"      # 庫存中
    DEPLOYED = "deployed"      # 自用部署中
    RENTED = "rented"          # 租賃中
    REPAIR = "repair"          # 維修中
    DISPOSED = "disposed"      # 已報廢
    LOST = "lost"              # 遺失

# 設備類別
class EquipmentCategory(str, Enum):
    MBES = "mbes"              # 多音束測深儀
    GNSS = "gnss"              # 衛星定位系統
    SVP = "svp"                # 聲速剖面儀
    SBP = "sbp"                # 淺層剖面儀
    USBL = "usbl"              # 水下定位系統
    ROV = "rov"                # 水下無人載具
    INS = "ins"                # 慣性導航系統
    MAG = "magnetometer"       # 磁力儀
    OTHER = "other"            # 其他

# 位置類型
class LocationType(str, Enum):
    WAREHOUSE = "warehouse"    # 倉庫
    VESSEL = "vessel"          # 船舶
    PLATFORM = "platform"      # 平台
    VEHICLE = "vehicle"        # 車輛
    EXTERNAL = "external"      # 外部（租賃客戶處）

# 租賃狀態
class RentalStatus(str, Enum):
    DRAFT = "draft"            # 草稿/報價中
    CONFIRMED = "confirmed"    # 已確認
    ACTIVE = "active"          # 租賃中
    OVERDUE = "overdue"        # 逾期未還
    RETURNED = "returned"      # 已歸還
    CANCELLED = "cancelled"    # 已取消

# 使用者角色
class UserRole(str, Enum):
    ADMIN = "admin"            # 系統管理員
    MANAGER = "manager"        # 設備經理
    OPERATOR = "operator"      # 操作員
    VIEWER = "viewer"          # 檢視者

# 異動紀錄類型
class EquipmentLogType(str, Enum):
    STATUS_CHANGE = "status_change"
    LOCATION_CHANGE = "location_change"
    RENTAL_START = "rental_start"
    RENTAL_END = "rental_end"
    CALIBRATION = "calibration"
    MAINTENANCE = "maintenance"
    NOTE = "note"
```

### 4.3 權限控制矩陣

| 功能 | Admin | Manager | Operator | Viewer |
|------|:-----:|:-------:|:--------:|:------:|
| 檢視設備 | ✅ | ✅ | ✅ | ✅ |
| 掃碼查詢 | ✅ | ✅ | ✅ | ✅ |
| 新增/編輯設備 | ✅ | ✅ | ❌ | ❌ |
| 刪除設備 | ✅ | ❌ | ❌ | ❌ |
| 部署/回收操作 | ✅ | ✅ | ✅ | ❌ |
| 租賃管理 | ✅ | ✅ | ❌ | ❌ |
| 客戶管理 | ✅ | ✅ | ❌ | ❌ |
| 使用者管理 | ✅ | ❌ | ❌ | ❌ |
| 系統設定 | ✅ | ❌ | ❌ | ❌ |

---

## 5. API 設計

### 5.1 認證 API

```
POST   /api/auth/login/step1        # 帳密驗證 → 返回臨時 token
POST   /api/auth/login/step2        # TOTP 驗證 → 返回 JWT
POST   /api/auth/logout             # 登出
POST   /api/auth/2fa/setup          # 設定 2FA (產生 QR)
POST   /api/auth/2fa/confirm        # 確認 2FA 綁定
POST   /api/auth/refresh            # 刷新 token
GET    /api/auth/me                 # 取得當前使用者資訊
```

### 5.2 使用者管理 API

```
GET    /api/users                   # 使用者列表 (Admin)
POST   /api/users                   # 新增使用者 (Admin)
GET    /api/users/{id}              # 使用者詳情
PUT    /api/users/{id}              # 更新使用者
DELETE /api/users/{id}              # 刪除使用者 (Admin)
POST   /api/users/{id}/reset-2fa    # 重設 2FA (Admin)
```

### 5.3 設備管理 API

```
GET    /api/equipment               # 設備列表 (支援篩選、分頁)
POST   /api/equipment               # 新增設備
GET    /api/equipment/{id}          # 設備詳情
PUT    /api/equipment/{id}          # 更新設備
DELETE /api/equipment/{id}          # 刪除設備 (Admin)

GET    /api/equipment/by-qr/{code}  # 透過 QR Code 查詢 (掃碼用)
GET    /api/equipment/{id}/logs     # 設備異動歷程
GET    /api/equipment/{id}/qrcode   # 取得 QR Code 圖片

POST   /api/equipment/{id}/deploy   # 部署出庫
POST   /api/equipment/{id}/return   # 回收入庫
POST   /api/equipment/{id}/repair   # 送修
```

### 5.4 位置/船舶 API

```
GET    /api/locations               # 位置列表
POST   /api/locations               # 新增位置
GET    /api/locations/{id}          # 位置詳情
PUT    /api/locations/{id}          # 更新位置
DELETE /api/locations/{id}          # 刪除位置

GET    /api/locations/{id}/equipment  # 該位置的設備清單
```

### 5.5 租賃管理 API

```
GET    /api/rentals                 # 租賃單列表
POST   /api/rentals                 # 新增租賃單
GET    /api/rentals/{id}            # 租賃單詳情
PUT    /api/rentals/{id}            # 更新租賃單
DELETE /api/rentals/{id}            # 刪除租賃單

POST   /api/rentals/{id}/confirm    # 確認租賃
POST   /api/rentals/{id}/deliver    # 交付出租
POST   /api/rentals/{id}/return     # 歸還
POST   /api/rentals/{id}/cancel     # 取消

GET    /api/customers               # 客戶列表
POST   /api/customers               # 新增客戶
GET    /api/customers/{id}          # 客戶詳情
PUT    /api/customers/{id}          # 更新客戶
GET    /api/customers/{id}/rentals  # 客戶租賃歷史
```

### 5.6 校驗維護 API

```
GET    /api/calibrations            # 校驗紀錄列表
POST   /api/calibrations            # 新增校驗紀錄
GET    /api/calibrations/{id}       # 校驗詳情
PUT    /api/calibrations/{id}       # 更新校驗紀錄
GET    /api/calibrations/due-soon   # 即將到期清單
```

### 5.7 統計報表 API

```
GET    /api/stats/dashboard         # 儀表板統計
GET    /api/stats/equipment-usage   # 設備使用率
GET    /api/stats/rental-revenue    # 租賃營收
GET    /api/stats/calibration-due   # 校驗到期統計
```

---

## 6. 認證流程

### 6.1 登入流程 (2FA)

```
┌─────────────────────────────────────────────────────────────────┐
│                        登入流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  使用者                     前端                      後端       │
│    │                        │                         │         │
│    │─── 輸入帳號密碼 ───────►│                         │         │
│    │                        │─── POST /login/step1 ──►│         │
│    │                        │                         │         │
│    │                        │◄── { temp_token } ──────│         │
│    │                        │                         │         │
│    │◄── 顯示 TOTP 輸入 ─────│                         │         │
│    │                        │                         │         │
│    │─── 輸入 6 位數碼 ──────►│                         │         │
│    │                        │─── POST /login/step2 ──►│         │
│    │                        │    { temp_token, code } │         │
│    │                        │                         │         │
│    │                        │◄── { access_token } ────│         │
│    │                        │                         │         │
│    │◄── 跳轉至首頁 ─────────│                         │         │
│    │                        │                         │         │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 首次 2FA 設定流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     2FA 設定流程                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 管理員建立使用者帳號（預設 2FA 未啟用）                        │
│                                                                 │
│  2. 使用者首次登入，系統導向 /setup-2fa 頁面                       │
│                                                                 │
│  3. 前端呼叫 POST /auth/2fa/setup                               │
│     → 後端產生 TOTP secret + QR Code + 備用碼                    │
│     → 返回 { secret, qr_code_base64, backup_codes }             │
│                                                                 │
│  4. 使用者開啟 Google/Microsoft Authenticator                    │
│     → 掃描 QR Code 或手動輸入 secret                             │
│     → App 顯示 6 位數動態碼                                      │
│                                                                 │
│  5. 使用者輸入驗證碼，前端呼叫 POST /auth/2fa/confirm             │
│     → 後端驗證 TOTP 碼                                          │
│     → 成功則啟用 2FA，標記 totp_enabled = true                   │
│                                                                 │
│  6. 使用者記錄備用碼（一次性顯示）                                 │
│                                                                 │
│  7. 跳轉至正常登入流程                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 TOTP 規格

| 項目 | 設定值 |
|------|--------|
| 演算法 | TOTP (RFC 6238) |
| 雜湊 | SHA-1 |
| 位數 | 6 digits |
| 週期 | 30 seconds |
| 容許誤差 | ±1 週期 (valid_window=1) |
| Secret 編碼 | Base32 |
| 備用碼數量 | 8 組 |
| 備用碼格式 | 8 hex chars (如 A1B2C3D4) |

---

## 7. 前端路由

```typescript
const routes = [
  // 公開頁面
  { path: '/login', component: LoginView, meta: { requiresAuth: false } },
  { path: '/setup-2fa', component: Setup2FAView, meta: { requires2FASetup: true } },
  
  // QR Code 掃描入口（需登入）
  { path: '/e/:assetCode', component: EquipmentQuickView, meta: { requiresAuth: true } },
  
  // 主要功能頁面
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: DashboardView },
      
      // 設備管理
      { path: 'equipment', component: EquipmentListView },
      { path: 'equipment/:id', component: EquipmentDetailView },
      
      // 掃碼功能
      { path: 'scan', component: ScannerView },
      
      // 位置/船舶
      { path: 'locations', component: LocationListView },
      { path: 'locations/:id', component: LocationDetailView },
      
      // 租賃管理
      { path: 'rentals', component: RentalListView },
      { path: 'rentals/:id', component: RentalDetailView },
      { path: 'customers', component: CustomerListView },
      { path: 'customers/:id', component: CustomerDetailView },
      
      // 校驗管理
      { path: 'calibrations', component: CalibrationListView },
      
      // 管理功能
      {
        path: 'admin',
        meta: { requiresRole: ['admin'] },
        children: [
          { path: 'users', component: UserListView },
          { path: 'users/:id', component: UserDetailView },
          { path: 'settings', component: SettingsView },
        ]
      }
    ]
  },
  
  // 404
  { path: '/:pathMatch(.*)*', component: NotFoundView }
]
```

---

## 8. QR Code 設計

### 8.1 QR Code 內容格式

```
https://{domain}/e/{asset_code}

範例:
https://equip.company.com/e/MBES-2024-001
https://equip.company.com/e/GNSS-2023-015
```

### 8.2 資產編號規則

```
格式: {類別}-{年份}-{序號}

範例:
MBES-2024-001    多音束測深儀
GNSS-2023-015    GNSS 接收器
SBP-2024-003     淺層剖面儀
SVP-2022-008     聲速剖面儀
```

### 8.3 QR 標籤設計

```
┌─────────────────────────────┐
│  ┌───────────────────────┐  │
│  │                       │  │
│  │      [QR Code]        │  │
│  │                       │  │
│  └───────────────────────┘  │
│                             │
│  MBES-2024-001              │
│  Kongsberg EM2040C          │
│  S/N: 12345678              │
│                             │
│  [公司 Logo]                 │
└─────────────────────────────┘
```

### 8.4 標籤材質建議

| 環境 | 材質建議 |
|------|----------|
| 室內/倉庫 | 防水貼紙 (PP/PET) |
| 船舶甲板 | 雷射雕刻金屬牌 |
| 水下設備 | 陽極處理鋁牌 |
| 高溫設備 | 耐高溫陶瓷標籤 |

---

## 9. 開發階段規劃

### Phase 1: 基礎架構 (Week 1-2)

```
□ 專案初始化
  □ 建立 backend/ 目錄結構
  □ 建立 frontend/ 目錄結構
  □ 撰寫 CLAUDE.md
  □ 設定 Git repository

□ 後端基礎
  □ FastAPI 專案初始化
  □ SQLAlchemy + SQLite 設定 (WAL 模式)
  □ Alembic migration 初始化
  □ 基本 models: User, Equipment, Location
  □ 環境設定 (config.py)

□ 認證模組
  □ 密碼雜湊 (bcrypt)
  □ JWT 產生/驗證
  □ TOTP 2FA 實作
  □ 認證 API endpoints

□ 前端基礎
  □ Vite + Vue 3 + Bun 專案初始化
  □ TailwindCSS 設定
  □ Vue Router 設定
  □ Pinia 狀態管理
  □ Axios API client 封裝
```

### Phase 2: 核心功能 (Week 3-4)

```
□ 使用者模組
  □ 使用者 CRUD API
  □ 角色權限控制
  □ 使用者管理頁面

□ 設備管理
  □ Equipment model 完整欄位
  □ 設備 CRUD API
  □ 設備列表頁 (含篩選、搜尋、分頁)
  □ 設備詳情頁
  □ 設備表單 (新增/編輯)

□ 位置/船舶管理
  □ Location model
  □ 位置 CRUD API
  □ 位置管理頁面

□ QR Code 功能
  □ QR Code 產生 API
  □ 標籤預覽/下載
  □ 批次列印功能
```

### Phase 3: 調度與租賃 (Week 5-6)

```
□ 部署調度
  □ Deployment model
  □ 部署/回收 API
  □ 部署紀錄頁面
  □ 設備狀態流轉

□ 租賃管理
  □ Rental, Customer models
  □ 租賃 CRUD API
  □ 租賃單頁面
  □ 客戶管理頁面
  □ 租金計算

□ 異動歷程
  □ EquipmentLog model
  □ 自動記錄異動
  □ 歷程查詢頁面
```

### Phase 4: 行動與 PWA (Week 7-8)

```
□ PWA 設定
  □ vite-plugin-pwa 設定
  □ Service Worker
  □ 離線 cache 策略
  □ App manifest

□ 手機掃碼
  □ 相機權限處理
  □ vue-qrcode-reader 整合
  □ 掃碼頁面
  □ 設備快速檢視頁

□ RWD 優化
  □ 響應式版面調整
  □ 行動版導航
  □ 觸控優化
```

### Phase 5: 校驗與報表 (Week 9-10)

```
□ 校驗管理
  □ Calibration model
  □ 校驗 CRUD API
  □ 到期提醒功能
  □ 校驗紀錄頁面

□ 儀表板與報表
  □ 統計 API
  □ Dashboard 頁面
  □ 圖表元件 (Chart.js / ECharts)
  □ 匯出功能 (Excel)

□ 測試與優化
  □ 後端單元測試
  □ API 整合測試
  □ 效能優化
  □ 安全性檢查
```

---

## 10. CLAUDE.md 範本

```markdown
# 海洋設備 QR Code 管理系統

## 專案概述

海洋調查設備資產管理系統，支援 QR Code 掃描、設備追蹤、租賃管理。

## 技術棧

- **後端**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + SQLite
- **前端**: Bun + Vue 3 + Vite + TailwindCSS + PWA
- **認證**: JWT + TOTP 2FA (Google/Microsoft Authenticator)

## 開發指令

### 後端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 執行 migration
alembic upgrade head

# 啟動開發伺服器
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
bun install
bun dev          # 開發伺服器 (port 5173)
bun run build    # 生產建置
```

## 資料庫

- 使用 SQLite，檔案位於 `backend/data/marine_equipment.db`
- 啟用 WAL 模式提升並發效能
- Migration 檔案在 `backend/alembic/versions/`

## API 文件

- 開發環境: http://localhost:8000/docs (Swagger UI)
- 替代文件: http://localhost:8000/redoc

## 命名慣例

- Python: snake_case
- TypeScript/Vue: camelCase (變數), PascalCase (元件)
- API endpoints: kebab-case
- 資料庫表: 複數形式 (equipments, calibrations)

## 設備類別代碼

| 代碼 | 中文 | 英文 |
|------|------|------|
| MBES | 多音束測深儀 | Multibeam Echosounder |
| GNSS | 衛星定位系統 | GNSS Receiver |
| SVP | 聲速剖面儀 | Sound Velocity Profiler |
| SBP | 淺層剖面儀 | Sub-bottom Profiler |
| USBL | 水下定位系統 | Ultra-Short Baseline |
| ROV | 水下無人載具 | Remotely Operated Vehicle |
| INS | 慣性導航系統 | Inertial Navigation System |
| MAG | 磁力儀 | Magnetometer |

## 重要檔案位置

- 環境設定: `backend/app/core/config.py`
- 資料庫模型: `backend/app/models/`
- API 路由: `backend/app/api/`
- 認證邏輯: `backend/app/core/security.py`
- 前端路由: `frontend/src/router/index.ts`
- 狀態管理: `frontend/src/stores/`
- API 封裝: `frontend/src/api/`

## 環境變數

建立 `backend/.env`:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/marine_equipment.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
TEMP_TOKEN_EXPIRE_MINUTES=5
```

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
```

---

## 11. 部署架構

### 11.1 簡易部署 (單一伺服器)

```
┌─────────────────────────────────────────┐
│            單一伺服器 / NAS             │
├─────────────────────────────────────────┤
│                                         │
│   ┌─────────┐      ┌─────────────────┐ │
│   │  Nginx  │─────►│  FastAPI        │ │
│   │ (Proxy) │      │  (uvicorn)      │ │
│   │ :80/443 │      │  :8000          │ │
│   └────┬────┘      └────────┬────────┘ │
│        │                    │          │
│        │           ┌────────▼────────┐ │
│   Vue PWA          │    SQLite       │ │
│   靜態檔案         │  marine.db      │ │
│                    └─────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### 11.2 Docker 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/marine_equipment.db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## 12. 安全性考量

### 12.1 認證安全

| 項目 | 措施 |
|------|------|
| 密碼儲存 | bcrypt 雜湊 (cost=12) |
| Token | JWT RS256 或 HS256 |
| 2FA | TOTP (RFC 6238) |
| Session | Token 過期時間 30 分鐘 |
| 暴力破解 | 登入嘗試次數限制 |

### 12.2 API 安全

| 項目 | 措施 |
|------|------|
| HTTPS | 強制 TLS 1.2+ |
| CORS | 限制允許來源 |
| Rate Limit | API 請求頻率限制 |
| Input Validation | Pydantic 嚴格驗證 |
| SQL Injection | SQLAlchemy ORM |

### 12.3 資料備份

```bash
# 每日備份 SQLite
cp backend/data/marine_equipment.db backup/marine_equipment_$(date +%Y%m%d).db

# 保留 30 天
find backup/ -name "*.db" -mtime +30 -delete
```

---

## 附錄 A: 依賴套件清單

### Python (backend/requirements.txt)

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.0
alembic>=1.13.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pyotp>=2.9.0
qrcode[pil]>=7.4.0
python-multipart>=0.0.9
aiosqlite>=0.20.0
```

### Node/Bun (frontend/package.json)

```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "pinia-plugin-persistedstate": "^4.0.0",
    "axios": "^1.7.0",
    "@vueuse/core": "^11.0.0",
    "vue-qrcode-reader": "^5.5.0",
    "qrcode": "^1.5.0",
    "@headlessui/vue": "^2.2.0",
    "@heroicons/vue": "^2.1.0"
  },
  "devDependencies": {
    "vite": "^6.0.0",
    "vite-plugin-pwa": "^0.21.0",
    "@vitejs/plugin-vue": "^5.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "typescript": "^5.6.0",
    "vue-tsc": "^2.1.0"
  }
}
```

---

## 附錄 B: 參考資源

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [Vue 3 官方文件](https://vuejs.org/)
- [SQLAlchemy 2.0 文件](https://docs.sqlalchemy.org/)
- [Bun 官方文件](https://bun.sh/docs)
- [TailwindCSS 文件](https://tailwindcss.com/docs)
- [TOTP RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238)
- [PWA 開發指南](https://web.dev/progressive-web-apps/)

---

**文件結束**
