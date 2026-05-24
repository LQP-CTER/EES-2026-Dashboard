"""
Visualization utilities – EES 2026
Hàm vẽ biểu đồ chuẩn dùng chung cho tất cả nhóm.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import numpy as np

# ============================================================
# COLOR PALETTE
# ============================================================

COLORS = {
    'primary': '#E53935',     # GHN Red
    'secondary': '#FF7043',   # GHN Orange
    'accent': '#FFA726',      # Gold
    'positive': '#43A047',    # Green
    'negative': '#E53935',    # Red
    'neutral': '#78909C',     # Gray
    'bg': '#FAFAFA',
    'text': '#212121',
}

PALETTE_5 = ['#E53935', '#FF7043', '#FFA726', '#66BB6A', '#42A5F5']
PALETTE_14 = sns.color_palette('husl', 14)
PALETTE_SENTIMENT = {'tích_cực': '#43A047', 'tiêu_cực': '#E53935', 'trung_lập': '#78909C'}

# ============================================================
# SETUP
# ============================================================

def setup_style():
    """Thiết lập style biểu đồ chuẩn."""
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': '#FAFAFA',
        'axes.grid': True,
        'grid.alpha': 0.3,
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'figure.dpi': 150,
    })
    sns.set_style('whitegrid')

setup_style()

# ============================================================
# BIỂU ĐỒ
# ============================================================

def plot_bar_horizontal(data, title, xlabel, save_path=None, figsize=(12, 6), color=None):
    """Biểu đồ cột ngang."""
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(range(len(data)), list(data.values()),
                   color=color or PALETTE_5[0], alpha=0.85, edgecolor='white')
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(list(data.keys()))
    ax.set_xlabel(xlabel)
    ax.set_title(title, pad=15)
    for bar, val in zip(bars, data.values()):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}' if isinstance(val, float) else str(val),
                va='center', fontsize=9)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_distribution(values, title, xlabel, save_path=None, bins=None):
    """Biểu đồ phân bổ (histogram + KDE)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    if bins is None:
        bins = 'auto'
    ax.hist(values, bins=bins, color=PALETTE_5[0], alpha=0.7, edgecolor='white', density=True)
    try:
        sns.kdeplot(values, ax=ax, color=PALETTE_5[1], linewidth=2)
    except Exception:
        pass
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Mật độ')
    ax.set_title(title, pad=15)
    # Stats annotation
    mean_val = np.mean(values)
    median_val = np.median(values)
    ax.axvline(mean_val, color='red', linestyle='--', alpha=0.7, label=f'TB = {mean_val:.2f}')
    ax.axvline(median_val, color='blue', linestyle='--', alpha=0.7, label=f'Trung vị = {median_val:.2f}')
    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_heatmap(data, title, save_path=None, figsize=(14, 8), fmt='.1f', cmap='RdYlGn'):
    """Biểu đồ nhiệt."""
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(data, annot=True, fmt=fmt, cmap=cmap, ax=ax,
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'Giá trị'})
    ax.set_title(title, pad=15)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_radar(categories, values_dict, title, save_path=None):
    """Biểu đồ radar cho so sánh đa chiều."""
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for i, (label, values) in enumerate(values_dict.items()):
        vals = list(values) + [values[0]]
        ax.plot(angles, vals, 'o-', linewidth=2, label=label, color=PALETTE_5[i % len(PALETTE_5)])
        ax.fill(angles, vals, alpha=0.1, color=PALETTE_5[i % len(PALETTE_5)])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_title(title, pad=20, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_enps_gauge(enps_score, title='eNPS', save_path=None):
    """Biểu đồ gauge cho eNPS."""
    fig, ax = plt.subplots(figsize=(6, 3))
    # Simple bar visualization
    color = COLORS['positive'] if enps_score >= 30 else (
        COLORS['accent'] if enps_score >= 0 else COLORS['negative'])
    ax.barh(0, enps_score, color=color, height=0.5, alpha=0.85)
    ax.set_xlim(-100, 100)
    ax.set_yticks([])
    ax.axvline(0, color='black', linewidth=1)
    ax.set_title(f'{title}: {enps_score:+.0f}', fontsize=14, fontweight='bold')
    ax.set_xlabel('eNPS Score')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig


def plot_pillar_comparison(pillar_scores, title, save_path=None):
    """Biểu đồ so sánh 5 trụ cột."""
    labels = list(pillar_scores.keys())
    values = list(pillar_scores.values())
    colors = [COLORS['positive'] if v >= 65 else (
        COLORS['accent'] if v >= 50 else COLORS['negative']) for v in values]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=colors, alpha=0.85, edgecolor='white', width=0.6)
    ax.set_ylabel('Điểm (%)')
    ax.set_title(title, pad=15)
    ax.set_ylim(0, 100)
    ax.axhline(y=65, color='green', linestyle='--', alpha=0.5, label='Khỏe mạnh (65)')
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Cần theo dõi (50)')
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.1f}%', ha='center', fontweight='bold')
    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig
