# ONTAP Cluster & Admin Fundamentals

> **Scope:** Cluster-wide administration, AutoSupport, node management, job scheduling, system health, boot/shutdown procedures.
> **Applies to:** ONTAP 8.x (7-Mode and Cluster-Mode), ONTAP 9.x
> **Source folders:** NetApp Cluster commands, Word Docs from Tim, NetApp Log commands, NetApp SP commands

---

## Task: Show cluster autosupport configuration

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin privileges

**When to use:** Verify AutoSupport is enabled and correctly configured to send alerts to NOC/support contacts.

**Commands:**
```
autosupport show
autosupport show -instance
autosupport show -node *
```

**Examples:**
```
NETCLSMDF1::> autosupport show
NETCLSMDF1::> autosupport show -instance
NETCLSMDF1::> autosupport invoke -node * -type test -message "Test AutoSupport"
```

**Validation commands:**
- `autosupport show`
- `autosupport history show`

**Rollback / Caution:** None — read-only commands.

**Related tasks:** Configure AutoSupport SMTP, check event log

**Source docs:** Netapp Cluster Commands 10.docx, NetApp Autosupport Commands Cluster.docx

---

## Task: Configure AutoSupport

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, valid SMTP relay, NOC email addresses

**When to use:** Initial cluster setup or when updating notification recipients.

**Commands:**
```
autosupport modify -node <node> -state enable -from <filer@domain> -to <noc@domain>,<admin@domain> -mail-hosts <smtp-relay-ip>
autosupport modify -node * -state enable
autosupport invoke -node * -type test
```

**Validation commands:**
- `autosupport show -node *`
- `autosupport history show`

**Rollback / Caution:** Disabling AutoSupport removes proactive alerting. Always test after changes.

**Related tasks:** View autosupport history, trigger manual autosupport

**Source docs:** Netapp Cluster Commands 10.docx

---

## Task: View and manage cluster nodes

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Check node health, uptime, ONTAP version, failover status.

**Commands:**
```
cluster show
cluster show -health true
node show
node show -instance
version
system node show
system node show -instance
node run -node <nodename>
```

**Examples:**
```
NETCLSMDF1::> cluster show
NETCLSMDF1::> node show
NETCLSMDF1::> system node show -fields node,health,uptime,model,serial-number
NETCLSMDF1::> version
```

**Validation commands:**
- `cluster show`
- `system node show -fields health`

**Rollback / Caution:** `node run` drops you to the 7-Mode shell of a node — use `exit` or Ctrl-D to return.

**Related tasks:** Node failover, cluster health check, firmware update

**Source docs:** NetApp Cluster commands, Word Docs from Tim

---

## Task: View and create job schedules

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Before creating snapshot policies or SnapMirror schedules, confirm available schedules or create new ones.

**Commands:**
```
job schedule show
job schedule cron show
job schedule cron create -name <name> -dayofweek "<days>" -hour <hours> -minute <minute>
job schedule interval create -name <name> -minutes <interval>
```

**Examples:**
```
NETCLSMDF1::> job schedule show
NETCLSMDF1::> job schedule cron create -name "Daily_2300" -hour 23 -minute 0
NETCLSMDF1::> job schedule cron create -name "Hourly_Sched_5-9-13-17" -dayofweek "Monday,Tuesday,Wednesday,Thursday,Friday" -hour 5,9,13,17 -minute 5
```

**Validation commands:**
- `job schedule show`
- `job schedule cron show -name <name>`

**Rollback / Caution:** Deleting a schedule used by a snapshot policy or SnapMirror will break those jobs.

**Related tasks:** Create snapshot policy, configure SnapMirror schedule

**Source docs:** NetApp Snapshot Commands Cluster.docx

---

## Task: Check and manage system events and logs

**Applies to:** ONTAP 8.x, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Troubleshooting, auditing, health checks.

**Commands:**
```
event log show
event log show -severity ERROR
event log show -node <node> -time >1h
event log show -messagename <event-name>
syslog show
logger -t <tag> -p <priority> "<message>"
```

**Examples:**
```
NETCLSMDF1::> event log show -severity ERROR
NETCLSMDF1::> event log show -time >24h -fields time,node,severity,messagename,description
```

**Validation commands:**
- `event log show -severity EMERGENCY`
- `event log show -severity CRITICAL`

**Rollback / Caution:** Read-only. Log rotation is automatic.

**Related tasks:** AutoSupport, EMS configuration, SNMP alerts

**Source docs:** NetApp Log commands

---

## Task: Manage cluster time and NTP

**Applies to:** ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Initial setup or when time drift is detected.

**Commands:**
```
cluster time-service ntp server show
cluster time-service ntp server create -server <ntp-server>
cluster date show
cluster date modify -timezone <tz>
```

**Validation commands:**
- `cluster time-service ntp server show`
- `cluster date show`

**Rollback / Caution:** Time changes can affect Kerberos and CIFS authentication. Change during maintenance window.

**Related tasks:** LDAP/Kerberos setup, CIFS authentication

**Source docs:** NetApp Cluster commands

---

## Task: Cluster health check — quick runbook

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Morning health checks, before/after maintenance, incident response.

**Commands:**
```
cluster show
system health status show
system health alert show
storage failover show
network interface show -status-oper down
volume show -state !online
disk show -broken
aggr show -state !online
system node show -fields health
event log show -severity EMERGENCY,CRITICAL,ERROR -time >8h
```

