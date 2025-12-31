# Equipment 設備管理模組 UX 改善分析報告

**日期**: 2025-12-31 17:30  
**版本**: v3.0  
**目的**: 分析現有架構痛點，提出整合與優化方案（含 Location 管理、Software 管理、Action Wizard）

---

## 執行摘要

經過分析你的設備管理模組，主要問題包括：
1. **介面分散、操作流程過長** - 需要多次頁面切換完成簡單任務
2. **缺乏結構化位置管理** - GPS 座標不適合追蹤邏輯位置
3. **缺乏軟體授權管理** - Dongle、License 無系統化追蹤
4. **Asset Code 編碼限制** - 年度流水號只能到 999

本文件提出完整的改善方案，包括：
- Location 管理機制（Vessel、Warehouse、Person）
- Project 與 Vessel 的關聯設計（Project 在 Vessel 內選擇）
- Software / Dongle 管理模組
- Action Wizard 操作流程
- 新的 Asset Code 編碼規則

---

## 一、系統架構設計

### 1.1 整體架構

```
┌─────────────────────────────────────────────────────────────────┐
│                     Asset Management System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Equipment  │  │  Software   │  │  Locations  │             │
│  │  Management │  │  & Licenses │  │  Management │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│  ┌───────────────────────┴───────────────────────┐             │
│  │              Action Wizards                    │             │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐         │             │
│  │  │Transfer │ │Calibrate│ │ Repair  │ ...     │             │
│  │  └─────────┘ └─────────┘ └─────────┘         │             │
│  └───────────────────────────────────────────────┘             │
│                                                                 │
│  Location Types:                                                │
│  ├─ 🚢 Vessel (含 Project 關聯)                                │
│  ├─ 🏭 Warehouse                                                │
│  └─ 👤 Person (Employee / Party Chief)                         │
│                                                                 │
│  Equipment Installation Types:                                  │
│  ├─ Permanent (固定安裝，不隨專案移動)                          │
│  ├─ Project (專案設備，專案結束需撤回)                          │
│  └─ Temporary (臨時部署)                                        │
│                                                                 │
│  Software License Assignment:                                   │
│  ├─ 👤 Person (個人使用)                                        │
│  ├─ 🚢 Vessel (船上使用)                                        │
│  └─ 📦 Equipment (綁定硬體)                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Location Types 定義

| Type | 說明 | 用途 |
|------|------|------|
| `vessel` | 船舶 | 設備部署到船上，可關聯 Project |
| `warehouse` | 倉庫 | 設備入庫、回收 |
| `person` | 人員 | 設備領用（Party Chief）、軟體分配 |

> **注意**：已移除 `client` 類型。租賃給客戶應使用 Rental 模組處理。

---

## 二、Location 管理模組

### 2.1 資料庫設計

```python
# models/location.py

class LocationType(str, Enum):
    VESSEL = "vessel"           # 船舶
    WAREHOUSE = "warehouse"     # 倉庫
    PERSON = "person"           # 人員 (Party Chief / Employee)

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    
    # === 基本資訊 ===
    name = Column(String(100), nullable=False)          # 顯示名稱
    location_type = Column(Enum(LocationType), nullable=False)
    code = Column(String(20), unique=True)              # 簡碼
    description = Column(Text)
    
    # === 聯絡資訊 ===
    contact_person = Column(String(50))
    contact_phone = Column(String(20))
    contact_email = Column(String(100))
    
    # === 船舶專用欄位 ===
    # 識別碼（至少填一個）
    vessel_imo = Column(String(10), unique=True, nullable=True)         # IMO 編號
    vessel_mmsi = Column(String(9), unique=True, nullable=True)         # MMSI
    vessel_national_id = Column(String(30), unique=True, nullable=True) # 國籍編號 (如 CT-XXXXX)
    vessel_internal_code = Column(String(20), unique=True, nullable=True) # 內部編碼
    
    # 船舶資訊
    vessel_name = Column(String(100))                   # 船名（可變更）
    vessel_flag = Column(String(50))                    # 船旗國
    vessel_type = Column(String(50))                    # 船型 (Survey, Supply, etc.)
    vessel_owner = Column(String(100))                  # 船東/營運商
    vessel_call_sign = Column(String(20))               # 呼號
    
    # 當前專案（船舶可關聯專案）
    current_project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    current_project = relationship("Project", back_populates="vessels")
    
    # === 倉庫/辦公室專用欄位 ===
    address = Column(String(200))
    city = Column(String(50))
    country = Column(String(50))
    default_latitude = Column(Float)
    default_longitude = Column(Float)
    
    # === 人員專用欄位 ===
    employee_id = Column(String(20))                    # 員工編號
    department = Column(String(50))                     # 部門
    job_title = Column(String(50))                      # 職稱
    
    # === 狀態 ===
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

