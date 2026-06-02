with open('extracted_code.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_block(n):
    start = -1
    end = -1
    for i, l in enumerate(lines):
        if l.startswith(f'# BLOCK {n}'):
            start = i + 1
        elif start != -1 and l.startswith(f'# BLOCK {n+1}'):
            end = i
            break
    if end == -1: end = len(lines)
    return ''.join(lines[start:end])

b0 = get_block(0)

with open('shared/codebook.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'EWS_TENURE_THRESHOLD' not in content:
    # Just append it to the top after imports / basic constants
    idx = content.find('PILLAR_WEIGHTS = {')
    if idx != -1:
        new_content = content[:idx] + b0 + '\n\n' + content[idx:]
        with open('shared/codebook.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('Updated codebook.py')
    else:
        print('Could not find PILLAR_WEIGHTS in codebook.py')
else:
    print('codebook.py already updated')