**Validation commands:**
- `cluster show` — all nodes healthy
- `system health status show` — status: ok

**Rollback / Caution:** Read-only health check. No changes made.

**Related tasks:** Troubleshooting, disk replacement, aggregate repair

**Source docs:** NetApp Cluster commands, Word Docs from Tim

---

## Task: Run node-level (7-Mode shell) commands from cluster

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** When a command is only available in the 7-Mode node shell (e.g., `storage show`, `sysconfig`).

**Commands:**
```
node run -node <nodename> <command>
node run -node <nodename>
  <7-mode-command>
  exit
```

**Examples:**
```
NETCLSMDF1::> node run -node NETCLSMDF1-01 sysconfig -a
NETCLSMDF1::> node run -node NETCLSMDF1-01 storage show disk
NETCLSMDF1::> node run -node NETCLSMDF1-01 df -h
```

**Validation commands:**
- `node run -node <nodename> uptime`

**Rollback / Caution:** Some node-shell commands can impact system performance. Avoid long-running operations during peak hours.

**Related tasks:** Disk diagnostics, storage show, sysconfig

**Source docs:** NetApp Cluster commands, NetApp SP commands

---

## Task: Service Processor (SP) management

**Applies to:** ONTAP 8.x, ONTAP 9.x

**Prereqs:** Cluster admin, SP network configured

**When to use:** Remote management, node reboots, console access when ONTAP is unresponsive.

**Commands:**
```
system service-processor show
system service-processor show -instance
system service-processor network show
system service-processor network modify -node <node> -address-family IPv4 -enable true -ip-address <ip> -netmask <mask> -gateway <gw>
system service-processor reboot-sp -node <node>
system node power off -node <node>
system node reboot -node <node>
```

**Examples:**
```
NETCLSMDF1::> system service-processor show
NETCLSMDF1::> system service-processor network show
NETCLSMDF1::> system service-processor network modify -node NETCLSMDF1-01 -address-family IPv4 -enable true -ip-address 10.0.1.10 -netmask 255.255.255.0 -gateway 10.0.1.1
```

**Validation commands:**
- `system service-processor show`
- `system service-processor network show`

**Rollback / Caution:** SP IP changes take effect immediately. Verify network reachability before and after. An incorrect gateway will make the SP unreachable.

**Related tasks:** Node reboot, out-of-band management, SP firmware update

**Source docs:** NetApp SP commands


---

# SVM and Networking

> **Scope:** Storage Virtual Machine (SVM/Vserver) management, network interfaces, routing, DNS, LDAP, security configuration.
> **Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x
> **Source folders:** NetApp Network commands, NetApp LDAP commands, NetApp Security commands

---

## Task: List and view SVMs (Vservers)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Audit SVMs, check SVM state, identify which protocols are enabled.

**Commands:**
```
vserver show
vserver show -instance
vserver show -type data
vserver show -fields name,state,allowed-protocols,operational-state
```

**Examples:**
```
NETCLSMDF1::> vserver show
NETCLSMDF1::> vserver show -type data -fields name,state,allowed-protocols
```

**Validation commands:**
- `vserver show -fields state`

**Rollback / Caution:** Read-only.

**Related tasks:** Create SVM, configure NFS/CIFS, SVM networking

**Source docs:** NetApp Network commands

---

## Task: Create a new SVM (Vserver)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, aggregate available, IP range planned

**When to use:** Provisioning a new data-serving SVM for NFS, CIFS, or iSCSI.

**Commands:**
```
vserver create -vserver <svm-name> -aggregate <aggr-name> -rootvolume <rootvol-name> -rootvolume-security-style <unix|ntfs|mixed> -language <en_US.UTF-8>
vserver modify -vserver <svm-name> -allowed-protocols <nfs,cifs,iscsi,fcp>
```

**Examples:**
```
NETCLSMDF1::> vserver create -vserver svm_prod -aggregate aggr1_n01 -rootvolume svm_prod_root -rootvolume-security-style unix -language en_US.UTF-8
```

**Validation commands:**
- `vserver show -vserver <svm-name>`
- `vserver show -vserver <svm-name> -fields allowed-protocols,state`

**Rollback / Caution:** Deleting an SVM removes all volumes and data within it. There is no undo.

**Related tasks:** Create volume, configure NFS export, configure CIFS share

**Source docs:** NetApp Network commands

---

## Task: Show and manage network interfaces (LIFs)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Check LIF status, verify data LIFs are on correct nodes/ports, troubleshoot connectivity.

**Commands:**
```
network interface show
network interface show -vserver <svm>
network interface show -status-oper down
network interface show -fields vserver,lif,address,port,status-oper,status-admin
network interface revert -vserver <svm> -lif <lif-name>
network interface migrate -vserver <svm> -lif <lif-name> -dest-node <node> -dest-port <port>
```

**Examples:**
```
NETCLSMDF1::> network interface show
NETCLSMDF1::> network interface show -status-oper down
NETCLSMDF1::> network interface revert -vserver svm_prod -lif svm_prod_nfs1
```

**Validation commands:**
- `network interface show -fields status-oper`
- `network ping -lif <lif-name> -destination <ip>`

**Rollback / Caution:** Migrating a LIF during active client connections will cause a brief interruption. Revert after maintenance.

