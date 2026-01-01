# SSL Certificate Setup for neptus-station

This guide explains how to set up SSL certificates for HTTPS on your Synology DS223 NAS with Tailscale.

## Your Tailscale Configuration

| Item | Value |
|------|-------|
| Machine name | neptus-station |
| Tailscale IP | 100.119.150.20 |
| Full domain | **neptus-station.boga-ulmer.ts.net** |
| MagicDNS | Enabled |

## Prerequisites

- [x] Tailscale installed and running on DS223
- [x] MagicDNS enabled (confirmed)
- [ ] HTTPS Certificates enabled in Tailscale admin console

## Step 1: Enable HTTPS Certificates in Tailscale

1. Go to [Tailscale Admin Console - DNS](https://login.tailscale.com/admin/dns)
2. Scroll down to **HTTPS Certificates**
3. Click **Enable HTTPS**

## Step 2: Generate Certificates on NAS

### Option A: Via SSH (if enabled)
```bash
ssh admin@100.119.150.20
sudo tailscale cert neptus-station.boga-ulmer.ts.net
```

### Option B: Via DSM Task Scheduler (recommended if SSH disabled)

1. Open DSM **Control Panel** > **Task Scheduler**
2. Click **Create** > **Scheduled Task** > **User-defined script**
3. Settings:
   - Task: `Generate Tailscale Cert`
   - User: `root`
   - Schedule: Run once (or weekly for renewal)
4. Task Settings - User-defined script:
```bash
#!/bin/bash
cd /volume1/docker/marine-equipment/ssl
/var/packages/Tailscale/target/bin/tailscale cert neptus-station.boga-ulmer.ts.net
mv neptus-station.boga-ulmer.ts.net.crt server.crt
mv neptus-station.boga-ulmer.ts.net.key server.key
chmod 644 server.crt
chmod 600 server.key
touch https_enabled
```
5. Click **OK** and run the task

## Step 3: Create Directory Structure on NAS

Use DSM **File Station** to create:

```
/volume1/docker/marine-equipment/
├── ssl/
│   ├── server.crt          (will be created by task)
│   ├── server.key          (will be created by task)
│   └── https_enabled       (will be created by task)
├── docker-compose.yml      (upload from Windows)
└── .env                    (copy from .env.production)
```

## Step 4: Upload Files to NAS

From Windows, upload these files to `/volume1/docker/marine-equipment/`:

1. `docker-compose.yml`
2. `.env.production` → rename to `.env`
3. `docker-images/backend-arm64.tar` → to `/volume1/docker/marine-equipment/images/`
4. `docker-images/frontend-arm64.tar` → to `/volume1/docker/marine-equipment/images/`

## Step 5: Edit .env on NAS

After uploading, edit `.env` to set your SECRET_KEY:

```bash
# Generate a new secret key on your Windows machine:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output and update SECRET_KEY in .env
```

## Step 6: Import Docker Images

In DSM **Container Manager**:

1. Go to **Image** tab
2. Click **Add** > **Add from file**
3. Select `/volume1/docker/marine-equipment/images/backend-arm64.tar`
4. Wait for import to complete
5. Repeat for `frontend-arm64.tar`

You should see:
- `marine-equipment-backend:arm64`
- `marine-equipment-frontend:arm64`

## Step 7: Create and Start Project

1. Go to **Container Manager** > **Project**
2. Click **Create**
3. Settings:
   - Project name: `marine-equipment`
   - Path: `/volume1/docker/marine-equipment`
   - Source: Use existing docker-compose.yml
4. Click **Next** to review
5. Click **Build** (or **Apply**)

## Step 8: Verify Deployment

### Check Container Status
In Container Manager, both containers should show:
- `marine-equipment-backend`: Running (Healthy)
- `marine-equipment-frontend`: Running (Healthy)

### Test Access
From any device on your Tailscale network:

| URL | Expected |
|-----|----------|
| `https://neptus-station.boga-ulmer.ts.net` | Frontend loads |
| `https://neptus-station.boga-ulmer.ts.net/api/docs` | Swagger UI |
| `https://neptus-station.boga-ulmer.ts.net/api/health` | `{"status":"ok"}` |

### Verify HTTPS
- Browser should show green padlock 🔒
- No certificate warnings
- Certificate issued to `neptus-station.boga-ulmer.ts.net`

## Certificate Renewal (Automatic)

Set up weekly renewal task in DSM Task Scheduler:

1. **Control Panel** > **Task Scheduler**
2. **Create** > **Scheduled Task** > **User-defined script**
3. Settings:
   - Task: `Renew Tailscale Cert`
   - User: `root`
   - Schedule: Every Sunday at 3:00 AM
4. Script:
```bash
#!/bin/bash
cd /volume1/docker/marine-equipment/ssl
/var/packages/Tailscale/target/bin/tailscale cert neptus-station.boga-ulmer.ts.net
mv neptus-station.boga-ulmer.ts.net.crt server.crt
mv neptus-station.boga-ulmer.ts.net.key server.key
chmod 644 server.crt
chmod 600 server.key
docker restart marine-equipment-frontend
```

## Troubleshooting

### "Certificate not found" error
- Run the certificate generation task in Task Scheduler
- Verify files exist: Check `/volume1/docker/marine-equipment/ssl/` in File Station

### HTTPS not working (connection refused)
- Check port 443 is not blocked by DS223 firewall
- Verify `https_enabled` file exists in ssl directory
- Check nginx logs: Container Manager > marine-equipment-frontend > Logs

### Certificate warning in browser
- Use full domain `neptus-station.boga-ulmer.ts.net`, not IP address
- Ensure device is connected to Tailscale network

### PWA not installing
- Must access via HTTPS (not HTTP)
- Clear browser cache and reload
- Check browser console for service worker errors

### Container won't start
- Check `.env` file has valid SECRET_KEY
- Verify SSL certificates are in correct location
- Check Container Manager logs for specific error
