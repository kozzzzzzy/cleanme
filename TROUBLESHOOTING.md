# CleanMe Dashboard Troubleshooting Checklist

Use this checklist to diagnose and fix dashboard issues.

## ✅ Pre-Flight Checklist

### 1. Installation Complete?
- [ ] CleanMe installed via HACS or manually
- [ ] Home Assistant restarted after installation
- [ ] At least one zone configured

**How to verify**: Settings → Devices & Services → Search for "CleanMe"

---

### 2. Custom Cards Installed?
- [ ] Mushroom Cards installed from HACS
- [ ] Card Mod installed from HACS
- [ ] Home Assistant restarted after installing cards
- [ ] Browser cache cleared (Ctrl+Shift+R or Cmd+Shift+R)

**How to verify**: 
1. Go to HACS → Frontend
2. Search for "Mushroom" and "Card Mod"
3. Both should show "Installed"

**Install if missing**:
1. HACS → Frontend → Explore & Download Repositories
2. Search and install: "Mushroom" and "Card Mod"
3. Restart Home Assistant

---

### 3. Dashboard Mode?
Determine which dashboard mode you're using:

**Storage Mode (Default)**:
- [ ] You edit dashboards in the UI
- [ ] No `lovelace:` section in your `configuration.yaml`
- [ ] Dashboard should appear automatically in sidebar

**YAML Mode**:
- [ ] You have `lovelace: mode: yaml` in `configuration.yaml`
- [ ] You edit `ui-lovelace.yaml` file
- [ ] Need to manually add dashboard view

**Not sure?** You're probably in Storage Mode (the default).

---

## 🔍 Common Issues

### Issue 1: Dashboard Not Appearing in Sidebar

**Storage Mode Users:**
1. [ ] Check Settings → System → Logs for CleanMe errors
2. [ ] Verify `/config/cleanme.log` exists and check for errors
3. [ ] Try: Developer Tools → Services → `cleanme.regenerate_dashboard`
4. [ ] Restart Home Assistant
5. [ ] Check if CleanMe item appears in sidebar

**YAML Mode Users:**
1. [ ] Dashboard won't appear automatically
2. [ ] You must manually add view to `ui-lovelace.yaml`
3. [ ] See `examples/ui-lovelace.yaml` for template
4. [ ] Or add dashboard reference in `configuration.yaml`
5. [ ] See `examples/configuration.yaml` for template

---

### Issue 2: "Custom element doesn't exist: custom:mushroom-template-card"

**Problem**: Mushroom Cards not installed or not loaded

**Solution**:
1. [ ] Install Mushroom Cards via HACS
2. [ ] Restart Home Assistant
3. [ ] Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
4. [ ] Check resources loaded: Settings → Dashboards → Resources
5. [ ] Should see: `/hacsfiles/lovelace-mushroom/mushroom.js`

**Alternative**: Use basic dashboard without custom cards:
```yaml
service: cleanme.export_basic_dashboard
```
Then use `/config/dashboards/cleanme-basic.yaml`

---

### Issue 3: Cards Show "Entity not available"

**Problem**: Zone entities don't exist or names don't match

**Diagnosis**:
1. [ ] Go to Settings → Devices & Services → Entities
2. [ ] Search for "cleanme" or your zone name
3. [ ] Verify entities exist: `binary_sensor.{zone}_tidy`, `sensor.{zone}_tasks`
4. [ ] Check entity names match dashboard YAML (replace spaces with underscores)

**Example**:
- Zone name: "Living Room"
- Entity: `binary_sensor.living_room_tidy` (not `binary_sensor.living-room_tidy`)

**Solution**:
1. [ ] If entities exist with correct names, regenerate dashboard:
   ```yaml
   service: cleanme.regenerate_dashboard
   ```
2. [ ] If entities missing, reconfigure zone in Settings → Devices & Services

---

### Issue 4: Dashboard File Not Generated

**Problem**: `/config/dashboards/cleanme.yaml` doesn't exist

**Diagnosis**:
1. [ ] Check `/config/cleanme.log` for errors
2. [ ] Verify PyYAML is installed: `pip3 list | grep PyYAML`
3. [ ] Check directory permissions: `/config/dashboards/` should be writable

