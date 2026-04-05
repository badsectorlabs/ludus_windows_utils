# ludus_ad_misconfigs

An Ansible role for Ludus that configures common Windows/Active Directory security misconfigurations for attack lab scenarios. Supports both custom configurations and pre-defined GOAD (Game of Active Directory) scenarios.

## Purpose

This role enables security researchers, red teamers, and penetration testers to quickly deploy realistic AD attack lab environments with intentional vulnerabilities. All misconfigurations are commonly found in real enterprise environments.

## Supported Misconfigurations

| Category | Misconfiguration | Attack Vector |
|----------|-----------------|---------------|
| **Network** | Disable Windows Firewall | Lateral movement, service enumeration |
| **Name Resolution** | Enable LLMNR | Responder/relay attacks |
| **Name Resolution** | Enable NBT-NS | Responder/relay attacks |
| **NTLM** | NTLM Downgrade (LmCompatibilityLevel) | NTLMv1 relay, hash cracking |
| **Credentials** | LSA Protection (PPL) | Credential extraction bypass practice |
| **Credentials** | Autologon | Credential harvesting |
| **Credentials** | Credential Manager entries | cmdkey extraction |
| **Kerberos** | AS-REP Roasting | Offline password cracking |
| **Kerberos** | Unconstrained Delegation | TGT harvesting, domain compromise |
| **Kerberos** | Constrained Delegation (Any Auth) | S4U2Self/S4U2Proxy impersonation |
| **Kerberos** | Constrained Delegation (Kerb Only) | Kerberos delegation attacks |
| **Kerberos** | Account Not Delegated | Protected account bypass practice |
| **Automation** | Scheduled Tasks (Bots) | NTLM relay triggers, credential harvesting |
| **GPO** | GPO Abuse | GPO hijacking, privilege escalation |

## Requirements

- Ansible 2.14+
- Windows Server 2019 or 2022
- Collections: `ansible.windows`, `community.windows`
- Active Directory domain (for Kerberos/AD features)
- RSAT tools installed on DCs (for AD PowerShell cmdlets)

## Role Variables

### Global Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_misconfigs_mode` | `"custom"` | Mode: `"custom"` for granular control, `"goad"` for GOAD defaults |

### Firewall

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_firewall_disabled` | `false` | Disable Windows Firewall |
| `ludus_firewall_profiles` | `[Domain, Private, Public]` | Profiles to disable |

### LLMNR / NBT-NS

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_llmnr_enabled` | `false` | Enable LLMNR (Responder attacks) |
| `ludus_nbt_ns_enabled` | `false` | Enable NBT-NS (Responder attacks) |
| `ludus_nbt_ns_node_type` | `"0x00000008"` | NBT-NS node type (8 = hybrid) |

### NTLM

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_ntlm_downgrade_enabled` | `false` | Enable NTLM downgrade |
| `ludus_ntlm_lm_compatibility_level` | `2` | LmCompatibilityLevel (0-5) |

### LSA Protection

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_lsa_ppl_enabled` | `false` | Enable RunAsPPL (requires reboot) |

### Autologon

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_autologon_enabled` | `false` | Enable automatic login |
| `ludus_autologon_user` | `""` | Username for autologon |
| `ludus_autologon_password` | `""` | Password for autologon |
| `ludus_autologon_domain` | `""` | Domain for autologon |

### Credential Manager

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_credential_manager_entries` | `[]` | List of credentials to store |

### AS-REP Roasting

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_asrep_roast_users` | `[]` | Users with DoesNotRequirePreAuth |

### Kerberos Delegation

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_unconstrained_delegation_users` | `[]` | Users with unconstrained delegation |
| `ludus_unconstrained_delegation_computers` | `[]` | Computers with unconstrained delegation |
| `ludus_constrained_delegation_any` | `[]` | Constrained delegation with protocol transition |
| `ludus_constrained_delegation_kerb_only` | `[]` | Constrained delegation (Kerberos only) |
| `ludus_account_not_delegated` | `[]` | Accounts marked as sensitive |

