# CIFS / NFS / SMB Management

> **Scope:** NFS export policies, CIFS shares, SMB configuration, NFS client access, protocol auditing, security styles, quota management.
> **Applies to:** ONTAP 8.x (7-Mode and Cluster-Mode), ONTAP 9.x
> **Source folders:** NetApp NFS commands, NetApp Security commands, NetApp Quota commands, NetApp LDAP commands

---

## Task: Show NFS export policies and rules

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Audit which clients have access to which volumes; troubleshoot NFS mount failures.

**Commands:**
```
vserver export-policy show
vserver export-policy rule show -policyname <policy-name>
vserver export-policy rule show -vserver <svm>
vserver export-policy show -fields policy-name,vserver
volume show -fields export-policy
```

**Examples:**
```
NETCLSMDF1::> vserver export-policy rule show -policyname default
NETCLSMDF1::> vserver export-policy rule show -vserver svm_prod
NETCLSMDF1::> volume show -vserver svm_prod -fields export-policy
```

**Validation commands:**
- `vserver export-policy rule show -policyname <policy>`
- `vserver export-policy check-access -vserver <svm> -volume <vol> -client-ip <ip> -authentication-method sys -protocol nfs3 -access-type read-write`

**Rollback / Caution:** Read-only.

**Related tasks:** Create export policy, modify access rules, NFS mount troubleshooting

**Source docs:** NetApp NFS commands

---

## Task: Create an NFS export policy and rules

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Grant NFS client access to a volume; restrict access by IP or subnet.

**Commands:**
```
vserver export-policy create -vserver <svm> -policyname <policy-name>
vserver export-policy rule create -vserver <svm> -policyname <policy-name> -clientmatch <ip/subnet/hostname> -rorule sys -rwrule sys -superuser sys -anon 65534
volume modify -vserver <svm> -volume <vol> -policy <policy-name>
```

**Examples:**
```
NETCLSMDF1::> vserver export-policy create -vserver svm_prod -policyname prod_nfs
NETCLSMDF1::> vserver export-policy rule create -vserver svm_prod -policyname prod_nfs -clientmatch 10.10.1.0/24 -rorule sys -rwrule sys -superuser sys -anon 65534
NETCLSMDF1::> volume modify -vserver svm_prod -volume vol_data01 -policy prod_nfs
```

**Validation commands:**
- `vserver export-policy rule show -policyname <policy>`
- `vserver export-policy check-access -vserver <svm> -volume <vol> -client-ip <ip> -authentication-method sys -protocol nfs3 -access-type read-write`

**Rollback / Caution:** Using `0.0.0.0/0` as clientmatch opens access to all hosts. Always restrict to known subnets. Setting `superuser sys` grants root access — use only for trusted admin hosts.

**Related tasks:** Volume creation, junction path, client NFS mount

**Source docs:** NetApp NFS commands

---

## Task: Enable and configure NFS on an SVM

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, SVM created

**When to use:** First-time NFS setup on an SVM.

**Commands:**
```
nfs create -vserver <svm> -access true -v3 enabled -v4.0 enabled -v4.1 enabled
nfs show -vserver <svm>
nfs modify -vserver <svm> -v4.0 enabled
vserver nfs show
```

**Examples:**
```
NETCLSMDF1::> nfs create -vserver svm_prod -access true -v3 enabled -v4.1 enabled
NETCLSMDF1::> nfs show -vserver svm_prod
```

**Validation commands:**
- `nfs show -vserver <svm>`
- `vserver show -vserver <svm> -fields allowed-protocols`

**Rollback / Caution:** Enabling NFS v4.1 requires pNFS/session trunking awareness on clients. Test with a single client before enabling broadly.

**Related tasks:** Export policy, LIF creation, DNS/LDAP setup

**Source docs:** NetApp NFS commands

---

## Task: Show and manage CIFS shares

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin, CIFS service running on SVM

**When to use:** Audit share configurations, add new shares, troubleshoot access.

**Commands:**
```
cifs share show
cifs share show -vserver <svm>
cifs share show -vserver <svm> -share-name <share> -instance
cifs share create -vserver <svm> -share-name <share> -path <junction-path>
cifs share modify -vserver <svm> -share-name <share> -comment "<description>"
cifs share access-control show
```

**Examples:**
```
NETCLSMDF1::> cifs share show -vserver svm_prod
NETCLSMDF1::> cifs share create -vserver svm_prod -share-name data01 -path /vol_data01
NETCLSMDF1::> cifs share access-control show -vserver svm_prod
```

**Validation commands:**
- `cifs share show -vserver <svm> -share-name <share>`
- Test from Windows: `net use \\<svm-lif>\<share>`

**Rollback / Caution:** A CIFS share requires a valid junction path. If the volume is unmounted, the share will be inaccessible.

**Related tasks:** CIFS setup, AD join, volume junction, access control

**Source docs:** NetApp Security commands, NetApp NFS commands

---

## Task: Show and manage quotas

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Enforce per-user, per-group, or per-volume space limits.

**Commands:**
```
quota show -vserver <svm> -volume <vol>
quota policy rule show -vserver <svm>
quota policy rule create -vserver <svm> -policy-name default -volume <vol> -type user -target "" -disk-limit <size>g -file-limit <n>
quota on -vserver <svm> -volume <vol>
quota off -vserver <svm> -volume <vol>
quota resize -vserver <svm> -volume <vol>
quota report -vserver <svm> -volume <vol>
```

**Examples:**
```
NETCLSMDF1::> quota policy rule create -vserver svm_prod -policy-name default -volume vol_home -type user -target "" -disk-limit 50g
NETCLSMDF1::> quota on -vserver svm_prod -volume vol_home
NETCLSMDF1::> quota report -vserver svm_prod -volume vol_home
```

**Validation commands:**
- `quota show -vserver <svm> -volume <vol>`
- `quota report -vserver <svm> -volume <vol>`

**Rollback / Caution:** Enabling quotas on a large volume with many users/files can cause a brief performance impact during initialization. Run `quota on` during off-peak hours. `quota resize` applies rule changes without reinitializing.

**Related tasks:** LDAP user/group lookup, export policy, volume capacity

**Source docs:** NetApp Quota commands

---

## Task: NFS access troubleshooting

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Client cannot mount or gets permission denied; verify access path.

**Commands:**
```
vserver export-policy check-access -vserver <svm> -volume <vol> -client-ip <ip> -authentication-method sys -protocol nfs3 -access-type read-write
network ping -vserver <svm> -destination <client-ip>
vserver services name-service getxxbynametype -vserver <svm> -database passwd -name <username>
vserver nfs show -vserver <svm>
nfs check -vserver <svm>
```

