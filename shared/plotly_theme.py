"""
Plotly Theme — GHN EES 2026 Brand
Đồng bộ palette với ees-tracking dashboard.
"""
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════
# COLOR PALETTE (GHN Brand)
# ══════════════════════════════════════════════════════════════
COLORS = {
    'navy': '#2B3674',
    'navy2': '#1B2559',
    'orange': '#FFB547',
    'orange_light': '#FFD18B',
    'blue': '#4318FF',
    'blue_light': '#868CFF',
    'green': '#05CD99',
    'green_light': '#43E8B5',
    'red': '#EE5D50',
    'red_light': '#FF7D73',
    'gold': '#FFB547',
    'grey': '#A3AED0',
    'muted': '#A3AED0',
    'text': '#2B3674',
    'bg': '#FFFFFF',
    'slate': '#F4F7FE',
    'line': '#E2E8F0',
}

# Palettes
PAL_DIVERGING = ['#EE5D50', '#FF7D73', '#FFB547', '#FFD18B', '#43E8B5', '#05CD99']
PAL_SEQUENTIAL = ['#F4F7FE', '#868CFF', '#4318FF', '#1B2559']
PAL_CATEGORY = ['#4318FF', '#05CD99', '#FFB547', '#EE5D50', '#2B3674', '#00B5D8', '#868CFF']
PAL_ENPS = {'Promoter': '#05CD99', 'Passive': '#FFB547', 'Detractor': '#EE5D50'}
PAL_EI = {'Xuất sắc': '#05CD99', 'Khỏe mạnh': '#43E8B5', 'Cần theo dõi': '#FFB547', 'Nghiêm trọng': '#EE5D50'}
PAL_PILLAR = ['#4318FF', '#05CD99', '#FFB547', '#EE5D50', '#2B3674']

# ══════════════════════════════════════════════════════════════
# PLOTLY TEMPLATE
# ══════════════════════════════════════════════════════════════
LAYOUT_DEFAULTS = dict(
    font=dict(family='Inter, "Segoe UI", system-ui, sans-serif', size=13, color=COLORS['text']),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=40, r=40, t=70, b=40),
    hoverlabel=dict(bgcolor='white', font_size=13, font_family='Inter', bordercolor=COLORS['line']),
    colorway=PAL_CATEGORY,
    # Giới hạn decimal toàn cục 1 chữ số
    xaxis=dict(hoverformat='.1f', separatethousands=True, showgrid=False, showline=True, linecolor=COLORS['line']),
    yaxis=dict(hoverformat='.1f', separatethousands=True, showgrid=True, gridcolor=COLORS['slate'], gridwidth=1, zeroline=False),
    separators=',.',
)


def apply_theme():
    """Apply GHN premium theme globally."""
    pio.templates['ghn_premium'] = go.layout.Template(layout=go.Layout(**LAYOUT_DEFAULTS))
    pio.templates.default = 'plotly_white+ghn_premium'


def fig_card(fig, title, subtitle=None, height=400):
    """Style a figure as a premium card with title and force 1 decimal text."""
    fig.update_layout(
        title=dict(
            text=f'<span style="font-size:16px; font-weight:700; color:{COLORS["navy"]}">{title}</span>' + 
                 (f'<br><span style="font-size:12px; font-weight:400; color:{COLORS["muted"]}">{subtitle}</span>' if subtitle else ''),
            x=0, xanchor='left', y=0.95),
        height=height,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',
    )
    # Tự động force label hiển thị 1 số thập phân cho biểu đồ bar nếu có thể
    for trace in fig.data:
        if getattr(trace, 'type', '') == 'bar':
            has_texttemplate = getattr(trace, 'texttemplate', None) is not None
            has_text = getattr(trace, 'text', None) is not None
            if not has_texttemplate and not has_text:
                trace.texttemplate = '%{value:.1f}'
    return fig


def color_by_score(value, thresholds=None):
    """Return color based on score thresholds."""
    if thresholds is None:
        thresholds = [(80, COLORS['green']), (65, COLORS['green_light']),
                      (50, COLORS['gold']), (0, COLORS['red'])]
    for threshold, color in thresholds:
        if value >= threshold:
            return color
    return COLORS['red']


def color_enps(score):
    """Color for eNPS score."""
    if score >= 30: return COLORS['green']
    if score >= 0: return COLORS['blue']
    return COLORS['red']


def make_kpi_indicator(value, title, reference=None, suffix='', number_format='.1f'):
    """Create a single KPI indicator trace."""
    return go.Indicator(
        mode='number+delta' if reference is not None else 'number',
        value=value,
        title=dict(text=title, font=dict(size=13, color=COLORS['muted'])),
        number=dict(font=dict(size=36, color=COLORS['navy']),
                    suffix=suffix, valueformat=number_format),
        delta=dict(reference=reference, relative=False,
                   increasing=dict(color=COLORS['green']),
                   decreasing=dict(color=COLORS['red'])) if reference else None,
    )


