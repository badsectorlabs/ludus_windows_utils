# ludus_ad_anonymous_rpc

An Ansible role for [Ludus](https://ludus.cloud) that enables anonymous RPC and SMB enumeration on Windows domain controllers. Configures registry keys, null session pipes, and the Pre-Windows 2000 Compatible Access group membership required on Server 2016+.

## Purpose

Enable anonymous/null session enumeration so security practitioners can practice reconnaissance techniques with tools like `enum4linux`, `rpcclient`, `lookupsid.py`, and CrackMapExec.

## Requirements

- Windows Server 2019/2022 Domain Controller
- `ansible.windows` collection
- `community.windows` collection

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `ludus_anonymous_sam_enumeration` | `true` | Allow anonymous SAM enumeration |
| `ludus_anonymous_lsa_enumeration` | `true` | Allow anonymous LSA/SID enumeration |
| `ludus_restrict_anonymous` | `0` | RestrictAnonymous level (0 = most permissive) |
| `ludus_restrict_anonymous_sam` | `0` | RestrictAnonymousSAM (0 = allow) |
| `ludus_anonymous_named_pipes` | `["netlogon", "samr", "lsarpc", "srvsvc", "browser"]` | Named pipes for null sessions |
| `ludus_everyone_includes_anonymous` | `true` | Add anonymous to Everyone group |
| `ludus_null_session_fallback` | `true` | Allow null session fallback |

## Attack Techniques Enabled

- **Anonymous RPC enumeration** — `rpcclient -U '' -N <dc> -c enumdomusers`
- **Anonymous SMB share listing** — `smbclient -N -L //<dc>`
- **LSA SID enumeration** — `lookupsid.py anonymous@<dc>`
- **CrackMapExec anonymous** — `nxc smb <dc> -u '' -p ''`

## Example Ludus Range Config

```yaml
ludus:
  - vm_name: "{{ range_id }}-DC01"
    hostname: dc01
    template: win2022-server-x64-template
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: lab.local
      role: primary-dc
    roles:
      - ludus_ad_anonymous_rpc
```

## Ludus Notes

- On Server 2016+/2022, registry settings alone are **not sufficient** — the role also adds ANONYMOUS LOGON to the Pre-Windows 2000 Compatible Access group
- A full reboot is required for LSA registry changes to take effect (handled automatically)

## Dependencies

None.

## Author

Bad Sector Labs