**Examples:**
```
NETCLSMDF1::> vserver export-policy check-access -vserver svm_prod -volume vol_data01 -client-ip 10.10.1.100 -authentication-method sys -protocol nfs3 -access-type read-write
```

**Validation commands:**
- Export policy check returns `access: read-write`
- `network ping` succeeds from SVM LIF to client

**Rollback / Caution:** Read-only diagnostics.

**Related tasks:** Export policy, LDAP configuration, name service switch

**Source docs:** NetApp NFS commands, NetApp LDAP commands

---

## Task: Security tracing — trace file access for a user

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Diagnose permission denied errors for specific users; trace NFS or CIFS access decisions.

**Commands:**
```
vserver security trace filter create -vserver <svm> -index 1 -client-ip <ip> -unix-user <user> -trace-allow true -enabled true
vserver security trace filter show -vserver <svm>
vserver security trace trace-result show -vserver <svm>
vserver security trace filter delete -vserver <svm> -index 1
```

**Examples:**
```
NETCLSMDF1::> vserver security trace filter create -vserver svm_prod -index 1 -client-ip 10.10.1.100 -unix-user jsmith -trace-allow true -enabled true
NETCLSMDF1::> vserver security trace trace-result show -vserver svm_prod
NETCLSMDF1::> vserver security trace filter delete -vserver svm_prod -index 1
```

**Validation commands:**
- `vserver security trace trace-result show` — shows allow/deny decisions per path

**Rollback / Caution:** Always delete trace filters after use — they add overhead. Do not leave active trace filters in production.

**Related tasks:** Export policy check, LDAP, NFS troubleshooting

**Source docs:** NetApp Security commands


---

# Hardware / Storage Shelf Operations

> **Scope:** ACP (Alternate Control Path), shelf management, IOM modules, disk management, disk replacement, firmware, LUN/iGroup management.
> **Applies to:** ONTAP 8.x (7-Mode and Cluster-Mode), ONTAP 9.x
> **Source folders:** NetApp ACP commands, NetApp Disc commands, NetApp IGroup commands, NetApp Lun commands

---

## Task: Show ACP (Alternate Control Path) status

**Applies to:** ONTAP 8.x (primarily 7-Mode and early Cluster-Mode)

**Prereqs:** Node shell access or cluster admin with `node run`

**When to use:** Verify ACP connectivity for all shelf IOM modules; diagnose shelf communication issues.

**Commands:**
```
storage show acp -a (7-Mode node shell)
node run -node <node> storage show acp -a
storage shelf acp module show -fields module-name,protocol-version,firmware-version,shelf-serial-number,iom-type,state
acpadmin list_all (7-Mode node shell)
```

**Examples:**
```
NETCLSMDF1-01> storage show acp -a
NETCLSMDF1::> node run -node NETCLSMDF1-01 storage show acp -a
NETCLSMDF1::> storage shelf acp module show -fields module-name,protocol-version,firmware-version,iom-type,state
```

**Validation commands:**
- ACP Status: `Active`
- ACP Connectivity Status: `Full Connectivity`
- All IOM modules state: `active`

**Rollback / Caution:** Read-only. If ACP shows `No Connectivity`, check the ACP Ethernet cable on the shelf and the e0P port on the controller.

**Related tasks:** ACP firmware update, shelf cabling, IOM replacement

**Source docs:** NetApp ACP Cabling.txt, NetApp ACP Configuration Command.docx, NetApp ACP Connections Cluster 9 Command.docx

---

## Task: Check ACP firmware version and update

**Applies to:** ONTAP 8.x, ONTAP 9.x

**Prereqs:** Cluster admin or node shell, ACP active

**When to use:** During firmware maintenance; verify all IOM modules are on the same firmware version.

**Commands:**
```
storage shelf acp module show -fields module-name,firmware-version,iom-type,state
storage firmware update (7-Mode node shell)
acpadmin update_flash (7-Mode: update ACP firmware)
node run -node <node> acpadmin update_flash
storage shelf firmware show
```

**Examples:**
```
NETCLSMDF1::> storage shelf acp module show -fields module-name,firmware-version,state
NETCLSMDF1::> node run -node NETCLSMDF1-01 acpadmin update_flash
```

**Validation commands:**
- All modules on same firmware version
- `storage shelf acp module show -fields state` — all: `active`

**Rollback / Caution:** Firmware updates are applied to IOM modules individually. Do not interrupt power during update. Always update both IOM A and IOM B modules on each shelf.

**Related tasks:** ACP status, shelf health, IOM replacement

**Source docs:** NetApp ACP Firmware Show.docx, NetApp ACP Firmware Update Commands.docx, NetApp ACP Firmware Update Command 2020.docx

---

## Task: Show disk inventory and health

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Disk health audit, identify broken/failed disks, spare disk inventory.

**Commands:**
```
storage disk show
storage disk show -broken
storage disk show -container-type spare
storage disk show -fields disk,node,container-type,rpm,type,model,firmware-revision,serial-number
disk show (7-Mode node shell)
disk show -v (7-Mode: verbose)
disk show -n (7-Mode: show names)
storage disk show -state broken
```

**Examples:**
```
NETCLSMDF1::> storage disk show -broken
NETCLSMDF1::> storage disk show -container-type spare
NETCLSMDF1::> storage disk show -fields disk,node,container-type,type,rpm
```

**Validation commands:**
- `storage disk show -broken` — should return 0 results in healthy system
- `storage disk show -container-type spare` — confirms available spares

**Rollback / Caution:** Read-only.

**Related tasks:** Replace failed disk, add spare, aggregate rebuild

**Source docs:** NetApp Disc commands

---

## Task: Replace a failed disk

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, replacement disk of same type/size/RPM, aggregate in degraded state

**When to use:** After receiving a disk failure alert or finding a broken disk via `storage disk show -broken`.

**Commands:**
```
storage disk show -broken
storage disk show -fields disk,node,aggregate,container-type
storage disk replace -disk <disk-name> -replacement <spare-disk-name>
storage aggregate show -fields state,raidstatus
storage disk show -fields disk,container-type,aggregate
```

**Examples:**
```
NETCLSMDF1::> storage disk show -broken
NETCLSMDF1::> storage disk show -container-type spare
NETCLSMDF1::> storage disk replace -disk 1.0.5 -replacement 2.0.10
NETCLSMDF1::> storage aggregate show -fields state,raidstatus
```

**Validation commands:**
- `storage disk show -broken` — no broken disks after rebuild
- `storage aggregate show -fields state` — all aggregates: `online`
- `storage aggregate show -fields raidstatus` — status: `normal`

**Rollback / Caution:** Physical hot-swap is required — ensure the disk is physically replaced in the correct slot. RAID rebuild begins automatically after replacement. Monitor rebuild progress with `storage aggregate show -fields raidstatus`. Do not remove a second disk from the same RAID group during rebuild — this causes data loss.

