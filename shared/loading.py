from html import escape
from time import strftime


class TerminalLoader:
    """Lightweight Streamlit loading console."""

    def __init__(self, slot, title="Đang tải dữ liệu EES 2026", max_lines=14):
        self.slot = slot
        self.title = title
        self.max_lines = max_lines
        self.lines = []

    def add(self, message, status="run"):
        self.lines.append((strftime("%H:%M:%S"), status, message))
        self.lines = self.lines[-self.max_lines:]
        self.render()

    def done(self, message="Hoàn tất. Đang dựng dashboard..."):
        self.add(message, status="ok")

    def clear(self):
        self.slot.empty()

    def render(self):
        rows = []
        for ts, status, message in self.lines:
            prefix = "OK" if status == "ok" else "RUN"
            color = "#10B981" if status == "ok" else "#FF5200"
            rows.append(
                f'<div class="tl-row">'
                f'<span class="tl-time">{escape(ts)}</span>'
                f'<span class="tl-tag" style="color:{color};border-color:{color}">{prefix}</span>'
                f'<span class="tl-msg">{escape(str(message))}</span>'
                f'</div>'
            )

        self.slot.markdown(
            f"""
<style>
.tl-box {{
    position: fixed;
    right: 18px;
    bottom: max(18px, env(safe-area-inset-bottom));
    z-index: 99990;
    width: min(520px, calc(100vw - 36px));
    margin: 0;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    background: #0B1220;
    color: #D6E4FF;
    box-shadow: 0 16px 40px rgba(15,23,42,.18);
    overflow: hidden;
}}
.tl-head {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(148,163,184,.18);
    color: #F8FAFC;
    font: 700 12px/1.4 Consolas, Monaco, monospace;
}}
.tl-dot {{ width: 7px; height: 7px; border-radius: 999px; background: #FF5200; }}
.tl-body {{ padding: 11px 14px 13px; font: 12px/1.65 Consolas, Monaco, monospace; }}
.tl-row {{ display: flex; gap: 9px; align-items: baseline; white-space: nowrap; overflow: hidden; }}
.tl-time {{ color: #64748B; flex: 0 0 auto; }}
.tl-tag {{ flex: 0 0 auto; min-width: 34px; text-align: center; border: 1px solid; border-radius: 4px; font-size: 10px; font-weight: 700; line-height: 1.35; }}
.tl-msg {{ color: #D6E4FF; overflow: hidden; text-overflow: ellipsis; }}
@media (max-width: 768px) {{
    .tl-box {{
        left: 12px;
        right: 12px;
        bottom: max(12px, env(safe-area-inset-bottom));
        width: auto;
        max-height: 42vh;
    }}
    .tl-body {{
        max-height: 32vh;
        overflow-y: auto;
    }}
    .tl-row {{
        white-space: normal;
        align-items: flex-start;
    }}
}}
</style>
<div class="tl-box">
    <div class="tl-head"><span class="tl-dot"></span><span>{escape(self.title)}</span></div>
    <div class="tl-body">{''.join(rows)}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
