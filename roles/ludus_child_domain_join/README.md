# ludus_child_domain_join

An Ansible role for Ludus that joins a Windows machine to an existing child domain.

## Purpose

This role joins a Windows Server or Workstation to a **child domain** (e.g., `north.sevenkingdoms.local`) that was created using the `ludus_child_domain` role.

## Requirements

- **Ansible Collections**: `microsoft.ad` >= 1.3.0
- **OS Support**: Windows Server 2016, 2019, 2022; Windows 10/11
- **Ludus**: Tested with Ludus 1.5+
- **Child Domain**: Must have a working child domain DC already deployed

## Role Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ludus_child_domain_fqdn` | FQDN of the child domain to join | `north.sevenkingdoms.local` |
| `ludus_child_dc_ip` | IP address of the child domain DC | `10.2.10.11` |
| `ludus_parent_domain_fqdn` | FQDN of the parent/root domain | `sevenkingdoms.local` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ludus_domain_admin_user` | Parent domain admin (UPN format) | `defaults.ad_domain_admin@parent_fqdn` |
| `ludus_domain_admin_password` | Parent domain admin password | `defaults.ad_domain_admin_password` |

**Note:** This role uses the **parent domain's Enterprise Admin** credentials to join machines to the child domain. Enterprise Admins from the forest root can join machines to any domain in the forest.

## Dependencies

- `ludus_child_domain` role must have been run to create the child domain first

## Example Ludus Range Config

```yaml
ludus:
  # Parent Domain Controller
  - vm_name: "{{ range_id }}-DC01"
    hostname: kingslanding
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    ram_gb: 8
    cpus: 4
    windows:
      sysprep: false
    domain:
      fqdn: sevenkingdoms.local
      role: primary-dc

  # Child Domain Controller
  - vm_name: "{{ range_id }}-DC02"
    hostname: winterfell
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 11
    ram_gb: 8
    cpus: 4
    windows:
      sysprep: true
    roles:
      - ludus_child_domain
    role_vars:
      ludus_child_domain_fqdn: north.sevenkingdoms.local
      ludus_parent_domain_fqdn: sevenkingdoms.local
      ludus_parent_dc_ip: "10.{{ range_second_octet }}.10.10"

  # Member Server in Child Domain
  - vm_name: "{{ range_id }}-SRV02"
    hostname: castelblack
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 12
    ram_gb: 6
    cpus: 2
    windows:
      sysprep: true
    roles:
      - ludus_child_domain_join
    role_vars:
      ludus_child_domain_fqdn: north.sevenkingdoms.local
      ludus_child_dc_ip: "10.{{ range_second_octet }}.10.11"
      ludus_parent_domain_fqdn: sevenkingdoms.local
```

## How It Works

1. **Configures DNS** - Points to the child domain DC
2. **Joins Domain** - Uses `microsoft.ad.membership` with retry logic (10 retries, 60s delay)

## Idempotency

This role is idempotent:
- `microsoft.ad.membership` checks current domain membership state
- Skips join if already a member of the specified domain

## Ludus Notes

- The child domain DC must be deployed before this role runs
- Ludus processes VMs in config order, so place child DC before member servers
- Uses Ludus default credentials unless overridden

## Troubleshooting

### Error: Domain join failed after retries

1. Ensure child domain DC is fully deployed and ADWS is running
2. Verify DNS can resolve the child domain FQDN
3. Check network connectivity to the child DC (port 389, 636, etc.)

### Error: Authentication failed

Ensure credentials use UPN format: `domainadmin@north.sevenkingdoms.local`

## Author

RodSec Labs / Bad Sector Labs