**Related tasks:** Aggregate health, disk inventory, add spare disks

**Source docs:** NetApp Disc commands

---

## Task: Show and manage iGroups (initiator groups)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin, SAN protocol configured (iSCSI or FC)

**When to use:** Manage which hosts have access to LUNs via iSCSI or FC.

**Commands:**
```
igroup show
igroup show -vserver <svm>
igroup show -igroup <igroup-name> -instance
igroup create -vserver <svm> -igroup <igroup-name> -protocol <iscsi|fcp|mixed> -ostype <windows|linux|vmware|solaris>
igroup add -vserver <svm> -igroup <igroup-name> -initiator <iqn-or-wwpn>
igroup remove -vserver <svm> -igroup <igroup-name> -initiator <iqn-or-wwpn>
```

**Examples:**
```
NETCLSMDF1::> igroup show -vserver svm_prod
NETCLSMDF1::> igroup create -vserver svm_prod -igroup esxi_cluster01 -protocol iscsi -ostype vmware
NETCLSMDF1::> igroup add -vserver svm_prod -igroup esxi_cluster01 -initiator iqn.2020-04.com.vmware:esxi01
```

**Validation commands:**
- `igroup show -igroup <name> -instance`
- `lun mapping show -igroup <name>`

**Rollback / Caution:** Removing an initiator from an iGroup while a LUN is mapped and in use will cause the host to lose access immediately. Always unmount/quiesce the workload first.

**Related tasks:** LUN creation, LUN mapping, iSCSI configuration

**Source docs:** NetApp IGroup commands

---

## Task: Show and manage LUNs

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin, iSCSI or FC protocol enabled

**When to use:** Create, map, resize LUNs for SAN workloads (VMware datastores, databases, Windows volumes).

**Commands:**
```
lun show
lun show -vserver <svm>
lun show -fields lun,vserver,volume,size,state,mapped
lun create -vserver <svm> -volume <vol> -lun <lun-name> -size <size> -ostype <vmware|windows|linux>
lun map -vserver <svm> -volume <vol> -lun <lun-name> -igroup <igroup-name>
lun mapping show
lun resize -vserver <svm> -volume <vol> -lun <lun-name> -size <new-size>
lun offline -vserver <svm> -volume <vol> -lun <lun-name>
lun online -vserver <svm> -volume <vol> -lun <lun-name>
```

**Examples:**
```
NETCLSMDF1::> lun create -vserver svm_prod -volume vol_san01 -lun lun01 -size 200g -ostype vmware
NETCLSMDF1::> lun map -vserver svm_prod -volume vol_san01 -lun lun01 -igroup esxi_cluster01
NETCLSMDF1::> lun show -vserver svm_prod -fields lun,size,state,mapped
```

**Validation commands:**
- `lun show -fields state,mapped`
- `lun mapping show -lun <lun-name>`
- From host: rescan HBA/iSCSI and verify LUN visible

**Rollback / Caution:** LUN resize requires the host to recognize the new size (rescan or extend filesystem). LUNs cannot be shrunk. Taking a LUN offline disconnects all hosts using it.

**Related tasks:** iGroup management, iSCSI configuration, volume creation for LUN hosting

**Source docs:** NetApp Lun commands

---

## Task: Show shelf and IOM module status

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Health audit of storage shelves; verify IOM modules are active and firmware is current.

**Commands:**
```
storage shelf show
storage shelf show -instance
storage shelf show -fields shelf-id,connection-type,state,module-count
storage shelf show-bay
storage shelf port show
storage shelf acp show
```

**Examples:**
```
NETCLSMDF1::> storage shelf show
NETCLSMDF1::> storage shelf show -fields shelf-id,state,connection-type
```

**Validation commands:**
- `storage shelf show -fields state` — all shelves: `online`

**Rollback / Caution:** Read-only.

**Related tasks:** ACP status, IOM firmware, disk replacement

**Source docs:** NetApp ACP commands, NetApp Disc commands


---

# Troubleshooting and Health Checks

> **Scope:** System health, event logs, performance diagnostics, network troubleshooting, disk/aggregate issues, NFS/CIFS access problems, SP/console access.
> **Applies to:** ONTAP 8.x (7-Mode and Cluster-Mode), ONTAP 9.x
> **Source folders:** NetApp Log commands, NetApp Performance commands, NetApp Cluster commands, NetApp Network commands, NetApp Disc commands

---

## Task: Full system health check runbook

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Morning health check, post-maintenance validation, incident triage.

**Commands:**
```
cluster show
system health status show
system health alert show
system health alert show -state unacknowledged
storage failover show
storage disk show -broken
storage aggregate show -state !online
volume show -state !online
network interface show -status-oper down
event log show -severity EMERGENCY,CRITICAL,ERROR -time >8h
system node show -fields health,uptime
```

**Examples:**
```
NETCLSMDF1::> cluster show
NETCLSMDF1::> system health status show
NETCLSMDF1::> system health alert show -state unacknowledged
NETCLSMDF1::> event log show -severity ERROR -time >24h
```

**Validation commands:**
- All nodes healthy: `cluster show`
- No broken disks: `storage disk show -broken`
- No offline volumes: `volume show -state !online`
- No down LIFs: `network interface show -status-oper down`

**Rollback / Caution:** Read-only health check — no changes.

**Related tasks:** Event log review, disk replacement, LIF revert, aggregate repair

**Source docs:** NetApp Cluster commands, NetApp Log commands

---

## Task: View and filter the event log

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Investigate alerts, errors, or unexpected behavior.

**Commands:**
```
event log show
event log show -severity EMERGENCY
event log show -severity CRITICAL
event log show -severity ERROR
event log show -time >1h
event log show -node <node>
event log show -messagename <messagename>
event log show -fields time,node,severity,messagename,description
event log show -count 50
```

**Examples:**
```
NETCLSMDF1::> event log show -severity ERROR,CRITICAL -time >24h -fields time,node,severity,messagename,description
NETCLSMDF1::> event log show -messagename raid.rg.degrade
```

**Validation commands:**
- No EMERGENCY or CRITICAL events in past 24h in a healthy system

**Rollback / Caution:** Read-only.

**Related tasks:** AutoSupport, SNMP, disk replacement, aggregate repair

**Source docs:** NetApp Log commands

---

## Task: Check storage failover (HA) status

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Verify HA pair is healthy; check whether a takeover has occurred.

**Commands:**
```
storage failover show
storage failover show -instance
storage failover show -fields node,partner-name,possible,state-description
storage failover takeover -ofnode <node> -option immediate (CAUTION: initiates takeover)
storage failover giveback -ofnode <node>
```