### 2.2 Vessel 識別碼設計

由於小型測量船可能沒有 IMO，系統支援多種識別方式：

| 識別碼類型 | 說明 | 適用情況 |
|-----------|------|---------|
| IMO | 國際海事組織編號（7位數） | 大型商船、調查船 |
| MMSI | 海上移動業務識別碼（9位數） | 有 AIS 的船舶 |
| 國籍編號 | 如台灣小船執照 CT-XXXXX | 小型工作船、漁船 |
| 內部編碼 | 系統自動產生 INT-SV-YYYYNNN | 無官方編號的船舶 |

**識別碼優先順序**（UI 顯示）：
```
IMO > MMSI > 國籍編號 > 內部編碼
```

**顯示範例**：
```
🚢 Ocean Explorer (IMO 9876543)
🚢 測量一號 (CT-12345)
🚢 作業艇 A (INT-SV-2025001)
```

### 2.3 Project 資料模型

Project 作為 Vessel 的子屬性，在 Vessel 表單中選擇：

```python
# models/project.py

class ProjectStatus(str, Enum):
    PLANNING = "planning"       # 規劃中
    ACTIVE = "active"           # 進行中
    ON_HOLD = "on_hold"         # 暫停
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    
    # 基本資訊
    code = Column(String(30), unique=True, nullable=False)  # 專案編號
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 客戶資訊
    client_name = Column(String(100))
    client_contact = Column(String(50))
    client_phone = Column(String(20))
    client_email = Column(String(100))
    
    # 日期
    start_date = Column(Date)
    end_date = Column(Date)
    
    # 狀態
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    
    # 關聯
    vessels = relationship("Location", back_populates="current_project")
    equipment = relationship("Equipment", back_populates="project")
```

### 2.4 新增船舶表單（含 Project 選擇）

```vue
<!-- views/location/VesselForm.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    
    <!-- 基本資訊 -->
    <section>
      <h3 class="text-lg font-semibold mb-4">Basic Information</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Vessel Name" required>
          <input v-model="form.vessel_name" class="input" required />
        </FormField>
        <FormField label="Vessel Type">
          <select v-model="form.vessel_type" class="input">
            <option value="">-- Select --</option>
            <option value="survey">Survey Vessel</option>
            <option value="supply">Supply Vessel</option>
            <option value="research">Research Vessel</option>
            <option value="workboat">Workboat</option>
            <option value="other">Other</option>
          </select>
        </FormField>
        <FormField label="Flag State">
          <input v-model="form.vessel_flag" class="input" />
        </FormField>
        <FormField label="Owner / Operator">
          <input v-model="form.vessel_owner" class="input" />
        </FormField>
      </div>
    </section>
    
    <!-- 識別碼 -->
    <section>
      <h3 class="text-lg font-semibold mb-2">Vessel Identifier</h3>
      <p class="text-sm text-gray-500 mb-4">At least one identifier is required</p>
      
      <div class="space-y-3">
        <FormField label="IMO Number">
          <input v-model="form.vessel_imo" class="input" placeholder="7 digits" pattern="[0-9]{7}" />
        </FormField>
        <FormField label="MMSI">
          <input v-model="form.vessel_mmsi" class="input" placeholder="9 digits" pattern="[0-9]{9}" />
        </FormField>
        <FormField label="National Registration">
          <input v-model="form.vessel_national_id" class="input" placeholder="e.g., CT-12345" />
        </FormField>
        
        <div v-if="!hasOfficialId" class="bg-yellow-50 border border-yellow-200 rounded p-3">
          <p class="text-sm text-yellow-800 mb-2">No official ID. Internal code will be generated.</p>
          <div class="flex gap-2">
            <input v-model="form.vessel_internal_code" class="input flex-1" />
            <AppButton type="button" size="sm" @click="generateInternalCode">Generate</AppButton>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 當前專案（在 Vessel 內選擇）-->
    <section>
      <h3 class="text-lg font-semibold mb-4">Current Project</h3>
      <FormField label="Assigned Project">
        <ProjectSelect v-model="form.current_project_id" allow-empty />
        <p class="text-sm text-gray-500 mt-1">
          Select if this vessel is currently assigned to a project
        </p>
      </FormField>
    </section>
    
    <!-- 聯絡資訊 -->
    <section>
      <h3 class="text-lg font-semibold mb-4">Contact Information</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <FormField label="Contact Person">
          <input v-model="form.contact_person" class="input" />
        </FormField>
        <FormField label="Phone">
          <input v-model="form.contact_phone" class="input" type="tel" />
        </FormField>
        <FormField label="Email">
          <input v-model="form.contact_email" class="input" type="email" />
        </FormField>
      </div>
    </section>
    
    <!-- 送出 -->
    <div class="flex justify-end gap-3 pt-4 border-t">
      <AppButton type="button" variant="secondary" @click="cancel">Cancel</AppButton>
      <AppButton type="submit" :loading="saving" :disabled="!hasAnyId">
        {{ isEdit ? 'Update' : 'Create' }} Vessel
      </AppButton>
    </div>
  </form>
</template>
```

