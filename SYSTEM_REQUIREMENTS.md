# System Requirements and Guidelines

## Windows Batch Files (.bat)

**IMPORTANT**: All Windows batch files MUST use pure English/ASCII characters only.

### Rules:
1. **NO Chinese characters** - Causes encoding issues
2. **NO UTF-8 encoding** (no `chcp 65001`)
3. **Pure ASCII text only**
4. All messages in English
5. All window titles in English

### Reason:
- Chinese characters cause batch file corruption
- Results in errors like: 'ment', 'pment', 'tart' not recognized
- Encoding issues vary across Windows systems
- ASCII ensures universal compatibility

### Compliant Batch Files:
- ✅ manage.bat - Control panel (pure English)
- ✅ quick_start.bat - Quick start (pure English)
- ✅ restart_all.bat - Restart all (pure English)
- ✅ stop_all.bat - Stop all (pure English)
- ✅ start_all.bat - Start all (pure English)
- ✅ start_backend.bat - Start backend (pure English)
- ✅ start_frontend.bat - Start frontend (pure English)
- ✅ setup_first_time.bat - First time setup (pure English)

### Deprecated Files:
- ❌ 快速啟動.bat - Use `quick_start.bat` instead

---

## Development Guidelines

### Backend Development:
- Python code can use Chinese in comments
- Database can store Chinese data
- API responses can include Chinese
- Only batch files must be pure English

### Frontend Development:
- Vue components can use Chinese
- UI text will be in Chinese (future i18n)
- Config files can have Chinese comments
- Build scripts should be English

### System Scripts:
- All .bat files: Pure English only
- All .sh files (if any): Can use UTF-8
- PowerShell scripts (.ps1): Can use UTF-8

---

## manage.bat Menu Structure

```
[1] Start All - Backend and Frontend
[2] Stop All
[3] Restart All

[4] Start Backend Only
[5] Start Frontend Only
[6] Restart Backend Only       <- NEW
[7] Restart Frontend Only      <- NEW

[8] Stop Backend Only
[9] Stop Frontend Only

[S] Check Status
[H] First Time Setup (Help)

[0] Exit
```

### New Features:
- **[6] Restart Backend Only**: Useful after backend code changes
- **[7] Restart Frontend Only**: Useful after config changes
- **[S] Status Check**: View running services
- **[H] Help/Setup**: Run first-time setup

---

## Quick Reference

### Daily Development:
```cmd
manage.bat → [3] Restart All
```

### After Backend Code Changes:
```cmd
manage.bat → [6] Restart Backend Only
```

### After Frontend Config Changes:
```cmd
manage.bat → [7] Restart Frontend Only
```

### Check What's Running:
```cmd
manage.bat → [S] Check Status
```

### Clean Stop:
```cmd
manage.bat → [2] Stop All
```

---

**Last Updated**: 2025-12-30
**Requirement**: Pure English/ASCII for all .bat files
