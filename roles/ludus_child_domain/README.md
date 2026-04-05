# ludus_child_domain

An Ansible role for Ludus that creates an Active Directory child domain using the `microsoft.ad.domain_child` module.

## Purpose

This role promotes a Windows Server to a domain controller for a new **child domain** under an existing parent domain. For example, creating `north.sevenkingdoms.local` as a child of `sevenkingdoms.local`.

## Requirements

- **Ansible Collections**: `microsoft.ad` >= 1.6.0 (for `domain_child` module)
- **OS Support**: Windows Server 2016, 2019, 2022
- **Ludus**: Tested with Ludus 1.5+
- **Parent Domain**: Must have a working parent domain with a primary DC already deployed

### Installing Required Collection

If your Ludus server has `microsoft.ad` < 1.6.0, update it:

```bash
ludus ansible collections add microsoft.ad --version 1.8.1
```

## Role Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ludus_child_domain_fqdn` | FQDN of the child domain to create | `north.sevenkingdoms.local` |
| `ludus_parent_domain_fqdn` | FQDN of the parent domain | `sevenkingdoms.local` |
| `ludus_parent_dc_ip` | IP address of the parent DC | `10.2.10.10` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ludus_domain_admin_user` | Parent domain admin (UPN format) | `defaults.ad_domain_admin@parent_fqdn` |
| `ludus_domain_admin_password` | Parent domain admin password | `defaults.ad_domain_admin_password` |
| `ludus_safe_mode_password` | DSRM password | `defaults.ad_domain_safe_mode_password` |
| `ludus_create_dns_delegation` | Create DNS delegation in parent | `true` |

### Ludus-Provided Variables

The following variables are automatically available:

- `ansible_host` - The IP address of the current VM
- `defaults.ad_domain_admin` - The default domain admin username (default: `domainadmin`)
- `defaults.ad_domain_admin_password` - The default domain admin password
- `defaults.ad_domain_safe_mode_password` - The default safe mode password
- `ludus_dns_server` - The .254 of this VM's VLAN

## Dependencies

None (uses built-in Ludus variables).

## Example Ludus Range Config

```yaml
ludus:
  # Parent Domain Controller (must be deployed first)
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
```

## How It Works

1. **Installs AD DS** - Installs Active Directory Domain Services and RSAT tools
2. **Configures DNS** - Sets DNS servers to parent DC IP and self (for AD registration)
3. **Creates Child Domain** - Uses `microsoft.ad.domain_child` to promote the server
4. **Waits for ADWS** - Ensures AD Web Services are running after reboot

## Idempotency

This role is idempotent:
- `win_feature` skips if features already installed
- `microsoft.ad.domain_child` skips if server is already a DC for the specified domain

## Ludus Notes

- The parent domain controller must be fully deployed before this role runs
- Ludus automatically handles the ordering when using the native `domain:` block for the parent DC
- Use `sysprep: true` for the child DC VM to ensure a unique SID
- The role uses Ludus default credentials unless overridden in `role_vars`

## Troubleshooting

### Error: DCPromo exited with 77

This usually means the parent domain cannot be contacted. Check:
1. Parent DC is fully deployed and AD services are running
2. DNS is correctly pointing to the parent DC
3. Network connectivity between VMs (check VLAN rules)

### Error: Authentication failed

Ensure you're using UPN format for credentials: `domainadmin@domain.fqdn` (not `DOMAIN\user`).

## License

MIT

## Author

RodSec Labs / Bad Sector Labs
