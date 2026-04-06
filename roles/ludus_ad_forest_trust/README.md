# ludus_ad_forest_trust

An Ansible role for [Ludus](https://ludus.cloud) that creates bidirectional Active Directory forest trusts with DNS conditional forwarders. Optionally enables SID history on the trust for migration/attack scenarios.

## Purpose

Establish trust relationships between AD forests in multi-domain cyber range topologies, enabling cross-forest attack paths (e.g., GOAD's sevenkingdoms.local ↔ essos.local trust).

## Requirements

- Windows Server 2019/2022 Domain Controller
- `ansible.windows` collection
- Both forests must be reachable (same VLAN or routed)

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_trust_domain_admin` | Ludus default | Domain admin username |
| `ludus_trust_domain_admin_password` | Ludus default | Domain admin password |
| `ludus_trust_partner_domain` | `""` | Partner domain FQDN (required) |
| `ludus_trust_partner_dc_ip` | `""` | Partner DC IP address (required) |
| `ludus_dns_forward_zone` | `""` | DNS conditional forwarder zone |
| `ludus_dns_forward_server` | `""` | DNS conditional forwarder target IP |
| `ludus_enable_sid_history` | `false` | Enable SID history on the trust |
| `ludus_cross_domain_group_members` | `[]` | Cross-domain group memberships to create |

### Cross-Domain Group Members Format

```yaml
ludus_cross_domain_group_members:
  - group: "AcrossTheNarrowSea"
    members:
      - "essos.local\\daenerys.targaryen"
```

## Example Ludus Range Config

```yaml
ludus:
  - vm_name: "{{ range_id }}-DC01"
    hostname: kingslanding
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: sevenkingdoms.local
      role: primary-dc
    roles:
      - name: ludus_ad_forest_trust
        depends_on:
          - vm_name: "{{ range_id }}-DC03"
            role: primary-dc
    role_vars:
      ludus_trust_partner_domain: essos.local
      ludus_trust_partner_dc_ip: "10.{{ range_second_octet }}.10.13"
      ludus_dns_forward_zone: essos.local
      ludus_dns_forward_server: "10.{{ range_second_octet }}.10.13"
      ludus_enable_sid_history: true
```

## Ludus Notes

- Use `depends_on` in range configs to ensure the partner DC is fully promoted before trust creation
- This role is **not idempotent** on re-run if the trust already exists — use `--only-roles` to skip on redeployments
- DNS conditional forwarders are created automatically for cross-forest name resolution

## Dependencies

None.

## Author

Bad Sector Labs