---

## 三、Equipment 模組更新

### 3.1 資料模型更新

```python
class InstallationType(str, Enum):
    PERMANENT = "permanent"      # 固定安裝（不隨專案移動）
    PROJECT = "project"          # 專案設備（專案結束需撤回）
    TEMPORARY = "temporary"      # 臨時部署

class Equipment(Base):
    # ... 現有欄位 ...
    
    # === 位置關聯 ===
    current_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    current_location = relationship("Location")
    
    # 專案關聯（設備部署到船上時，自動繼承船的專案或選擇其他專案）
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project")
    
    # 安裝類型（僅當 location 是 vessel 時有意義）
    installation_type = Column(Enum(InstallationType), nullable=True)
    installation_date = Column(Date, nullable=True)
    installation_notes = Column(Text, nullable=True)
```

### 3.2 Asset Code 新編碼規則

**格式**：`{Category}-{ModelCode}-{Identifier}`

| 情況 | 格式 | 範例 |
|------|------|------|
| 有 Serial Number | `{Cat}-{Model}-SN{Serial}` | `MBES-EM2040C-SN12345` |
| 無 Serial Number | `{Cat}-{Model}-{Seq:4位}` | `MBES-EM2040C-0001` |

**主設備範例**：

| Category | Model | Serial | Asset Code |
|----------|-------|--------|------------|
| MBES | EM 2040C | 12345 | `MBES-EM2040C-SN12345` |
| MBES | EM 2040C | (無) | `MBES-EM2040C-0001` |
| POSMV | POS MV 320 | 98765 | `POSMV-POSMV320-SN98765` |
| GNSS | ZED-F9P | ABC123 | `GNSS-ZEDF9P-SNABC123` |

**子設備範例**：

| Parent | Component | Serial | Sub Asset Code |
|--------|-----------|--------|----------------|
| MBES-EM2040C-SN12345 | Antenna 1 | - | `MBES-EM2040C-SN12345/ANT1` |
| MBES-EM2040C-SN12345 | Cable | 789 | `MBES-EM2040C-SN12345/CABLE-SN789` |

### 3.3 Asset Code 產生邏輯

```python
def generate_asset_code(category: str, model: str, serial_number: str | None, db) -> str:
    model_code = re.sub(r'[^A-Za-z0-9]', '', model)[:10].upper()
    prefix = f"{category}-{model_code}"
    
    if serial_number:
        clean_sn = re.sub(r'[^A-Za-z0-9]', '', serial_number).upper()
        asset_code = f"{prefix}-SN{clean_sn}"
        # 檢查重複，重複則加時間戳
        if exists(asset_code):
            asset_code = f"{prefix}-SN{clean_sn}-{datetime.now().strftime('%y%m')}"
    else:
        # 流水號（4位數，支援到 9999）
        next_seq = get_next_sequence(prefix)
        asset_code = f"{prefix}-{next_seq:04d}"
    
    return asset_code
```

---

## 四、Software 管理模組

### 4.1 資料庫設計

