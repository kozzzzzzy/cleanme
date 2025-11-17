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