### Scheduled Tasks

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_scheduled_tasks` | `[]` | List of scheduled tasks to create |

### GPO Abuse

| Variable | Default | Description |
|----------|---------|-------------|
| `ludus_gpo_abuse_enabled` | `false` | Enable GPO abuse configuration |
| `ludus_gpo_name` | `""` | Name of GPO to create |
| `ludus_gpo_link_target` | `""` | OU to link GPO |
| `ludus_gpo_editors` | `[]` | Users with edit permissions |

## Dependencies

- `ansible.windows`
- `community.windows`

## Example Ludus Range Config

### GOAD Mode (Pre-configured)

```yaml
ludus:
  - vm_name: '{{ range_id }}-DC02'
    hostname: winterfell
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 11
    domain:
      fqdn: north.sevenkingdoms.local
      role: primary-dc
    roles:
      - ludus_ad_misconfigs
    role_vars:
      ludus_misconfigs_mode: "goad"
```

### Custom Mode

```yaml
ludus:
  - vm_name: '{{ range_id }}-DC01'
    hostname: dc01
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: lab.local
      role: primary-dc
    roles:
      - ludus_ad_misconfigs
    role_vars:
      ludus_misconfigs_mode: "custom"
      # Disable firewall
      ludus_firewall_disabled: true
      # Enable LLMNR for Responder attacks
      ludus_llmnr_enabled: true
      ludus_nbt_ns_enabled: true
      # AS-REP roastable accounts
      ludus_asrep_roast_users:
        - name: "svc_backup"
          domain: "lab.local"
      # Unconstrained delegation
      ludus_unconstrained_delegation_users:
        - name: "web_svc"
          domain: "lab.local"
      # Constrained delegation with protocol transition
      ludus_constrained_delegation_any:
        - name: "sql_svc"
          domain: "lab.local"
          spns:
            - "MSSQLSvc/sql01.lab.local:1433"
          allowed_to_delegate:
            - "CIFS/dc01.lab.local"
            - "CIFS/dc01"
      # Scheduled task for NTLM relay
      ludus_scheduled_tasks:
        - name: "backup_bot"
          description: "Backup job simulation"
          user: "LAB\\admin"
          password: "P@ssw0rd!"
          command: "cmd.exe"
          arguments: '/c net use \\\\fileserver\\backup /user:LAB\\admin P@ssw0rd!'
          repeat_interval: "PT5M"
```

## GOAD Pre-configured Hosts

When `ludus_misconfigs_mode: "goad"`, the role automatically applies the correct misconfigurations based on hostname:

| Hostname | Misconfigurations Applied |
|----------|--------------------------|
| **winterfell** | Firewall off, LLMNR, NBT-NS, Autologon (robb.stark), Credential Manager, AS-REP (brandon.stark), Unconstrained (sansa.stark), Constrained (jon.snow, castelblack), Scheduled tasks (3 bots), GPO abuse |
| **kingslanding** | Firewall off, AccountNotDelegated (renly.baratheon) |
| **meereen** | Firewall off, NTLM downgrade, AS-REP (missandei) |
| **castelblack** | Firewall off |
| **braavos** | Firewall off, LSA PPL enabled |

## Attack Scenarios Enabled

### AS-REP Roasting
```bash
# From Kali
impacket-GetNPUsers north.sevenkingdoms.local/ -usersfile users.txt -format hashcat
```

### Unconstrained Delegation
```powershell
# Monitor for TGTs with Rubeus
.\Rubeus.exe monitor /interval:5 /targetuser:administrator
```

### Constrained Delegation (S4U)
```bash
# S4U2Self + S4U2Proxy attack
impacket-getST -spn CIFS/dc01.lab.local -impersonate administrator lab.local/sql_svc:password
```

### Responder (LLMNR/NBT-NS)
```bash
# Run Responder to capture hashes
sudo responder -I eth0 -rdwv
```

### GPO Abuse
```powershell
# Use SharpGPOAbuse to add immediate task
.\SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author "NT AUTHORITY\SYSTEM" --Command "cmd.exe" --Arguments "/c net user backdoor P@ssw0rd! /add" --GPOName "StarkWallpaper"
```

## Ludus Notes

- Run this role **after** users/groups are created (depends on `ludus_bulk_ad_content`)
- For Kerberos delegation, the target SPNs must exist in AD
- Scheduled tasks require valid domain credentials
- LSA PPL requires a reboot to take effect
- GOAD mode uses hostname matching (case-insensitive)

## License

MIT

## Author

Bad Sector Labs