**Examples:**
```
NETCLSMDF1::> storage failover show
NETCLSMDF1::> storage failover show -fields node,possible,state-description
```

**Validation commands:**
- `storage failover show` — possible: `true` for both nodes
- State: `Connected to partner`

**Rollback / Caution:** `storage failover takeover` immediately moves the partner's resources to this node — disruptive for SAN workloads. Only run during planned maintenance or actual node failure. Use `storage failover giveback` to return resources after maintenance.

**Related tasks:** Node maintenance, firmware update, node replacement

**Source docs:** NetApp Cluster commands, Word Docs from Tim

---

## Task: Diagnose network connectivity

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Client can't reach storage; NFS/CIFS mount failures; SnapMirror transfer failures.

**Commands:**
```
network ping -vserver <svm> -destination <ip>
network ping -lif <lif-name> -destination <ip>
network interface show -status-oper down
network port show -fields link,health-status
network interface revert -vserver <svm> -lif <lif-name>
network interface migrate -vserver <svm> -lif <lif-name> -dest-node <node> -dest-port <port>
network route show -vserver <svm>
```

**Examples:**
```
NETCLSMDF1::> network ping -vserver svm_prod -destination 10.10.1.100
NETCLSMDF1::> network interface show -status-oper down
NETCLSMDF1::> network interface revert -vserver svm_prod -lif svm_prod_nfs1
```

**Validation commands:**
- `network ping` succeeds
- `network interface show -status-oper down` — no results

**Rollback / Caution:** `network interface migrate` is temporary — use `revert` to return the LIF to its home port.

**Related tasks:** LIF management, routing, NFS/CIFS troubleshooting

**Source docs:** NetApp Network commands

---

## Task: Performance diagnostics — system throughput and latency

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Investigate slow NFS/CIFS performance, high latency, or throughput bottlenecks.

**Commands:**
```
statistics start -object volume -instance <vol> -interval 5 -count 3
statistics show -object volume
statistics show -object volume -instance <vol> -counter read_ops,write_ops,avg_latency
qos statistics volume show
qos statistics workload show
node run -node <node> sysstat -c 5 (7-Mode)
node run -node <node> stats show -i 5 (7-Mode)
```

**Examples:**
```
NETCLSMDF1::> statistics start -object volume -instance vol_data01 -interval 5 -count 6
NETCLSMDF1::> statistics show -object volume -instance vol_data01 -counter read_ops,write_ops,avg_latency
```

**Validation commands:**
- Latency under 1ms (SSD), under 5ms (SAS) for healthy workloads
- No single volume consuming disproportionate ops

**Rollback / Caution:** Statistics collection adds minor overhead. Limit collection intervals to diagnostic periods.

**Related tasks:** QoS policy, workload analysis, identify hot volumes

**Source docs:** NetApp Performance commands

---

## Task: Identify and address full aggregates

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Aggregate approaching 90%+ usage; volumes failing to grow; autosize failing.

**Commands:**
```
storage aggregate show -fields aggregate,usedsize,availsize,percent-used,state
storage aggregate show-space -aggregate <aggr>
volume show -aggregate <aggr> -fields volume,size,available,percent-used
snapshot list /vol/* (7-Mode: look for large snapshots)
volume snapshot show -vserver <svm> -fields snapshot,size -sortby size
```

**Examples:**
```
NETCLSMDF1::> storage aggregate show -fields aggregate,percent-used,availsize
NETCLSMDF1::> storage aggregate show-space -aggregate aggr1_n01
NETCLSMDF1::> volume snapshot show -vserver svm_prod -fields snapshot,size
```

**Validation commands:**
- Aggregate percent-used under 85%
- Available space sufficient for largest volume autosize increment

**Rollback / Caution:** Aggregates over 95% can cause volumes to go offline. Proactive monitoring is critical. Remediation options: delete snapshots, move volumes, add disks, delete unneeded volumes.

**Related tasks:** Add disks to aggregate, delete snapshots, volume move, thin provisioning

**Source docs:** NetApp Aggregate commands, NetApp Volume commands

---

## Task: Check and repair RAID group status

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** After disk failure; aggregate in degraded or broken state.

**Commands:**
```
storage aggregate show -fields state,raidstatus
aggr status -v (7-Mode node shell: detailed RAID group view)
storage disk show -broken
storage disk show -container-type maintenance
storage aggregate verify start -aggregate <aggr>
```

**Examples:**
```
NETCLSMDF1::> storage aggregate show -fields aggregate,state,raidstatus
NETCLSMDF1::> storage disk show -broken
NETCLSMDF1::> storage aggregate show -fields aggregate,raidstatus
```

**Validation commands:**
- `storage aggregate show -fields raidstatus` — `normal`
- `storage disk show -broken` — empty

**Rollback / Caution:** A `degraded` RAID group is running without redundancy — replace failed disk immediately. A `broken` aggregate requires NetApp support. Never remove additional disks from a degraded RAID group.

**Related tasks:** Disk replacement, add spare disks, aggregate repair

**Source docs:** NetApp Disc commands, NetApp Aggregate commands

---

## Task: SP (Service Processor) out-of-band access

**Applies to:** ONTAP 8.x, ONTAP 9.x

**Prereqs:** SP IP configured and reachable, SP credentials

**When to use:** Node is unresponsive via SSH; need to power cycle or access console.

**Commands:**
```
system service-processor show
system service-processor ssh show
ssh -l admin <sp-ip>
  system power off
  system power on
  system reset
  sp status
  sp log messages
```

**Examples:**
```
# From cluster:
NETCLSMDF1::> system service-processor show

# Via SSH directly to SP:
ssh admin@10.0.1.10
sp> system power off
sp> system power on
sp> sp status
```

**Validation commands:**
- `system service-processor show -fields ip-address,status`
- SP status: `online`

**Rollback / Caution:** `system power off` immediately cuts power — no graceful shutdown. Data loss possible if NVRAM not flushed. Use `system node halt -node <node>` from ONTAP first if possible.

**Related tasks:** Node reboot, SP network configuration, console access

**Source docs:** NetApp SP commands


---

# Common Operational Runbooks

> **Scope:** End-to-end multi-step procedures combining commands from multiple categories. Each runbook is a complete workflow for a common operational task.
> **Applies to:** ONTAP 8.x (Cluster-Mode), ONTAP 9.x
> **Source folders:** All categories — Cluster, SVM, Network, Volume, Aggregate, Snapshot, SnapMirror, NFS, Disc, SP commands

---

## Runbook: Provision a new NFS volume end-to-end

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, SVM exists with NFS enabled, aggregate with sufficient free space

**When to use:** New application team requests shared NFS storage.

**Steps:**

### 1. Verify aggregate has space
```
storage aggregate show -fields aggregate,percent-used,availsize
```

