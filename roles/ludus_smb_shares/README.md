# ludus_smb_shares

An Ansible role for [Ludus](https://ludus.cloud) that creates SMB shares with configurable permissions. Supports anonymous/null session access via guest account activation and GOAD preset configurations.

## Purpose

Deploy SMB shares in cyber range environments for practicing share enumeration, NTLM relay to writable shares, anonymous access exploitation, and lateral movement techniques.

## Requirements

- Windows Server 2019/2022
- `ansible.windows` collection
- `community.windows` collection

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_smb_shares_mode` | `"custom"` | Mode: `"custom"` or `"goad"` |
| `ludus_smb_shares` | `[]` | List of shares to create (custom mode) |
| `ludus_smb_shares_hostname_override` | `""` | Hostname override for GOAD lookup |

### Share Definition Format

```yaml
ludus_smb_shares:
  - name: "public"
    path: "C:\\shares\\public"
    description: "Public share"
    full_access:
      - "Everyone"
    read_access: []
    change_access: []
    no_access: []
    allow_anonymous: true   # Enable null session access
```

## Example Ludus Range Config

### Custom shares

```yaml
ludus:
  - vm_name: "{{ range_id }}-SRV01"
    hostname: srv01
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 11
    domain:
      fqdn: lab.local
      role: member
    roles:
      - ludus_smb_shares
    role_vars:
      ludus_smb_shares:
        - name: "Public"
          path: "C:\\Shares\\Public"
          full_access:
            - "Everyone"
          description: "Public file share"
          allow_anonymous: true
        - name: "IT"
          path: "C:\\Shares\\IT"
          full_access:
            - "LAB\\Domain Admins"
          read_access:
            - "LAB\\Domain Users"
```

### GOAD mode

```yaml
    roles:
      - ludus_smb_shares
    role_vars:
      ludus_smb_shares_mode: "goad"
```

## GOAD Preset Shares

| Hostname | Shares |
|---|---|
| castelblack | `all` (Domain Users RW), `public` (anonymous read) |
| braavos | `all` (Domain Users RW), `CertEnroll` |
| winterfell | `SYSVOL` |
| kingslanding | `SYSVOL` |
| meereen | `SYSVOL` |

## Ludus Notes

- Shares with `allow_anonymous: true` activate the Guest account and configure null session registry keys
- The role verifies domain secure channel health before resolving domain principals (resilient after reboots from other roles)

## Dependencies

None.

## Author

Bad Sector Labs