```python
class SoftwareLicenseType(str, Enum):
    SOFT_DONGLE = "soft_dongle"       # USB 軟體金鑰 (HASP, Sentinel)
    HARD_DONGLE = "hard_dongle"       # 硬體鎖
    LICENSE_KEY = "license_key"       # 序號授權
    SUBSCRIPTION = "subscription"     # 訂閱制
    PERPETUAL = "perpetual"           # 永久授權
    FLOATING = "floating"             # 浮動授權（網路版）

class Software(Base):
    """軟體主檔"""
    __tablename__ = "software"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    vendor = Column(String(100))
    version = Column(String(50))
    category = Column(String(50))
    description = Column(Text)
    website = Column(String(200))

class SoftwareLicense(Base):
    """軟體授權 / Dongle"""
    __tablename__ = "software_licenses"
    
    id = Column(Integer, primary_key=True)
    asset_code = Column(String(50), unique=True, nullable=False)
    
    # 關聯
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    
    # 授權資訊
    license_type = Column(Enum(SoftwareLicenseType), nullable=False)
    license_key = Column(String(200))           # 序號
    dongle_id = Column(String(100))             # Dongle ID
    seats = Column(Integer, default=1)          # 授權數量
    
    # 重要日期
    purchase_date = Column(Date)
    activation_date = Column(Date)
    expiry_date = Column(Date)                  # 授權到期日
    maintenance_expiry = Column(Date)           # 維護合約到期日
    
    # 分配
    assigned_to_id = Column(Integer, ForeignKey("locations.id"))  # Person/Vessel
    assigned_date = Column(Date)
    assigned_equipment_id = Column(Integer, ForeignKey("equipments.id"))  # 綁定設備
    
    # 狀態
    status = Column(String(20), default="available")  # available, assigned, expired
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
```

### 4.2 Software Asset Code 格式

```
格式：SW-{SoftwareCode}-{TypeCode}-{Identifier}

範例：
SW-CARISHPS-SD-SN12345      (CARIS HIPS, Soft Dongle)
SW-CARISHPS-HD-SN98765      (CARIS HIPS, Hard Dongle)
SW-QINSY-LK-001             (QINSy, License Key, 流水號)
SW-HYPACK-SUB-2025          (Hypack, Subscription)
```

### 4.3 Software 管理 UI 摘要

**列表頁面顯示**：
- 軟體名稱 + 授權類型 Badge
- Asset Code
- 分配對象（人員/船舶）
- 授權到期日 + 維護到期日（含倒數天數警示）

**詳細頁面包含**：
- 授權資訊（類型、Dongle ID、序號）
- 重要日期（購買、啟用、到期、維護到期）
- 當前分配狀態
- Activity Log

**到期提醒**：
- Dashboard 顯示 90 天內到期的授權
- 依嚴重程度分級：expired（紅）、critical ≤30天（橘）、warning ≤90天（黃）

---

## 五、Action Wizard 系統

### 5.1 設計概念

設備/軟體操作採用 Wizard 引導完成完整流程：

| Wizard | 用途 | 主要步驟 |
|--------|------|---------|
| Transfer | 設備轉移 | 目的地 → 安裝類型 → 詳細資訊 → 狀態檢查 → 確認 |
| Return | 設備回收 | 選擇倉庫 → 狀態檢查 → 確認 |
| Calibration | 送校正 | 廠商 → 校正項目 → 文件 → 確認 |
| Repair | 送維修 | 廠商 → 問題描述 → 文件 → 確認 |
| Software Assign | 軟體分配 | 對象 → 詳細資訊 → 確認 |

### 5.2 Transfer Wizard 流程

```
Step 1: Select Destination
┌──────────────────────────────────────────────────────────────┐
│  Where is this equipment going?                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │     🚢       │  │     👤       │  │     🏭       │       │
│  │   Vessel     │  │   Person     │  │  Warehouse   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘

Step 2: Vessel Details（選擇 Vessel 時）
┌──────────────────────────────────────────────────────────────┐
│  Select Vessel:                                              │
│  [🚢 Ocean Explorer (IMO 9876543) - 南海測量專案 ▼]          │
│                                                              │
│  Installation Type:                                          │
│  ○ Permanent - Fixed, won't move with projects              │
│  ● Project - For current project, retrieve when done        │
│  ○ Temporary - Short-term deployment                        │
│                                                              │
│  (Project 自動繼承自 Vessel 的 current_project)              │
└──────────────────────────────────────────────────────────────┘

Step 3: Transfer Details
┌──────────────────────────────────────────────────────────────┐
│  Transfer Date:      [2025-12-31]                           │
│  Expected Return:    [          ] (Optional)                │
│  Responsible Person: [王大明 ▼]                              │
│  Notes:              [________________________]              │
└──────────────────────────────────────────────────────────────┘

Step 4: Condition Check (Optional)
┌──────────────────────────────────────────────────────────────┐
│  Condition: ○ Excellent ● Good ○ Fair ○ Poor                │
│  Photos: [📷 Take Photo] [📁 Upload]                        │
│  Checklist:                                                  │
│  ☑ All accessories  ☑ Power cable  ☐ Calibration valid     │
└──────────────────────────────────────────────────────────────┘

Step 5: Confirmation
┌──────────────────────────────────────────────────────────────┐
│  Equipment:    MBES-EM2040C-SN12345                         │
│  From:         高雄總倉                                      │
│  To:           Ocean Explorer (IMO 9876543)                 │
│  Project:      南海測量專案 2025                             │
│  Install Type: Project Deployment                            │
│  Date:         2025-12-31                                    │
│                                                              │
│  ☑ I confirm this transfer is authorized                    │
│                                    [← Back] [Confirm ✓]     │
└──────────────────────────────────────────────────────────────┘
```

