#!/usr/bin/env python3
"""Structural validator only; it does not validate poetic quality or prosody."""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
for d in (ROOT/'skills').iterdir():
 if not d.is_dir(): continue
 p=d/'SKILL.md'
 if not p.exists(): errors.append(f'Missing SKILL.md: {d.name}'); continue
 s=p.read_text(encoding='utf-8')
 if not s.startswith('---\n'): errors.append(f'Missing frontmatter: {d.name}'); continue
 parts=s.split('---',2)
 if len(parts)<3: errors.append(f'Unclosed frontmatter: {d.name}'); continue
 m=re.search(r'(?m)^name:\s*([a-z0-9-]+)\s*$',parts[1]); desc=re.search(r'(?m)^description:\s*(.+)$',parts[1])
 if not m or m.group(1)!=d.name: errors.append(f'name missing/mismatch: {d.name}')
 if not desc or not desc.group(1).strip(): errors.append(f'description missing: {d.name}')
 for md in d.rglob('*.md'):
  body=md.read_text(encoding='utf-8')
  for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',body):
   if target.startswith(('http://','https://','#','mailto:')): continue
   local=(md.parent/target.split('#',1)[0]).resolve()
   if target.split('#',1)[0] and not local.exists(): errors.append(f'Broken link: {md.relative_to(ROOT)} -> {target}')
 try:
  cases=json.loads((d/'evals/evals.json').read_text(encoding='utf-8')).get('cases',[])
  if len(cases)<5: errors.append(f'Need at least five evals: {d.name}')
  for c in cases:
   if not c.get('id') or not c.get('prompt') or not c.get('acceptance'): errors.append(f'Malformed eval: {d.name}')
 except Exception as e: errors.append(f'Invalid eval file {d.name}: {e}')
if errors:
 print('VALIDATION FAILED'); [print('ERROR:',e) for e in errors]; sys.exit(1)
print('STRUCTURE OK'); print('Checked skills, frontmatter, local Markdown links and eval cases.'); print('This does not validate literary quality, grammar, meter or rhyme.')
