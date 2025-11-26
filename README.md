# CleanMe – AI Tidy Task Tracker

**Transform your Home Assistant into an intelligent home cleaning assistant!**

CleanMe uses Google's Gemini AI to analyze camera snapshots of your rooms and provide actionable tidying checklists. It's like having a helpful (and configurable) housemate who keeps an eye on your spaces.

## 🌟 Features

- 🤖 **Gemini AI Integration** - Advanced vision AI for accurate room analysis
- 🎭 **5 AI Personalities** - Choose how your AI "judges" your space (Chill, Thorough, Strict, Sarcastic, Professional)
- 🎚️ **Adjustable Pickiness** - 1-5 scale from lenient to perfectionist
- 📸 **Camera Integration** - Works with any Home Assistant camera entity
- ⏰ **Flexible Scheduling** - Manual, 1x, 2x, or 4x daily automatic checks
- 📊 **Rich Sensors** - Binary status, task lists, timestamps, and metadata
- 🎯 **Actionable Tasks** - Get specific, practical checklists for each room
- 🔧 **Service Actions** - Request checks, snooze zones, clear tasks programmatically
- 🎨 **Auto-Generated Dashboard** - Beautiful Lovelace UI cards for all your zones
- 📋 **Automation Blueprints** - Pre-built automations for daily summaries, alerts, and more

## 📋 Requirements

- **Home Assistant** 2024.6.0 or newer
- **Camera entity** for each room you want to monitor
- **Gemini API key** from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **HACS** (optional but recommended) for easy installation

