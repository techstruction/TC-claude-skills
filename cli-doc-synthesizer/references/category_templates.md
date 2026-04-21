# Category Templates for Common Vendors

Use these as starting points when defining the output category structure. Adjust based on
the actual source folders and content the user has.

---

## NetApp ONTAP (proven — 10 files)

```
01_ONTAP_Cluster_Admin_Fundamentals.md
   Sources: Cluster commands, Log commands, SP commands
   Covers: autosupport, node mgmt, job schedules, NTP, health status, SP/BMC access

02_SVM_and_Networking.md
   Sources: Network commands, LDAP commands
   Covers: SVM create/show, LIF management, routing, DNS, LDAP, name service switch

03_Volumes_and_Aggregates.md
   Sources: Volume commands, Aggregate commands, Deduplication commands
   Covers: aggr show/create/add-disks, vol create/modify/move, autosize, dedup, efficiency

04_SnapMirror_and_Replication.md
   Sources: Snapshot commands (SnapMirror section), Word Docs from Tim
   Covers: snapmirror show/init/update/quiesce/break/resync, schedule/policy

05_Snapshot_and_Backup.md
   Sources: Snapshot commands
   Covers: snapshot show/create/policy/schedule/delete/restore, reserve

06_CIFS_NFS_SMB_Management.md
   Sources: NFS commands, Security commands, Quota commands, LDAP commands
   Covers: export policies, NFS enable, CIFS shares, quotas, security tracing

07_Hardware_Storage_Shelf_Operations.md
   Sources: ACP commands, Disc commands, IGroup commands, Lun commands
   Covers: ACP status/firmware, disk inventory/replacement, iGroups, LUNs, shelf/IOM

08_Troubleshooting_and_Health_Checks.md
   Sources: Log commands, Performance commands, Cluster commands, Network commands, Disc commands
   Covers: health runbook, event log, HA status, network diag, perf stats, RAID, SP

09_Common_Runbooks.md
   Sources: All categories (cross-cutting)
   Covers: NFS provision end-to-end, CIFS share, DR failover, disk replace, SVM setup,
           morning health check, upgrade pre-checks, aggregate expansion

10_Deprecated_Dangerous_Commands.md
   Sources: All categories (extract warnings/cautions)
   Covers: 7-Mode→Cluster-Mode mapping, destructive commands, dangerous configs, risk table
```

---

## Cisco IOS / IOS-XE (suggested — 8 files)

```
01_Device_Administration.md
   Covers: show version, hostname, clock, NTP, logging, reload, config archive

02_Interfaces_and_VLANs.md
   Covers: show interfaces, ip address, shutdown/no shutdown, switchport, vlan, trunk

03_Routing.md
   Covers: ip route, show ip route, OSPF basics, BGP basics, route redistribution

04_Access_Control_and_Security.md
   Covers: ACLs, AAA, TACACS+/RADIUS, SSH config, console/vty access, enable secret

05_Switching_and_STP.md
   Covers: spanning-tree, portfast, BPDU guard, EtherChannel/LACP, port security

06_High_Availability.md
   Covers: HSRP, VRRP, NSF/SSO, redundant supervisors, failover

07_Troubleshooting_and_Diagnostics.md
   Covers: ping, traceroute, debug, show log, show processes cpu, show memory, CDP

08_Deprecated_Dangerous_Commands.md
   Covers: no ip domain-lookup side effects, debug all (dangerous), write erase,
           legacy commands replaced in IOS-XE
```

---

## Palo Alto PAN-OS (suggested — 8 files)

```
01_Device_and_System_Administration.md
   Covers: show system info, set deviceconfig, NTP, DNS, admin users, licenses

02_Network_Interfaces_and_Zones.md
   Covers: show interface all, set network interface, zones, virtual routers

03_Security_Policies.md
   Covers: show security policy, rule base, address objects, service objects, policy hit counts

04_NAT_and_Routing.md
   Covers: NAT rules, static routes, OSPF, BGP, show routing route

05_VPN_and_GlobalProtect.md
   Covers: IPsec tunnels, GlobalProtect gateway/portal, tunnel status, troubleshooting

06_Threat_Prevention_and_Profiles.md
   Covers: antivirus, anti-spyware, URL filtering, wildfire, security profiles

07_Monitoring_and_Troubleshooting.md
   Covers: show log, traffic logs, threat logs, packet capture, test security-policy-match

08_Deprecated_Dangerous_Commands.md
   Covers: request system private-data-reset (destructive), debug commands, legacy syntax
```

---

## VMware vSphere CLI / ESXi (suggested — 7 files)

```
01_Host_Administration.md
   Covers: esxcli system info, hostname, NTP, syslog, maintenance mode, reboot

02_Networking.md
   Covers: esxcli network ip interface, vSwitch, portgroup, vmknic, routing

03_Storage_and_Datastores.md
   Covers: esxcli storage core, rescan, datastore list, multipath, NFS/iSCSI mounts

04_Virtual_Machine_Operations.md
   Covers: vim-cmd vmsvc, power on/off/reset, snapshot, migration (vMotion)

05_Performance_and_Monitoring.md
   Covers: esxtop, esxcli system stats, resxtop, vimtop, log locations

06_Troubleshooting.md
   Covers: vmkping, esxcli network diag, vobd, hostd restart, PSA troubleshooting

07_Deprecated_Dangerous_Commands.md
   Covers: esxcfg-* legacy commands, direct host management cautions, unsupported configs
```