### 2. Create the volume
```
volume create -vserver <svm> -volume <vol-name> -aggregate <aggr> -size <size>g -junction-path /<vol-name> -space-guarantee none -snapshot-policy default
```

### 3. Set autosize (optional but recommended)
```
volume modify -vserver <svm> -volume <vol-name> -autosize-mode grow -autosize-maximum <max-size>g -autosize-grow-threshold-percent 80
```

### 4. Create export policy
```
vserver export-policy create -vserver <svm> -policyname <policy-name>
vserver export-policy rule create -vserver <svm> -policyname <policy-name> -clientmatch <ip/subnet> -rorule sys -rwrule sys -superuser sys -anon 65534
```

### 5. Apply export policy to volume
```
volume modify -vserver <svm> -volume <vol-name> -policy <policy-name>
```

### 6. Verify volume is online and mounted
```
volume show -vserver <svm> -volume <vol-name> -fields state,junction-path,size,available,export-policy
```

### 7. Test NFS access from client
```
vserver export-policy check-access -vserver <svm> -volume <vol-name> -client-ip <client-ip> -authentication-method sys -protocol nfs3 -access-type read-write
```

**Validation:**
- Volume state: `online`
- Junction path set
- Export policy check returns `access: read-write`
- Client can mount: `mount -t nfs <svm-lif-ip>:/<vol-name> /mnt/test`

**Rollback:**
```
volume offline -vserver <svm> -volume <vol-name>
volume delete -vserver <svm> -volume <vol-name>
vserver export-policy delete -vserver <svm> -policyname <policy-name>
```

**Source docs:** NetApp Volume commands, NetApp NFS commands, NetApp Aggregate commands

---

## Runbook: Provision a new CIFS (SMB) share end-to-end

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, SVM joined to Active Directory, CIFS service running

**When to use:** New Windows/SMB share requested for a department or application.

**Steps:**

### 1. Verify CIFS service is running on SVM
```
vserver cifs show -vserver <svm>
```

### 2. Check aggregate space
```
storage aggregate show -fields aggregate,percent-used,availsize
```

### 3. Create the volume
```
volume create -vserver <svm> -volume <vol-name> -aggregate <aggr> -size <size>g -junction-path /<vol-name> -security-style ntfs -snapshot-policy default
```

### 4. Create the CIFS share
```
cifs share create -vserver <svm> -share-name <share-name> -path /<vol-name>
```

### 5. Verify share is visible
```
cifs share show -vserver <svm> -share-name <share-name>
```

### 6. Set NTFS permissions (if needed, from Windows)
- Map the share: `net use Z: \\<svm-lif>\<share-name>`
- Set ACLs via Windows Security properties

**Validation:**
- `cifs share show` returns share with correct path
- `volume show -fields state` — volume online
- Windows client can access: `net use \\<svm-lif>\<share-name>`

**Rollback:**
```
cifs share delete -vserver <svm> -share-name <share-name>
volume offline -vserver <svm> -volume <vol-name>
volume delete -vserver <svm> -volume <vol-name>
```

**Source docs:** NetApp Security commands, NetApp NFS commands, NetApp Volume commands

---

## Runbook: SnapMirror DR failover procedure

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin on DR cluster, SnapMirror relationship exists, source cluster unavailable or maintenance

**When to use:** Declared DR event; source site unavailable; planned DR test.

**Steps:**

### 1. Verify SnapMirror relationship state
```
snapmirror show -fields source-volume,destination-volume,state,status,lag-time
```

### 2. (If source accessible) Trigger final update to minimize data loss
```
snapmirror update -destination-path <dr-svm>:<dr-vol>
snapmirror show -destination-volume <dr-vol> -fields status,lag-time
```

### 3. Quiesce the relationship
```
snapmirror quiesce -destination-path <dr-svm>:<dr-vol>
snapmirror show -destination-volume <dr-vol> -fields status
```
Wait for status: `quiesced`

### 4. Break the SnapMirror relationship
```
snapmirror break -destination-path <dr-svm>:<dr-vol>
snapmirror show -destination-volume <dr-vol> -fields state
```
State should be: `broken-off`

### 5. Mount the DR volume
```
volume mount -vserver <dr-svm> -volume <dr-vol> -junction-path /<dr-vol>
```

### 6. Verify volume is online and accessible
```
volume show -vserver <dr-svm> -volume <dr-vol> -fields state,junction-path
```

### 7. Point clients to DR LIF
- Update DNS to resolve to DR site LIF IP
- Or: remount NFS/CIFS clients using DR site address

**Failback procedure (after source site recovery):**
```
# Re-establish replication from DR → Source (reverse resync)
snapmirror resync -destination-path <prod-svm>:<prod-vol>
# Monitor until synced
snapmirror show -fields lag-time,status
# Once synced: quiesce DR, break, remount at production, resume normal SnapMirror direction
```

**Validation:**
- `snapmirror show -fields state` — `broken-off`
- `volume show -fields state` — `online`
- Clients can mount and read/write data
- Application team confirms data integrity

**Rollback / Caution:** Breaking SnapMirror is irreversible without resync. Any data written to DR volume after break will be lost on resync. Always snapshot the DR volume before resync if preservation is needed.

**Source docs:** NetApp snapshot commands, Word Docs from Tim

---

## Runbook: Replace a failed disk and monitor rebuild

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, replacement disk available (same type, size, RPM), disk physically hot-swappable

**When to use:** Disk failure alert received; `storage disk show -broken` shows failed disk.

**Steps:**

### 1. Identify the failed disk
```
storage disk show -broken
storage disk show -fields disk,node,aggregate,container-type,rpm,type,model
```
Note the disk name (e.g., `1.0.5`), which shelf/bay it's in, and which aggregate it belongs to.

### 2. Check RAID status of affected aggregate
```
storage aggregate show -fields aggregate,state,raidstatus
```
Expected: `degraded` (running without redundancy).

### 3. Identify available spare disk
```
storage disk show -container-type spare -fields disk,node,type,rpm,size
```
Match type (SAS/SATA/NVMe), RPM, and size.

### 4. Physically replace the disk
- Identify the disk by slot location on the shelf
- Hot-swap the failed disk with the replacement
- ONTAP will detect the new disk automatically

### 5. (Optional) Initiate replacement explicitly
```
storage disk replace -disk <failed-disk> -replacement <spare-disk>
```

### 6. Monitor RAID rebuild progress
```
storage aggregate show -fields aggregate,state,raidstatus
storage disk show -fields disk,container-type,aggregate
```
RAID status will show `reconstructing` during rebuild.

### 7. Confirm rebuild complete
```
storage aggregate show -fields raidstatus
storage disk show -broken
```
- RAID status: `normal`
- `storage disk show -broken` — empty

