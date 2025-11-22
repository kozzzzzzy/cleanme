# CleanMe Dashboard Examples

This directory contains example configuration files for setting up the CleanMe dashboard in various Home Assistant configurations.

## 📁 Files in This Directory

### `dashboard-example.yaml`
**Purpose**: Complete example of what the auto-generated dashboard looks like.

**Usage**:
- Shows the structure of a CleanMe dashboard view
- Includes example cards for Kitchen and Living Room zones
- Can be used as a template for manual dashboard creation

**Note**: This is just an example. The integration automatically generates `/config/dashboards/cleanme.yaml` with your actual zones.

---

### `configuration.yaml`
**Purpose**: Example configuration snippets for `configuration.yaml`.

**Usage**:
- Shows how to set up YAML mode dashboards
- Shows how to reference the auto-generated dashboard file
- Includes optional automation examples
- Copy relevant sections to your own `configuration.yaml`

**Includes**:
- Lovelace dashboard configuration
- Dashboard registration for mixed mode
- Automation to regenerate dashboard on startup
- Script to export dashboard manually

---

### `ui-lovelace.yaml`
**Purpose**: Example for users who use YAML mode for their main dashboard.

**Usage**:
- Complete example dashboard file structure
- Shows where to add the CleanMe view
- Includes placeholder instructions for adding zone cards
- Merge with your existing `ui-lovelace.yaml`

**Who should use this**:
- Users with `lovelace: mode: yaml` in their `configuration.yaml`
- Users who edit their entire dashboard via YAML files

---

### `lovelace-resources.yaml`
**Purpose**: Shows how to load required custom card resources.

**Usage**:
- Examples for both YAML mode and Storage mode
- Shows correct URLs for Mushroom Cards and Card Mod
- Instructions for adding resources via UI or YAML

**Required custom cards**:
- Mushroom Cards (`piitaya/lovelace-mushroom`)
- Card Mod (`thomasloven/lovelace-card-mod`)

---

## 🚀 Quick Start

**Most users should follow these steps:**

1. **Install custom cards** via HACS:
   - Mushroom Cards
   - Card Mod

2. **Add CleanMe zones** via Settings → Devices & Services

3. **Dashboard auto-appears** in your sidebar!

That's it! No manual configuration needed for Storage mode users.

---

## 📋 Configuration Modes

### Mode 1: Storage (Default) - No Examples Needed!
**Who**: Default Home Assistant users  
**Setup**: None! Dashboard appears automatically in sidebar  
**Files Needed**: None

### Mode 2: YAML Mode
**Who**: Users with `lovelace: mode: yaml`  
**Setup**: See `ui-lovelace.yaml` example  
**Files Needed**: `ui-lovelace.yaml`

### Mode 3: Mixed Mode
**Who**: Users who want CleanMe separate from main dashboard  
**Setup**: See `configuration.yaml` example  
**Files Needed**: `configuration.yaml`

### Mode 4: Manual Cards
**Who**: Users who want to manually add cards to existing dashboards  
**Setup**: See `dashboard-example.yaml` for card structure  
**Files Needed**: Copy cards from `/config/dashboards/cleanme.yaml`

---

## 🔧 Auto-Generated Files

When you add zones, CleanMe automatically creates:

### `/config/dashboards/cleanme.yaml`
- Complete dashboard view with all your zones
- Updates automatically when you add/remove zones
- Can be referenced in `configuration.yaml` or copied to other dashboards

### `/config/dashboards/cleanme-basic.yaml` (optional)
- Generated when you call `cleanme.export_basic_dashboard` service
- Uses standard entities cards (no custom cards required)
- Fallback option if you haven't installed Mushroom/Card Mod

---

## 📖 Documentation

For detailed setup instructions, see:
- **[QUICK_START.md](../QUICK_START.md)** - 5-minute setup guide
- **[DASHBOARD_SETUP.md](../DASHBOARD_SETUP.md)** - Comprehensive guide for all modes
- **[README.md](../README.md)** - Main integration documentation

---

## 🆘 Need Help?

1. Check the documentation files above
2. Look at `/config/cleanme.log` for errors
3. Open an issue: https://github.com/cozbox/cleanme/issues

---

**Example files are provided as-is for reference. Your actual setup may vary based on your Home Assistant configuration.**
