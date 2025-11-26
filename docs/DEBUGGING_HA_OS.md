# Debugging CleanMe on Home Assistant OS

This guide covers CLI commands that work on **Home Assistant OS** (including installations on Proxmox, VM, or dedicated hardware). These commands are different from Docker or Core installations.

> **Key difference:** On HA OS, use `ha` CLI commands and config is at `/config/`, not `/homeassistant/` or other paths.

---

## Entity Registry (find entity IDs)

```bash
cat /config/.storage/core.entity_registry | grep -i cleanme
```