**Related tasks:** Create LIF, configure failover groups, check port health

**Source docs:** NetApp Network commands

---

## Task: Create a data LIF

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, SVM exists, port/VLAN available

**When to use:** Adding a new NFS or CIFS LIF to an SVM.

**Commands:**
```
network interface create -vserver <svm> -lif <lif-name> -role data -data-protocol <nfs|cifs|iscsi> -home-node <node> -home-port <port> -address <ip> -netmask <mask> -status-admin up -firewall-policy data -auto-revert true
```

**Examples:**
```
NETCLSMDF1::> network interface create -vserver svm_prod -lif svm_prod_nfs1 -role data -data-protocol nfs -home-node NETCLSMDF1-01 -home-port e0c -address 10.10.1.50 -netmask 255.255.255.0 -status-admin up -firewall-policy data -auto-revert true
```

**Validation commands:**
- `network interface show -lif <lif-name>`
- `network ping -lif <lif-name> -destination <gateway>`

**Rollback / Caution:** Incorrect IP or port will make the LIF unreachable. Verify with network team before creating.

**Related tasks:** Configure failover, test LIF reachability, NFS/CIFS export

**Source docs:** NetApp Network commands

---

## Task: Show and configure routing

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Verify SVM can reach DNS, LDAP, or NTP servers; add static routes.

**Commands:**
```
network route show
network route show -vserver <svm>
network route create -vserver <svm> -destination <subnet/prefix> -gateway <gw-ip> -metric <metric>
```

**Examples:**
```
NETCLSMDF1::> network route show
NETCLSMDF1::> network route create -vserver svm_prod -destination 0.0.0.0/0 -gateway 10.10.1.1
```

**Validation commands:**
- `network route show -vserver <svm>`
- `network ping -vserver <svm> -destination <ip>`

**Rollback / Caution:** Incorrect default gateway will isolate the SVM. Always ping after adding a route.

**Related tasks:** DNS configuration, LIF creation, NFS/CIFS connectivity

**Source docs:** NetApp Network commands

---

## Task: Configure DNS for an SVM

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, DNS server IPs

**When to use:** Required for CIFS (AD join), LDAP, and NFS Kerberos.

**Commands:**
```
vserver services dns show
vserver services dns create -vserver <svm> -domains <domain> -name-servers <dns-ip1>,<dns-ip2>
vserver services dns modify -vserver <svm> -name-servers <dns-ip1>,<dns-ip2>
```

**Examples:**
```
NETCLSMDF1::> vserver services dns create -vserver svm_prod -domains csun.edu -name-servers 130.166.1.10,130.166.1.11
NETCLSMDF1::> vserver services dns show -vserver svm_prod
```

**Validation commands:**
- `vserver services dns show -vserver <svm>`
- `vserver services name-service dns check -vserver <svm>`

**Rollback / Caution:** CIFS shares and LDAP will break if DNS is misconfigured.

**Related tasks:** CIFS setup, LDAP configuration, NFS Kerberos

**Source docs:** NetApp Network commands, NetApp LDAP commands

---

## Task: Configure LDAP for an SVM

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, LDAP server details, bind credentials

**When to use:** Required for Unix UID/GID lookups when serving NFS to AD-authenticated users.

**Commands:**
```
ldap client create -client-config <config-name> -servers <ldap-server-ip> -base-dn <base-dn> -bind-dn <bind-dn> -bind-password <password> -schema <RFC-2307>
vserver services name-service ldap create -vserver <svm> -client-config <config-name> -client-enabled true
ldap check -vserver <svm>
```

**Examples:**
```
NETCLSMDF1::> ldap client create -client-config csun_ldap -servers 130.166.1.20 -base-dn "dc=csun,dc=edu" -bind-dn "cn=netapp-bind,ou=serviceaccounts,dc=csun,dc=edu" -bind-password <password> -schema RFC-2307
NETCLSMDF1::> vserver services name-service ldap create -vserver svm_prod -client-config csun_ldap -client-enabled true
NETCLSMDF1::> ldap check -vserver svm_prod
```

**Validation commands:**
- `ldap check -vserver <svm>`
- `vserver services name-service ldap show`
- `getXXentries passwd <username>` (from node shell)

**Rollback / Caution:** Incorrect bind credentials or base DN will break all UID lookups. Test with `ldap check` before rolling out NFS mounts.

**Related tasks:** NFS export policy, name service switch, CIFS setup

**Source docs:** NetApp LDAP commands

---

## Task: Name service switch configuration

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, LDAP or NIS configured

**When to use:** Configure lookup order for users, groups, netgroups.

**Commands:**
```
vserver services name-service ns-switch show -vserver <svm>
vserver services name-service ns-switch modify -vserver <svm> -database passwd -sources ldap,files
vserver services name-service ns-switch modify -vserver <svm> -database group -sources ldap,files
vserver services name-service ns-switch modify -vserver <svm> -database netgroup -sources ldap,files
```

**Validation commands:**
- `vserver services name-service ns-switch show`
- `vserver services name-service getxxbynametype -vserver <svm> -database passwd -name <username>`

**Rollback / Caution:** Wrong lookup order can cause NFS permission failures. Always test with a known user after changes.

**Related tasks:** LDAP setup, NFS export policy, CIFS authentication

