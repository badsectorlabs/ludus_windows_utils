# ludus_ad_gmsa

Creates **Group Managed Service Accounts (gMSA)** using PowerShell DSC (Desired State Configuration) resources for declarative, idempotent configuration.

## Features

- **DSC-based configuration** using `ansible.windows.win_dsc` module
- Creates KDS Root Key (backdated for immediate use in labs)
- Creates gMSA accounts with SPNs and permitted principals
- Automatically installs the `ActiveDirectoryDsc` PowerShell module
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
| `ludus_gmsa_domain_admin` | Ludus default | Domain admin username |
| `ludus_gmsa_domain_admin_password` | Ludus default | Domain admin password |
| `ludus_gmsa_accounts` | `[]` | List of gMSA accounts to create |

### gMSA Account Structure

```yaml
ludus_gmsa_accounts:
  - name: gmsaServiceAccount     # gMSA account name (without $)
    dns_hostname: server.domain.local
    spns:
      - "HTTP/server.domain.local"
      - "HTTP/server"
    permitted_hosts:
      - "COMPUTERNAME$"          # Computers that can retrieve the password
```

## Example Ludus Range Config

```yaml
ludus:
  - vm_name: "{{ range_id }}-dc01"
    hostname: "dc01"
    template: win2019-server-x64-template
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: corp.local
      role: primary-dc
    roles:
      - badsectorlabs.ludus_ad_gmsa
    role_vars:
      ludus_gmsa_accounts:
        - name: gmsaSQLService
          dns_hostname: dc01.corp.local
          spns:
            - "MSSQLSvc/sqlserver.corp.local:1433"
            - "MSSQLSvc/sqlserver.corp.local"
          permitted_hosts:
            - "SQLSERVER$"
```

## How It Works

This role uses **PowerShell DSC resources** instead of raw PowerShell scripts:

| Task | DSC Resource | Benefit |
|------|-------------|---------|
| KDS Root Key | `ADKDSKey` | Declarative, handles idempotency |
| gMSA Account | `ADManagedServiceAccount` | Desired state, automatic SPNs |

### DSC Resources Used

1. **`ADKDSKey`** - Creates the Key Distribution Service root key required for gMSA
   - `EffectiveTime`: Set 10 hours in past for immediate use (lab environment)
   - `AllowUnsafeEffectiveTime`: Required for backdated key

2. **`ADManagedServiceAccount`** - Creates the gMSA account
   - `AccountType: Group` - Specifies gMSA (vs standalone MSA)
   - `PrincipalsAllowedToRetrieveManagedPassword`: Computer accounts that can use the gMSA

## Testing gMSA

After running the role, verify on a permitted host:

```powershell
# Install the gMSA on a permitted computer
Install-ADServiceAccount -Identity gmsaServiceAccount

# Test the gMSA works
Test-ADServiceAccount -Identity gmsaServiceAccount
# Should return: True
```

