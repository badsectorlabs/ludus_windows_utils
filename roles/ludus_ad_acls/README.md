# ludus_ad_acls

An Ansible role for [Ludus](https://ludus.cloud) that sets Active Directory ACL entries for building attack chains. Supports GOAD predefined attack paths and custom ACE definitions.

## Purpose

Configure AD object permissions (GenericAll, WriteDacl, ForceChangePassword, etc.) to create realistic attack paths in cyber range environments. Supports both the GOAD dataset and fully custom ACL entries.

## Requirements

- Windows Server 2019/2022 Domain Controller
- `ansible.windows` collection
- `community.windows` collection
- RSAT / AD PowerShell module

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_ad_acl_mode` | `"goad"` | Mode: `"goad"`, `"custom"`, or `"both"` |
| `ludus_ad_acl_domain` | `""` | Domain override (auto-detected if empty) |
| `ludus_ad_acl_hostname_override` | `""` | Hostname override for GOAD lookup |
| `ludus_ad_acl_entries` | `[]` | Custom ACL entries (see below) |

### Custom ACL Entry Format

```yaml
ludus_ad_acl_entries:
  - principal: "attacker.user"
    target: "victim.user"
    right: "GenericAll"
    target_type: "user"       # user, group, computer, ou, container
    well_known: false          # true for ANONYMOUS LOGON etc.
```

### Supported Rights

`GenericAll`, `GenericWrite`, `GenericRead`, `GenericExecute`, `WriteDacl`, `WriteOwner`, `WriteProperty`, `ReadProperty`, `ForceChangePassword`, `Self-Membership`

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
      - ludus_ad_acls
    role_vars:
      ludus_ad_acl_mode: "custom"
      ludus_ad_acl_entries:
        - principal: "svc_sql"
          target: "Domain Admins"
          target_type: "group"
          right: "GenericAll"
```

## Dependencies

None.

## Author

Bad Sector Labs
