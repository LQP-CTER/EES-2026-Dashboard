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
    Render a premium HTML KPI Card with Circular Donut Progress (matches reference image).
    color: 'blue', 'orange', 'green', 'red'
    """
    color_map = {
        "blue": ("#4318FF", "rgba(67, 24, 255, 0.05)"),
        "orange": ("#FFB547", "rgba(255, 181, 71, 0.05)"),
        "green": ("#05CD99", "rgba(5, 205, 153, 0.05)"),
        "red": ("#EE5D50", "rgba(238, 93, 80, 0.05)"),
    }
    main_color, bg_color = color_map.get(color, color_map["blue"])
    
    delta_color = "#05CD99" if (delta and ("+" in str(delta) or float(str(delta).replace('%','')) > 0)) else "#EE5D50"
    delta_sign = "+" if (isinstance(delta, (int, float)) and delta > 0) else ""
    delta_str = f"{delta_sign}{delta}" if delta is not None else ""

    p_val = max(0, min(100, float(progress_val))) if progress_val is not None else 0
    dash_val = (p_val / 100) * 100

    donut_html = ""
    if progress_val is not None:
        donut_html = f"""
        <div style="position: relative; width: 64px; height: 64px;">
            <svg viewBox="0 0 36 36" style="width: 100%; height: 100%; transform: rotate(-90deg);">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#F4F7FE" stroke-width="4" />
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="{main_color}" stroke-width="4" stroke-dasharray="{dash_val}, 100" stroke-linecap="round" />
            </svg>
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 700; color: #2B3674;">
                {int(p_val)}%
            </div>
        </div>
        """

    html = f"""
    <div style="background: #FFFFFF; border-radius: 20px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: space-between; height: 100%; min-height: 150px;">
        <!-- Top row: Title and pills -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <span style="color: #2B3674; font-weight: 700; font-size: 1.05rem;">{title}</span>
            <div style="display: flex; gap: 4px;">
                <span style="background: {bg_color}; color: {main_color}; font-size: 0.7rem; padding: 4px 8px; border-radius: 6px; font-weight: 600;">Metric</span>
                <span style="background: {main_color}; color: white; font-size: 0.7rem; padding: 4px 8px; border-radius: 6px; font-weight: 600;">{icon}</span>
            </div>
        </div>
        
        <!-- Middle row: Circular Progress and Value -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
            {donut_html}
            
            <!-- Right side: Value and Button -->
            <div style="display: flex; flex-direction: column; align-items: flex-end;">
                <span style="font-size: 1.8rem; font-weight: 800; color: #2B3674; line-height: 1;">{value}</span>
                <div style="margin-top: 8px; display: flex; align-items: center; gap: 8px;">
                    <span style="color: {delta_color}; font-size: 0.85rem; font-weight: 600;">{delta_str}</span>
                    <div style="width: 24px; height: 24px; background: {main_color}; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return html
