/**
 * extract_docx_browser.js
 *
 * Self-contained .docx text extractor for use in the browser (Chrome DevTools / MCP).
 * No external libraries required — uses native DecompressionStream API (Chrome 80+).
 *
 * Usage: paste into browser console or execute via Claude-in-Chrome javascript_tool.
 *
 * IMPORTANT: Replace <TENANT> with your SharePoint tenant name (e.g., mycsunemail).
 */

// ─── Core extraction function ─────────────────────────────────────────────────

window.extractDocx = async (arrayBuf) => {
  const bytes = new Uint8Array(arrayBuf);

  const findPK = (from) => {
    for (let i = from; i < bytes.length - 3; i++) {
      if (bytes[i] === 0x50 && bytes[i+1] === 0x4B &&
          bytes[i+2] === 0x03 && bytes[i+3] === 0x04) return i;
    }
    return -1;
  };

  let pos = 0;
  while ((pos = findPK(pos)) !== -1) {
    const fnLen   = bytes[pos+26] | (bytes[pos+27] << 8);
    const extraLen = bytes[pos+28] | (bytes[pos+29] << 8);
    const fnStart = pos + 30;
    const fn = new TextDecoder().decode(bytes.slice(fnStart, fnStart + fnLen));
    const dataStart = fnStart + fnLen + extraLen;
    const compSize  = bytes[pos+18] | (bytes[pos+19]<<8) | (bytes[pos+20]<<16) | (bytes[pos+21]<<24);
    const method    = bytes[pos+8]  | (bytes[pos+9]  << 8);

    if (fn === 'word/document.xml') {
      let xmlBytes;
      if (method === 8) {
        // Deflate-compressed (standard for .docx)
        const stream = new DecompressionStream('deflate-raw');
        const writer = stream.writable.getWriter();
        writer.write(bytes.slice(dataStart, dataStart + compSize));
        writer.close();
        xmlBytes = new Uint8Array(await new Response(stream.readable).arrayBuffer());
      } else {
        // Stored (uncompressed)
        xmlBytes = bytes.slice(dataStart, dataStart + compSize);
      }
      const xml = new TextDecoder().decode(xmlBytes);
      // Extract text nodes from <w:t> tags, add spaces between runs
      return xml
        .replace(/<w:t[^>]*>([^<]*)<\/w:t>/g, '$1 ')
        .replace(/<[^>]+>/g, '')
        .replace(/\s+/g, ' ')
        .trim();
    }
    pos = dataStart + compSize;
  }
  return null; // word/document.xml not found
};

// ─── Download one folder's contents as a combined .txt file ───────────────────

window._downloadFolder = async (folder, tenant) => {
  const base = `https://${tenant}-my.sharepoint.com`;
  const url  = `${base}/_api/v2.0/me/drive/items/${folder.id}/children?$select=name,id,file&$top=200`;

  const resp = await fetch(url, {
    credentials: 'include',
    headers: { 'Accept': 'application/json' }
  });
  const data = await resp.json();

  const files = (data.value || []).filter(f =>
    f.file && (f.name.endsWith('.docx') || f.name.endsWith('.txt'))
  );

  console.log(`Folder: ${folder.name} — ${files.length} files`);

  let combined = `=== FOLDER: ${folder.name} ===\n\n`;

  for (const file of files) {
    console.log(`  Downloading: ${file.name}`);
    const dlResp = await fetch(
      `${base}/_api/v2.0/me/drive/items/${file.id}/content`,
      { credentials: 'include' }
    );
    const buf = await dlResp.arrayBuffer();

    let text = '';
    if (file.name.endsWith('.docx')) {
      text = await window.extractDocx(buf) || '(no text extracted)';
    } else {
      text = new TextDecoder().decode(buf);
    }
    combined += `\n--- FILE: ${file.name} ---\n${text}\n`;
  }

  // Trigger browser download as .txt
  const blob = new Blob([combined], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `raw_${folder.name.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  console.log(`  ✓ Downloaded: raw_${folder.name.replace(/[^a-zA-Z0-9]/g, '_')}.txt`);
};

// ─── Process folders in batches of 3 ─────────────────────────────────────────
// Call this after defining your folders array:
//
// const TENANT = 'mycsunemail';  // <-- change this
// const folders = [ {name: 'ACP commands', id: '...'}, ... ];
//
// // Batch 1: indices 0-2
// for (const f of folders.slice(0, 3)) { await window._downloadFolder(f, TENANT); }
//
// // Batch 2: indices 3-5
// for (const f of folders.slice(3, 6)) { await window._downloadFolder(f, TENANT); }
//
// etc.

console.log('extract_docx_browser.js loaded. Define folders array and call _downloadFolder().');
