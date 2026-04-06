# ludus_ad_password_policy

An Ansible role for [Ludus](https://ludus.cloud) that sets the Active Directory domain password policy. Supports weak GOAD presets and fully custom policy values.

## Purpose

Configure domain password policies for cyber range environments — typically weakened to allow lab accounts with simple passwords for attack scenarios (password spraying, Kerberoasting, etc.).

## Requirements

- Windows Server 2019/2022 Domain Controller
- `ansible.windows` collection
- `microsoft.ad` collection

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_password_policy_mode` | `"goad"` | Mode: `"goad"` (weak) or `"custom"` |
| `ludus_password_policy_min_length` | `7` | Minimum password length |
| `ludus_password_policy_complexity` | `true` | Require password complexity |
| `ludus_password_policy_lockout_threshold` | `5` | Account lockout threshold |
| `ludus_password_policy_lockout_duration` | `"00:30:00"` | Lockout duration |
| `ludus_password_policy_lockout_observation` | `"00:30:00"` | Lockout observation window |
| `ludus_password_policy_history_count` | `24` | Password history count |
| `ludus_password_policy_max_age_days` | `90` | Maximum password age (days) |
| `ludus_password_policy_min_age_days` | `1` | Minimum password age (days) |
| `ludus_password_policy_force_replication` | `true` | Force AD replication after change |

### GOAD Preset Values

When `ludus_password_policy_mode: "goad"`:
- Min length: 5, Complexity: disabled, Lockout: 5 attempts / 5 min, No history, No max age

## Example Ludus Range Config

```yaml
ludus:
  - vm_name: "{{ range_id }}-DC01"
    hostname: dc01
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: lab.local
      role: primary-dc
    roles:
      - ludus_ad_password_policy
    role_vars:
      ludus_password_policy_mode: "custom"
      ludus_password_policy_min_length: 1
      ludus_password_policy_complexity: false
      ludus_password_policy_lockout_threshold: 0
```

## Ludus Notes

- Run this role **before** `ludus_bulk_ad_content` so users can be created with weak passwords
- GOAD mode auto-applies the weak policy matching the original GOAD project

## Dependencies

None.

## Author

Bad Sector Labs
