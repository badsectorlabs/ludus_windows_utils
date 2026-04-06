# ludus_files

An Ansible role for [Ludus](https://ludus.cloud) that deploys files, honeypot bait documents, and credential breadcrumbs to Windows VMs. Designed to make cyber ranges feel realistic for security practitioners practicing post-exploitation, credential harvesting, and lateral movement techniques.

## Modes

| Mode | Description |
|---|---|
| `custom` | Deploy your own files via `role_vars` — any file, any location |
| `goad` | Deploy GOAD-specific files (bot scripts, SYSVOL content, web pages, share files) |
| `honeypot` | Generate realistic bait files that look valuable during post-exploitation |
| `breadcrumbs` | Drop credential artifacts — PowerShell history, config files, registry entries, sticky notes |
| `all` | Combine all modes for maximum range realism |

## What Practitioners Can Practice

### Honeypot Files (post-exploitation data discovery)
- **Credential files**: `passwords.txt`, KeePass CSV exports, legacy password lists
- **IT documentation**: Server inventories, network diagrams, backup configurations
- **HR data**: Employee directories with org structure
- **Financial data**: Budget spreadsheets
- **Executive docs**: Board meeting notes with M&A details, security posture info

### Breadcrumbs (credential harvesting & pivoting)
- **PowerShell history**: `ConsoleHost_history.txt` with embedded credentials and lateral movement commands
- **Browser bookmarks**: IE/Edge favorites pointing to internal management interfaces
- **Connection strings**: `web.config` and `.env` files with database credentials
- **Sticky notes**: Desktop text files with passwords
- **Recent documents**: Shortcuts revealing file server paths and SYSVOL scripts
- **Registry entries**: PuTTY saved sessions, WinSCP stored credentials

## Requirements

- Ludus server with Ansible 2.14+
- Windows Server 2019/2022 target VMs
- `ansible.windows` collection (installed by default on Ludus)

## Role Variables

See [`defaults/main.yml`](defaults/main.yml) for all variables with descriptions.

| Variable | Default | Description |
|---|---|---|
| `ludus_files_mode` | `"custom"` | Mode: `custom`, `goad`, `honeypot`, `breadcrumbs`, `all` |
| `ludus_files_custom` | `[]` | List of custom file definitions (`src`/`content` + `dest`) |
| `ludus_files_goad` | *(GOAD presets)* | GOAD files keyed by hostname |
| `ludus_honeypot_enabled` | `true` | Enable honeypot file generation |
| `ludus_honeypot_categories` | `[credentials, financial, hr, it, executive]` | Which categories to deploy |
| `ludus_honeypot_locations` | *(see defaults)* | Target directories for honey files |
| `ludus_honeypot_density` | `1` | Files per category per location (1-3) |
| `ludus_honeypot_include_legacy` | `true` | Include "old" files for realism |
| `ludus_honeypot_company_name` | `{{ ludus_domain_netbios_name }}` | Company name in generated content |
| `ludus_honeypot_domain` | `{{ ludus_domain_fqdn }}` | Domain name in generated content |
| `ludus_breadcrumbs_enabled` | `true` | Enable breadcrumb deployment |
| `ludus_breadcrumbs_types` | `[registry_creds, powershell_history, browser_bookmarks, recent_docs, connection_strings, sticky_notes]` | Breadcrumb types to scatter |
| `ludus_breadcrumbs_custom` | `[]` | Additional custom breadcrumb entries |

## Example Ludus Range Config

### Honeypot + Breadcrumbs on all servers

```yaml
ludus:
  - vm_name: "{{ range_id }}-DC01"
    hostname: dc01
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: false
    domain:
      fqdn: yourcompany.local
      role: primary-dc
    roles:
      - ludus_files
    role_vars:
      ludus_files_mode: "all"

  - vm_name: "{{ range_id }}-SRV01"
    hostname: websrv
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 11
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: true
    domain:
      fqdn: yourcompany.local
      role: member
    roles:
      - ludus_files
    role_vars:
      ludus_files_mode: "honeypot"
      ludus_honeypot_categories:
        - credentials
        - it
        - executive
```

### GOAD mode (deploy GOAD-specific files)

```yaml
  - vm_name: "{{ range_id }}-DC02"
    hostname: winterfell
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 11
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: false
    domain:
      fqdn: north.sevenkingdoms.local
      role: primary-dc
    roles:
      - ludus_files
    role_vars:
      ludus_files_mode: "goad"
```

### Custom file deployment

```yaml
    roles:
      - ludus_files
    role_vars:
      ludus_files_mode: "custom"
      ludus_files_custom:
        - content: |
            Write-Host "Hello from custom script"
          dest: "C:\\setup\\hello.ps1"
          create_dirs:
            - "C:\\setup"
          description: "Custom setup script"
        - src: "configs/app.config"
          dest: "C:\\Program Files\\MyApp\\app.config"
          description: "Application config"
```

## Dependencies

None.

## Ludus Notes

- All content uses Ludus-provided variables (`ludus_domain_fqdn`, `range_second_octet`, etc.) automatically
- Honeypot and breadcrumb content references realistic service accounts, IP addresses, and domain structures that adapt to your range topology
- GOAD mode files are keyed by `ansible_hostname` (lowercase) — matches Ludus VM hostname config
- This role is designed to run **after** domain join and role deployment — place it last in the roles list
- Complements `ludus_random_files` (published) — that role generates random binary files for volume; this role generates _meaningful_ text content for post-exploitation practice

