# Ansible Collection: Windows & AD Utilities for Ludus

[![Ansible Galaxy](https://img.shields.io/badge/galaxy-badsectorlabs.ludus__windows__utils-blue)](https://galaxy.ansible.com/ui/repo/published/badsectorlabs/ludus_windows_utils/)

A collection of Ansible roles for configuring Windows and Active Directory environments in [Ludus](https://ludus.cloud) cyber ranges. Build realistic, composable attack labs with data-driven configuration — ACLs, LAPS, child domains, forest trusts, SMB shares, misconfigurations, and more.

All roles are fully parameterized via `role_vars` in your Ludus range config. No hardcoded hostnames or domain names — every role works with any domain, any topology.

## Requirements

- **Ludus** v2.0+ (https://ludus.cloud)
- **Ansible** >= 2.14
- **Collections** (installed on Ludus server by default):
  - `ansible.windows`
  - `community.windows`
  - `microsoft.ad`

## Installation

### Via Ansible Galaxy

```bash
ansible-galaxy collection install badsectorlabs.ludus_windows_utils
```

### Via Ludus

```bash
ludus ansible collection add badsectorlabs.ludus_windows_utils
```

## Included Roles

| Role | Description | Target |
|---|---|---|
| [`ludus_ad_acls`](#ludus_ad_acls) | Set AD ACL entries (GenericAll, WriteDacl, etc.) for attack chains | Domain Controllers |
| [`ludus_ad_anonymous_rpc`](#ludus_ad_anonymous_rpc) | Enable anonymous RPC/SMB enumeration on DCs | Domain Controllers |
| [`ludus_ad_forest_trust`](#ludus_ad_forest_trust) | Create bidirectional AD forest trusts with DNS forwarders | Domain Controllers |
| [`ludus_ad_gmsa`](#ludus_ad_gmsa) | Create Group Managed Service Accounts (gMSA) | Domain Controllers |
| [`ludus_ad_laps`](#ludus_ad_laps) | Configure Microsoft LAPS (schema, GPO, DACL, client) | DCs + Member Servers |
| [`ludus_ad_misconfigs`](#ludus_ad_misconfigs) | Apply common Windows/AD security misconfigurations | Any Windows VM |
| [`ludus_ad_password_policy`](#ludus_ad_password_policy) | Set AD domain password policy | Domain Controllers |
| [`ludus_bulk_ad_content`](#ludus_bulk_ad_content) | Bulk-create OUs, groups, users, and computers in AD | Domain Controllers |
| [`ludus_child_domain`](#ludus_child_domain) | Create an AD child domain | Child DC |
| [`ludus_child_domain_join`](#ludus_child_domain_join) | Join a Windows machine to a child domain | Member Servers |
| [`ludus_files`](#ludus_files) | Deploy files, honeypot documents, and credential breadcrumbs | Any Windows VM |
| [`ludus_iis_webdav`](#ludus_iis_webdav) | Install WebDAV client and/or IIS WebDAV server | Member Servers |
| [`ludus_smb_shares`](#ludus_smb_shares) | Create SMB shares with permissions and optional anonymous access | Any Windows VM |

---

## Role Details

### ludus_ad_acls

Sets Active Directory ACL entries for building attack paths. Supports custom ACE definitions with any combination of AD rights.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_ad_acls_entries` | `[]` | List of ACE entries to apply (see example below) |

**Example `role_vars`:**
```yaml
role_vars:
  ludus_ad_acls_entries:
    - source: "YOURDOM\\user1"
      destination: "YOURDOM\\target_group"
      rights: "GenericAll"
    - source: "YOURDOM\\helpdesk"
      destination: "YOURDOM\\admin_user"
      rights: "ForceChangePassword"
```

---

### ludus_ad_anonymous_rpc

Configures anonymous RPC and SMB enumeration on domain controllers. Sets the necessary registry keys, null session pipes, and adds ANONYMOUS LOGON to the Pre-Windows 2000 Compatible Access group (required on Server 2016+).

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_ad_anonymous_rpc_enabled` | `true` | Enable anonymous RPC enumeration |
| `ludus_ad_anonymous_rpc_null_session_pipes` | `["samr", "lsarpc", "netlogon"]` | Named pipes for null sessions |

---

### ludus_ad_forest_trust

Creates bidirectional AD forest trusts between two domain controllers, including DNS conditional forwarders for cross-forest name resolution. Optionally enables SID history on the trust.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_forest_trust_dc_fqdn` | *(required)* | FQDN of the remote DC to trust |
| `ludus_forest_trust_dc_ip` | *(required)* | IP of the remote DC |
| `ludus_forest_trust_domain_fqdn` | *(required)* | FQDN of the remote domain |
| `ludus_forest_trust_domain_admin` | `"domainadmin"` | Remote domain admin username |
| `ludus_forest_trust_domain_admin_password` | `"password"` | Remote domain admin password |
| `ludus_forest_trust_enable_sid_history` | `false` | Enable SID history on the trust |

> **Note:** Use `depends_on` in range configs to ensure the remote DC's domain is created before establishing the trust.

---

### ludus_ad_gmsa

Creates Group Managed Service Accounts (gMSA) in Active Directory. Configures KDS root key, service accounts, and principal access.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_gmsa_accounts` | `[]` | List of gMSA accounts to create |

**Example `role_vars`:**
```yaml
role_vars:
  ludus_gmsa_accounts:
    - name: gmsaSvc1
      dns_hostname: gmsaSvc1.yourdomain.local
      principals_allowed:
        - "Domain Controllers"
```

---

### ludus_ad_laps

Configures Microsoft LAPS (Local Administrator Password Solution). Handles DC-side setup (schema extension, GPO, OU delegation) and client-side installation.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_laps_target_ou` | `""` | Target OU for LAPS DACL delegation |
| `ludus_laps_delegates` | `[]` | Groups granted LAPS read permission |
| `ludus_laps_install_client` | `false` | Install LAPS client (member servers) |

---

### ludus_ad_misconfigs

Applies common Windows and AD security misconfigurations for attack lab scenarios. Each misconfiguration is individually toggleable.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_misconfigs_disable_smb_signing` | `false` | Disable SMB signing |
| `ludus_misconfigs_enable_webdav_client` | `false` | Install WebDAV client (WebClient service) |
| `ludus_misconfigs_disable_ldap_signing` | `false` | Disable LDAP signing requirements |
| `ludus_misconfigs_disable_ldap_channel_binding` | `false` | Disable LDAP channel binding |
| `ludus_misconfigs_enable_spooler` | `false` | Enable Print Spooler service |
| `ludus_misconfigs_enable_ipv6` | `false` | Enable IPv6 on all interfaces |
| `ludus_misconfigs_disable_epa` | `false` | Disable Extended Protection for Authentication |

---

### ludus_ad_password_policy

Sets the Active Directory domain password policy. Supports custom policy values for password length, complexity, lockout, and history.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_password_policy_min_length` | `7` | Minimum password length |
| `ludus_password_policy_complexity` | `true` | Require password complexity |
| `ludus_password_policy_min_age_days` | `1` | Minimum password age (days) |
| `ludus_password_policy_max_age_days` | `42` | Maximum password age (days) |
| `ludus_password_policy_history_count` | `24` | Password history count |
| `ludus_password_policy_lockout_threshold` | `0` | Account lockout threshold (0 = disabled) |
| `ludus_password_policy_lockout_duration_minutes` | `30` | Account lockout duration |
| `ludus_password_policy_lockout_window_minutes` | `30` | Lockout observation window |

---

### ludus_bulk_ad_content

Bulk-creates Active Directory content: OUs, groups, users, and computers. Supports custom datasets or randomized generation for realistic lab populations.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_bulk_ad_ous` | `[]` | List of OUs to create |
| `ludus_bulk_ad_groups` | `[]` | List of groups to create |
| `ludus_bulk_ad_users` | `[]` | List of users to create with group memberships |
| `ludus_bulk_ad_computers` | `[]` | List of computer objects to create |

**Example `role_vars`:**
```yaml
role_vars:
  ludus_bulk_ad_ous:
    - name: IT
      path: "DC=yourdomain,DC=local"
    - name: HR
      path: "DC=yourdomain,DC=local"
  ludus_bulk_ad_users:
    - name: jsmith
      firstname: John
      lastname: Smith
      password: "P@ssw0rd123"
      ou: "OU=IT,DC=yourdomain,DC=local"
      groups:
        - Domain Admins
```

---

### ludus_child_domain

Creates an Active Directory child domain under an existing forest root. Uses the `microsoft.ad.domain_child` module.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_child_domain_name` | *(required)* | NetBIOS name of the child domain |
| `ludus_child_domain_parent_fqdn` | *(required)* | FQDN of the parent domain |
| `ludus_child_domain_parent_dc_ip` | *(required)* | IP of the parent DC |
| `ludus_child_domain_admin_user` | `"domainadmin"` | Parent domain admin username |
| `ludus_child_domain_admin_password` | `"password"` | Parent domain admin password |
| `ludus_child_domain_safe_mode_password` | `"password"` | DSRM password |

---

### ludus_child_domain_join

Joins a Windows machine to an existing child domain. Uses `microsoft.ad.membership`.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_child_domain_join_fqdn` | *(required)* | FQDN of the child domain to join |
| `ludus_child_domain_join_dc_ip` | *(required)* | IP of the child domain DC |
| `ludus_child_domain_join_admin_user` | `"domainadmin"` | Domain admin username |
| `ludus_child_domain_join_admin_password` | `"password"` | Domain admin password |

> **Note:** Use `depends_on` in range configs to ensure the child domain DC is fully configured before joining member servers.

---

### ludus_files

Deploys files, honeypot bait documents, and credential breadcrumbs to Windows VMs. Supports templated content for realistic post-exploitation scenarios.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_files_deploy` | `[]` | List of files to deploy |
| `ludus_files_honeypots` | `[]` | Honeypot bait documents |
| `ludus_files_breadcrumbs` | `[]` | Credential breadcrumb files |

---

### ludus_iis_webdav

Installs the WebDAV client (WebClient service for NTLM coercion attacks) and/or configures IIS Web Server with WebDAV Publishing authoring rules.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_iis_webdav_install_client` | `false` | Install WebDAV client (WebClient service) |
| `ludus_iis_webdav_install_server` | `false` | Install IIS with WebDAV publishing |
| `ludus_iis_webdav_site_name` | `"Default Web Site"` | IIS site name for WebDAV |
| `ludus_iis_webdav_physical_path` | `"C:\\inetpub\\wwwroot"` | WebDAV root path |

---

### ludus_smb_shares

Creates SMB shares with configurable permissions. Supports anonymous access via guest account activation and registry configuration.

**Key Variables:**

| Variable | Default | Description |
|---|---|---|
| `ludus_smb_shares` | `[]` | List of shares to create |
| `ludus_smb_shares_enable_anonymous` | `false` | Enable anonymous/guest access |

**Example `role_vars`:**
```yaml
role_vars:
  ludus_smb_shares_enable_anonymous: true
  ludus_smb_shares:
    - name: Public
      path: "C:\\Shares\\Public"
      full_access:
        - Everyone
      description: "Public file share"
    - name: IT
      path: "C:\\Shares\\IT"
      full_access:
        - "YOURDOM\\Domain Admins"
      read_access:
        - "YOURDOM\\Domain Users"
```

---

## Example Ludus Range Config

This example shows a minimal range using several roles from the collection:

```yaml
ludus:
  - vm_name: "{{ range_id }}-DC01"
    hostname: "{{ range_id }}-DC01"
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: false
    domain:
      fqdn: lab.local
      role: primary-dc
    roles:
      - badsectorlabs.ludus_windows_utils.ludus_ad_password_policy
      - badsectorlabs.ludus_windows_utils.ludus_bulk_ad_content
      - badsectorlabs.ludus_windows_utils.ludus_ad_acls
      - badsectorlabs.ludus_windows_utils.ludus_ad_gmsa
      - badsectorlabs.ludus_windows_utils.ludus_ad_anonymous_rpc
    role_vars:
      ludus_password_policy_min_length: 1
      ludus_password_policy_complexity: false
      ludus_password_policy_lockout_threshold: 0
      ludus_bulk_ad_ous:
        - name: IT
          path: "DC=lab,DC=local"
      ludus_bulk_ad_users:
        - name: svc_sql
          firstname: SQL
          lastname: Service
          password: "Password123"
          ou: "OU=IT,DC=lab,DC=local"
          groups:
            - Domain Admins
      ludus_ad_acls_entries:
        - source: "LAB\\svc_sql"
          destination: "LAB\\Domain Admins"
          rights: "GenericAll"
      ludus_gmsa_accounts:
        - name: gmsaSvc1
          dns_hostname: gmsaSvc1.lab.local

  - vm_name: "{{ range_id }}-SRV01"
    hostname: "{{ range_id }}-SRV01"
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 11
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: true
    domain:
      fqdn: lab.local
      role: member
    roles:
      - badsectorlabs.ludus_windows_utils.ludus_ad_misconfigs
      - badsectorlabs.ludus_windows_utils.ludus_smb_shares
      - badsectorlabs.ludus_windows_utils.ludus_iis_webdav
    role_vars:
      ludus_misconfigs_disable_smb_signing: true
      ludus_misconfigs_enable_spooler: true
      ludus_smb_shares_enable_anonymous: true
      ludus_smb_shares:
        - name: Public
          path: "C:\\Shares\\Public"
          full_access:
            - Everyone
      ludus_iis_webdav_install_client: true

  - vm_name: "{{ range_id }}-kali"
    hostname: "{{ range_id }}-kali"
    template: kali-x64-desktop-template
    vlan: 99
    ip_last_octet: 1
    ram_gb: 4
    cpus: 2
    linux: true
    testing:
      snapshot: false
      block_internet: false
```

## Cross-VM Dependencies

When a role on one VM depends on a role completing on another VM, use `depends_on`:

```yaml
roles:
  - name: badsectorlabs.ludus_windows_utils.ludus_child_domain_join
    depends_on:
      - vm_name: "{{ range_id }}-DC02"
        role: badsectorlabs.ludus_windows_utils.ludus_child_domain
```

Roles on the **same VM** run sequentially in listed order — `depends_on` is only needed for **cross-VM** dependencies.

## Acknowledgments

This collection was inspired by and builds upon the work of:

- **[GOAD (Game of Active Directory)](https://github.com/Orange-Cyberdefense/GOAD)** by [@Mayfly277](https://github.com/Mayfly277) and the [Orange Cyberdefense](https://github.com/Orange-Cyberdefense) team — the original AD attack lab that inspired many of these role configurations
- **[@ChoiSG](https://github.com/ChoiSG)** and their [ludus_ansible_roles](https://github.com/ChoiSG/ludus_ansible_roles) — early Ludus community role contributions that helped shape the approach

## License

GPLv3

## Author Information

This collection was created by [Bad Sector Labs](https://github.com/badsectorlabs), for [Ludus](https://ludus.cloud/).
