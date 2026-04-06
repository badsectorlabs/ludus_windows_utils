# ludus_ad_laps

An Ansible role for [Ludus](https://ludus.cloud) that configures Microsoft LAPS (Local Administrator Password Solution). Handles DC-side setup (schema extension, GPO, OU delegation) and client-side MSI installation.

## Purpose

Deploy LAPS in cyber range environments so security practitioners can practice LAPS password extraction, DACL enumeration, and privilege escalation via LAPS reader abuse.

## Requirements

- Windows Server 2019/2022
- `ansible.windows` collection
- `community.windows` collection
- Domain Controller for schema/GPO tasks, or member server for client-only mode

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_laps_domain_admin` | Ludus default | Domain admin username |
| `ludus_laps_domain_admin_password` | Ludus default | Domain admin password |
| `ludus_laps_domain_fqdn` | `""` | Domain FQDN override (auto-detected) |
| `ludus_laps_msi_url` | Microsoft official URL | LAPS MSI download URL |
| `ludus_laps_ou` | `""` | Target OU for LAPS-managed computers |
| `ludus_laps_gpo_name` | `"LAPS Policy"` | GPO name for LAPS settings |
| `ludus_laps_readers` | `[]` | Users/groups granted LAPS read permission |
| `ludus_laps_client_only` | `false` | Install client only (for member servers) |

## Example Ludus Range Config

```yaml
ludus:
  - vm_name: "{{ range_id }}-SRV03"
    hostname: braavos
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 14
    domain:
      fqdn: essos.local
      role: member
    roles:
      - ludus_ad_laps
    role_vars:
      ludus_laps_ou: "OU=Laps,DC=essos,DC=local"
      ludus_laps_readers:
        - jorah.mormont
        - Spys
```

## Ludus Notes

- On DCs: extends schema, creates GPO, sets OU delegation
- On members (`ludus_laps_client_only: true`): installs LAPS MSI and moves computer to target OU
- Uses `hostvars[inventory_hostname]['ludus_domain_fqdn']` for safe cross-VM delegation context

## Dependencies

None.

## Author

Bad Sector Labs
