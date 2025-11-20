# CleanMe – Tidy Task Tracker

Look at a room. Ask an AI what needs tidying. Get a checklist in Home Assistant.

CleanMe is a Home Assistant custom integration that:

- Takes a snapshot from any `camera.*` entity
- Sends it to an AI vision model (OpenAI / Claude / Gemini / OpenRouter / custom)
- Asks **"Is there anything to tidy here? If yes, give me a short checklist."**
- Exposes sensors for:
  - Overall tidy status
  - Task count
  - Last analysed time


See `custom_components/cleanme` for the integration code.

## Installation

### HACS (Custom Repository)
- In HACS, add this repository as a **Custom Repository** with category **Integration**.
- Install the integration, then restart Home Assistant so the new components load.

### Manual
- Copy the `custom_components/cleanme` folder into your Home Assistant `custom_components` directory.
- Restart Home Assistant after copying so the integration is discovered.

### Troubleshooting
- If the config flow page fails to load, check **Settings → System → Logs** for messages from `custom_components.cleanme` and share them when reporting issues.
- After updating the integration, always restart Home Assistant so the refreshed files and translations are used.