**Source docs:** NetApp LDAP commands, NetApp Network commands

---

## Task: Show network port health and speed

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Verify port link state, speed, and duplex; diagnose network issues.

**Commands:**
```
network port show
network port show -node <node> -port <port>
network port show -fields speed,duplex,link,mtu,health-status
network port modify -node <node> -port <port> -mtu <mtu> -flowcontrol-admin none
```

**Validation commands:**
- `network port show -fields link,health-status`

**Rollback / Caution:** Modifying port MTU during active traffic causes brief interruption. Change during maintenance window.

**Related tasks:** LIF creation, VLAN configuration, jumbo frames

**Source docs:** NetApp Network commands


---

# Volumes and Aggregates

> **Scope:** Aggregate creation and management, volume creation, capacity, autosize, efficiency, reallocation, block size, deduplication savings, volume move/copy.
> **Applies to:** ONTAP 8.x (7-Mode and Cluster-Mode), ONTAP 9.x
> **Source folders:** NetApp Volume commands, NetApp Aggregate commands, NetApp Deduplication commands, NetApp Disc commands

---

## Task: Show aggregates and their status

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Capacity planning, health checks, pre-volume-creation validation.

**Commands:**
```
aggr show
aggr show -state online
aggr show -fields aggregate,size,availsize,usedsize,state,node
storage aggregate show
storage aggregate show -fields aggregate,availsize,usedsize,state,node
storage aggregate show -instance
```

**Examples:**
```
NETCLSMDF1::> aggr show
NETCLSMDF1::> storage aggregate show -fields aggregate,size,availsize,percent-used,state
```

**Validation commands:**
- `aggr show -state !online`
- `storage aggregate show -fields state`

**Rollback / Caution:** Read-only.

**Related tasks:** Add disks to aggregate, create volume, check disk health

**Source docs:** NetApp Aggregate commands

---

## Task: Show aggregate space usage detail

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Capacity management, before provisioning new volumes.

**Commands:**
```
storage aggregate show-space -aggregate <aggr-name>
storage aggregate show-space
df -Ah (7-Mode node shell)
```

**Examples:**
```
NETCLSMDF1::> storage aggregate show-space -aggregate aggr1_n01
NETCLSMDF1::> storage aggregate show-space
```

**Validation commands:**
- `storage aggregate show-space -aggregate <aggr>`

**Rollback / Caution:** Read-only.

**Related tasks:** Volume capacity, add disks, thin provisioning

**Source docs:** NetApp Aggregate commands

---

## Task: Add disks to an aggregate

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, spare disks available

**When to use:** When aggregate is near capacity and spare disks are available.

**Commands:**
```
storage aggregate add-disks -aggregate <aggr> -diskcount <n>
storage disk show -container-type spare -fields disk,node
aggr add -a <aggr-name> <n>d (7-Mode)
```

**Examples:**
```
NETCLSMDF1::> storage aggregate add-disks -aggregate aggr1_n01 -diskcount 4
```

**Validation commands:**
- `storage aggregate show -aggregate <aggr> -fields size`
- `aggr status -v <aggr>` (node shell)

**Rollback / Caution:** Adding disks triggers RAID rebuild/parity. Monitor with `storage aggregate show` until complete. Do not add disks to a degraded aggregate without NetApp support guidance.

**Related tasks:** Check spare disks, RAID group sizing, disk replacement

**Source docs:** NetApp Aggregate commands, NetApp Disc commands

---

## Task: Create a volume

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, aggregate with available space, SVM exists

**When to use:** Provisioning new storage for NFS, CIFS, or iSCSI workloads.

**Commands:**
```
volume create -vserver <svm> -volume <vol-name> -aggregate <aggr> -size <size> -security-style <unix|ntfs|mixed> -junction-path <path> -policy <export-policy> -space-guarantee <none|volume|file>
volume show -vserver <svm> -volume <vol-name>
```

**Examples:**
```
NETCLSMDF1::> volume create -vserver svm_prod -volume vol_data01 -aggregate aggr1_n01 -size 500g -security-style unix -junction-path /vol_data01 -policy default -space-guarantee none
NETCLSMDF1::> volume show -vserver svm_prod -volume vol_data01
```

**Validation commands:**
- `volume show -vserver <svm> -volume <vol>`
- `df -h` (from node shell)

**Rollback / Caution:** Thin-provisioned volumes (`-space-guarantee none`) can over-commit. Monitor aggregate usage carefully.

**Related tasks:** Configure NFS export, create CIFS share, set autosize, configure snapshot policy

**Source docs:** NetApp Volume commands

---

## Task: Show volume capacity and usage

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Daily capacity monitoring, identify full or near-full volumes.

**Commands:**
```
volume show -fields volume,vserver,size,available,used,percent-used,state
volume show -percent-used >80
df -h (7-Mode or node shell)
df -Ah (7-Mode: all volumes)
volume show -vserver <svm> -fields volume,size,available,percent-used
```

**Examples:**
```
NETCLSMDF1::> volume show -fields volume,size,available,percent-used
NETCLSMDF1::> volume show -percent-used >85
```

**Validation commands:**
- `volume show -fields percent-used`

**Rollback / Caution:** Read-only.

**Related tasks:** Volume autosize, expand volume, move volume, snapshot cleanup

**Source docs:** NetApp Volume commands, NetApp df volume size commands.txt

