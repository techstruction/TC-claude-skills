---
name: cli-doc-synthesizer
description: >
  Use this skill whenever the user wants to synthesize, organize, or convert a collection
  of CLI or vendor documentation files into structured knowledge files for AI tools, custom
  GPTs, chatbots, or reference wikis. Triggers include: "turn my docs into knowledge files",
  "synthesize my NetApp/Cisco/VMware/Palo Alto docs", "build a CustomGPT knowledge base from
  my command docs", "organize my runbooks into structured markdown", "I have a bunch of .docx
  command files I want to clean up", "pull my docs from SharePoint and synthesize them", or
  any mention of converting vendor CLI documentation into structured chunks. Also use when the
  user has already downloaded raw docs and wants them categorized and formatted with consistent
  task entries (prereqs, commands, examples, validation, rollback).
---

# CLI Documentation Synthesizer

You are running a pipeline that turns a raw collection of vendor CLI/command documentation
(Word docs, text files, PDFs) into a set of structured Markdown knowledge files — ready for
upload to a CustomGPT, RAG system, or internal wiki.

The output is a set of `.md` files, one per logical category, where every task follows a
consistent chunk format that AI tools can reliably parse and retrieve.

---

## Step 0: Understand the User's Situation

Before doing anything, figure out where the documents live:

**Option A — Files already on disk (local folder)**
The user has a folder of `.docx`, `.txt`, or `.pdf` files already accessible. Ask them to
select the folder via the folder-picker, or confirm the path if you already have access.
→ Skip to Step 2 (Extract Text).

**Option B — Files in SharePoint / OneDrive for Business**
The user's docs are in Microsoft SharePoint (OneDrive for Business). You'll need the
Claude-in-Chrome MCP extension to retrieve them via the SharePoint REST API.
→ Proceed from Step 1 (Download from SharePoint).

If unsure, ask: "Are your documents already in a local folder, or are they in SharePoint/OneDrive?"

---

## Step 1: Download from SharePoint (Only if needed)

**Prerequisites:**
- User must have the Claude-in-Chrome browser extension installed and active
- User must be logged into their SharePoint / OneDrive in the browser
- User must navigate to their document library folder in the browser tab

### 1a. Discover the drive root and folder ID

Run this in the browser tab (via Chrome MCP `javascript_tool`):

```javascript
const resp = await fetch(
  'https://<tenant>-my.sharepoint.com/_api/v2.0/me/drive/root',
  { credentials: 'include', headers: { 'Accept': 'application/json' } }
);
const data = await resp.json();
console.log(JSON.stringify({ id: data.id, name: data.name, webUrl: data.webUrl }));
```

Replace `<tenant>` with the SharePoint tenant (e.g., `mycsunemail`). If you don't know it,
check the URL bar of the active tab — it's the subdomain before `-my.sharepoint.com`.

### 1b. List subfolders under the target folder

```javascript
const resp = await fetch(
  'https://<tenant>-my.sharepoint.com/_api/v2.0/me/drive/root:/Documents/<path>:/children?$select=name,id,folder&$top=200',
  { credentials: 'include', headers: { 'Accept': 'application/json' } }
);
const data = await resp.json();
console.log(JSON.stringify((data.value || []).filter(i => i.folder).map(f => ({ name: f.name, id: f.id }))));
```

### 1c. Download files from each folder as text

Process folders in batches of 3 to avoid Chrome's 45-second CDP timeout. For each batch,
run this JavaScript (substitute real folder IDs):

