# ludus_ad_group_add_member

Adds an existing AD group to be a member of another existing AD Group.

## Features

- Fully idempotent - safe to run multiple times

## Requirements

- **Target: Domain Controller only**
- Windows Server 2019/2022
- Collections:
  - `ansible.windows` >= 1.0.0
  - `community.windows` >= 1.0.0

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_ad_group_add_member_items` | `[]` | List of items containing a group to add a group to  |

### ludus_ad_group_add_member_items Structure

```yaml
ludus_ad_group_add_member_items:
    # Add custom group `Server Admins` to be a member of custom group `Global Admins` located at path `OU=Domain Groups,OU=Company,DC=corp,DC=local`
    - parent_group: Global Admins
      path: OU=Domain Groups,OU=Company,DC=corp,DC=local
      child_group: CN=Server Admins,OU=Domain Groups,OU=Company,DC=corp,DC=local
    # Add custom group `Workstation Admins` to be a member of custom group `Global Admins` located at path `OU=Domain Groups,OU=Company,DC=corp,DC=local`
    - parent_group: Global Admins
      path: OU=Domain Groups,OU=Company,DC=corp,DC=local
      child_group: CN=Workstation Admins,OU=Domain Groups,OU=Company,DC=corp,DC=local
    # Add custom group `Global Admins` to be a member of built-in group `Domain Admins`
    - parent_group: Domain Admins
      child_group: CN=Global Admins,OU=Domain Groups,OU=Company,DC=corp,DC=local
```

## Example Ludus Range Config

```yaml
ludus:
  - vm_name: "{{ range_id }}-dc01"
    hostname: "dc01"
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    ram_gb: 8
    cpus: 4
    windows:
      sysprep: false
    domain:
      fqdn: corp.local
      role: primary-dc
    roles:
      - name: badsectorlabs.ludus_windows_utils.ludus_bulk_ad_content
      - name: badsectorlabs.ludus_windows_utils.ludus_ad_group_add_member
    role_vars:
      ludus_ad_content_mode: custom
      ludus_organisation_units:
        - name: Company
          path: DC=corp,DC=local
        - name: Domain Groups
          path: OU=Company,DC=corp,DC=local
      ludus_groups:
        global:
          - name: Global Admins
            path: OU=Domain Groups,OU=Company,DC=corp,DC=local
          - name: Server Admins
            path: OU=Domain Groups,OU=Company,DC=corp,DC=local
          - name: Workstation Admins
            path: OU=Domain Groups,OU=Company,DC=corp,DC=local
          - name: Standard Users
            path: OU=Domain Groups,OU=Company,DC=corp,DC=local
      ludus_ad_group_add_member_items:
        - parent_group: Global Admins
          path: OU=Domain Groups,OU=Company,DC=corp,DC=local
          child_group: CN=Server Admins,OU=Domain Groups,OU=Company,DC=corp,DC=local
        - parent_group: Global Admins
          path: OU=Domain Groups,OU=Company,DC=corp,DC=local
          child_group: CN=Workstation Admins,OU=Domain Groups,OU=Company,DC=corp,DC=local
        - parent_group: Domain Admins
          child_group: CN=Global Admins,OU=Domain Groups,OU=Company,DC=corp,DC=local
```

## How It Works

This role uses ansible `microsoft.ad.group` and iterates over the provided list to setup group memberships.

## Testing

After running the role, verify with powershell that the groups contain the member/s:

```
Get-LocalGroupMember -Group "Global Admins"
Get-LocalGroupMember -Group "Domain Admins"
```