---

## Task: Configure volume autosize

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Prevent volumes from going full by enabling automatic growth.

**Commands:**
```
volume autosize -vserver <svm> -volume <vol> -mode grow -maximum-size <max-size> -increment-size <increment> -grow-threshold-percent <pct>
volume autosize -vserver <svm> -volume <vol> -mode grow_shrink
volume autosize -vserver <svm> -volume <vol>
volume show -vserver <svm> -volume <vol> -fields autosize-mode,autosize-maximum,autosize-increment
```

**Examples:**
```
NETCLSMDF1::> volume autosize -vserver svm_prod -volume vol_data01 -mode grow -maximum-size 1tb -increment-size 10g -grow-threshold-percent 85
NETCLSMDF1::> volume autosize -vserver svm_prod -volume vol_data01
```

**Validation commands:**
- `volume show -fields autosize-mode,autosize-maximum`

**Rollback / Caution:** Autosize requires available aggregate space. If aggregate is full, autosize will fail silently. Monitor both volume and aggregate usage.

**Related tasks:** Aggregate capacity, volume capacity monitoring, snapshot reserve

**Source docs:** NetApp Volume Autosize Cluster Commands.docx, NetApp Volume Autosize & Increment Command.docx

---

## Task: Move a volume to another aggregate or node

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, destination aggregate with sufficient free space

**When to use:** Load balancing, aggregate consolidation, node evacuation.

**Commands:**
```
volume move start -vserver <svm> -volume <vol> -destination-aggregate <dest-aggr>
volume move show
volume move show -vserver <svm> -volume <vol>
```

**Examples:**
```
NETCLSMDF1::> volume move start -vserver svm_prod -volume vol_data01 -destination-aggregate aggr2_n02
NETCLSMDF1::> volume move show
```

**Validation commands:**
- `volume move show -vserver <svm> -volume <vol>`
- `volume show -vserver <svm> -volume <vol> -fields aggregate`

**Rollback / Caution:** Volume move is non-disruptive for NFS/CIFS. For SAN (iSCSI/FC), a brief cutover pause occurs. Monitor progress with `volume move show`. If it stalls, check aggregate space.

**Related tasks:** Aggregate rebalancing, node decommission, capacity management

**Source docs:** NetApp Vol Move Commands Cluster.docx, NetApp Vol Move Progress docx

---

## Task: Deduplication and space efficiency

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Reduce space consumption on volumes with repetitive data (VMs, user home dirs, databases).

**Commands:**
```
volume efficiency show
volume efficiency show -vserver <svm> -volume <vol>
volume efficiency on -vserver <svm> -volume <vol>
volume efficiency start -vserver <svm> -volume <vol> -scan-old-data true
volume efficiency stop -vserver <svm> -volume <vol>
volume efficiency modify -vserver <svm> -volume <vol> -schedule <schedule-name>
volume show -vserver <svm> -volume <vol> -fields dedupe-space-saved,compression-space-saved
sis status (7-Mode node shell)
sis on /vol/<volname> (7-Mode)
sis start -s /vol/<volname> (7-Mode: scan old data)
```

**Examples:**
```
NETCLSMDF1::> volume efficiency on -vserver svm_prod -volume vol_data01
NETCLSMDF1::> volume efficiency start -vserver svm_prod -volume vol_data01 -scan-old-data true
NETCLSMDF1::> volume efficiency show -vserver svm_prod -volume vol_data01
```

**Validation commands:**
- `volume efficiency show -fields state,status,percent-saved`
- `volume show -fields dedupe-space-saved`

**Rollback / Caution:** Initial scan on large volumes can be I/O-intensive. Schedule during off-peak hours. Use `-scan-old-data true` only once per volume (existing data); subsequent deduplication runs automatically on new writes.

**Related tasks:** Compression, thin provisioning, capacity reporting

**Source docs:** NetApp Deduplication commands, Netapp Volume Deduplication Savings.docx

---

## Task: Volume reallocation

**Applies to:** ONTAP 8.x (primarily 7-Mode), ONTAP 9.x (limited)

**Prereqs:** Cluster admin or node shell access

**When to use:** Improve sequential read performance after heavy random writes or fragmentation. Commonly used on SnapMirrored volumes after break.

**Commands:**
```
reallocate start /vol/<volname>
reallocate start -p /vol/<volname>/<lun-path>
reallocate status /vol/<volname>
reallocate stop /vol/<volname>
reallocate measure /vol/<volname>
```

**Examples:**
```
NETCLSMDF1-01> reallocate start /vol/vol_data01
NETCLSMDF1-01> reallocate status /vol/vol_data01
NETCLSMDF1-01> reallocate measure /vol/vol_data01
```

**Validation commands:**
- `reallocate status /vol/<volname>`
- `reallocate measure /vol/<volname>` (check optimization score before/after)

**Rollback / Caution:** Reallocation is I/O intensive and should run during maintenance or low-use windows. On SnapMirrored volumes, run reallocation AFTER breaking the mirror and before re-establishing. Can cause high disk utilization for hours on large volumes.

**Related tasks:** SnapMirror break/resync, volume optimization, LUN reallocation

**Source docs:** NetApp Reallocation Commands 2020.docx, NetApp Reallocation on a Snapmirrored Volume Commands.docx

---