**Solution**:
1. [ ] Create directory manually: `mkdir /config/dashboards`
2. [ ] Try: Developer Tools → Services → `cleanme.regenerate_dashboard`
3. [ ] Check logs: `/config/cleanme.log`
4. [ ] If PyYAML missing, install: `pip3 install PyYAML`

---

### Issue 5: Cards Look Broken or Unstyled

**Problem**: Card Mod not installed or not working

**Solution**:
1. [ ] Install Card Mod via HACS
2. [ ] Restart Home Assistant
3. [ ] Clear browser cache (Ctrl+Shift+R)
4. [ ] Cards should now show borders and styling

**Note**: Cards will work without Card Mod, just won't have custom styling.

---

### Issue 6: Dashboard Not Updating When I Add Zones

**Problem**: Dashboard doesn't reflect new zones

**Solution**:
1. [ ] Try: Developer Tools → Services → `cleanme.regenerate_dashboard`
2. [ ] Check `/config/dashboards/cleanme.yaml` was updated (check file timestamp)
3. [ ] In YAML mode: Copy updated cards to your `ui-lovelace.yaml`
4. [ ] In Storage mode: Try refreshing browser or restarting HA

**Auto-update**: Dashboard should update automatically when zones are added/removed. If not, there may be an error in logs.

---

## 🧪 Testing Services

Test if CleanMe services work:

### Test 1: Dashboard Regeneration
```yaml
service: cleanme.regenerate_dashboard
```
**Expected**: Log message in `/config/cleanme.log`  
**Check**: `/config/dashboards/cleanme.yaml` updated

### Test 2: Basic Dashboard Export
```yaml
service: cleanme.export_basic_dashboard
```
**Expected**: New file created  
**Check**: `/config/dashboards/cleanme-basic.yaml` exists

### Test 3: Zone Check
```yaml
service: cleanme.request_check
data:
  zone: Kitchen  # Replace with your zone name
```
**Expected**: Camera snapshot taken, AI analysis performed  
**Check**: Sensor entities update with new data

---

## 📋 Information Gathering for Support

If you need to report an issue, gather this information:

1. **Home Assistant Version**: 
   Settings → System → About

2. **Dashboard Mode**: 
   Storage or YAML? (check configuration.yaml)

3. **Custom Cards Installed**:
   HACS → Frontend (list installed cards)

4. **Log Errors**:
   ```
   Settings → System → Logs (filter "cleanme")
   OR check /config/cleanme.log
   ```

5. **File Check**:
   ```bash
   ls -la /config/dashboards/
   cat /config/dashboards/cleanme.yaml
   ```

6. **Entity Check**:
   Settings → Devices & Services → Entities (filter "cleanme")

---

## 🔧 Manual Dashboard Creation

If auto-generation fails completely, create manually:

### Option A: Basic Entities Card (No Custom Cards)
```yaml
type: entities
title: 🧹 Kitchen
entities:
  - entity: binary_sensor.kitchen_tidy
    name: Status
  - entity: sensor.kitchen_tasks
    name: Task Count
  - entity: sensor.kitchen_last_check
    name: Last Check
```

### Option B: Mushroom Card (Requires Custom Cards)
```yaml
type: custom:mushroom-template-card
primary: 🧹 Kitchen
secondary: "{{ state_attr('sensor.kitchen_tasks', 'comment') }}"
icon: >
  {% if is_state('binary_sensor.kitchen_tidy', 'on') %}
  mdi:check-circle
  {% else %}
  mdi:alert-circle
  {% endif %}
icon_color: >
  {% if is_state('binary_sensor.kitchen_tidy', 'on') %}
  green
  {% else %}
  red
  {% endif %}
tap_action:
  action: more-info
```

---

## 📞 Still Need Help?

1. **Re-read documentation**:
   - [QUICK_START.md](QUICK_START.md)
   - [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md)

2. **Check Home Assistant logs**:
   - Settings → System → Logs
   - `/config/cleanme.log`

3. **Open an issue**:
   - https://github.com/cozbox/cleanme/issues
   - Include: HA version, dashboard mode, logs, error messages

4. **Home Assistant Community**:
   - https://community.home-assistant.io/
   - Tag with `custom-component` and `cleanme`

---

**Most issues are resolved by:**
1. ✅ Installing custom cards (Mushroom + Card Mod)
2. ✅ Restarting Home Assistant
3. ✅ Clearing browser cache
4. ✅ Running `cleanme.regenerate_dashboard` service
