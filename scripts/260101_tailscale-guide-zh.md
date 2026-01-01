# Tailscale VPN 連線指南

本指南說明如何透過 Tailscale VPN 連線至海洋設備管理系統。

## 系統資訊

| 項目 | 資訊 |
|------|------|
| 系統名稱 | Marine Equipment QR System |
| 存取網址 | `https://neptus-station.boga-ulmer.ts.net:8443` |
| 需要 VPN | Tailscale |

---

## 管理員：建立邀請連結

> 此章節僅供管理員參考

### 步驟 1：登入 Tailscale Admin Console

1. 開啟瀏覽器，前往 [Tailscale Admin Console](https://login.tailscale.com/admin)
2. 使用管理員帳號登入

### 步驟 2：建立邀請連結

1. 點擊左側選單 **Users**
2. 點擊右上角 **Invite users**
3. 選擇 **Create invite link**
4. 設定選項：
   - **Role**: Member (一般使用者)
   - **Expiration**: 建議 7 days 或 30 days
5. 點擊 **Create link**
6. 複製產生的連結

### 步驟 3：產生 QR Code (選用)

將邀請連結轉換為 QR Code，方便手機用戶掃描：

1. 前往 [QR Code Generator](https://www.qrcode-generator.de/)
2. 貼上邀請連結
3. 下載 QR Code 圖片
4. 傳送給需要連線的用戶

---

## 用戶快速開始

### 方式一：使用邀請連結

管理員會提供您一個邀請連結，格式如下：
```
https://login.tailscale.com/admin/invite/xxx...
```

點擊連結後依照指示完成註冊即可。

### 方式二：掃描 QR Code

如果管理員提供 QR Code：

1. 使用手機相機掃描 QR Code
2. 點擊開啟的連結
3. 依照指示完成註冊

---

## 平台安裝指南

### iOS (iPhone / iPad)

#### 步驟 1：下載 Tailscale App

[![App Store](https://img.shields.io/badge/App_Store-Download-blue)](https://apps.apple.com/app/tailscale/id1470499037)

或在 App Store 搜尋 **Tailscale**

#### 步驟 2：安裝並開啟 App

1. 點擊 **取得** 下載安裝
2. 安裝完成後開啟 **Tailscale** App

#### 步驟 3：登入

**方式 A - 使用邀請連結：**
1. 點擊管理員提供的邀請連結
2. 自動跳轉至 Tailscale App
3. 選擇登入方式 (Google / Microsoft / GitHub 等)
4. 完成驗證

**方式 B - 手動登入：**
1. 在 App 中點擊 **Get Started**
2. 選擇登入方式
3. 等待管理員核准加入 (如需要)

#### 步驟 4：啟用 VPN

1. 首次連線會要求允許 VPN 設定
2. 點擊 **Allow** 允許
3. 驗證 Face ID / Touch ID 或輸入密碼
4. 確認狀態顯示 **Connected**

---

### Android

#### 步驟 1：下載 Tailscale App

[![Google Play](https://img.shields.io/badge/Google_Play-Download-green)](https://play.google.com/store/apps/details?id=com.tailscale.ipn)

或在 Google Play 商店搜尋 **Tailscale**

#### 步驟 2：安裝並開啟 App

1. 點擊 **安裝** 下載
2. 安裝完成後開啟 **Tailscale** App

#### 步驟 3：登入

**方式 A - 使用邀請連結：**
1. 點擊管理員提供的邀請連結
2. 選擇使用 Tailscale App 開啟
3. 選擇登入方式
4. 完成驗證

**方式 B - 手動登入：**
1. 在 App 中點擊 **Get Started**
2. 選擇登入方式
3. 等待管理員核准加入 (如需要)

#### 步驟 4：啟用 VPN

1. 首次連線會要求設定 VPN
2. 點擊 **確定** 允許
3. 確認狀態顯示 **Connected**

---

### Windows

#### 步驟 1：下載 Tailscale

前往 [Tailscale Download](https://tailscale.com/download/windows) 下載 Windows 版本

#### 步驟 2：安裝

1. 執行下載的 `tailscale-setup-xxx.exe`
2. 依照安裝精靈完成安裝
3. 安裝完成後 Tailscale 會自動啟動

#### 步驟 3：登入

1. 點擊系統匣 (右下角) 的 Tailscale 圖示
2. 點擊 **Log in**
3. 瀏覽器會開啟登入頁面

**使用邀請連結：**
- 直接點擊管理員提供的邀請連結
- 在瀏覽器中完成登入

**手動登入：**
- 選擇登入方式 (Google / Microsoft / GitHub 等)
- 完成驗證後自動連線

#### 步驟 4：確認連線

1. 系統匣圖示變為 **綠色** 表示已連線
2. 點擊圖示可查看連線狀態

---

### macOS

#### 步驟 1：下載 Tailscale

**方式 A - App Store：**

[![Mac App Store](https://img.shields.io/badge/Mac_App_Store-Download-blue)](https://apps.apple.com/app/tailscale/id1475387142)

**方式 B - 官網下載：**

前往 [Tailscale Download](https://tailscale.com/download/mac) 下載

#### 步驟 2：安裝

**App Store 版本：**
1. 點擊 **取得** 下載安裝
2. 安裝完成後開啟 Tailscale

**官網版本：**
1. 開啟下載的 `.pkg` 檔案
2. 依照安裝精靈完成安裝

#### 步驟 3：登入

1. 點擊選單列 (右上角) 的 Tailscale 圖示
2. 點擊 **Log in**
3. 在瀏覽器中完成登入

#### 步驟 4：確認連線

1. 選單列圖示變為 **實心** 表示已連線
2. 點擊圖示可查看連線狀態

---

## 連線至系統

確認 Tailscale 已連線後：

### 步驟 1：開啟瀏覽器

使用任何瀏覽器 (Chrome / Safari / Edge / Firefox)

### 步驟 2：輸入網址

```
https://neptus-station.boga-ulmer.ts.net:8443
```

### 步驟 3：登入系統

使用管理員提供的帳號密碼登入

### 步驟 4：加入書籤 (建議)

將網址加入書籤或儲存至主畫面，方便日後快速存取

---

## 疑難排解

### 無法連線 - "Connection refused"

**原因**：Tailscale 未啟動或未連線

**解決方法**：
1. 確認 Tailscale App 已開啟
2. 確認狀態顯示 **Connected** (綠色)
3. 嘗試關閉再重新開啟 Tailscale

---

### 憑證錯誤 - "Certificate error"

**原因**：使用 IP 位址而非網域名稱

**解決方法**：
- 使用完整網址 `https://neptus-station.boga-ulmer.ts.net:8443`
- 不要使用 IP 位址 (如 `100.x.x.x`)

---

### 網頁無法載入 - "Page not found"

**原因**：NAS 可能離線或服務未啟動

**解決方法**：
1. 確認您已連線至 Tailscale
2. 聯繫管理員確認 NAS 狀態

---

### 登入失敗 - "Invalid credentials"

**原因**：帳號或密碼錯誤

**解決方法**：
1. 確認帳號密碼正確
2. 注意大小寫
3. 聯繫管理員重設密碼

---

### Tailscale 顯示 "Waiting for approval"

**原因**：需要管理員核准加入

**解決方法**：
- 聯繫管理員核准您的裝置

---

## 聯絡管理員

如有任何問題，請聯繫系統管理員：

| 項目 | 資訊 |
|------|------|
| 管理員 | `[管理員姓名]` |
| Email | `[管理員 Email]` |
| 電話 | `[聯絡電話]` |

---

## 相關連結

- [Tailscale 官方文件](https://tailscale.com/kb/)
- [Tailscale 下載頁面](https://tailscale.com/download)
- [系統登入頁面](https://neptus-station.boga-ulmer.ts.net:8443)