## Task: Show volume block size and detail

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Auditing, capacity planning, troubleshooting block-size mismatches.

**Commands:**
```
volume show -fields volume,vserver,aggregate,block-size,state,junction-path
volume show -instance -vserver <svm> -volume <vol>
```

**Validation commands:**
- `volume show -fields block-size`

**Rollback / Caution:** Block size is set at volume creation and cannot be changed.

**Related tasks:** Volume creation, LUN alignment

**Source docs:** NetApp Volume Block Size List.docx


---

# SnapMirror and Replication

> **Scope:** SnapMirror setup, initialization, update, break, resync, quiesce, DR failover/failback, schedule management.
> **Applies to:** ONTAP 8.x (7-Mode and Cluster-Mode), ONTAP 9.x
> **Source folders:** NetApp snapshot commands (includes SnapMirror), NetApp Volume commands, Word Docs from Tim

---

## Task: Show SnapMirror relationships

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Verify replication status, lag time, last transfer time.

**Commands:**
```
snapmirror show
snapmirror show -destination-volume <vol>
snapmirror show -source-vserver <svm>
snapmirror show -fields source-volume,destination-volume,state,status,lag-time,last-transfer-size,last-transfer-end-timestamp
snapmirror show -type DP
snapmirror show -type XDP
snapmirror status (7-Mode)
```

**Examples:**
```
NETCLSMDF1::> snapmirror show
NETCLSMDF1::> snapmirror show -fields lag-time,status,state
NETCLSMDF1::> snapmirror show -state snapmirrored
```

**Validation commands:**
- `snapmirror show -fields lag-time,status`
- Lag time should be under your RPO threshold

**Rollback / Caution:** Read-only.

**Related tasks:** SnapMirror update, initialize, break for DR

**Source docs:** NetApp snapshot commands, Word Docs from Tim

---

## Task: Initialize a SnapMirror relationship

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** SnapMirror relationship already created (via `snapmirror create`), destination volume exists, network connectivity between source and destination cluster

**When to use:** First-time seeding of a DR mirror; after relationship is created with `snapmirror create`.

**Commands:**
```
snapmirror initialize -destination-path <svm:vol>
snapmirror initialize -destination-path <svm:vol> -source-path <src-svm:src-vol>
snapmirror show -destination-volume <vol> -fields state,status
```

**Examples:**
```
NETCLSMDF1::> snapmirror initialize -destination-path svm_dr:vol_data01_dr
NETCLSMDF1::> snapmirror show -destination-volume vol_data01_dr -fields state,status,last-transfer-size
```

**Validation commands:**
- `snapmirror show -destination-volume <vol> -fields state,status`
- State should go: `uninitialized` → `snapmirrored`

**Rollback / Caution:** Initialization transfers ALL data from source. On large volumes this takes hours. Monitor with `snapmirror show`. Do not break relationship during transfer.

**Related tasks:** Create SnapMirror relationship, SnapMirror update, SnapMirror schedule

**Source docs:** NetApp snapshot commands

---

## Task: Update a SnapMirror relationship (manual)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** SnapMirror relationship in `snapmirrored` state

**When to use:** Trigger an on-demand update before a DR test or maintenance window.

**Commands:**
```
snapmirror update -destination-path <svm:vol>
snapmirror update -destination-path <svm:vol> -source-path <svm:vol>
snapmirror show -destination-volume <vol> -fields status,lag-time
```

**Examples:**
```
NETCLSMDF1::> snapmirror update -destination-path svm_dr:vol_data01_dr
NETCLSMDF1::> snapmirror show -destination-volume vol_data01_dr -fields status,lag-time
```

**Validation commands:**
- `snapmirror show -fields status,lag-time`
- Status: `idle`, lag time reduced

**Rollback / Caution:** Manual updates are additive — only changed blocks transfer. Safe to run at any time. Avoid during heavy source I/O if bandwidth is limited.

**Related tasks:** SnapMirror schedule, SnapMirror break, DR failover

**Source docs:** NetApp snapshot commands

---

## Task: Quiesce a SnapMirror relationship

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** SnapMirror in `snapmirrored` state

**When to use:** Pause replication before breaking mirror for DR failover, testing, or maintenance.

**Commands:**
```
snapmirror quiesce -destination-path <svm:vol>
snapmirror show -destination-volume <vol> -fields status
```

**Examples:**
```
NETCLSMDF1::> snapmirror quiesce -destination-path svm_dr:vol_data01_dr
NETCLSMDF1::> snapmirror show -destination-volume vol_data01_dr -fields status
```

**Validation commands:**
- Status: `quiesced`

**Rollback / Caution:** Quiesce stops future transfers but does not delete the relationship. To resume: `snapmirror resume`.

**Related tasks:** SnapMirror break, SnapMirror resync, DR failover

**Source docs:** NetApp snapshot commands

---

## Task: Break a SnapMirror relationship (DR failover)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** SnapMirror quiesced or idle

**When to use:** DR failover — make destination volume read-write so clients can access it.

**Commands:**
```
snapmirror break -destination-path <svm:vol>
snapmirror show -destination-volume <vol> -fields state,status
volume show -vserver <svm> -volume <vol> -fields state,junction-path
```

