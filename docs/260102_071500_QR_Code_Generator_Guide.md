# QR Code Generator Guide

本指南說明如何使用 QR Code 生成工具建立自定義 QR Code。

## 腳本位置

```
scripts/generate_qr.py
```

## 前置需求

- Python 3.12+
- qrcode 套件（已包含在 backend/requirements.txt）

## 使用方法

### 方法一：命令列模式

```powershell
# 進入專案目錄
cd E:\QT_project\DG_workshop

# 基本用法：指定完整 URL
.\backend\venv\Scripts\python.exe scripts\generate_qr.py <url> [output_file]
```

#### 範例

```powershell
# 生成 login 頁面 QR code
.\backend\venv\Scripts\python.exe scripts\generate_qr.py https://neptus-station.boga-ulmer.ts.net:8443/login login_qr.png

# 只輸入路徑（自動加上預設 domain）
.\backend\venv\Scripts\python.exe scripts\generate_qr.py /login

# 生成到指定目錄
.\backend\venv\Scripts\python.exe scripts\generate_qr.py /login frontend/public/login_qr.png

# 自動生成檔名（含時間戳記）
.\backend\venv\Scripts\python.exe scripts\generate_qr.py /dashboard
# 輸出: qr_20260102_120000.png
```

### 方法二：互動模式

```powershell
.\backend\venv\Scripts\python.exe scripts\generate_qr.py --interactive
```

互動模式提供選單介面：

```
============================================================
QR Code Generator - Interactive Mode
============================================================
Default domain: https://neptus-station.boga-ulmer.ts.net:8443

------------------------------------------------------------
Options:
  [1-5] Generate QR for common pages
    1. Login Page (/login)
    2. Dashboard (/dashboard)
    3. Equipment List (/equipment)
    4. API Docs (/api/docs)
    5. Health Check (/api/health)
  [C]   Custom URL
  [F]   Full custom URL (enter complete URL)
  [Q]   Quit

Select option:
```

## 預設常用頁面

| 選項 | 頁面名稱 | 路徑 | 完整 URL |
|------|----------|------|----------|
| 1 | Login Page | `/login` | `https://neptus-station.boga-ulmer.ts.net:8443/login` |
| 2 | Dashboard | `/dashboard` | `https://neptus-station.boga-ulmer.ts.net:8443/dashboard` |
| 3 | Equipment List | `/equipment` | `https://neptus-station.boga-ulmer.ts.net:8443/equipment` |
| 4 | API Docs | `/api/docs` | `https://neptus-station.boga-ulmer.ts.net:8443/api/docs` |
| 5 | Health Check | `/api/health` | `https://neptus-station.boga-ulmer.ts.net:8443/api/health` |

## 預設設定

腳本中的預設 domain 設定：

```python
DEFAULT_DOMAIN = "neptus-station.boga-ulmer.ts.net:8443"
DEFAULT_PROTOCOL = "https"
```

如需修改預設 domain，請編輯 `scripts/generate_qr.py` 中的這兩個變數。

## 輸出檔案

### 檔案格式
- 格式：PNG
- 預設大小：約 800-1000 bytes
- QR Code 規格：Version 1, Error Correction M

### 建議存放位置

| 用途 | 路徑 | 說明 |
|------|------|------|
| 前端靜態資源 | `frontend/public/` | 可透過 `/<filename>` 存取 |
| 文件/列印用 | `docs/qrcodes/` | 與文件一起管理 |
| NAS 部署 | `/volume1/docker/marine-equipment/` | NAS 本地使用 |

## 在 NAS 上使用

### 上傳腳本到 NAS

```bash
# 上傳到 /volume1/docker/marine-equipment/
```

### 透過 Task Scheduler 執行

```bash
#!/bin/bash
docker cp /volume1/docker/marine-equipment/generate_qr.py marine-equipment-backend:/app/
docker exec marine-equipment-backend python generate_qr.py /login /app/data/login_qr.png
docker cp marine-equipment-backend:/app/data/login_qr.png /volume1/docker/marine-equipment/
```

## 程式碼範例

### 在 Python 中直接調用

```python
from scripts.generate_qr import generate_qr_code

# 生成 QR code
output_path = generate_qr_code(
    url="https://neptus-station.boga-ulmer.ts.net:8443/login",
    output_path="login_qr.png",
    box_size=10,
    border=4
)
print(f"QR code saved to: {output_path}")
```

### 自訂 QR Code 參數

```python
from qrcode.constants import ERROR_CORRECT_H

output_path = generate_qr_code(
    url="https://example.com",
    output_path="high_quality_qr.png",
    box_size=15,           # 較大的方塊
    border=6,              # 較寬的邊框
    error_correction=ERROR_CORRECT_H  # 最高錯誤修正
)
```

## 錯誤修正等級

| 等級 | 說明 | 可修復資料 |
|------|------|-----------|
| L | 低 | ~7% |
| M | 中（預設） | ~15% |
| Q | 較高 | ~25% |
| H | 最高 | ~30% |

較高的錯誤修正等級會產生較大的 QR code，但在部分遮擋或損壞時仍可掃描。

## 已生成的 QR Code

| 檔案 | URL | 位置 |
|------|-----|------|
| `login_qr.png` | `/login` | `frontend/public/` |

## 相關文件

- [部署指南](../scripts/DEPLOY.md)
- [Tailscale 連線指南](../scripts/260101_tailscale-guide-zh.md)