**Validation:**
- `storage aggregate show -fields state` — `online`
- `storage aggregate show -fields raidstatus` — `normal`
- No alerts in `system health alert show`

**Caution:** Never remove a second disk from the same RAID group during rebuild — this causes data loss and can bring the aggregate offline. Monitor rebuild to completion before performing any further disk operations.

**Source docs:** NetApp Disc commands, NetApp Aggregate commands

---

## Runbook: New SVM setup end-to-end

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, aggregate available, network subnet and IP addresses planned, DNS server details available

**When to use:** Onboarding a new tenant, application team, or department that needs isolated storage.

**Steps:**

### 1. Create the SVM
```
vserver create -vserver <svm-name> -rootvolume <svm-name>_root -aggregate <aggr> -rootvolume-security-style unix -language C.UTF-8
```

### 2. Enable required protocols
```
# For NFS:
nfs create -vserver <svm-name> -access true -v3 enabled -v4.1 enabled

# For CIFS (requires AD join — see Step 5):
# cifs create -vserver <svm-name> -cifs-server <netbios-name> -domain <domain.com>
```

### 3. Create a data LIF
```
network interface create -vserver <svm-name> -lif <lif-name> -role data -data-protocol nfs -home-node <node> -home-port <port> -address <ip-address> -netmask <netmask>
```

### 4. Add a routing entry
```
network route create -vserver <svm-name> -destination 0.0.0.0/0 -gateway <gateway-ip>
```

### 5. Configure DNS
```
vserver services name-service dns create -vserver <svm-name> -domains <domain.com> -name-servers <dns-ip1>,<dns-ip2>
```

### 6. (Optional) Configure LDAP for user/group lookups
```
vserver services name-service ldap client create -vserver <svm-name> -client-config <ldap-config> -ad-domain <domain.com> -schema MS-AD-BIS -port 389
vserver services name-service ldap create -vserver <svm-name> -client-config <ldap-config>
```

### 7. Set name service switch
```
vserver services name-service ns-switch create -vserver <svm-name> -database passwd -sources ldap,local
vserver services name-service ns-switch create -vserver <svm-name> -database group -sources ldap,local
```

### 8. Verify SVM is online
```
vserver show -vserver <svm-name>
network interface show -vserver <svm-name>
network ping -vserver <svm-name> -destination <gateway-ip>
```

### 9. Create a test volume
```
volume create -vserver <svm-name> -volume vol_test -aggregate <aggr> -size 1g -junction-path /vol_test
```

**Validation:**
- `vserver show -vserver <svm-name>` — State: `running`
- `network interface show -vserver <svm-name> -fields status-oper` — `up`
- `network ping` succeeds
- NFS client can mount test volume

**Source docs:** NetApp Cluster commands, NetApp Network commands, NetApp NFS commands, NetApp LDAP commands

---

## Runbook: Morning health check

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Daily operational check, post-maintenance validation.

**Steps:**

### 1. Overall cluster health
```
cluster show
system health status show
system health alert show -state unacknowledged
```

### 2. Node status and uptime
```
system node show -fields health,uptime
```

### 3. Storage failover (HA pair)
```
storage failover show -fields node,possible,state-description
```
Expected: `possible: true`, `state-description: Connected to partner`

### 4. Disk and RAID health
```
storage disk show -broken
storage aggregate show -fields aggregate,state,raidstatus,percent-used
```
- Broken disks: none
- All aggregates: `online`, RAID status: `normal`
- Percent-used: under 85%

### 5. Volume health
```
volume show -state !online
volume show -fields volume,size,available,percent-used | grep -v online
```

### 6. Network / LIF status
```
network interface show -status-oper down
network port show -fields link,health-status
```

### 7. Recent critical events (past 24 hours)
```
event log show -severity EMERGENCY,CRITICAL,ERROR -time >24h
```

### 8. SnapMirror lag
```
snapmirror show -fields lag-time,status,state
```
Check all relationships: lag under RPO threshold, status `idle`.

### 9. AutoSupport (confirm last delivery)
```
system node autosupport history show -fields last-subject,status -count 5
```

**Expected healthy state:**
- No unacknowledged health alerts
- No broken disks
- No offline volumes
- No down LIFs
- No EMERGENCY/CRITICAL events in past 24h
- All SnapMirror relationships within RPO

**Source docs:** NetApp Cluster commands, NetApp Log commands, NetApp Disc commands, NetApp snapshot commands

---

## Runbook: ONTAP upgrade pre-checks

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, maintenance window scheduled, new ONTAP image available

**When to use:** Before performing a non-disruptive ONTAP upgrade (NDU).

**Steps:**

### 1. Full health check (see Morning Health Check runbook)
All systems must be healthy before upgrade.

### 2. Check current version
```
system image show
cluster image show
```

### 3. Verify HA status
```
storage failover show
```
Both nodes must have `possible: true`.

### 4. Check epsilon and quorum
```
cluster show -fields epsilon,health
```

### 5. Check for any active jobs
```
job show -state running
```
Wait for any long-running jobs (SnapMirror transfers, volume moves) to complete.

### 6. Create pre-upgrade snapshots
```
snapshot create -vserver <svm> -volume <critical-vol> -snapshot pre_upgrade_<date>
```
Create on all critical volumes.

### 7. Verify AutoSupport is working
```
system node autosupport invoke -node * -type all -message "Starting ONTAP upgrade"
system node autosupport history show -fields last-subject,status -count 3
```

### 8. Notify application teams
Document current state, notify dependent teams of maintenance window.

**Post-upgrade validation:**
```
cluster show
system image show
system health status show
storage failover show
volume show -state !online
network interface show -status-oper down
event log show -severity EMERGENCY,CRITICAL -time >1h
```

**Source docs:** NetApp Cluster commands, NetApp Snapshot Commands Cluster.docx

---

## Runbook: Expand aggregate capacity (add disks)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, spare disks of same type/size/RPM available

**When to use:** Aggregate approaching 80-85% utilization; volumes unable to grow.

**Steps:**

### 1. Identify the aggregate needing expansion
```
storage aggregate show -fields aggregate,percent-used,availsize,diskcount
```

### 2. Find available spare disks
```
storage disk show -container-type spare -fields disk,node,type,rpm,size,model
```
Confirm disks match existing aggregate disk type and RPM.

### 3. Check current RAID group configuration
```
storage aggregate show -instance -aggregate <aggr>
```
Note current RAID group size and type (RAID-DP or RAID4).

### 4. Add disks to aggregate
```
storage aggregate add-disks -aggregate <aggr> -diskcount <n>
```

### 5. Monitor RAID expansion
```
storage aggregate show -fields aggregate,raidstatus,diskcount,state
```
Status: `adding_spare_disks` → `normal`