**Examples:**
```
NETCLSMDF1::> snapmirror quiesce -destination-path svm_dr:vol_data01_dr
NETCLSMDF1::> snapmirror break -destination-path svm_dr:vol_data01_dr
NETCLSMDF1::> volume show -vserver svm_dr -volume vol_data01_dr -fields state
```

**Validation commands:**
- `snapmirror show -destination-volume <vol> -fields state`
- State: `broken-off`
- `volume show -fields state` — volume: `online`

**Rollback / Caution:** After break, destination is writable. The relationship is severed — data written to destination is NOT replicated back. To resume protection: quiesce, resync (overwrites destination with source). Breaking is irreversible without resync.

**Related tasks:** SnapMirror resync, DR failback, volume reallocation post-break

**Source docs:** NetApp snapshot commands, NetApp Reallocation on a Snapmirrored Volume Commands.docx

---

## Task: Resync a SnapMirror relationship (failback)

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** SnapMirror in `broken-off` state; source cluster available

**When to use:** After DR failover, to re-establish replication back to the original direction (or reverse-resync for reverse replication).

**Commands:**
```
snapmirror resync -destination-path <svm:vol>
snapmirror show -destination-volume <vol> -fields state,status
```

**Examples:**
```
NETCLSMDF1::> snapmirror resync -destination-path svm_prod:vol_data01
```

**Validation commands:**
- `snapmirror show -fields state,status`
- State: `snapmirrored`

**Rollback / Caution:** Resync overwrites the destination with source data. Any writes made to the destination while broken will be LOST. Coordinate carefully with data owners. Consider a snapshot of destination before resync if needed.

**Related tasks:** SnapMirror break, DR failover, SnapMirror update

**Source docs:** NetApp snapshot commands, Word Docs from Tim

---

## Task: Create a SnapMirror schedule and policy

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, job schedules exist

**When to use:** Automate SnapMirror updates at desired RPO intervals.

**Commands:**
```
snapmirror policy show
snapmirror policy create -vserver <svm> -policy <policy-name> -type async-mirror
snapmirror modify -destination-path <svm:vol> -schedule <schedule-name>
snapmirror modify -destination-path <svm:vol> -policy <policy-name>
```

**Examples:**
```
NETCLSMDF1::> snapmirror modify -destination-path svm_dr:vol_data01_dr -schedule hourly
NETCLSMDF1::> snapmirror show -fields schedule,policy
```

**Validation commands:**
- `snapmirror show -fields schedule,policy`

**Rollback / Caution:** Setting too frequent a schedule on large volumes consumes bandwidth. Align schedule with RPO requirements and available WAN capacity.

**Related tasks:** Job schedule creation, SnapMirror policy, data protection SLAs

**Source docs:** NetApp snapshot commands


---

# Snapshot and Backup Operations

> **Scope:** Snapshot creation, policy management, schedule configuration, listing, deletion, restore from snapshot, snapshot reserve.
> **Applies to:** ONTAP 8.x (7-Mode and Cluster-Mode), ONTAP 9.x
> **Source folders:** NetApp snapshot commands, NetApp Volume commands

---

## Task: Show snapshots on a volume

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Audit snapshot inventory, identify old snapshots consuming space, verify policy is working.

**Commands:**
```
snapshot show -vserver <svm> -volume <vol>
snapshot show -vserver <svm> -volume <vol> -fields snapshot,create-time,size,owners
volume snapshot show -vserver <svm> -volume <vol>
snap list /vol/<volname> (7-Mode node shell)
```

**Examples:**
```
NETCLSMDF1::> snapshot show -vserver svm_prod -volume vol_data01
NETCLSMDF1::> snapshot show -vserver svm_prod -volume vol_data01 -fields snapshot,create-time,size
```

**Validation commands:**
- `snapshot show -vserver <svm> -volume <vol>`

**Rollback / Caution:** Read-only.

**Related tasks:** Create snapshot, delete snapshot, restore from snapshot

**Source docs:** NetApp Snapshot Commands Cluster.docx

---

## Task: Create a manual snapshot

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin, volume online

**When to use:** Before maintenance, upgrades, application changes, or any risky operation.

**Commands:**
```
snapshot create -vserver <svm> -volume <vol> -snapshot <snapshot-name>
volume snapshot create -vserver <svm> -volume <vol> -snapshot <snapshot-name>
snap create /vol/<volname> <snapshot-name> (7-Mode)
```

**Examples:**
```
NETCLSMDF1::> snapshot create -vserver svm_prod -volume vol_data01 -snapshot pre_upgrade_20240115
NETCLSMDF1::> snapshot show -vserver svm_prod -volume vol_data01 -snapshot pre_upgrade_20240115
```

**Validation commands:**
- `snapshot show -vserver <svm> -volume <vol> -snapshot <name>`

**Rollback / Caution:** Snapshots consume space proportional to change rate. Always delete pre-maintenance snapshots after successful validation.

**Related tasks:** Restore from snapshot, delete snapshot, SnapMirror update

**Source docs:** NetApp Snapshot Commands Cluster.docx

---

## Task: Create and manage snapshot policies

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, job schedules exist

**When to use:** Automate snapshot creation on a schedule; standardize retention across volumes.

**Commands:**
```
snapshot policy show
snapshot policy create -policy <policy-name> -enabled true -schedule1 <schedule> -count1 <n> -schedule2 <schedule> -count2 <n>
volume modify -vserver <svm> -volume <vol> -snapshot-policy <policy-name>
snapshot policy show -policy <policy-name> -instance
```