def annotate_insight(fig, text, x=0.5, y=-0.15, xref='paper', yref='paper'):
    """Add narrative insight annotation below chart."""
    fig.add_annotation(
        text=f' <i>{text}</i>',
        x=x, y=y, xref=xref, yref=yref,
        showarrow=False, font=dict(size=11, color=COLORS['navy2']),
        bgcolor='#FFF8E1', bordercolor=COLORS['gold'], borderwidth=1,
        borderpad=8, align='left',
    )
    return fig

def make_html_kpi(title, value, delta=None, color="blue", icon="", progress_val=None, sparkline_data=None):
    """
    Clean, professional KPI card — no emoji icons, minimal design.
    color: 'blue' (GHN orange accent) | 'orange' | 'green' | 'red'
    """
    color_map = {
        "blue":   ("#FF5200", "#FFF3EE"),
        "orange": ("#F59E0B", "#FFFBEB"),
        "green":  ("#10B981", "#F0FDF4"),
        "red":    ("#EF4444", "#FEF2F2"),
        "purple": ("#8B5CF6", "#F5F3FF"),
        "teal":   ("#06B6D4", "#ECFEFF"),
    }
    main_color, _bg = color_map.get(color, color_map["blue"])

    # Delta styling
    delta_color = "#94A3B8"
    delta_bg    = "#F8FAFC"
    if delta and str(delta) not in ("N/A", "0", "0%", "0.0%"):
        d_str = str(delta).replace('%', '').replace('+', '').strip()
        try:
            d_val = float(d_str)
            if d_val > 0:
                delta_color, delta_bg = "#16A34A", "#F0FDF4"
            elif d_val < 0:
                delta_color, delta_bg = "#DC2626", "#FEF2F2"
        except ValueError:
            pass

    delta_html = ""
    if delta and str(delta) != "N/A":
        delta_html = (
            f'<span style="font-size:0.71rem;font-weight:600;color:{delta_color};'
            f'background:{delta_bg};padding:2px 8px;border-radius:20px;'
            f'display:inline-block;margin-top:5px;">{delta} vs 2025</span>'
        )

    # Circular donut
    p_val = max(0.0, min(100.0, float(progress_val))) if progress_val is not None else 0.0
    donut_html = ""
    if progress_val is not None:
        donut_html = (
            f'<div style="position:relative;width:54px;height:54px;flex-shrink:0">'
            f'<svg viewBox="0 0 36 36" style="width:100%;height:100%;transform:rotate(-90deg)">'
            f'<path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"'
            f' fill="none" stroke="#F1F5F9" stroke-width="3.5"/>'
            f'<path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"'
            f' fill="none" stroke="{main_color}" stroke-width="3.5"'
            f' stroke-dasharray="{p_val:.1f},100" stroke-linecap="round"/>'
            f'</svg>'
            f'<div style="position:absolute;top:0;left:0;width:100%;height:100%;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:0.66rem;font-weight:700;color:#64748B">{int(p_val)}%</div>'
            f'</div>'
        )

    html = (
        f'<div style="background:#FFF;border:1px solid #E2E8F0;border-radius:12px;'
        f'padding:20px 22px;height:100%;box-sizing:border-box">'
        f'<div style="font-size:0.67rem;font-weight:700;letter-spacing:0.09em;'
        f'text-transform:uppercase;color:#94A3B8;margin-bottom:16px">{title}</div>'
        f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px">'
        f'<div><div style="font-size:2.1rem;font-weight:900;color:#0A1F44;'
        f'letter-spacing:-0.03em;line-height:1">{value}</div>{delta_html}</div>'
        f'{donut_html}</div></div>'
    )
    return html


def section_header(title, subtitle=None):
    """Render a clean professional section header (no emoji)."""
    accent = (
        '<span style="width:3px;height:15px;background:#FF5200;border-radius:2px;'
        'display:inline-block;flex-shrink:0"></span>'
    )
    h = (
        f'<h3 style="font-size:0.92rem;font-weight:700;color:#0A1F44;'
        f'margin:30px 0 14px;padding-bottom:10px;border-bottom:1px solid #F1F5F9;'
        f'display:flex;align-items:center;gap:8px">{accent}{title}</h3>'
    )
    if subtitle:
        h += (
            f'<p style="font-size:0.82rem;color:#64748B;'
            f'margin:-8px 0 18px;font-weight:500">{subtitle}</p>'
        )
    return h
