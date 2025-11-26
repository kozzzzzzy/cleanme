# Debugging CleanMe on Home Assistant OS

This guide covers CLI commands that work on **Home Assistant OS** (including installations on Proxmox, VM, or dedicated hardware). These commands are different from Docker or Core installations.

> **Key difference:** On HA OS, use `ha` CLI commands and config is at `/config/`, not `/homeassistant/` or other paths.

---

## Entity Registry (find entity IDs)

```bash
cat /config/.storage/core.entity_registry | grep -i <search_term>
```

Example - find all CleanMe entities:
```bash
cat /config/.storage/core.entity_registry | grep -i cleanme
```

---

## Config Entries (find integrations/zones)

```bash
cat /config/.storage/core.config_entries | grep -i <search_term>
```

---

## Device Registry (find devices)

```bash
cat /config/.storage/core.device_registry | grep -i <search_term>
```

---

## View HA Core Logs

```bash
ha core logs 2>&1 | tail -200
```

---

## Live Log Streaming

```bash
ha core logs -f 2>&1
```

---

## Filter Logs for Specific Integration

```bash
ha core logs 2>&1 | grep -i cleanme
```

---

## HA Core Info

```bash
ha core info
```

---

## Restart HA Core

```bash
ha core restart
```

---

## Check HA Supervisor Status

```bash
ha supervisor info
```

---

## List All Storage Files

```bash
ls -la /config/.storage/
```

---

## Pretty Print JSON (if jq installed)

```bash
cat /config/.storage/core.entity_registry | jq '.data.entities[] | select(.platform == "cleanme")'
```

---

## Check Custom Components

```bash
ls -la /config/custom_components/
```

---

## View CleanMe's Log File

CleanMe creates its own log file:

```bash
cat /config/cleanme.log
```

---

## Common Debugging Scenarios

### Entities not appearing

1. Check if entities are registered:
   ```bash
   cat /config/.storage/core.entity_registry | grep -i cleanme
   ```

2. Check CleanMe logs for errors:
   ```bash
   cat /config/cleanme.log | tail -100
   ```

3. Check HA core logs:
   ```bash
   ha core logs 2>&1 | grep -i cleanme
   ```

### Integration not loading

1. Check config entries:
   ```bash
   cat /config/.storage/core.config_entries | grep -i cleanme
   ```

2. Check for Python errors:
   ```bash
   ha core logs 2>&1 | grep -i "error\|exception" | tail -50
   ```

### Device not created

1. Check device registry:
   ```bash
   cat /config/.storage/core.device_registry | grep -i cleanme
   ```

---

## Important Notes

- **DO NOT** use commands meant for Docker installations (like `docker logs`)
- **DO NOT** look for config at `/homeassistant/` - it's at `/config/`
- The `ha` CLI is the primary tool for HA OS
- Storage files are JSON - use `grep` or `jq` to parse them
