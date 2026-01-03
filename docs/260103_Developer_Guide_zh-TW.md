# 開發者指南 (Developer Guide)

**海洋調查設備資產管理系統**

本文件為後續開發者提供完整的技術參考，包含架構說明、共用元件、開發慣例等。

---

## 目錄

1. [技術棧概覽](#技術棧概覽)
2. [專案架構](#專案架構)
3. [共用元件清單](#共用元件清單)
4. [Composables 使用指南](#composables-使用指南)
5. [API 封裝層](#api-封裝層)
6. [後端核心模組](#後端核心模組)
7. [資料模型關係](#資料模型關係)
8. [開發慣例](#開發慣例)
9. [安全機制](#安全機制)
10. [新功能開發流程](#新功能開發流程)

---

## 技術棧概覽

### 後端技術 (Python/FastAPI)

| 類別 | 套件 | 版本 | 說明 |
|------|------|------|------|
| **Web Framework** | FastAPI | ≥0.115.0 | 高效能非同步 Web API 框架 |
| | uvicorn | ≥0.32.0 | ASGI Server |
| **Database** | SQLAlchemy | ≥2.0.0 | ORM，使用非同步模式 |
| | Alembic | ≥1.13.0 | 資料庫版本控制與 Migration |
| | aiosqlite | ≥0.20.0 | SQLite 非同步驅動程式 |
| **Validation** | Pydantic | ≥2.0.0 | 資料驗證與序列化 |
| | pydantic-settings | ≥2.0.0 | 環境變數管理 |
| **Authentication** | python-jose | ≥3.3.0 | JWT Token 生成與驗證 |
| | bcrypt | ≥4.0.0 | 密碼雜湊演算法 |
| | pyotp | ≥2.9.0 | TOTP 雙因素認證 |
| **Security** | slowapi | ≥0.1.9 | API Rate Limiting |
| **QR Code** | qrcode[pil] | ≥7.4.0 | QR Code 圖片生成 |
| **Testing** | pytest | ≥8.0.0 | 單元測試框架 |
| | httpx | ≥0.27.0 | 非同步 HTTP Client（測試用） |

### 前端技術 (Vue 3/Vite)

| 類別 | 套件 | 版本 | 說明 |
|------|------|------|------|
| **Core** | Vue | ^3.5.0 | Composition API 模式 |
| | Vue Router | ^4.4.0 | SPA 路由管理 |
| | Pinia | ^2.2.0 | 狀態管理（取代 Vuex） |
| **Build Tool** | Vite | ^6.0.0 | 開發伺服器與生產建置 |
| | TypeScript | ^5.6.0 | 靜態型別檢查 |
| | vue-tsc | ^2.1.0 | Vue 專用 TypeScript 編譯器 |
| **Styling** | TailwindCSS | ^3.4.0 | Utility-first CSS 框架 |
| **UI Components** | @headlessui/vue | ^1.7.0 | 無障礙 UI 元件庫 |
| | @heroicons/vue | ^2.1.0 | SVG 圖示庫 |
| **HTTP Client** | Axios | ^1.7.0 | HTTP 請求處理 |
| **QR Code** | vue-qrcode-reader | ^5.5.0 | QR Code 掃描器 |
| | qrcode | ^1.5.0 | QR Code 生成器 |
| **Security** | DOMPurify | ^3.2.0 | XSS 防護，HTML 清理 |
| **PWA** | vite-plugin-pwa | ^0.21.0 | Progressive Web App 支援 |
| **Utilities** | @vueuse/core | ^11.0.0 | Vue Composables 工具集 |

---

## 專案架構

```
DG_workshop/
├── backend/                          # Python FastAPI 後端
│   ├── app/
│   │   ├── main.py                  # FastAPI 應用程式入口
│   │   ├── api/                     # API 路由模組（14 個檔案）
│   │   │   ├── router.py           # 路由註冊中心
│   │   │   ├── auth.py             # 認證相關（JWT + 2FA）
│   │   │   ├── equipment.py        # 設備 CRUD + 狀態操作
│   │   │   ├── calibrations.py     # 校正記錄管理
│   │   │   ├── uploads.py          # 檔案上傳處理
│   │   │   ├── dashboard.py        # 儀表板統計 API
│   │   │   ├── users.py            # 使用者管理
│   │   │   ├── locations.py        # 位置管理
│   │   │   ├── projects.py         # 專案管理
│   │   │   ├── maintenance.py      # 維護記錄
│   │   │   ├── sub_equipment.py    # 子設備管理
│   │   │   ├── qrcode.py           # QR Code 生成
│   │   │   ├── customers.py        # 客戶管理
│   │   │   └── rentals.py          # 租賃管理
│   │   ├── core/                    # 核心模組
│   │   │   ├── config.py           # 環境變數與設定
│   │   │   ├── database.py         # 資料庫連線管理
│   │   │   ├── security.py         # JWT、密碼、TOTP 工具
│   │   │   ├── deps.py             # Dependency Injection
│   │   │   └── csrf.py             # CSRF 保護機制
│   │   ├── models/                  # SQLAlchemy Models（17 個）
│   │   │   ├── user.py             # 使用者
│   │   │   ├── equipment.py        # 設備
│   │   │   ├── equipment_log.py    # 設備操作日誌
│   │   │   ├── log_attachment.py   # 日誌附件
│   │   │   ├── calibration.py      # 校正記錄
│   │   │   ├── maintenance.py      # 維護記錄
│   │   │   ├── location.py         # 位置（船舶/倉庫）
│   │   │   ├── project.py          # 專案
│   │   │   ├── sub_equipment.py    # 子設備
│   │   │   ├── customer.py         # 客戶
│   │   │   ├── rental.py           # 租賃
│   │   │   ├── trusted_device.py   # 記住的裝置
│   │   │   ├── refresh_token.py    # Refresh Token
│   │   │   ├── backup_code.py      # 2FA 備用碼
│   │   │   └── used_totp_code.py   # 已使用的 TOTP 碼
│   │   ├── schemas/                 # Pydantic Schemas（11 個）
│   │   │   └── ...                 # 對應各 Model 的驗證 Schema
│   │   └── utils/                   # 工具函數
│   │       ├── asset_code.py       # 資產編號自動生成
│   │       ├── file_validator.py   # 檔案安全驗證
│   │       ├── rental_number.py    # 租賃編號生成
│   │       └── security_checker.py # 安全檢查工具
│   ├── alembic/                     # 資料庫 Migration 檔案
│   │   └── versions/               # Migration 版本
│   ├── data/                        # SQLite 資料庫檔案
│   └── uploads/                     # 上傳檔案儲存
│
├── frontend/                         # Vue 3 前端
│   └── src/
│       ├── api/                     # API 封裝層（10 個檔案）
│       │   ├── client.ts           # Axios 實例 + Interceptors
│       │   ├── auth.ts             # 認證 API
│       │   ├── equipment.ts        # 設備 API
│       │   ├── calibrations.ts     # 校正 API
│       │   ├── dashboard.ts        # 儀表板 API
│       │   ├── locations.ts        # 位置 API
│       │   ├── projects.ts         # 專案 API
│       │   ├── users.ts            # 使用者 API
│       │   ├── maintenance.ts      # 維護 API
│       │   └── subEquipment.ts     # 子設備 API
│       ├── stores/                  # Pinia Stores（7 個）
│       │   ├── auth.ts             # 認證狀態
│       │   ├── equipment.ts        # 設備狀態
│       │   ├── locations.ts        # 位置狀態
│       │   ├── projects.ts         # 專案狀態
│       │   ├── users.ts            # 使用者狀態
│       │   ├── subEquipment.ts     # 子設備狀態
│       │   └── ui.ts               # UI 狀態
│       ├── composables/             # Vue Composables（2 個）
│       │   ├── useEquipmentLabels.ts  # 設備狀態/類別標籤轉換
│       │   └── useActivityLog.ts      # 活動日誌格式處理
│       ├── components/              # Vue 元件
│       │   ├── common/             # ⭐ 基礎共用元件
│       │   ├── dashboard/          # 儀表板專用元件
│       │   └── equipment/          # 設備專用元件
│       ├── layouts/                 # 版面配置元件
│       │   ├── MainLayout.vue      # 主要版面（含導航）
│       │   └── AuthLayout.vue      # 認證頁面版面
│       ├── views/                   # 頁面視圖（23 個）
│       │   ├── auth/               # 登入、2FA 設定
│       │   ├── equipment/          # 設備相關頁面
│       │   ├── locations/          # 位置管理頁面
│       │   ├── projects/           # 專案管理頁面
│       │   ├── admin/              # 管理者頁面
│       │   ├── maintenance/        # 維護頁面
│       │   └── subEquipment/       # 子設備頁面
│       ├── router/                  # Vue Router 設定
│       ├── types/                   # TypeScript 型別定義
│       └── utils/                   # 工具函數
│           ├── filterUtils.ts      # API 過濾器工具
│           ├── sanitizer.ts        # XSS 清理（DOMPurify）
│           └── deviceFingerprint.ts # 裝置識別
│
├── docs/                             # 專案文件
├── plan/                             # 開發計畫與規劃
└── manage.bat                        # Windows 開發控制面板
```

---

## 共用元件清單

以下元件為**全專案共用**，開發新功能時應優先使用這些元件以維持一致性。

### 基礎共用元件 (`frontend/src/components/common/`)

| 元件名稱 | 功能說明 | Props 參數 | Slots 插槽 |
|----------|----------|------------|------------|
| **AppButton.vue** | 統一按鈕樣式，支援多種變體與狀態 | `variant`: primary / secondary / danger / ghost<br>`size`: sm / md / lg<br>`loading`: boolean（顯示載入中）<br>`fullWidth`: boolean（滿版寬度）<br>`disabled`: boolean | default（按鈕文字） |
| **BaseModal.vue** | Modal 對話框基礎元件，所有 Modal 都應繼承此元件 | `show`: boolean（顯示狀態）<br>`title`: string（標題）<br>`size`: sm / md / lg / xl / 2xl<br>`closeOnBackdrop`: boolean（點擊背景關閉）<br>`showCloseButton`: boolean | default（內容）<br>#title（自訂標題）<br>#footer（底部按鈕區） |
| **FileUpload.vue** | 檔案上傳元件，含拖放支援 | `accept`: string（允許的檔案類型）<br>`maxSize`: number（最大檔案大小） | - |
| **AppInput.vue** | 表單輸入框，統一樣式 | `type`, `placeholder`, `disabled`, `error` | - |

#### BaseModal 使用範例

```vue
<template>
  <BaseModal
    :show="isOpen"
    title="確認操作"
    size="md"
    @close="isOpen = false"
  >
    <!-- Modal 內容 -->
    <p>您確定要執行此操作嗎？</p>

    <!-- 底部按鈕 -->
    <template #footer>
      <AppButton variant="secondary" @click="isOpen = false">
        取消
      </AppButton>
      <AppButton @click="handleConfirm">
        確認
      </AppButton>
    </template>
  </BaseModal>
</template>
```

### 設備專用元件 (`frontend/src/components/equipment/`)

這些元件專為設備管理功能設計，可在設備相關頁面重複使用。

#### Sections（區塊元件）

| 元件名稱 | 功能說明 | 使用位置 |
|----------|----------|----------|
| **EquipmentHeaderSection.vue** | 設備詳情頁標題區，含資產編號、型號、狀態 | EquipmentDetailView |
| **BasicInformationCard.vue** | 基本資訊卡片，顯示設備規格 | EquipmentDetailView |
| **StatusActionsCard.vue** | 狀態操作按鈕區，根據當前狀態顯示可用操作 | EquipmentDetailView |
| **LocationProjectInfoCard.vue** | 位置與專案資訊卡片 | EquipmentDetailView |
| **EquipmentLogSection.vue** | 活動日誌區塊，顯示設備操作歷史 | EquipmentDetailView |
| **ChildrenEquipmentSection.vue** | 子設備列表區塊 | EquipmentDetailView |

#### Modals（對話框元件）

| 元件名稱 | 功能說明 | 觸發條件 |
|----------|----------|----------|
| **DeployEquipmentModal.vue** | 部署設備至船舶/位置 | 狀態為 In Stock |
| **ReturnEquipmentModal.vue** | 歸還設備（從部署狀態） | 狀態為 Deployed |
| **SendToRepairModal.vue** | 送修設備 | 任何狀態 |
| **SendToCalibrationModal.vue** | 送校正設備 | 任何狀態 |
| **SetToInStockModal.vue** | 設為入庫狀態 | 狀態為 Repair/Calibrating |
| **SetToRentedModal.vue** | 設為租賃狀態 | 狀態為 In Stock |
| **AddMaintenanceRecordModal.vue** | 新增維護記錄 | 任何狀態 |
| **DetachFromParentModal.vue** | 從父設備分離 | 有父設備時 |
| **QuickActionModal.vue** | 快速操作（編輯/新增日誌） | 任何狀態 |

#### Log（日誌元件）

| 元件名稱 | 功能說明 |
|----------|----------|
| **LogEditModal.vue** | 編輯活動日誌內容 |
| **LogAttachmentsModal.vue** | 管理日誌附件（上傳/下載/刪除） |
| **LogChangeRecordDisplay.vue** | 顯示日誌變更記錄的 JSON 格式 |

#### Form（表單元件）

| 元件名稱 | 功能說明 |
|----------|----------|
| **FormCategorySection.vue** | 設備類別選擇區塊 |
| **FormLocationProjectSection.vue** | 位置與專案選擇區塊 |

### 版面配置 (`frontend/src/layouts/`)

| 元件名稱 | 功能說明 | 使用時機 |
|----------|----------|----------|
| **MainLayout.vue** | 主要版面配置，包含頂部導航欄、側邊欄 | 需要導航的一般頁面 |
| **AuthLayout.vue** | 認證頁面版面，簡潔無導航 | 登入、2FA 設定頁面 |

---

## Composables 使用指南

Composables 是 Vue 3 的可重用邏輯封裝，本專案提供以下 Composables：

### useEquipmentLabels

用於將設備的狀態碼、類別碼轉換為顯示用文字和 CSS 樣式。

```typescript
import { useEquipmentLabels } from '@/composables/useEquipmentLabels'

// 在 setup 中使用
const { categoryLabel, statusLabel, statusBadgeClass, locationTypeLabel } = useEquipmentLabels()

// 類別轉換
categoryLabel('mbes')  // → "MBES - Multibeam Echosounder"
categoryLabel('gnss')  // → "GNSS - Receiver"
categoryLabel('svp')   // → "SVP - Sound Velocity Profiler"

// 狀態轉換
statusLabel('in_stock')   // → "In Stock"
statusLabel('deployed')   // → "Deployed"
statusLabel('calibrating') // → "Calibrating"

// 狀態 Badge CSS Class
statusBadgeClass('in_stock')  // → "bg-green-100 text-green-800"
statusBadgeClass('deployed')  // → "bg-blue-100 text-blue-800"
statusBadgeClass('repair')    // → "bg-orange-100 text-orange-800"

// 位置類型轉換
locationTypeLabel('vessel')    // → "Vessel"
locationTypeLabel('warehouse') // → "Warehouse"
```

### useActivityLog

用於處理設備活動日誌的顯示格式。

```typescript
import { useActivityLog } from '@/composables/useActivityLog'

const { formatLogDetails, getActionIcon, getActionColor } = useActivityLog()

// 格式化日誌詳情
formatLogDetails(logEntry)

// 取得操作圖示
getActionIcon('deploy')  // → "🚀"
getActionIcon('return')  // → "📦"

// 取得操作顏色
getActionColor('deploy') // → "text-blue-600"
```

---

## API 封裝層

所有 API 請求透過 `frontend/src/api/client.ts` 統一處理，確保一致的錯誤處理和認證機制。

### client.ts 核心功能

```typescript
// client.ts 提供的功能：
// 1. Axios 實例配置（baseURL、timeout、credentials）
// 2. Request Interceptor - 自動附加 CSRF Token
// 3. Response Interceptor - 401 自動登出、錯誤處理
// 4. 安全事件記錄（認證失敗、權限拒絕等）

import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000,
  withCredentials: true,  // 發送 httpOnly cookies
})

// Request Interceptor：自動附加 CSRF Token
apiClient.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrf_token')
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})

// Response Interceptor：處理認證錯誤
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 自動登出並導向登入頁
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### API 模組結構範例

```typescript
// frontend/src/api/equipment.ts
import apiClient from './client'
import type { Equipment, EquipmentCreate, EquipmentFilter } from '@/types'

export const equipmentApi = {
  // 取得設備列表
  getList: (params: EquipmentFilter) =>
    apiClient.get<Equipment[]>('/api/equipment', { params }),

  // 取得單一設備
  getById: (id: number) =>
    apiClient.get<Equipment>(`/api/equipment/${id}`),

  // 新增設備
  create: (data: EquipmentCreate) =>
    apiClient.post<Equipment>('/api/equipment', data),

  // 更新設備
  update: (id: number, data: Partial<Equipment>) =>
    apiClient.put<Equipment>(`/api/equipment/${id}`, data),

  // 刪除設備
  delete: (id: number) =>
    apiClient.delete(`/api/equipment/${id}`),

  // 狀態操作
  deploy: (id: number, locationId: number) =>
    apiClient.post(`/api/equipment/${id}/deploy`, { location_id: locationId }),

  returnEquipment: (id: number) =>
    apiClient.post(`/api/equipment/${id}/return`),
}
```

### 在元件中使用

```typescript
// 在 Vue 元件中使用
import { equipmentApi } from '@/api/equipment'

const loadEquipment = async (id: number) => {
  try {
    const response = await equipmentApi.getById(id)
    equipment.value = response.data
  } catch (error) {
    console.error('載入設備失敗:', error)
  }
}
```

---

## 後端核心模組

### core/config.py - 環境變數管理

使用 Pydantic Settings 管理所有環境變數，支援 `.env` 檔案讀取。

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 應用程式設定
    APP_NAME: str = "Marine Equipment QR System"
    DEBUG: bool = False

    # 安全設定
    SECRET_KEY: str  # 必填，用於 JWT 簽名
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 資料庫
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/marine_equipment.db"

    # CORS 設定
    BACKEND_CORS_ORIGINS: list[str] = []

    class Config:
        env_file = ".env"

settings = Settings()
```

### core/database.py - 資料庫連線

使用 SQLAlchemy 2.0 非同步模式。

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### core/security.py - 認證與安全

提供 JWT、密碼雜湊、TOTP 相關工具。

```python
from jose import jwt
from passlib.context import CryptContext
import pyotp

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
```

### core/deps.py - Dependency Injection

FastAPI 依賴注入函數，用於路由中取得資料庫連線和當前使用者。

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # 驗證 JWT Token，返回當前使用者
    ...

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="使用者已停用")
    return current_user

# 權限檢查 Dependency
def require_role(minimum_role: str):
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if not has_permission(current_user.role, minimum_role):
            raise HTTPException(status_code=403, detail="權限不足")
        return current_user
    return role_checker
```

---

## 資料模型關係

以下為主要資料表之間的關聯關係：

```
┌─────────┐
│  User   │
└────┬────┘
     │ created_by / edited_by
     ▼
┌─────────────┐       ┌──────────────┐
│  Equipment  │──────▶│ EquipmentLog │
└──────┬──────┘       └──────┬───────┘
       │                     │
       │                     ▼
       │              ┌──────────────┐
       │              │LogAttachment │
       │              └──────────────┘
       │
       ├──────────────▶ Calibration
       │
       ├──────────────▶ Maintenance
       │
       └──────────────▶ SubEquipment


┌──────────┐                    ┌─────────────┐
│ Location │◀── current_location ──│  Equipment  │
└──────────┘                    └──────┬──────┘
                                       │
┌──────────┐                           │
│ Project  │◀───── project ────────────┘
└──────────┘
```

### 主要關聯說明

| 關聯 | 類型 | 說明 |
|------|------|------|
| User → Equipment | One-to-Many | 使用者建立/編輯的設備 |
| Equipment → EquipmentLog | One-to-Many | 設備的操作日誌 |
| EquipmentLog → LogAttachment | One-to-Many | 日誌的附件檔案 |
| Equipment → Calibration | One-to-Many | 設備的校正記錄 |
| Equipment → Maintenance | One-to-Many | 設備的維護記錄 |
| Equipment → SubEquipment | One-to-Many | 父設備與子設備 |
| Location → Equipment | One-to-Many | 位置內的設備 |
| Project → Equipment | One-to-Many | 專案中的設備 |

---

## 開發慣例

### 命名規範

| 類型 | 命名慣例 | 範例 |
|------|----------|------|
| **Python 變數/函數** | snake_case | `equipment_id`, `get_by_id()` |
| **Python 類別** | PascalCase | `Equipment`, `EquipmentCreate` |
| **TypeScript 變數** | camelCase | `equipmentId`, `getById()` |
| **Vue 元件檔名** | PascalCase | `EquipmentDetailView.vue` |
| **API 路由** | kebab-case | `/api/equipment-logs` |
| **資料庫表名** | 複數 snake_case | `equipments`, `equipment_logs` |
| **環境變數** | UPPER_SNAKE_CASE | `SECRET_KEY`, `DATABASE_URL` |

### 程式碼風格

#### Python (後端)

- 使用 Type Hints 標註參數和返回值
- 使用 Pydantic Schema 進行資料驗證
- 非同步函數使用 `async def`
- 日誌使用 `logger.info()` / `logger.debug()`，避免記錄敏感資訊

```python
async def get_equipment(
    equipment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Equipment:
    """取得單一設備資訊"""
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="設備不存在")
    return equipment
```

#### TypeScript/Vue (前端)

- 使用 Composition API (`<script setup>`)
- 明確定義 Props 和 Emits 型別
- 使用 `ref()` 和 `reactive()` 管理狀態
- 開發環境的 console.log 需使用 `import.meta.env.DEV` 包裝

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Equipment } from '@/types'

interface Props {
  equipmentId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  updated: [equipment: Equipment]
}>()

const equipment = ref<Equipment | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await equipmentApi.getById(props.equipmentId)
    equipment.value = response.data
  } finally {
    loading.value = false
  }
})
</script>
```

### 程式碼品質檢查

```bash
# 前端型別檢查
cd frontend && bun run type-check

# 前端 ESLint 檢查
cd frontend && bun run lint

# 後端單元測試
cd backend && pytest -v

# 後端測試覆蓋率
cd backend && pytest --cov=app
```

---

## 安全機制

本系統實作多層安全防護：

| 安全機制 | 實作位置 | 說明 |
|----------|----------|------|
| **JWT + httpOnly Cookie** | `core/security.py`, `api/auth.py` | Access Token 存於 httpOnly Cookie，前端無法透過 JavaScript 存取，防止 XSS 竊取 Token |
| **TOTP 雙因素認證** | `api/auth.py` | 使用 pyotp 實作，支援 Google Authenticator / Microsoft Authenticator |
| **CSRF Protection** | `core/csrf.py` | Double Submit Cookie 模式，每次請求需附帶 CSRF Token |
| **Rate Limiting** | `main.py` | 使用 slowapi 限制 API 請求頻率，防止暴力破解 |
| **檔案上傳驗證** | `utils/file_validator.py` | 三重驗證：Magic Number（檔案簽名）+ MIME Type + 副檔名 |
| **PDF 安全掃描** | `utils/file_validator.py` | 檢測 JavaScript、自動執行巨集、嵌入式檔案等危險內容 |
| **XSS 防護** | `utils/sanitizer.ts` | 使用 DOMPurify 清理所有使用者輸入的 HTML 內容 |
| **密碼雜湊** | `core/security.py` | 使用 bcrypt 演算法，不可逆雜湊 |
| **SQL Injection 防護** | SQLAlchemy ORM | 所有資料庫操作使用參數化查詢 |
| **日誌脫敏** | 後端 logger | 日誌中不記錄密碼、Token，使用者以 ID 替代 username |

---

## 新功能開發流程

### 後端 API 開發 Checklist

1. **定義 Pydantic Schema**
   ```bash
   # 在 app/schemas/ 建立對應的 Schema
   touch backend/app/schemas/new_feature.py
   ```

2. **建立 SQLAlchemy Model**（如需新資料表）
   ```bash
   touch backend/app/models/new_feature.py
   ```

3. **建立 API Router**
   ```bash
   touch backend/app/api/new_feature.py
   ```

4. **註冊路由**
   ```python
   # 在 app/api/router.py 加入
   from app.api import new_feature
   api_router.include_router(new_feature.router, prefix="/new-feature", tags=["NewFeature"])
   ```

5. **執行資料庫 Migration**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add new_feature table"
   alembic upgrade head
   ```

6. **撰寫測試**
   ```bash
   touch backend/tests/test_new_feature.py
   pytest tests/test_new_feature.py -v
   ```

### 前端頁面開發 Checklist

1. **建立 API 封裝**
   ```bash
   # 在 src/api/ 建立 API 檔案
   touch frontend/src/api/newFeature.ts
   ```

2. **建立 Pinia Store**（如需全域狀態）
   ```bash
   touch frontend/src/stores/newFeature.ts
   ```

3. **建立頁面元件**
   ```bash
   mkdir -p frontend/src/views/newFeature
   touch frontend/src/views/newFeature/NewFeatureListView.vue
   ```

4. **新增路由**
   ```typescript
   // 在 src/router/index.ts 加入
   {
     path: '/new-feature',
     name: 'NewFeatureList',
     component: () => import('@/views/newFeature/NewFeatureListView.vue'),
     meta: { requiresAuth: true }
   }
   ```

5. **優先使用共用元件**
   - 按鈕：`AppButton`
   - Modal：`BaseModal`
   - 表單輸入：`AppInput`
   - 檔案上傳：`FileUpload`

6. **型別檢查**
   ```bash
   cd frontend && bun run type-check
   ```

---

## 常見問題排除

### 後端問題

| 問題 | 可能原因 | 解決方案 |
|------|----------|----------|
| ImportError | Python 環境未啟動 | `venv\Scripts\activate` |
| 資料庫連線失敗 | .env 設定錯誤 | 檢查 DATABASE_URL |
| JWT 驗證失敗 | SECRET_KEY 變更 | 重新登入取得新 Token |
| Alembic 衝突 | Migration 版本不一致 | `alembic history` 檢查 |

### 前端問題

| 問題 | 可能原因 | 解決方案 |
|------|----------|----------|
| Module not found | 依賴未安裝 | `bun install` |
| TypeScript 錯誤 | 型別定義缺失 | 更新 `types/` 定義 |
| CORS 錯誤 | 後端未允許 Origin | 檢查 `BACKEND_CORS_ORIGINS` |
| 401 Unauthorized | Cookie 未發送 | 確認 `withCredentials: true` |

---

## 聯絡資訊

- **專案維護**: CHC Team
- **技術支援**: GitHub Issues
- **Email**: jin_chang@me.com

---

**文件版本**: 1.0
**最後更新**: 2026-01-03
