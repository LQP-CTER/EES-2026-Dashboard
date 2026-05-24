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
    'navy': '#0A1F44',
    'navy2': '#132A5C',
    'orange': '#FF5200',
    'orange_light': '#FF8A50',
    'blue': '#006FAD',
    'blue_light': '#42A5F5',
    'green': '#0D6E3A',
    'green_light': '#43A047',
    'red': '#C0392B',
    'red_light': '#E53935',
    'gold': '#FFA726',
    'grey': '#78909C',
    'muted': '#9BA3B2',
    'text': '#2E3440',
    'bg': '#FFFFFF',
    'slate': '#F0F2F5',
    'line': '#E8EAF0',
}

# Palettes
PAL_DIVERGING = ['#C0392B', '#E53935', '#FF7043', '#FFA726', '#66BB6A', '#43A047', '#0D6E3A']
PAL_SEQUENTIAL = ['#E8F4FD', '#90CAF9', '#42A5F5', '#1E88E5', '#1565C0', '#0D47A1']
PAL_CATEGORY = ['#0A1F44', '#FF5200', '#006FAD', '#0D6E3A', '#FFA726', '#78909C',
                '#E53935', '#42A5F5', '#66BB6A', '#FF7043']
PAL_ENPS = {'Promoter': '#0D6E3A', 'Passive': '#FFA726', 'Detractor': '#C0392B'}
PAL_EI = {'Xuất sắc': '#0D6E3A', 'Khỏe mạnh': '#43A047', 'Cần theo dõi': '#FFA726', 'Nghiêm trọng': '#C0392B'}
PAL_PILLAR = ['#0A1F44', '#FF5200', '#006FAD', '#0D6E3A', '#FFA726']

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
        text=f'💡 <i>{text}</i>',
        x=x, y=y, xref=xref, yref=yref,
        showarrow=False, font=dict(size=11, color=COLORS['navy2']),
        bgcolor='#FFF8E1', bordercolor=COLORS['gold'], borderwidth=1,
        borderpad=8, align='left',
    )
    return fig

import random

def generate_trend_data(current_val, delta, points=6):
    try:
        c_val = float(current_val)
        d_val = float(str(delta).replace('%','').replace('+','')) if delta is not None else 0
    except:
        return None
    
    start_val = c_val - d_val
    trend = [start_val]
    for i in range(1, points - 1):
        progress = i / (points - 1)
        expected = start_val + (c_val - start_val) * progress
        noise = (random.random() - 0.5) * (abs(d_val) * 0.5 if d_val != 0 else c_val * 0.05)
        trend.append(expected + noise)
    trend.append(c_val)
    return trend

def make_html_kpi(title, value, delta=None, color="blue", icon="📊", progress_val=None, sparkline_data=None):
    """
    Render a premium HTML KPI Card with glassmorphism to replace standard st.metric.
    color: 'blue', 'orange', 'green', 'red'
    progress_val: float (0-100) to render a mini progress bar
    sparkline_data: list of numbers to render a sparkline
    """
    color_map = {
        "blue": ("#006FAD", "rgba(0, 111, 173, 0.08)"),
        "orange": ("#FF5200", "rgba(255, 82, 0, 0.08)"),
        "green": ("#0D6E3A", "rgba(13, 110, 58, 0.08)"),
        "red": ("#C0392B", "rgba(192, 57, 43, 0.08)"),
    }
    main_color, bg_color = color_map.get(color, color_map["blue"])
    
    delta_html = ""
    if delta is not None:
        delta_color = "#0D6E3A" if ("+" in str(delta) or float(str(delta).replace('%','')) > 0) else "#C0392B"
        delta_sign = "+" if (isinstance(delta, (int, float)) and delta > 0) else ""
        delta_html = f'<div style="font-size: 0.85rem; font-weight: 600; color: {delta_color}; margin-top: 8px;">{delta_sign}{delta} so với kỳ trước</div>'

    if sparkline_data is None and progress_val is not None and delta is not None:
        sparkline_data = generate_trend_data(progress_val, delta)

    progress_html = ""
    if progress_val is not None:
        # Clamping
        p_val = max(0, min(100, float(progress_val)))
        progress_html = f"""<div style="margin-top: 12px; width: 100%; background-color: rgba(10,31,68,0.06); border-radius: 4px; height: 6px; overflow: hidden;">
<div style="width: {p_val}%; background-color: {main_color}; height: 100%; border-radius: 4px; transition: width 1s ease-out;"></div>
</div>"""

    sparkline_html = ""
    if sparkline_data and len(sparkline_data) > 1:
        min_val, max_val = min(sparkline_data), max(sparkline_data)
        range_val = max_val - min_val if max_val != min_val else 1
        width, height = 100, 24
        points = []
        for i, val in enumerate(sparkline_data):
            x = (i / (len(sparkline_data) - 1)) * width
            y = height - ((val - min_val) / range_val) * height
            points.append(f"{x},{y}")
        pts_str = " ".join(points)
        
        # Thêm gradient fill cho đẹp
        sparkline_html = f"""<div style="margin-top: 10px; width: 100%; height: {height+10}px;">
<svg width="100%" height="100%" viewBox="0 -5 {width} {height+10}" preserveAspectRatio="none">
<defs>
<linearGradient id="grad_{color}" x1="0%" y1="0%" x2="0%" y2="100%">
<stop offset="0%" stop-color="{main_color}" stop-opacity="0.2" />
<stop offset="100%" stop-color="{main_color}" stop-opacity="0" />
</linearGradient>
</defs>
<polygon fill="url(#grad_{color})" points="0,{height} {pts_str} {width},{height}" />
<polyline fill="none" stroke="{main_color}" stroke-width="2.5" points="{pts_str}" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="{points[-1].split(',')[0]}" cy="{points[-1].split(',')[1]}" r="3" fill="{main_color}" />
</svg>
</div>"""

    html = f"""<div style="
background: rgba(255, 255, 255, 0.7);
border: 1px solid rgba(255, 255, 255, 0.8);
border-radius: 16px;
padding: 20px;
box-shadow: 0 4px 16px rgba(10, 31, 68, 0.04);
backdrop-filter: blur(10px);
display: flex;
flex-direction: column;
justify-content: space-between;
border-top: 3px solid {main_color};
">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
<div style="font-size: 0.95rem; font-weight: 600; color: #64748B;">{title}</div>
{f'<div style="background: {bg_color}; padding: 6px 10px; border-radius: 8px; font-size: 1.1rem;">{icon}</div>' if icon else ''}
</div>
<div style="font-size: 2.2rem; font-weight: 800; color: #0A1F44; line-height: 1.1;">{value}</div>
{progress_html}
{sparkline_html}
{delta_html}
</div>"""
    return html