### 6. Verify space increased
```
storage aggregate show -fields aggregate,availsize,percent-used
```

**Validation:**
- Aggregate `raidstatus`: `normal`
- Available space increased
- Percent-used reduced to acceptable level

**Caution:** Adding disks triggers RAID expansion, which runs in background. Performance impact is minimal but monitor with `statistics show -object aggregate`.

**Source docs:** NetApp Aggregate commands, NetApp Disc commands



---

# Deprecated and Dangerous Commands

> **Scope:** Commands that are deprecated, dangerous, version-specific, or require extreme caution. Includes 7-Mode commands that do not apply to Cluster-Mode, destructive operations, and ONTAP version differences.
> **Applies to:** ONTAP 8.x (7-Mode), ONTAP 8.x Cluster-Mode, ONTAP 9.x
> **Purpose for CustomGPT:** Prevent incorrect command recommendations; flag when user context implies a dangerous or version-inappropriate command.

---

## Category: 7-Mode Node Shell Commands (Not for Cluster-Mode)

These commands are run from the **7-Mode node shell** (either directly on a 7-Mode filer or via `node run -node <node>` in Cluster-Mode). They behave differently or do not exist in the Cluster-Mode ONTAP CLI.

**Do NOT use these at the cluster CLI prompt in Cluster-Mode:**

| 7-Mode Command | Cluster-Mode Equivalent |
|---|---|
| `vol status` | `volume show` |
| `vol status -b` | `volume show -fields block-type` |
| `vol offline <vol>` | `volume offline -vserver <svm> -volume <vol>` |
| `vol online <vol>` | `volume online -vserver <svm> -volume <vol>` |
| `aggr status` | `storage aggregate show` |
| `aggr status -v` | `storage aggregate show -instance` |
| `aggr create` | `storage aggregate create` |
| `aggr add` | `storage aggregate add-disks` |
| `aggr destroy` | `storage aggregate delete` |
| `snap list /vol/<vol>` | `volume snapshot show -vserver <svm>` |
| `snap create /vol/<vol> <name>` | `volume snapshot create -vserver <svm>` |
| `snap delete /vol/<vol> <name>` | `volume snapshot delete -vserver <svm>` |
| `snap restore -s <snap> /vol/<vol>` | `volume snapshot restore -vserver <svm>` |
| `snap reserve /vol/<vol> <pct>` | `volume modify -snapshot-reserve-percent` |
| `disk show` | `storage disk show` |
| `disk show -v` | `storage disk show -instance` |
| `storage show acp -a` | `storage shelf acp module show` |
| `sysstat -c 5` | `statistics start/show` |
| `stats show -i 5` | `statistics show` |
| `snapmirror status` | `snapmirror show` |
| `wrfile` / `rdfile` | `vserver services name-service getxxbynametype` |

**To access 7-Mode commands from Cluster-Mode:**
```
node run -node <node> <7-mode-command>
```
Example:
```
NETCLSMDF1::> node run -node NETCLSMDF1-01 aggr status -v
NETCLSMDF1::> node run -node NETCLSMDF1-01 vol status
```

---

## Category: Destructive Snapshot Commands

### `snapshot delete -vserver <svm> -volume <vol> -snapshot *`

**Risk:** Deletes ALL snapshots on a volume in a single command.

**Caution:**
- SnapMirror base snapshots will be deleted, breaking incremental replication chains — requires full re-initialization.
- Cannot be undone. There is no recycle bin.
- If AutoSupport or compliance uses snapshots, they are gone.

**Safer alternative:** Delete snapshots individually after reviewing each one:
```
snapshot show -vserver <svm> -volume <vol> -fields snapshot,create-time,size,owners
snapshot delete -vserver <svm> -volume <vol> -snapshot <specific-snapshot-name>
```

**7-Mode equivalent (also dangerous):**
```
snap delete -a /vol/<volname>   (deletes all — use with extreme caution)
```

---

### `volume snapshot restore -vserver <svm> -volume <vol> -snapshot <snap>`

**Risk:** DESTRUCTIVE — rolls back the entire volume. All data written after the snapshot is permanently lost.

**Caution:**
- This is not a copy operation. The volume is reverted in place.
- Any writes between the snapshot time and now are gone.
- Always take a snapshot of the current state before restoring:
```
snapshot create -vserver <svm> -volume <vol> -snapshot pre_restore_<date>
```
- Notify all users and unmount the volume from clients before restore.

---

## Category: Destructive Aggregate and Volume Commands

### `storage aggregate delete -aggregate <aggr>`

**Risk:** Permanently destroys an aggregate and all data on it. Non-recoverable.

**Requirements before use:**
- All volumes in the aggregate must be offline and deleted first
- All LUNs within those volumes must be unmapped and taken offline
- Confirm no SnapMirror relationships reference any volumes in the aggregate

**Command sequence if aggregate destruction is truly intended:**
```
volume show -aggregate <aggr>
volume offline -vserver <svm> -volume <vol>
volume delete -vserver <svm> -volume <vol>
storage aggregate offline -aggregate <aggr>
storage aggregate delete -aggregate <aggr>
```

**7-Mode equivalent:**
```
aggr destroy <aggr>   (node shell — equally destructive)
```

---

### `volume delete -vserver <svm> -volume <vol>`

**Risk:** Permanently deletes the volume and all its data, snapshots, and LUNs.

**Caution:**
- ONTAP does NOT have a trash/recycle bin for volumes.
- Volume must be offline first: `volume offline -vserver <svm> -volume <vol>`
- Check for SnapMirror: `snapmirror show -source-volume <vol>` — if a relationship exists, delete it first.
- Check for clones: `volume clone show -parent-volume <vol>`

**Safer alternative if space is the concern:** Consider `volume move` to a different aggregate or reduce snapshot reserve instead of deletion.

---

### `volume offline -vserver <svm> -volume <vol>`

**Risk:** Immediately disconnects all clients and makes data inaccessible. Though recoverable (`volume online`), any in-flight I/O is dropped.

**Caution:**
- All NFS/CIFS clients accessing the volume will receive I/O errors immediately.
- LUNs within the volume become inaccessible to SAN hosts.
- Only use during planned maintenance with clients unmounted/quiesced first.

---

## Category: Dangerous SnapMirror Operations

### `snapmirror break -destination-path <svm>:<vol>`

**Risk:** Severs the replication relationship. Destination becomes read-write. Data written to destination is NOT synced back.

**Caution:**
- Cannot be reversed without `snapmirror resync`, which **overwrites destination with source** — losing any writes made to destination post-break.
- Always run `snapmirror quiesce` before break to ensure the last transfer completed.
- Document the break time for data recovery planning.

---

