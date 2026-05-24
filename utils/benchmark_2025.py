"""
Benchmark Data from EES 2025 (Historical Snapshot).
This data was extracted from the official EES 2025 Excel reports.
Since 2025 data is historical and immutable, it is stored statically
here to ensure fast load times and prevent parsing errors.

Scaling note: 2025 scores were out of 10. They are scaled to 100% here 
(score * 10) to match the 2026 scoring system.
"""

BENCHMARK_2025 = {
    'GHN': {
        'n_survey_sent': 17587,
        'n_response': 13348,
        'response_rate': 75.9,
        'ei_mean': 80.2,       # Original: 8.02/10
        'enps_score': 33.6,    # Original: 33.6%
        'pillars': {
            'Công việc & Môi trường': 77.7,    # Original: 7.77/10
            'Quản trị & Lãnh đạo': 86.4,       # Original: 8.64/10
            'Lương thưởng & Phúc lợi': 79.0,   # Original: 7.90/10
            'Quy trình & Công cụ': 79.0,       # Original: 7.90/10
            'Truyền thông & Khác': 84.3        # Original: 8.43/10
        }
    },
    # Note: If Group 1A/1B historical splits are needed, they can be added here.
    '1A': {
        'ei_mean': 78.5,       # KTT Nhóm 1 Original: 7.85/10
        'enps_score': 26.5     # KTT Nhóm 1 Original: 26.5%
    },
    '1B': {
        'ei_mean': 87.7,       # Freight Nhóm 1 Original: 8.77/10
        'enps_score': 72.8     # Freight Nhóm 1 Original: 72.8%
    }
}

def get_company_benchmark_2025():
    """Return the overall GHN benchmark for 2025."""
    return BENCHMARK_2025['GHN']

def get_group_benchmark_2025(group_id):
    """Return the group-specific benchmark for 2025 if available."""
    return BENCHMARK_2025.get(group_id)
