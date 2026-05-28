import glob, re, os

files_changed = []
total_replacements = 0

for p in glob.glob('d:/LQP/Project/EES_2026_Dashboard/**/*.py', recursive=True):
    if '__pycache__' in p:
        continue
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    count_before = len(re.findall(r'use_container_width', content))
    
    # Replace width='stretch' -> width='stretch'
    new_content = re.sub(r'\buse_container_width\s*=\s*True\b', "width='stretch'", content)
    # Replace width='content' -> width='content'
    new_content = re.sub(r'\buse_container_width\s*=\s*False\b', "width='content'", new_content)
    
    if new_content != content:
        total_replacements += count_before
        with open(p, 'w', encoding='utf-8') as f:
            f.write(new_content)
        rel = os.path.relpath(p, 'd:/LQP/Project/EES_2026_Dashboard')
        files_changed.append(f'  {rel} ({count_before} fixes)')

print(f'Total files changed: {len(files_changed)}')
print(f'Total replacements: {total_replacements}')
for f in files_changed:
    print(f)
