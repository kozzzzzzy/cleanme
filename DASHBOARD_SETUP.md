# CleanMe Dashboard Setup Guide

This guide covers all the different ways to set up the CleanMe dashboard in Home Assistant, depending on your configuration mode.

## 🎯 Which Setup Method Should I Use?

Home Assistant supports different dashboard configuration modes. Choose based on your setup:

- **Storage Mode (Default)** - You edit dashboards in the UI → Use Method 1
- **YAML Mode** - You edit `ui-lovelace.yaml` → Use Method 2
- **Mixed Mode** - Storage + YAML dashboards → Use Method 3

Not sure? Most users are in **Storage Mode** (the default).

---

## Method 1: Storage Mode (Automatic Dashboard Panel)

**Best for**: Default Home Assistant users who edit dashboards in the UI.

### Setup Steps:

1. **Install CleanMe** via HACS or manually
2. **Add your first zone** via Settings → Devices & Services → Add Integration → CleanMe
3. **Check the sidebar** - A "CleanMe" menu item should automatically appear
4. **Click "CleanMe"** in the sidebar to see your dashboard

### How It Works:

The integration automatically:
- Registers a Lovelace panel in the sidebar
- Generates dashboard cards for each configured zone
- Updates the dashboard when you add/remove zones

### Troubleshooting:

**Dashboard panel not showing up?**
- Restart Home Assistant after installing
- Check Settings → System → Logs for errors related to `custom_components.cleanme`
- Ensure you've added at least one zone

**Cards look broken?**
- Install Mushroom Cards via HACS: `piitaya/lovelace-mushroom`
- Install Card Mod via HACS: `thomasloven/lovelace-card-mod`
- Refresh your browser after installing custom cards

---

## Method 2: YAML Mode (ui-lovelace.yaml)

**Best for**: Users who manage their entire dashboard via `ui-lovelace.yaml`.

### Setup Steps:

1. **Enable YAML mode** in your `configuration.yaml`:
   ```yaml
   lovelace:
     mode: yaml
   ```

2. **Add CleanMe view** to your `ui-lovelace.yaml`:
   ```yaml
   title: Home
   views:
     # Your existing views...
     
     # CleanMe Dashboard
     - title: 🏠 Tidy Tracker
       path: cleanme
       icon: mdi:broom
       badges: []
       cards:
         # Copy cards from /config/dashboards/cleanme.yaml
         # Or manually create cards (see example below)
   ```

3. **Get auto-generated cards**:
   - The integration creates `/config/dashboards/cleanme.yaml`
   - Copy the `cards:` section from that file into your view
   - Or use the example in `examples/dashboard-example.yaml`

4. **Restart Home Assistant** to apply changes

### Manual Card Example:

```yaml
- type: custom:mushroom-template-card
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

### Regenerating Cards:

When you add/remove zones, regenerate the cards:
```yaml
# In Developer Tools → Services
service: cleanme.regenerate_dashboard
```

Then copy the updated cards from `/config/dashboards/cleanme.yaml`.

---

## Method 3: Mixed Mode (External Dashboard Files)

**Best for**: Users who want to keep CleanMe separate from main dashboard.

### Setup Steps:

1. **Add dashboard reference** to `configuration.yaml`:
   ```yaml
   lovelace:
     mode: storage  # Keep storage mode for main dashboard
     dashboards:
       cleanme-dashboard:
         mode: yaml
         title: CleanMe Tidy Tracker
         icon: mdi:broom
         show_in_sidebar: true
         filename: dashboards/cleanme.yaml
   ```

2. **Restart Home Assistant**

3. **Dashboard auto-generates** at `/config/dashboards/cleanme.yaml`

4. **CleanMe appears in sidebar** as a separate dashboard

### Benefits:
- Main dashboard stays in storage mode (editable in UI)
- CleanMe dashboard is separate and auto-updating
- Best of both worlds!

---

## Method 4: Manual Integration (Copy-Paste Cards)

**Best for**: Users who want to add CleanMe cards to existing dashboards.

### Setup Steps:

1. **Generate cards** by calling the service:
   ```yaml
   service: cleanme.regenerate_dashboard
   ```

2. **Find generated YAML** at `/config/dashboards/cleanme.yaml`

3. **Copy individual cards** to your dashboard:
   - In UI mode: Edit dashboard → Add card → Manual card
   - In YAML mode: Copy card YAML into your view

4. **Update cards manually** when zones change

---

## 🎨 Required Custom Cards

All methods require these HACS custom cards:

### 1. Mushroom Cards
- **HACS**: Search "Mushroom"
- **GitHub**: `piitaya/lovelace-mushroom`
- **Install**: HACS → Frontend → Explore & Download Repositories

### 2. Card Mod
- **HACS**: Search "Card Mod"
- **GitHub**: `thomasloven/lovelace-card-mod`
- **Install**: HACS → Frontend → Explore & Download Repositories

**After installing custom cards:**
1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Refresh Home Assistant
3. Check cards appear correctly

---

## 🔧 Useful Services

### Regenerate Dashboard
Manually regenerate the dashboard YAML file:
```yaml
service: cleanme.regenerate_dashboard
```

### Check Dashboard Config
View current dashboard configuration in logs:
```yaml
# Enable debug logging in configuration.yaml:
logger:
  default: info
  logs:
    custom_components.cleanme: debug
```

---

## 📁 File Locations

| File | Location | Purpose |
|------|----------|---------|
| Auto-generated dashboard | `/config/dashboards/cleanme.yaml` | Contains all zone cards |
| Integration code | `/config/custom_components/cleanme/` | CleanMe integration files |
| Logs | `/config/cleanme.log` | CleanMe-specific logs |
| Main config | `/config/configuration.yaml` | Home Assistant configuration |
| UI dashboard | `/config/ui-lovelace.yaml` | Main dashboard (YAML mode only) |

---

## 🐛 Troubleshooting

### Dashboard not appearing
1. Check logs: `/config/cleanme.log` and Settings → System → Logs
2. Verify PyYAML is installed: `pip3 list | grep PyYAML`
3. Ensure at least one zone is configured
4. Try manually regenerating: `service: cleanme.regenerate_dashboard`

### Cards show as "Custom element doesn't exist"
1. Install Mushroom Cards via HACS
2. Install Card Mod via HACS
3. Clear browser cache (Ctrl+Shift+R)
4. Restart Home Assistant

### Cards show old data
1. Check entity names match your zones
2. Replace spaces with underscores: "Living Room" → `living_room`
3. Check entities exist: Settings → Devices & Services → Entities
4. Regenerate dashboard: `service: cleanme.regenerate_dashboard`

### YAML file not generating
1. Check permissions: `/config/dashboards/` should be writable
2. Ensure PyYAML is installed
3. Check logs for errors: `/config/cleanme.log`
4. Try creating directory manually: `mkdir /config/dashboards`

---

## 📝 Example Files

- `examples/configuration.yaml` - Configuration snippets
- `examples/ui-lovelace.yaml` - YAML mode example
- `examples/dashboard-example.yaml` - Generated dashboard example

---

## 🆘 Still Having Issues?

1. **Check logs**: `/config/cleanme.log` for detailed errors
2. **Enable debug logging** (see above)
3. **Open an issue**: [GitHub Issues](https://github.com/cozbox/cleanme/issues)
4. **Include**:
   - Your dashboard mode (storage/YAML/mixed)
   - Relevant logs from `/config/cleanme.log`
   - Home Assistant version
   - Steps to reproduce

---

**Made with 🧹 for Home Assistant**