**Examples:**
```
NETCLSMDF1::> snapshot policy show
NETCLSMDF1::> snapshot policy create -policy daily_weekly -enabled true -schedule1 daily -count1 7 -schedule2 weekly -count2 4
NETCLSMDF1::> volume modify -vserver svm_prod -volume vol_data01 -snapshot-policy daily_weekly
```

**Validation commands:**
- `snapshot policy show`
- `volume show -fields snapshot-policy`

**Rollback / Caution:** A policy with a high count on a high-change-rate volume will consume significant aggregate space. Review space usage after enabling.

**Related tasks:** Job schedule creation, snapshot reserve, snapshot cleanup

**Source docs:** NetApp Snapshot Commands Cluster.docx

---

## Task: Create job schedules for snapshot policies

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin

**When to use:** Before creating snapshot policies; customize schedule to match backup SLA.

**Commands:**
```
job schedule cron create -name "Hourly_Sched" -minute 5
job schedule cron create -name "Daily_Sched" -hour 0 -minute 10
job schedule cron create -name "Weekly_Sched" -dayofweek Sunday -hour 0 -minute 15
job schedule cron create -name "Hourly_Sched_5-9-13-17" -dayofweek "Monday,Tuesday,Wednesday,Thursday,Friday" -hour 5,9,13,17 -minute 5
job schedule show
```

**Examples:**
```
NETCLSMDF1::> job schedule cron create -name "Daily_2300" -hour 23 -minute 0
NETCLSMDF1::> job schedule cron create -name "Daily Mon-Fr1" -dayofweek "Monday,Tuesday,Wednesday,Thursday,Friday" -hour 0 -minute 5
NETCLSMDF1::> job schedule show
```

**Validation commands:**
- `job schedule show`

**Rollback / Caution:** Deleting a schedule used by an active snapshot policy or SnapMirror will break those jobs silently.

**Related tasks:** Snapshot policy creation, SnapMirror schedule

**Source docs:** NetApp Snapshot Commands Cluster.docx

---

## Task: Delete snapshots

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin; snapshot not locked by SnapMirror or clone

**When to use:** Free space by removing old or unneeded snapshots.

**Commands:**
```
snapshot delete -vserver <svm> -volume <vol> -snapshot <snapshot-name>
snapshot delete -vserver <svm> -volume <vol> -snapshot *
snap delete /vol/<volname> <snapshot-name> (7-Mode)
snap delete -a /vol/<volname> (7-Mode: all)
```

**Examples:**
```
NETCLSMDF1::> snapshot delete -vserver svm_prod -volume vol_data01 -snapshot pre_upgrade_20240115
NETCLSMDF1::> snapshot show -vserver svm_prod -volume vol_data01
```

**Validation commands:**
- `snapshot show -vserver <svm> -volume <vol>` — snapshot absent
- `volume show -fields snapshot-used`

**Rollback / Caution:** SnapMirror-locked snapshots cannot be deleted — they will show `owners: snapmirror`. Deleting a snapshot used as a SnapMirror base snapshot will break the incremental chain; full re-initialization required.

**Related tasks:** Free volume space, snapshot policy cleanup, SnapMirror management

**Source docs:** NetApp Snapshot Commands Cluster.docx

---

## Task: Restore a volume from snapshot

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin, snapshot exists, volume can be taken offline briefly (for full restore)

**When to use:** Roll back a volume to a known-good state after data corruption or accidental deletion.

**Commands:**
```
volume snapshot restore -vserver <svm> -volume <vol> -snapshot <snapshot-name>
snap restore -s <snapshot-name> /vol/<volname> (7-Mode)
```

**Examples:**
```
NETCLSMDF1::> volume snapshot restore -vserver svm_prod -volume vol_data01 -snapshot pre_upgrade_20240115
```

**Validation commands:**
- `volume show -vserver <svm> -volume <vol> -fields state`
- Verify data integrity with application team after restore

**Rollback / Caution:** Volume snapshot restore is a DESTRUCTIVE operation — all data written AFTER the snapshot is LOST. Notify users and take a fresh snapshot of current state before restoring, in case you need to revert the revert.

**Related tasks:** Clone from snapshot, single-file restore, SnapMirror resync

**Source docs:** NetApp Snapshot Commands Cluster.docx

---

## Task: Manage snapshot reserve space

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Tune how much volume space is reserved for snapshots; reduce if snaps are consuming too much.

**Commands:**
```
volume show -fields snapshot-reserve-percent,snapshot-space-used
volume modify -vserver <svm> -volume <vol> -snapshot-reserve-percent <pct>
snap reserve /vol/<volname> <percent> (7-Mode)
```

**Examples:**
```
NETCLSMDF1::> volume show -fields snapshot-reserve-percent,snapshot-space-used
NETCLSMDF1::> volume modify -vserver svm_prod -volume vol_data01 -snapshot-reserve-percent 5
```

**Validation commands:**
- `volume show -fields snapshot-reserve-percent`

**Rollback / Caution:** Setting reserve too low causes snapshots to consume active filesystem space. Set based on change rate and retention schedule.

**Related tasks:** Volume capacity, snapshot policy, autosize

**Source docs:** NetApp Volume commands, NetApp Snapshot Commands Cluster.docx