### `snapmirror resync -destination-path <svm>:<vol>`

**Risk:** Overwrites the destination volume with source data. All writes made to destination while in `broken-off` state are lost.

**Caution:**
- Snapshot the destination before resync if any data needs to be preserved:
```
snapshot create -vserver <dr-svm> -volume <dr-vol> -snapshot pre_resync_<date>
```
- Resync is typically used for failback after DR. Coordinate with data owners before running.

---

## Category: Dangerous Storage Failover Commands

### `storage failover takeover -ofnode <node> -option immediate`

**Risk:** Immediately moves the specified node's resources (aggregates, LIFs, volumes) to the HA partner. Disruptive for SAN workloads.

**Caution:**
- Causes a brief disruption for SAN (iSCSI/FC) clients — host multipathing typically recovers, but in-flight I/O is dropped.
- NAS (NFS/CIFS) clients typically reconnect automatically via LIF failover.
- Only use during planned maintenance or confirmed node failure.
- Run `storage failover giveback -ofnode <node>` to return resources after maintenance.

**Verification before running:**
```
storage failover show -fields node,possible,state-description
```
Confirm `possible: true` — if false, do not proceed.

---

## Category: Service Processor Dangerous Commands

### `system power off` (from SP shell)

**Risk:** Immediately cuts power to the node. No graceful shutdown. Data in NVRAM that has not been flushed to disk may be lost.

**Caution:**
- Use ONTAP's graceful halt first if the node is accessible:
```
system node halt -node <node> -skip-lif-migration false
```
- Only use `sp> system power off` when the node is unresponsive and cannot be halted gracefully.
- After power-off, ONTAP will perform a NVRAM replay on next boot — but prolonged power failure with unclean shutdown increases risk.

### `system reset` (from SP shell)

**Risk:** Hard-resets the node immediately. No graceful shutdown. Equivalent to pressing the reset button.

**Caution:** Same caveats as `system power off`. Use only when node is unresponsive.

---

## Category: LUN and iGroup Dangerous Operations

### `lun offline -vserver <svm> -volume <vol> -lun <lun-name>`

**Risk:** Immediately disconnects all SAN hosts from the LUN.

**Caution:**
- Any host I/O in progress will fail immediately.
- VMware datastores will show as disconnected; VMs may pause or fail.
- Always quiesce the host workload and unmount or unpresent the LUN from hosts before taking offline.

### `igroup remove -vserver <svm> -igroup <igroup-name> -initiator <iqn-or-wwpn>`

**Risk:** Removes a host's access to all LUNs mapped to the iGroup immediately.

**Caution:**
- The host loses storage access with no warning.
- Unmount all filesystems and stop all I/O to the LUN from the host before removing.

---

## Category: Export Policy Dangerous Configurations

### `-clientmatch 0.0.0.0/0` in export policy rules

**Risk:** Grants NFS access to ALL hosts on the network, including untrusted or unknown clients.

**Caution:**
- Never use `0.0.0.0/0` in production export policies.
- Always restrict `clientmatch` to known subnets or specific IPs.
- Combined with `-superuser sys`, this grants root access to all hosts — a critical security risk.

**Secure alternative:**
```
vserver export-policy rule create -vserver <svm> -policyname <policy> -clientmatch 10.10.1.0/24 -rorule sys -rwrule sys -superuser none -anon 65534
```

---

## Category: Quota Commands with Side Effects

### `quota on -vserver <svm> -volume <vol>`

**Risk/Side effect:** Enabling quotas on a large volume with many files triggers quota tree initialization, which scans all files. On very large volumes (millions of files), this can cause a noticeable performance degradation.

**Best practice:** Run `quota on` during off-peak hours. Use `quota resize` instead of turning quotas off/on when modifying rules on an already-quota-enabled volume.

---

## Category: Reallocation Commands (ONTAP 8 — Deprecated in 9.x)

### `reallocate start -f /vol/<vol>` (7-Mode)
### `storage aggregate reallocation start -aggregate <aggr>` (Cluster-Mode 8.x)

**Status:** Deprecated in ONTAP 9.x. Not available or not needed in modern ONTAP.

**Risk:** Reallocation reorganizes data block layout for performance on HDDs. On active volumes, this adds I/O overhead. It was most relevant for RAID-4/RAID-DP on spinning disk.

**Modern replacement:** ONTAP 9.x uses automatic layout optimization. Manual reallocation is generally unnecessary and not supported in 9.x.

**Caution:** Do not attempt reallocation commands on ONTAP 9.x — they will fail or have no effect. Do not run on SnapMirror destination volumes.

---

## Category: `node run` Shell Access (Use Sparingly)

### `node run -node <node> <command>`

**Risk:** Provides access to the 7-Mode node shell from within Cluster-Mode. Commands run here operate outside of the cluster's RBAC and audit trail in some cases.

**Caution:**
- Changes made via `node run` can bypass cluster-level consistency checks.
- Not all 7-Mode shell commands behave predictably in a Cluster-Mode context.
- NetApp Support may require node shell access for diagnostics, but routine administration should use cluster-level commands.
- In ONTAP 9.x, `node run` access is restricted and some commands have been removed entirely.

**Preferred:** Always use the cluster CLI equivalents instead of `node run` unless specifically required.

---

## Summary Table: High-Risk Commands Quick Reference

| Command | Risk Level | Notes |
|---|---|---|
| `snapshot delete -snapshot *` | HIGH | Deletes all snapshots, breaks SnapMirror |
| `volume snapshot restore` | HIGH | Destructive rollback, data after snapshot is lost |
| `storage aggregate delete` | CRITICAL | Destroys aggregate and all data |
| `volume delete` | HIGH | Permanent, no recycle bin |
| `snapmirror break` | HIGH | Severs replication, data diverges |
| `snapmirror resync` | HIGH | Overwrites destination, post-break DR writes lost |
| `storage failover takeover -option immediate` | MEDIUM-HIGH | Disruptive, drops in-flight SAN I/O |
| `sp> system power off` | HIGH | Hard power cut, possible NVRAM data loss |
| `sp> system reset` | HIGH | Hard reset, no graceful shutdown |
| `lun offline` | HIGH | Immediate SAN host disconnection |
| `igroup remove` (while in use) | HIGH | Immediate loss of storage access for host |
| `clientmatch 0.0.0.0/0` | SECURITY | Grants NFS access to all hosts |
| `quota on` (large volume) | MEDIUM | Performance impact during initialization |
| `node run` shell commands | MEDIUM | Bypasses cluster RBAC, version-specific behavior |
| `reallocate start` | DEPRECATED | Not supported in ONTAP 9.x |
| All bare `aggr/vol/snap` commands | 7-MODE ONLY | Do not use at Cluster-Mode CLI |
