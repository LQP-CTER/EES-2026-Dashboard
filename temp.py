with open('shared/codebook.py', 'a', encoding='utf-8') as f:
    f.write('\n# ============================================================\n')
    f.write('# CODEBOOK NHÓM 2A, 2B, 3A, 3B (Auto-generated mapping)\n')
    f.write('# ============================================================\n\n')
    
    def gen_codebook(name, start_idx):
        cb = f'CODEBOOK_{name} = {{\n'
        cb += f"    'Q1': {{'col_idx': 1, 'tên': 'Năm sinh', 'loại': 'nhân_khẩu', 'trụ_cột': None}},\n"
        cb += f"    'Q2': {{'col_idx': 2, 'tên': 'Giới tính', 'loại': 'nhân_khẩu', 'trụ_cột': None}},\n"
        cb += f"    'Q5': {{'col_idx': 5, 'tên': 'Thâm niên', 'loại': 'nhân_khẩu', 'trụ_cột': None}},\n"
        
        # Likert (21 questions)
        pillars = ['TC1']*4 + ['TC2']*5 + ['TC3']*4 + ['TC4']*4 + ['TC5']*4
        for i in range(21):
            cb += f"    'Q{i+9}': {{'col_idx': {start_idx+i}, 'tên': 'Câu hỏi {i+1}', 'loại': 'likert', 'trụ_cột': '{pillars[i]}'}},\n"
            
        cb += f"    'Q30': {{'col_idx': {start_idx+21}, 'tên': 'Ý định ở lại', 'loại': 'intent', 'trụ_cột': None}},\n"
        cb += f"    'Q31': {{'col_idx': {start_idx+22}, 'tên': 'eNPS', 'loại': 'enps', 'trụ_cột': None}},\n"
        
        cb += f"    'Q32': {{'col_idx': {start_idx+23}, 'tên': 'Thích nhất', 'loại': 'open', 'trụ_cột': None}},\n"
        cb += f"    'Q33': {{'col_idx': {start_idx+24}, 'tên': 'Giúp gắn bó', 'loại': 'open', 'trụ_cột': None}},\n"
        cb += f"    'Q34': {{'col_idx': {start_idx+25}, 'tên': 'Cần cải thiện', 'loại': 'open', 'trụ_cột': None}},\n"
        cb += '}\n\n'
        return cb

    f.write(gen_codebook('2A', 13))
    f.write(gen_codebook('2B', 13))
    f.write(gen_codebook('3A', 15))
    f.write(gen_codebook('3B', 15))