```javascript
window.extractDocx = async (arrayBuf) => {
  const bytes = new Uint8Array(arrayBuf);
  const findPK = (from) => {
    for (let i = from; i < bytes.length - 3; i++) {
      if (bytes[i] === 0x50 && bytes[i+1] === 0x4B && bytes[i+2] === 0x03 && bytes[i+3] === 0x04) return i;
    }
    return -1;
  };
  let pos = 0, xmlContent = null;
  while ((pos = findPK(pos)) !== -1) {
    const fnLen = bytes[pos+26] | (bytes[pos+27] << 8);
    const extraLen = bytes[pos+28] | (bytes[pos+29] << 8);
    const fnStart = pos + 30;
    const fn = new TextDecoder().decode(bytes.slice(fnStart, fnStart + fnLen));
    const dataStart = fnStart + fnLen + extraLen;
    const compSize = bytes[pos+18] | (bytes[pos+19]<<8) | (bytes[pos+20]<<16) | (bytes[pos+21]<<24);
    const method = bytes[pos+8] | (bytes[pos+9] << 8);
    if (fn === 'word/document.xml') {
      let xmlBytes;
      if (method === 8) {
        const stream = new DecompressionStream('deflate-raw');
        const writer = stream.writable.getWriter();
        writer.write(bytes.slice(dataStart, dataStart + compSize));
        writer.close();
        xmlBytes = new Uint8Array(await new Response(stream.readable).arrayBuffer());
      } else {
        xmlBytes = bytes.slice(dataStart, dataStart + compSize);
      }
      xmlContent = new TextDecoder().decode(xmlBytes);
      break;
    }
    pos = dataStart + compSize;
  }
  if (!xmlContent) return null;
  return xmlContent.replace(/<w:t[^>]*>([^<]*)<\/w:t>/g, '$1 ').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
};

window._downloadFolder = async (folder) => {
  const url = `https://<tenant>-my.sharepoint.com/_api/v2.0/me/drive/items/${folder.id}/children?$select=name,id,file&$top=200`;
  const resp = await fetch(url, { credentials: 'include', headers: { 'Accept': 'application/json' } });
  const data = await resp.json();
  const files = (data.value || []).filter(f => f.file && (f.name.endsWith('.docx') || f.name.endsWith('.txt')));
  let combined = `=== FOLDER: ${folder.name} ===\n\n`;
  for (const file of files) {
    const dlResp = await fetch(
      `https://<tenant>-my.sharepoint.com/_api/v2.0/me/drive/items/${file.id}/content`,
      { credentials: 'include' }
    );
    const buf = await dlResp.arrayBuffer();
    let text = '';
    if (file.name.endsWith('.docx')) {
      text = await window.extractDocx(buf) || '';
    } else {
      text = new TextDecoder().decode(buf);
    }
    combined += `\n--- FILE: ${file.name} ---\n${text}\n`;
  }
  const blob = new Blob([combined], { type: 'text/plain' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = `netapp_raw_${folder.name.replace(/[^a-zA-Z0-9]/g, '_')}.txt`; a.click();
};

// Process batch (adjust indices as needed):
const folders = [ /* array of {name, id} objects */ ];
for (const f of folders.slice(0, 3)) { await window._downloadFolder(f); }
```

**Important Chrome settings:** If only the first download succeeds, the user must enable
automatic downloads for the SharePoint domain:
1. Go to `chrome://settings/content/automaticDownloads`
2. Add the SharePoint domain to the "Allowed" list

**Batching:** Process 3 folders per JS call. Wait for downloads to appear in the user's
Downloads folder before running the next batch.

### 1d. Move downloaded files to working directory

Once all `.txt` files are downloaded to the user's Downloads folder, move them to a
dedicated working directory:

```bash
mkdir -p /sessions/.../netapp_raw   # or use the mounted Downloads path
# Files will be in mnt/Downloads/*.txt — copy to working dir
```

---

## Step 2: Extract and Deduplicate Raw Text

If files were downloaded in duplicate (e.g., Chrome re-downloaded them), keep the most
recent version of each file:

```python
# scripts/deduplicate_files.py handles this — see scripts/ directory
python scripts/deduplicate_files.py <input_dir> <output_dir>
```

Or manually: if you have `filename.txt` and `filename (1).txt`, keep `filename (1).txt`
(the retry download is usually the more complete one).

Verify you have all expected folders covered:
```bash
ls <raw_dir>/ | wc -l    # count files
ls <raw_dir>/            # review names
```

---

## Step 3: Define the Category Structure

Before synthesizing, determine the output categories with the user. The goal is 6–12
fat `.md` files covering distinct functional areas. Each file becomes one knowledge source
for the CustomGPT.

**For NetApp/ONTAP**, the proven category set is:
```
01_ONTAP_Cluster_Admin_Fundamentals
02_SVM_and_Networking
03_Volumes_and_Aggregates
04_SnapMirror_and_Replication
05_Snapshot_and_Backup
06_CIFS_NFS_SMB_Management
07_Hardware_Storage_Shelf_Operations
08_Troubleshooting_and_Health_Checks
09_Common_Runbooks
10_Deprecated_Dangerous_Commands
```

**For other vendors** (Cisco IOS, Palo Alto PAN-OS, VMware vSphere CLI, etc.), derive
categories from the source folder names and the functional areas they represent. Good
universal categories include:
- System/Device Administration
- Networking and Interfaces
- Storage/Data Management (if applicable)
- Security and Access Control
- High Availability / Redundancy
- Monitoring, Logging, Troubleshooting
- Backup / Replication
- Common Runbooks (multi-step procedures)
- Deprecated / Dangerous Commands

Present the proposed categories to the user and confirm before synthesizing.

---

## Step 4: Synthesize into Structured Markdown

Read each raw source file and synthesize its content into structured task entries. Write
one `.md` file per category to the output directory.

### The chunk format (use for every task entry)

```markdown
## Task: <descriptive task name>

**Applies to:** <version(s) — e.g., ONTAP 9.x, IOS 15+, PAN-OS 10.x>

**Prereqs:** <what must exist or be configured before running these commands>

**When to use:** <the operational scenario — when would an admin reach for this>

**Commands:**
\`\`\`
<commands, one per line, with placeholders in <angle brackets>>
\`\`\`

**Examples:**
\`\`\`
<real-world example with realistic hostnames/values from the source docs>
\`\`\`

**Validation commands:**
- <command to verify the change took effect>

**Rollback / Caution:** <how to undo, or what could go wrong>

**Related tasks:** <names of other tasks that are commonly done before/after>

**Source docs:** <which source files this was synthesized from>
```

### Synthesis rules

- **One task per distinct operation.** Don't merge "show X" and "create X" into one entry —
  keep them separate so the AI can retrieve them independently.
- **Preserve real examples.** If the source docs contain real cluster names, IPs, or command
  output (e.g., `NETCLSMDF1::>`), keep them in the Examples block — they make the AI's
  answers more grounded.
- **Flag version differences explicitly.** If a command works differently in 7-Mode vs
  Cluster-Mode (for ONTAP), or across major versions, note it clearly with `(7-Mode)` or
  `(Cluster-Mode)` inline.
- **Rollback / Caution is never empty.** Even for read-only commands, write "Read-only — no
  changes." Never leave this blank.
- **Related tasks create a web of context.** Link to the tasks that logically precede or
  follow this one. This helps the AI walk the user through a full workflow.
- **Source docs enable traceability.** Always record which raw files the content came from.

### File header format

Each output `.md` file should start with:

```markdown
# <Category Name>

> **Scope:** <one-sentence description of what this file covers>
> **Applies to:** <versions>
> **Source folders:** <which raw source folders fed into this file>

---
```

### Synthesis strategy

Read raw files in logical groups based on which categories they feed. For a 10-category
output set, you'll typically read 2–4 source files per category. Don't try to read all
18+ source files at once — work category by category:

1. Write the file header
2. Read relevant source files (use `Read` tool)
3. Extract distinct tasks and write each as a chunk entry
4. Move to the next category

Aim for 6–15 task entries per file. Quality over quantity — a well-structured entry for a
common operation is more valuable than 30 shallow entries.

---

## Step 5: Special Handling for the Last Two Categories

### Common Runbooks (second-to-last file)

This file doesn't come from a single source folder — it synthesizes multi-step procedures
that span multiple categories. Each runbook should be a complete numbered workflow:

1. State what to verify/check first
2. Walk through each command in sequence
3. Include validation at each step
4. End with a full post-procedure validation block and rollback notes

Good runbook topics: end-to-end provisioning, DR failover, disk replacement, new device/SVM
setup, morning health check, pre-upgrade checklist.

### Deprecated / Dangerous Commands (last file)

This file serves as a safety guardrail for the CustomGPT — it prevents the AI from
recommending outdated or destructive commands. Structure it as:

- **Version-specific commands** with a mapping table (old → new equivalent)
- **Destructive operations** with explicit risk levels and required precautions
- **Dangerous configurations** (e.g., open ACLs, `0.0.0.0/0` rules)
- **A summary table** at the end: Command | Risk Level | Notes

---

## Step 6: Output and Delivery

Save all synthesized files to the output directory (`mnt/Downloads/<VendorName>_Synthesized/`
or as requested by the user). File naming convention: `NN_Category_Name.md` with zero-padded
sequence numbers.

When all files are written, present them with `computer://` links and confirm the count and
total size:

```
All 10 knowledge files are ready in Downloads/<VendorName>_Synthesized/.
Total: ~100KB across 10 files — ready for CustomGPT upload.
```

---

## Common Issues and Fixes

| Problem | Cause | Fix |
|---|---|---|
| Only 1 of N files downloaded | Chrome blocks multiple programmatic downloads | User adds domain to `chrome://settings/content/automaticDownloads` |
| CDP timeout (45s) after large JS call | Too many folders in one async call | Batch to 3 folders per JS call |
| SharePoint 404 on folder fetch | Wrong username in drive path | Call `/me/drive/root` first to discover actual username |
| JSZip / CDN script blocked | SharePoint CSP blocks external scripts | Use native `DecompressionStream('deflate-raw')` instead — bundled in `scripts/extract_docx.js` |
| Duplicate downloaded files (`file (1).txt`) | Download ran twice due to retry | Dedup by keeping `(1)` version; use `scripts/deduplicate_files.py` |
| `.docx` shows garbled/empty text | Incorrect deflate method | Use `deflate-raw` (not `deflate`) for Office Open XML files |
| Chrome extension blocks base64 returns | Extension content filter | Download as `.txt` blob to disk; don't return file content via JS return value |

---

## References

- `references/chunk_format_example.md` — A complete worked example of a synthesized task entry
- `references/category_templates.md` — Starter category lists for common vendors (NetApp, Cisco, Palo Alto, VMware)
- `scripts/deduplicate_files.py` — Deduplicates downloaded files keeping newest version
- `scripts/extract_docx_browser.js` — Self-contained JS for native .docx extraction (no CDN dependencies)
