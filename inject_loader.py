import re

with open('v3_pipeline.py', 'r', encoding='utf-8') as f:
    pipeline_code = f.read()

with open('utils/data_loader.py', 'r', encoding='utf-8') as f:
    data_loader_code = f.read()

# Fix imports in data_loader.py
import_block = """
from shared.codebook import (
    get_codebook, PILLAR_WEIGHTS, get_role_question, get_pillar_questions, 
    classify_ei, calc_engagement_pct, get_item,
    TENURE_MAP, TENURE_LABELS, EWS_TENURE_THRESHOLD, SENIOR_TENURE_THRESHOLD,
    ENPS_BINS, ENPS_LABELS, ENPS_PROMOTER_MIN, ENPS_DETRACTOR_MAX,
    MIN_UNIT_N, ANOMALY_STD_MULTIPLIER, DEFAULT_WEIGHTS, CALIBRATED_WEIGHTS,
    DEMO_MAP
)
from scipy import stats as scipy_stats
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score
import warnings
"""

# Replace the line containing get_codebook import with our extended import block
data_loader_code = re.sub(r'from shared\.codebook import .*?\n', import_block, data_loader_code)

# Prepend the pipeline code just before def load_group(group_id: str):
data_loader_code = data_loader_code.replace('def load_group(group_id: str):', pipeline_code + '\n\ndef load_group(group_id: str):')

# Now, we need to UPDATE load_group to actually call normalize_raw_data and compute_all_indices.
# In load_group:
# 1. df_raw = pd.DataFrame(data). Replace the manual demographic/likert decode with:
# df = df_raw.copy()
# df = normalize_raw_data(df, group_id)
# Then it does weighting, map_survey_to_org
# Then it does compute_all_indices.

# But wait, it's safer to just inject it properly. Let's write the modified data_loader_code back first.
with open('utils/data_loader.py', 'w', encoding='utf-8') as f:
    f.write(data_loader_code)
print("Injected v3 pipeline into data_loader.py")
