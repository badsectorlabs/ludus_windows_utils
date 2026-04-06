# ludus_iis_webdav

An Ansible role for [Ludus](https://ludus.cloud) that installs the WebDAV client (WebClient service for NTLM coercion attacks) and/or configures IIS Web Server with WebDAV Publishing authoring rules.

## Purpose

Enable WebDAV attack paths in cyber ranges — either the WebClient service for NTLM relay/coercion (PetitPotam, PrinterBug) or a full IIS WebDAV server for file upload attack scenarios.

## Requirements

- Windows Server 2019/2022
- `ansible.windows` collection

## Modes

| Mode | Description |
|---|---|
| `client` | WebDAV-Redirector only — starts WebClient service for NTLM coercion |
| `server` | Full IIS + WebDAV Publishing with authoring rules |
| `both` | Install both client and server features |

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_iis_webdav_mode` | `"client"` | Mode: `"client"`, `"server"`, or `"both"` |
| `ludus_webdav_client_start_service` | `true` | Auto-start WebClient service |
| `ludus_iis_install_aspnet` | `false` | Install ASP.NET 4.5 (needed for .aspx execution) |
| `ludus_iis_install_legacy_compat` | `false` | Install IIS 6 legacy compatibility |
| `ludus_iis_content_mode` | `"none"` | Content: `"none"`, `"custom"`, or `"goad"` |
| `ludus_iis_upload_dir` | `""` | Upload directory path (e.g., `C:\inetpub\wwwroot\upload`) |
| `ludus_iis_upload_dir_user` | `"IIS_IUSRS"` | Upload directory permission user |
| `ludus_iis_upload_dir_rights` | `"FullControl"` | Upload directory permission level |
| `ludus_iis_webdav_authoring_rules` | `[{users: "*", path: "*", access: "Read,Write,Source"}]` | WebDAV authoring rules |

## Example Ludus Range Config

### GOAD castelblack (IIS + WebDAV + ASP.NET upload)

```yaml
ludus:
  - vm_name: "{{ range_id }}-SRV02"
    hostname: castelblack
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 12
    domain:
      fqdn: north.sevenkingdoms.local
      role: member
    roles:
      - ludus_iis_webdav
    role_vars:
      ludus_iis_webdav_mode: "server"
      ludus_iis_install_aspnet: true
      ludus_iis_install_legacy_compat: true
      ludus_iis_content_mode: "goad"
      ludus_iis_upload_dir: "C:\\inetpub\\wwwroot\\upload"
      ludus_iis_upload_dir_user: "IIS_IUSRS"
      ludus_iis_upload_dir_rights: "FullControl"
```

### WebDAV client only (for NTLM coercion)

```yaml
    roles:
      - ludus_iis_webdav
    role_vars:
      ludus_iis_webdav_mode: "client"
```

## Ludus Notes

- GOAD content mode downloads the ASP.NET file upload app from the GOAD GitHub repo
- Client mode installs WebDAV-Redirector feature and enables the WebClient service (required for NTLM coercion via WebDAV)

## Dependencies

None.

## Author

Bad Sector Labs
