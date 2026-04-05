# ludus_bulk_ad_content

Bulk Active Directory content creation with **three operation modes**: embedded GOAD dataset, custom user-provided data, or randomized generation.

## Features

- **Three modes**: `goad`, `custom`, `random`
- Auto-detects domain name from host (or override via variable)
- Creates OUs, groups (global, domain-local, universal), and users
- Configures domain password policy (weak by default for labs)
- Sets SPNs, group memberships, and managed_by attributes
- Supports cross-domain group members (requires trust to be established)
- Random mode uses Faker for realistic names, falls back to simple random if unavailable

## Requirements

- **Target: Domain Controller only** (already promoted)
- Windows Server 2019/2022
- `microsoft.ad` collection: `ansible-galaxy collection install microsoft.ad`
- WinRM connectivity
- For random mode: Python 3.x on **Ludus server** (Faker auto-installed in virtualenv)

## Deployment Target

This role **must run on Domain Controllers**. It creates AD objects (users, groups, OUs) and modifies domain password policy, which requires the AD PowerShell module available on DCs.

**GOAD Deployment Example:**

| VM | Hostname | Domain | Run this role? |
|---|---|---|---|
| dc01 | kingslanding | sevenkingdoms.local | ✅ Yes |
| dc02 | winterfell | north.sevenkingdoms.local | ✅ Yes |
| dc03 | meereen | essos.local | ✅ Yes |
| srv02 | castelblack | north.sevenkingdoms.local | ❌ No (member server) |
| srv03 | braavos | essos.local | ❌ No (member server) |

Each DC runs the role once with its respective domain data. The domain is auto-detected from the host, or explicitly set via `ludus_domain_name`.

## Modes

### Mode: `goad` (default)

Uses the embedded GOAD (Game of Active Directory) dataset. Works out-of-box for GOAD lab deployments.

```yaml
role_vars:
  ludus_ad_content_mode: "goad"
  # Domain is auto-detected, or set explicitly:
  # ludus_domain_name: "sevenkingdoms.local"
```

**Supported GOAD domains:**
- `sevenkingdoms.local` — 11 users, 6 groups, 8 OUs
- `north.sevenkingdoms.local` — 12 users, 4 groups, 0 OUs  
- `essos.local` — 7 users, 7 groups, 0 OUs

### Mode: `custom`

Provide your own AD content via `role_vars`.

```yaml
role_vars:
  ludus_ad_content_mode: "custom"
  ludus_password_policy:
    min_password_length: 8
    password_complexity: true
    lockout_threshold: 5
    lockout_duration: "00:30:00"
    lockout_observation: "00:30:00"
  ludus_organisation_units:
    - name: IT
      path: "DC=corp,DC=local"
    - name: HR
      path: "DC=corp,DC=local"
  ludus_groups:
    global:
      - name: IT-Staff
        path: "OU=IT,DC=corp,DC=local"
        managed_by: "john.admin"
    domainlocal:
      - name: LocalAdmins
        path: "CN=Users,DC=corp,DC=local"
    universal: []
  ludus_users:
    - name: john.admin
      firstname: John
      surname: Admin
      password: "SecureP@ss123"
      path: "OU=IT,DC=corp,DC=local"
      groups:
        - IT-Staff
        - Domain Admins
      password_never_expires: true
    - name: svc_sql
      firstname: SQL
      surname: Service
      password: "SQLServiceP@ss!"
      path: "CN=Users,DC=corp,DC=local"
      groups: []
      spns:
        - "MSSQLSvc/sqlserver.corp.local:1433"
        - "MSSQLSvc/sqlserver.corp.local"
```

### Mode: `random`

Generate randomized AD content using a Python script with realistic names (via Faker).

```yaml
role_vars:
  ludus_ad_content_mode: "random"
  ludus_random_config:
    user_count: 50
    ou_count: 6
    group_count: 10
    password_style: "weak"      # Options: weak, realistic, strong
    department_names:
      - "HR"
      - "IT"
      - "Sales"
      - "Finance"
      - "Engineering"
    create_service_accounts: true
    service_account_count: 3
    seed: 12345                 # Optional: for reproducible generation
```

**Password styles:**
- `weak`: Common weak passwords (Password1, Summer2024, etc.)
- `realistic`: Company-style passwords (Company2024!, Welcome123)
- `strong`: Random 16-char passwords with symbols

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_ad_content_mode` | `"goad"` | Operation mode: `goad`, `custom`, `random` |
| `ludus_domain_name` | `""` | Domain FQDN (auto-detected if empty) |
| `ludus_domain_netbios` | `""` | NetBIOS name (auto-derived if empty) |
| `ludus_domain_admin` | `administrator` | Domain admin username |
| `ludus_domain_admin_password` | `password` | Domain admin password |

### Custom Mode Variables

| Variable | Description |
|---|---|
| `ludus_password_policy` | Dict with password policy settings |
| `ludus_organisation_units` | List of OUs to create |
| `ludus_groups` | Dict with `global`, `domainlocal`, `universal` group lists |
| `ludus_users` | List of users to create |
| `ludus_multi_domain_group_members` | Cross-domain group memberships |

### Random Mode Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_random_config.user_count` | `30` | Number of users to generate |
| `ludus_random_config.ou_count` | `5` | Number of OUs to create |
| `ludus_random_config.group_count` | `8` | Max number of groups |
| `ludus_random_config.password_style` | `"weak"` | Password generation style |
| `ludus_random_config.department_names` | `[HR, IT, ...]` | Department/OU names |
| `ludus_random_config.create_service_accounts` | `true` | Generate service accounts with SPNs |
| `ludus_random_config.service_account_count` | `2` | Number of service accounts |
| `ludus_random_config.seed` | `null` | Random seed for reproducibility |

## Example Ludus Range Config

```yaml
- vm_name: "{{ range_id }}-dc01"
  hostname: "dc01"
  template: win2019-server-x64-template
  domain:
    fqdn: corp.local
    role: primary-dc
  roles:
    - badsectorlabs.ludus_bulk_ad_content
  role_vars:
    # Use GOAD data for sevenkingdoms.local
    ludus_ad_content_mode: "goad"
    ludus_domain_name: "sevenkingdoms.local"

# Or for random generation:
- vm_name: "{{ range_id }}-dc02"
  hostname: "dc02"
  template: win2019-server-x64-template
  domain:
    fqdn: testlab.local
    role: primary-dc
  roles:
    - badsectorlabs.ludus_bulk_ad_content
  role_vars:
    ludus_ad_content_mode: "random"
    ludus_random_config:
      user_count: 100
      password_style: "weak"
      seed: 42  # Reproducible
```

## What Gets Created

### Password Policy
- Minimum password length (default: 5 for weak labs)
- Complexity requirements (default: disabled)
- Lockout threshold and duration

### Organisational Units
- Created at specified paths
- Protection from accidental deletion disabled

### Groups
- **Global**: Department/role groups with managed_by
- **Domain Local**: Local resource groups
- **Universal**: Cross-domain groups
- Group members (including nested groups)

### Users
- Full user attributes (firstname, surname, description, city)
- Password with configurable expiration
- Group memberships
- Service Principal Names (SPNs) for service accounts

## Cross-Domain Members

For multi-forest environments, the role supports adding members from trusted domains:

```yaml
ludus_multi_domain_group_members:
  - group: "DragonsFriends"
    members:
      - "otherdomain.local\\user1"
      - "otherdomain.local\\group1"
```

Note: Cross-domain membership requires the trust to be established first. The role will ignore errors if the trust is not yet live.

## License

Apache-2.0
