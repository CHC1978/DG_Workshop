# Tailscale VPN Connection Guide

This guide explains how to connect to the Marine Equipment Management System via Tailscale VPN.

## System Information

| Item | Information |
|------|-------------|
| System Name | Marine Equipment QR System |
| Access URL | `https://neptus-station.boga-ulmer.ts.net:8443` |
| VPN Required | Tailscale |

---

## Administrator: Create Invite Link

> This section is for administrators only

### Step 1: Login to Tailscale Admin Console

1. Open browser and go to [Tailscale Admin Console](https://login.tailscale.com/admin)
2. Login with your administrator account

### Step 2: Create Invite Link

1. Click **Users** in the left menu
2. Click **Invite users** in the top right
3. Select **Create invite link**
4. Configure options:
   - **Role**: Member (regular user)
   - **Expiration**: Recommend 7 days or 30 days
5. Click **Create link**
6. Copy the generated link

### Step 3: Generate QR Code (Optional)

Convert the invite link to a QR code for easy mobile scanning:

1. Go to [QR Code Generator](https://www.qrcode-generator.de/)
2. Paste the invite link
3. Download the QR code image
4. Send to users who need access

---

## User Quick Start

### Option 1: Use Invite Link

The administrator will provide you an invite link like:
```
https://login.tailscale.com/admin/invite/xxx...
```

Click the link and follow the instructions to complete registration.

### Option 2: Scan QR Code

If the administrator provides a QR code:

1. Use your phone camera to scan the QR code
2. Tap the link that appears
3. Follow the instructions to register

---

## Platform Installation Guide

### iOS (iPhone / iPad)

#### Step 1: Download Tailscale App

[![App Store](https://img.shields.io/badge/App_Store-Download-blue)](https://apps.apple.com/app/tailscale/id1470499037)

Or search for **Tailscale** in the App Store

#### Step 2: Install and Open the App

1. Tap **Get** to download and install
2. Open the **Tailscale** app after installation

#### Step 3: Login

**Option A - Using Invite Link:**
1. Tap the invite link provided by administrator
2. App will open automatically
3. Choose login method (Google / Microsoft / GitHub etc.)
4. Complete verification

**Option B - Manual Login:**
1. Tap **Get Started** in the app
2. Choose your login method
3. Wait for administrator approval (if required)

#### Step 4: Enable VPN

1. First connection will request VPN permission
2. Tap **Allow**
3. Verify with Face ID / Touch ID or enter passcode
4. Confirm status shows **Connected**

---

### Android

#### Step 1: Download Tailscale App

[![Google Play](https://img.shields.io/badge/Google_Play-Download-green)](https://play.google.com/store/apps/details?id=com.tailscale.ipn)

Or search for **Tailscale** in Google Play Store

#### Step 2: Install and Open the App

1. Tap **Install** to download
2. Open the **Tailscale** app after installation

#### Step 3: Login

**Option A - Using Invite Link:**
1. Tap the invite link provided by administrator
2. Choose to open with Tailscale app
3. Select login method
4. Complete verification

**Option B - Manual Login:**
1. Tap **Get Started** in the app
2. Choose your login method
3. Wait for administrator approval (if required)

#### Step 4: Enable VPN

1. First connection will request VPN setup
2. Tap **OK** to allow
3. Confirm status shows **Connected**

---

### Windows

#### Step 1: Download Tailscale

Go to [Tailscale Download](https://tailscale.com/download/windows) to download for Windows

#### Step 2: Install

1. Run the downloaded `tailscale-setup-xxx.exe`
2. Follow the installation wizard
3. Tailscale will start automatically after installation

#### Step 3: Login

1. Click the Tailscale icon in the system tray (bottom right)
2. Click **Log in**
3. Browser will open the login page

**Using Invite Link:**
- Click the invite link provided by administrator
- Complete login in browser

**Manual Login:**
- Choose login method (Google / Microsoft / GitHub etc.)
- Automatically connects after verification

#### Step 4: Verify Connection

1. System tray icon turns **green** when connected
2. Click the icon to view connection status

---

### macOS

#### Step 1: Download Tailscale

**Option A - App Store:**

[![Mac App Store](https://img.shields.io/badge/Mac_App_Store-Download-blue)](https://apps.apple.com/app/tailscale/id1475387142)

**Option B - Official Website:**

Go to [Tailscale Download](https://tailscale.com/download/mac)

#### Step 2: Install

**App Store Version:**
1. Click **Get** to download and install
2. Open Tailscale after installation

**Website Version:**
1. Open the downloaded `.pkg` file
2. Follow the installation wizard

#### Step 3: Login

1. Click the Tailscale icon in the menu bar (top right)
2. Click **Log in**
3. Complete login in browser

#### Step 4: Verify Connection

1. Menu bar icon becomes **solid** when connected
2. Click the icon to view connection status

---

## Connect to the System

After confirming Tailscale is connected:

### Step 1: Open Browser

Use any browser (Chrome / Safari / Edge / Firefox)

### Step 2: Enter URL

```
https://neptus-station.boga-ulmer.ts.net:8443
```

### Step 3: Login to System

Use the username and password provided by administrator

### Step 4: Bookmark (Recommended)

Add the URL to bookmarks or save to home screen for quick access

---

## Troubleshooting

### Cannot Connect - "Connection refused"

**Cause**: Tailscale is not running or not connected

**Solution**:
1. Confirm Tailscale app is open
2. Confirm status shows **Connected** (green)
3. Try turning Tailscale off and on again

---

### Certificate Error - "Certificate error"

**Cause**: Using IP address instead of domain name

**Solution**:
- Use full URL `https://neptus-station.boga-ulmer.ts.net:8443`
- Do not use IP address (e.g., `100.x.x.x`)

---

### Page Not Loading - "Page not found"

**Cause**: NAS may be offline or service not running

**Solution**:
1. Confirm you are connected to Tailscale
2. Contact administrator to check NAS status

---

### Login Failed - "Invalid credentials"

**Cause**: Wrong username or password

**Solution**:
1. Verify username and password
2. Check for case sensitivity
3. Contact administrator to reset password

---

### Tailscale Shows "Waiting for approval"

**Cause**: Administrator approval required

**Solution**:
- Contact administrator to approve your device

---

## Contact Administrator

If you have any issues, please contact the system administrator:

| Item | Information |
|------|-------------|
| Administrator | `[Administrator Name]` |
| Email | `[Administrator Email]` |
| Phone | `[Contact Phone]` |

---

## Related Links

- [Tailscale Documentation](https://tailscale.com/kb/)
- [Tailscale Downloads](https://tailscale.com/download)
- [System Login Page](https://neptus-station.boga-ulmer.ts.net:8443)
