# Chunk Format — Worked Example

This is a complete, well-formed task entry showing what the output should look like.

---

## Task: Show NFS export policies and rules

**Applies to:** ONTAP 8.x Cluster-Mode, ONTAP 9.x

**Prereqs:** Cluster admin or SVM admin

**When to use:** Audit which clients have access to which volumes; troubleshoot NFS mount
failures where the client gets "permission denied" or cannot reach the mount point.

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
- `vserver export-policy rule show -policyname <policy>` — confirm rules are listed
- `vserver export-policy check-access -vserver <svm> -volume <vol> -client-ip <ip> -authentication-method sys -protocol nfs3 -access-type read-write` — simulate access check

**Rollback / Caution:** Read-only — no changes made.

**Related tasks:** Create export policy, modify access rules, NFS mount troubleshooting,
NFS access check

**Source docs:** NetApp NFS commands

---

## What makes this a good entry

- **Task name** is an action phrase, not a noun ("Show NFS export policies", not "NFS Export Policies")
- **Applies to** is specific about version and mode (7-Mode vs Cluster-Mode matters for ONTAP)
- **When to use** describes a real operational scenario — not just "use when you want to see policies"
- **Commands** use `<angle-bracket>` placeholders for variable parts
- **Examples** use real cluster names from the source docs — this grounds the AI's answers
- **Validation commands** include a second, deeper check (the access simulation), not just the show command
- **Rollback** explicitly says "Read-only" — never left blank
- **Related tasks** form a navigation web so the AI can suggest next steps
- **Source docs** traces back to the raw input file