### 5.3 Calibration Wizard 流程

```
Step 1: Provider     → 選擇校正廠商
Step 2: Details      → 日期、類型、優先級、校正項目、特殊指示
Step 3: Documents    → 上次報告、設備照片、已知問題
Step 4: Confirmation → 摘要確認
```

### 5.4 Software Assignment Wizard 流程

```
Step 1: Target       → Person / Vessel / Equipment
Step 2: Details      → 日期、用途、預計歸還日
Step 3: Confirmation → 確認 + 發送通知選項
```

---

## 六、路由規劃

```typescript
const routes = [
  // Equipment
  { path: '/equipment', name: 'equipment-list' },
  { path: '/equipment/new', name: 'equipment-create' },
  { path: '/equipment/:id', name: 'equipment-detail' },
  { path: '/equipment/:id/edit', name: 'equipment-edit' },
  { path: '/e/:assetCode', name: 'equipment-scan' },  // QR Code
  
  // Locations
  { path: '/locations', name: 'location-list' },
  { path: '/locations/new', name: 'location-create' },
  { path: '/locations/:id', name: 'location-detail' },
  { path: '/locations/:id/edit', name: 'location-edit' },
  
  // Projects
  { path: '/projects', name: 'project-list' },
  { path: '/projects/new', name: 'project-create' },
  { path: '/projects/:id', name: 'project-detail' },
  { path: '/projects/:id/edit', name: 'project-edit' },
  
  // Software
  { path: '/software', name: 'software-list' },
  { path: '/software/new', name: 'software-create' },
  { path: '/software/:id', name: 'software-detail' },
  { path: '/software/:id/edit', name: 'software-edit' },
  
  // Dashboard
  { path: '/dashboard', name: 'dashboard' },
]
```

---

## 七、資料庫 Migration 摘要

### 新增資料表

1. **projects** - 專案管理
2. **locations** - 位置管理（Vessel/Warehouse/Person）
3. **software** - 軟體主檔
4. **software_licenses** - 軟體授權/Dongle
5. **software_license_logs** - 授權異動記錄

### 修改資料表

**equipments**：
- 新增 `current_location_id`
- 新增 `project_id`
- 新增 `installation_type`
- 新增 `installation_date`
- 新增 `installation_notes`

---

## 八、實作優先級

### Phase 1（2-3 週）- 基礎架構

| 項目 | 工時 |
|------|------|
| Location 資料表 + API（含 Vessel 多重識別碼） | 3-4 天 |
| Project 資料表 + API | 2-3 天 |
| LocationSelect 組件 | 2 天 |
| Equipment 關聯更新 | 2 天 |
| Asset Code 新規則 | 1-2 天 |

### Phase 2（2-3 週）- 核心功能

| 項目 | 工時 |
|------|------|
| Transfer Wizard | 4-5 天 |
| Calibration Wizard | 3-4 天 |
| 統一狀態操作 Modal | 2-3 天 |
| 新增頁面支援上傳 | 2 天 |

### Phase 3（2-3 週）- Software 模組

| 項目 | 工時 |
|------|------|
| Software 資料表 + API | 3-4 天 |
| Software License 列表/詳情 | 3-4 天 |
| Software Assignment Wizard | 2-3 天 |
| 到期提醒功能 | 2 天 |

### Phase 4（1-2 週）- 優化

| 項目 | 工時 |
|------|------|
| Location 詳情頁 | 2-3 天 |
| Sub-Equipment Inline 編輯 | 2-3 天 |
| 快取機制 | 2 天 |

---

## 九、結論

本 V3 方案涵蓋：

1. **Location 管理** - Vessel（含多重識別碼 + Project 選擇）、Warehouse、Person
2. **Project 關聯** - 作為 Vessel 的子屬性，設備部署時自動繼承
3. **Software 管理** - Dongle/License 全生命週期追蹤 + 到期提醒
4. **Action Wizard** - 引導式操作流程
5. **Asset Code 新規則** - `{Category}-{ModelCode}-SN{Serial}` 格式，支援到 9999

建議優先執行 Phase 1 + Phase 2，約 4-6 週可完成核心功能改善。

---

**文件結束**
