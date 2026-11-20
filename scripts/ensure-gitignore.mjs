#!/usr/bin/env node
// ---------------------------------------------------------------------------------
// AID - add lines to a project's .gitignore once (T17 I-26)
//
// WHY: link-project.sh appended `.mcp.json` with LF and link-project.bat with a blank line
// and CRLF, and each one's "is it there?" check missed the other's spelling. A project
// linked with both got the line twice, and `.aid/audit/` (the hook audit log) was never
// ignored at all.
// WHAT: a line is added only when no existing line equals it after stripping a trailing
// CR, spaces and tabs. A missing final newline is added first, no blank line is inserted,
// and new lines use CRLF when the file already has CRLF, else LF. Nothing is rewritten:
// the new lines are appended. The other patterns of
// .claude/templates/gitignore-aid-patterns.txt are NOT added (state and context may be
// team-tracked); one line points at that template.
// CONNECTION: called by link-project.sh and link-project.bat (both already need node).
// scripts/init-project.sh writes a new .gitignore that already holds `.aid/audit/`.
//
// Usage: node scripts/ensure-gitignore.mjs <target-project> <line>...
// Exit 0 on success (prints what it added); 1 when the file could not be read or written.
// ---------------------------------------------------------------------------------
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const TEMPLATE = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '.claude',
  'templates', 'gitignore-aid-patterns.txt');

function main() {
  const [target, ...wanted] = process.argv.slice(2);
  if (!target || wanted.length === 0) {
    process.stderr.write('usage: node ensure-gitignore.mjs <target-project> <line>...\n');
    process.exit(2);
  }
  const file = path.join(target, '.gitignore');
  // latin1 maps every byte to one char, so comparing and appending never re-encodes the
  // user's own lines. A UTF-8 BOM is not part of the first line.
  let text = '';
  try {
    text = fs.readFileSync(file).toString('latin1');
  } catch (e) {
    if (e.code !== 'ENOENT') {
      process.stderr.write('[ERROR] ensure-gitignore: cannot read ' + file + ': ' + e.message + '\n');
      process.exit(1);
    }
  }
  const body = text.startsWith('\xef\xbb\xbf') ? text.slice(3) : text;
  const have = new Set(body.split('\n').map((l) => l.replace(/[\r \t]+$/, '')));
  const eol = body.includes('\r\n') ? '\r\n' : '\n';

  let add = '';
  const added = [];
  for (const line of wanted) {
    if (have.has(line)) continue;
    have.add(line);
    add += line + eol;
    added.push(line);
  }
  if (added.length) {
    if (text.length && !text.endsWith('\n')) add = (text.endsWith('\r') ? '\n' : eol) + add;
    try {
      fs.appendFileSync(file, Buffer.from(add, 'latin1'));
    } catch (e) {
      process.stderr.write('[ERROR] ensure-gitignore: cannot write ' + file + ': ' + e.message + '\n');
      process.exit(1);
    }
    for (const line of added) process.stdout.write('  [OK] ' + line + ' added to .gitignore\n');
  }
  process.stdout.write('  [INFO] More AID ignore patterns (not added automatically): ' +
    TEMPLATE.split(path.sep).join('/') + '\n');
}

main();