### Optional (for dashboard)
- **Bubble Card** - For beautiful dashboard cards ([HACS](https://github.com/Clooos/Bubble-Card))

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant
2. Go to **Integrations**
3. Click the **⋮** menu (top right) → **Custom repositories**
4. Add `https://github.com/cozbox/cleanme` as an **Integration**
5. Click **Download** on the CleanMe card
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/cozbox/cleanme/releases)
2. Extract and copy the `custom_components/cleanme` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## ⚙️ Setup

### 1. Get a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy your key (keep it secure!)

**Cost Note:** Gemini API has generous free tier limits. Typical usage for home monitoring is well within free limits.

### 2. Add Your First Zone

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **CleanMe**
4. Fill in the configuration:
   - **Zone name**: e.g., "Kitchen", "Living Room"
   - **Camera entity**: Select from your existing cameras
   - **AI Personality**: Choose your preferred style
     - 😊 **Chill** - Relaxed, only flags obvious mess
     - 🤓 **Thorough** - Balanced, helpful approach (recommended)
     - 😤 **Strict** - Critical, demanding standards
     - 🤪 **Sarcastic** - Funny, entertaining feedback
     - 💼 **Professional** - Formal, business-like
   - **Pickiness level**: 1 (lenient) to 5 (perfectionist)
   - **Check frequency**: How often to auto-check
     - Manual only
     - 1x daily
     - 2x daily
     - 4x daily
   - **Gemini API key**: Paste your key

5. Click **Submit**

### 3. Repeat for More Zones

Add as many zones as you want! Each zone is independent and can have different settings.

## 📊 Entities Created

For each zone named "Kitchen", CleanMe creates:

### Binary Sensor: `binary_sensor.kitchen_tidy`
- **ON** (Green) = Room is tidy
- **OFF** (Red) = Room needs attention
- **Attributes:**
  - `personality`: AI personality used
  - `pickiness`: Pickiness level
  - `camera_entity`: Camera being monitored
  - `last_check`: Timestamp of last check
  - `snooze_until`: If snoozed, when it resumes

### Sensor: `sensor.kitchen_tasks`
- **State**: Number of tasks (0-99)
- **Attributes:**
  - `tasks`: List of task strings
  - `comment`: AI's overall comment
  - `full_analysis`: Complete JSON response from Gemini

### Sensor: `sensor.kitchen_last_check`
- **State**: Timestamp of last check
- **Attributes:**
  - `status`: "success" or "error"
  - `error_message`: If check failed
  - `image_size`: Size of captured image (bytes)
  - `api_response_time`: API latency (seconds)

## 🔧 Services

### `cleanme.request_check`
Trigger an immediate check of a zone.

```yaml
service: cleanme.request_check
data:
  zone: Kitchen
```

### `cleanme.snooze_zone`
Pause automatic checks for a specified duration.

```yaml
service: cleanme.snooze_zone
data:
  zone: Kitchen
  duration_minutes: 60
```

### `cleanme.clear_tasks`
Manually mark a zone as tidy and clear all tasks.

```yaml
service: cleanme.clear_tasks
data:
  zone: Kitchen
```

### `cleanme.add_zone`
Dynamically add a new zone (advanced users).

```yaml
service: cleanme.add_zone
data:
  name: Bedroom
  camera_entity: camera.bedroom_cam
  personality: thorough
  pickiness: 3
  check_frequency: 1x
  api_key: YOUR_API_KEY
```

## 🎨 Dashboard

CleanMe automatically creates a beautiful dashboard for all your zones! The dashboard shows:

- Zone status with color-coded indicators
- Current task count
- AI comments
- Quick action buttons (Check Now, Mark Done, Snooze)
- Last check timestamp

### 🚀 Quick Dashboard Setup

**For most users (Storage Mode):**
1. Install CleanMe via HACS
2. Install required custom card: [Bubble Card](https://github.com/Clooos/Bubble-Card)
3. Add your first zone via Settings → Integrations
4. Go to Settings → Dashboards → Add dashboard → Choose YAML → Select `/config/dashboards/cleanme.yaml`
5. Pin it to your sidebar! 🎉

**For YAML mode users:**
Add to `configuration.yaml`:
```yaml
lovelace:
  dashboards:
    cleanme-dashboard:
      mode: yaml
      title: CleanMe
      icon: mdi:broom
      show_in_sidebar: true
      filename: dashboards/cleanme.yaml
```

### 📚 Complete Dashboard Guide

**Need help?** See the complete dashboard setup guide:
- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
- **[DASHBOARD_SETUP.md](DASHBOARD_SETUP.md)** - Detailed guide for all configuration modes

### Dashboard Files Generated

The integration automatically creates:
- `/config/dashboards/cleanme.yaml` - Auto-generated dashboard YAML
- Cards update automatically when you add/remove zones

### Manual Card Example

If you want to manually create cards:

```yaml
type: custom:bubble-card
card_type: button
entity: binary_sensor.kitchen_tidy
name: Kitchen
icon: mdi:home
show_state: true
show_last_changed: true
sub_button:
  - name: Check
    icon: mdi:camera-iris
    show_background: false
    tap_action:
      action: call-service
      service: cleanme.request_check
      service_data:
        zone: Kitchen
  - name: Done
    icon: mdi:check-bold
    show_background: false
    tap_action:
      action: call-service
      service: cleanme.clear_tasks
      service_data:
        zone: Kitchen
```
  red
  {% endif %}
tap_action:
  action: more-info
```

### Regenerate Dashboard

To manually regenerate the dashboard YAML:
```yaml
service: cleanme.regenerate_dashboard
```

## 🤖 Automation Examples

### Example 1: Daily Summary Notification

```yaml
automation:
  - alias: "CleanMe Daily Summary"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "🏠 Daily Tidy Summary"
          message: >
            {% set tidy = states.binary_sensor 
               | selectattr('entity_id', 'search', '_tidy$')
               | selectattr('state', 'eq', 'on') | list | count %}
            {% set messy = states.binary_sensor 
               | selectattr('entity_id', 'search', '_tidy$')
               | selectattr('state', 'eq', 'off') | list | count %}
            Tidy: {{ tidy }} | Needs attention: {{ messy }}
```

### Example 2: Auto-Check on Arriving Home

```yaml
automation:
  - alias: "Check rooms when arriving home"
    trigger:
      - platform: state
        entity_id: person.you
        to: home
    action:
      - service: cleanme.request_check
        data:
          zone: Kitchen
      - service: cleanme.request_check
        data:
          zone: Living Room
```

### Example 3: Alert on Messy Room

```yaml
automation:
  - alias: "Alert when kitchen gets messy"
    trigger:
      - platform: state
        entity_id: binary_sensor.kitchen_tidy
        from: "on"
        to: "off"
    condition:
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Kitchen needs tidying"
          message: "{{ state_attr('sensor.kitchen_tasks', 'comment') }}"
```

## 🎁 Automation Blueprints

CleanMe includes pre-built automation blueprints in `blueprints/automations/`:

1. **daily_summary.yaml** - Daily tidy summary at customizable time
2. **morning_check.yaml** - Auto-check all zones every morning
3. **messy_alert.yaml** - Notification when room goes from tidy to messy
4. **weekly_deep.yaml** - Weekly comprehensive report

Import these via **Settings** → **Automations & Scenes** → **Blueprints** → **Import Blueprint**.

## 🐛 Troubleshooting

> **Running Home Assistant OS?** See the dedicated [HA OS Debugging Guide](docs/DEBUGGING_HA_OS.md) for CLI commands specific to HA OS (including Proxmox VMs).

### Config flow won't load
- Check **Settings** → **System** → **Logs** for errors from `custom_components.cleanme`
- Restart Home Assistant after installing or updating

### "Invalid API key" error
- Verify your Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
- Ensure you have the Gemini API enabled
- Check for typos or extra spaces in the key

### Camera image fails
- Verify camera entity is working: check the camera feed in HA
- Ensure camera provides JPEG images
- Check camera entity permissions

### AI gives weird results
- Try adjusting personality and pickiness levels
- Some cameras have poor lighting - adjust camera position/settings
- Manual checks work better than automatic during problem diagnosis

### Gemini API rate limits
- Free tier: 15 requests per minute, 1500 per day
- Reduce check frequency if hitting limits
- Consider upgrading API plan for heavy use

## 💰 Cost Estimates

Gemini API pricing (subject to change):
- **Free tier**: Very generous limits for personal use
- Typical home usage: 2-4 checks/day × 3 rooms = **6-12 requests/day**
- Well within free tier limits for most users

Check current pricing: [Google AI Pricing](https://ai.google.dev/pricing)

## 🔒 Privacy & Security

- Images are sent to Google Gemini API for analysis
- No images are stored by CleanMe
- API keys are stored securely in Home Assistant
- Consider local deployment if privacy is critical

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

- Built with ❤️ by [@cozbox](https://github.com/cozbox)
- Powered by Google Gemini AI
- Inspired by the Home Assistant community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/cozbox/cleanme/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cozbox/cleanme/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/cozbox/cleanme/wiki)

---

**Made with 🧹 for Home Assistant**
