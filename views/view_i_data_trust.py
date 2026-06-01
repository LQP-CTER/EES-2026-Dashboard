"""
View: Thẩm định & Độ tin cậy dữ liệu — EES 2026
Trình bày cách xử lý và thẩm định dữ liệu của từng nhóm để tăng độ tin cậy.
"""

import streamlit as st
import pandas as pd

# Base64 AI logo (same as ai_generator.py)
_AI_LOGO_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADT0lEQVR4nO1WTWwVVRT+zp15f33PlhojIivKAl0RiKgNCalhUV2ZEBODC+PPorpxQQIoG10TMLjDjQloSKORjUlTF6AYFdPUrjRFTU0auwBCAi/w/mbmns+cmVc0ffPo66I7Tu7M3HvPPd+558w5514hic0kt6noeKhgAAr7cnp/vnQfgOiNDMlYPdObHUVh/jTJZh3UdMu0N4FKVcKCMZMYrUZqTMoCIU6GRnKN6FFAQoTNuh7dJ3frCARJIkHAexGePSjHv7Ylpw/L3CWtlUQTBCE9WRsJTs1JdTQTH8ACQG4u40bsyuAQ4CHFgFcu8u1/bMvfX0Q5CG7VGUKaYBvceqcvztp/kFlw+7p+/Jrs3Me7N93laXjP0z9i7huGBfNHEuG5l+XIfoROXzgsw49zad4d+UJGt/VaYN7OoXZDo5Z2Wsn7BzgBf/adbDpemI1/nc36/uy7xjp+QDtNjdpsN3KR+iggqT45Ns4J6KGCX7lG9UziLiuJqd6vXNNDRU4gOfY8ve8Hk1eLfGKvKxdk4Spqjjt2u+27zPVBaHFFtQ7Ebd/FHbtRc7Lwi/5w4b7gGspTIOnk5XMoCCLF2B4bqu+yMm42HNvDSFEQfnfuP8F1FJBwjlELK4tSJBQYfTKN914iHt1mqVKkrCyaiHO9+d+nXEctiVtZIqF5Z7VCrLUUjXr6FUQta3nUoyCDKtdQGaYHSsD8DNUbirmF1tIhVTk/I2VIQlaGTeS++AMtMCAJi9y5Fx3hUAlLf/HzE3CBNQOQrK/nP5ClP1kpoSMytlfCYroDGfREk8kpCKEqtQDTJ/2ZN3T5NwvQJNbl3/XMmzJ9EtUAqlZaJ6f64uRXU1U450+9KjNf4rESkgT3PKoOT4wZ9/rf0lA8EjAI5VZHX3olOPpVJjKwAptM8/nDF2X+Z2wJEBaQRBKpMYvOHOJj3PZ8Zlw+mpVKzZyTV037nwdZUWo39NP38O1nEgPF1dqYQCKwAEy+JVOfSLmWU4LWV7CqA4Au/oRL5/nHVanfsNXDW/HUuBx83T29///LNq4gE05Tr5sTWeBXR7p4qgbdH33gI1O9qbEStEo+MVwL3HVog2cy08UP3PLAt4r8/cjG1j+82Q1Am367/hffvQmZc1fQbgAAAABJRU5ErkJggg=="


def _sec(title: str, subtitle: str = "") -> str:
    accent = '<span style="width:3px;height:15px;background:#FF5200;border-radius:2px;display:inline-block;flex-shrink:0"></span>'
    html = (
        f'<h3 style="font-size:0.92rem;font-weight:700;color:#0A1F44;'
        f'margin:28px 0 12px;padding-bottom:10px;border-bottom:1px solid #F1F5F9;'
        f'display:flex;align-items:center;gap:8px">{accent}{title}</h3>'
    )
    if subtitle:
        html += f'<p style="font-size:0.82rem;color:#64748B;margin:-6px 0 16px;font-weight:500">{subtitle}</p>'
    return html


def _callout(title: str, body: str, color: str = "#FF5200", bg: str = "#FFF8F5") -> str:
    return f"""
    <div style="background:{bg};border:1px solid {color}33;border-left:4px solid {color};
                border-radius:10px;padding:18px 22px;margin:16px 0;">
        <div style="font-size:0.88rem;font-weight:700;color:#0A1F44;margin-bottom:8px;
                    display:flex;align-items:center;gap:8px;">
            <img src="{_AI_LOGO_B64}" style="width:16px;height:16px"> {title}
        </div>
        <div style="font-size:0.84rem;color:#475569;line-height:1.7">{body}</div>
    </div>"""


def _info_box(body: str) -> str:
    return f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
                padding:16px 20px;margin:12px 0;font-size:0.85rem;color:#475569;line-height:1.7">
        {body}
    </div>"""


def render():
    # ── Page header ────────────────────────────────────────────────
    st.markdown("""
    <div class="pg-header">
        <div>
            <p class="pg-eyebrow">EES 2026 · Phương pháp luận</p>
            <h1 class="pg-title">Thẩm định &amp; Độ tin cậy dữ liệu</h1>
            <p class="pg-subtitle">Cách xử lý, làm sạch và đánh giá chất lượng dữ liệu trước khi phân tích</p>
        </div>
        <span class="pg-badge"><span class="pg-badge-dot"></span>Phần 1 · Data Quality</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Intro callout ───────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #0A1F44;
                border-radius:10px;padding:20px 24px;margin-bottom:28px;">
        <p style="font-size:0.88rem;color:#475569;line-height:1.75;margin:0">
            Trước khi diễn giải bất kỳ con số nào, dữ liệu được thẩm định độ tin cậy.
            Cách tiếp cận: <strong>không xóa phản hồi theo một đầu hiệu đơn lẻ</strong>, mà gán nhiều
            cơ chế chất lượng rồi gán <em>trọng số tin cậy liên tục</em> cho từng phản hồi.
            Phản hồi bị loại bỏ hoàn toàn chỉ khi đồng thời trả lời thẳng hàng một màu
            <strong>VÀ</strong> không để lại ý kiến mở nào — đúng kiểu phản hồi không có thông tin.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs for each section ───────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "1.1 · Tỷ lệ tham gia & đại diện",
        "1.2 · Phân hạng độ tin cậy & Base",
        "1.3 · Thang đo & Cronbach Alpha",
        "1.4 · Lưu ý sử dụng kết quả",
    ])

    # ═══════════════════════════════════════════════════
    # TAB 1: TỶ LỆ THAM GIA & ĐẠI DIỆN
    # ═══════════════════════════════════════════════════
    with tab1:
        st.markdown(_sec("Tỷ lệ tham gia & Tính đại diện"), unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75">
            Tỷ lệ tham gia toàn công ty đạt <strong>94.2%</strong> — rất cao so với chuẩn ngành
            (logistics thường 60–75%). Nhóm Shipper (1A) đạt <strong>93.4%</strong> với hơn 12.900
            phản hồi, tức gần như toàn bộ lực lượng. Điều này bác bỏ giả định rằng 1A chỉ là
            mẫu nhỏ: thực tế đây là một cuộc tổng điều tra (census), nên biên sai số gần như
            bằng 0 và kết quả 1A có thể coi là tiếng nói toàn thể, không phải ước lượng.
        </p>
        """, unsafe_allow_html=True)

        # KPI cards
        cols = st.columns(4)
        kpi_data = [
            ("Tổng GHN", "94.2%", "Tỷ lệ tham gia", "#FF5200", "#FFF3EE"),
            ("1A · Shipper", "93.4%", "12,955 phản hồi", "#10B981", "#F0FDF4"),
            ("1B · Tài xế", "~99%", "801 phản hồi", "#3B82F6", "#EFF6FF"),
            ("2A · NV Kho", "~95%", "4,892 phản hồi", "#8B5CF6", "#F5F3FF"),
        ]
        for col, (label, val, sub, color, bg) in zip(cols, kpi_data):
            with col:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {color}33;border-radius:12px;
                            padding:18px 20px;text-align:center;">
                    <div style="font-size:0.68rem;font-weight:700;color:{color};text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:8px">{label}</div>
                    <div style="font-size:2rem;font-weight:900;color:#0A1F44;line-height:1;
                                letter-spacing:-0.03em">{val}</div>
                    <div style="font-size:0.75rem;color:#64748B;margin-top:6px">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75">
            <strong>Hai nhóm nhỏ cần thận trọng khi đọc lát cắt sâu:</strong>
            Manager HO (3B, n=109, biên sai số ±3.4%) và Quản lý tuyến đầu (2B, n=425).
            Với các nhóm này, chênh lệch nhỏ giữa các đơn vị con có thể chỉ là nhiễu thống kê —
            không nên đọc như sự khác biệt cấu trúc mà không kiểm tra thêm.
        </p>
        """, unsafe_allow_html=True)

        st.markdown(_callout(
            "Ý nghĩa thực tiễn",
            "Với 1A, tỷ lệ trả lời thẳng hàng cao (54%) là <strong>đặc trưng tâm lý lực lượng lao động trực tiếp</strong> "
            "(trả lời nhanh, đồng thuận), không phải dữ liệu rác — nên được giảm trọng số chứ không loại bỏ. "
            "Kết quả vẫn đại diện cho toàn thể nhóm.",
            color="#10B981", bg="#F0FDF4"
        ), unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # TAB 2: PHÂN HẠNG ĐỘ TIN CẬY & BASE PHÂN TÍCH
    # ═══════════════════════════════════════════════════
    with tab2:
        st.markdown(_sec("Phân hạng độ tin cậy & Base phân tích"), unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75;margin-bottom:12px">
            Thay vì áp dụng cách làm truyền thống là xóa bỏ hàng loạt các phản hồi nghi ngờ, hệ thống áp dụng thuật toán <strong>Trọng số tin cậy (Reliability Weight)</strong> từ 0.0 đến 1.0 cho mỗi phản hồi dựa trên 3 nguyên tắc xử lý:
        </p>
        <ul style="font-size:0.85rem;color:#475569;line-height:1.7;margin-bottom:20px;padding-left:20px">
            <li><strong>Phát hiện Straight-lining (Đánh đồng màu):</strong> Tính toán độ biến thiên (variance) của các câu Likert. Nếu người tham gia đánh cùng 1 mức điểm cho 100% câu hỏi (variance cực thấp), hệ thống sẽ đánh cờ cảnh báo rác.</li>
            <li><strong>Kiểm tra Mâu thuẫn (Inconsistency):</strong> Đối chiếu điểm eNPS (Q33) với trung bình các câu Likert. Nếu có mâu thuẫn lớn (ví dụ: khuyên người thân làm việc ở mức 10/10 nhưng Likert lại toàn đánh 1 sao), điểm tin cậy sẽ bị trừ.</li>
            <li><strong>Cứu xét bằng Câu hỏi mở (Open-ended):</strong> Nếu người tham gia có để lại ý kiến đóng góp thực tế ở câu hỏi mở, hệ thống sẽ tự động cộng điểm tin cậy vì đây là bằng chứng cốt lõi của người làm khảo sát có đọc câu hỏi.</li>
            <li><strong>Quyết định:</strong> Chỉ những phản hồi vi phạm TẤT CẢ các lỗi trên (đánh đồng màu + mâu thuẫn + bỏ trống câu hỏi mở) mới bị loại bỏ hoàn toàn (DROP). Các phản hồi vi phạm nhẹ sẽ bị giảm trọng số đóng góp (ví dụ: x0.5) thay vì xóa bỏ.</li>
        </ul>
        """, unsafe_allow_html=True)

        # Bảng phân hạng
        table_data = {
            "Nhóm": ["1A - Giao hàng", "1B - Tài xế", "2A - NV Kho",
                     "2B - QL Tuyến", "3A - Văn phòng", "3B - QL Cấp cao"],
            "Mẫu thô": [12955, 801, 4892, 425, 917, 109],
            "Loại bỏ (DROP)": [175, 2, 31, 0, 0, 0],
            "Base phân tích": [12780, 799, 4861, 425, 917, 109],
            '"n hiệu dụng"': [9377, 630, 3827, 358, 798, 102],
            "Tỷ lệ giữ": ["72,4%", "78,7%", "78,2%", "84,2%", "87,0%", "93,3%"]
        }
        df_table = pd.DataFrame(table_data)

        # Render table with custom styling
        header_cols = st.columns([2, 1.2, 1.5, 1.5, 1.5, 1.2])
        headers = list(table_data.keys())
        header_styles = [
            "background:#0A1F44;color:white;padding:10px 12px;border-radius:8px 0 0 0;font-size:0.78rem;font-weight:700",
            "background:#0A1F44;color:white;padding:10px 12px;font-size:0.78rem;font-weight:700;text-align:right",
            "background:#FEF2F2;color:#DC2626;padding:10px 12px;font-size:0.78rem;font-weight:700;text-align:right",
            "background:#EFF6FF;color:#1D4ED8;padding:10px 12px;font-size:0.78rem;font-weight:700;text-align:right",
            "background:#F5F3FF;color:#7C3AED;padding:10px 12px;font-size:0.78rem;font-weight:700;text-align:right",
            "background:#F0FDF4;color:#15803D;padding:10px 12px;border-radius:0 8px 0 0;font-size:0.78rem;font-weight:700;text-align:right",
        ]
        for col, h, style in zip(header_cols, headers, header_styles):
            with col:
                st.markdown(f'<div style="{style}">{h}</div>', unsafe_allow_html=True)

        row_colors = ["#FFFFFF", "#F8FAFC"]
        for i, row in df_table.iterrows():
            row_cols = st.columns([2, 1.2, 1.5, 1.5, 1.5, 1.2])
            bg = row_colors[i % 2]
            cell_style = f"background:{bg};padding:9px 12px;font-size:0.84rem;border-bottom:1px solid #F1F5F9"
            num_style  = f"background:{bg};padding:9px 12px;font-size:0.84rem;border-bottom:1px solid #F1F5F9;text-align:right"
            with row_cols[0]:
                st.markdown(f'<div style="{cell_style};font-weight:600;color:#0A1F44">{row["Nhóm"]}</div>', unsafe_allow_html=True)
            with row_cols[1]:
                st.markdown(f'<div style="{num_style};color:#0A1F44">{row["Mẫu thô"]:,}</div>', unsafe_allow_html=True)
            with row_cols[2]:
                st.markdown(f'<div style="{num_style};color:#DC2626;font-weight:600">{row["Loại bỏ (DROP)"]:,}</div>', unsafe_allow_html=True)
            with row_cols[3]:
                st.markdown(f'<div style="{num_style};color:#1D4ED8;font-weight:600">{row["Base phân tích"]:,}</div>', unsafe_allow_html=True)
            with row_cols[4]:
                st.markdown(f'<div style="{num_style};color:#7C3AED;font-weight:700">{row[chr(34)+"n hiệu dụng"+chr(34)]:,}</div>', unsafe_allow_html=True)
            with row_cols[5]:
                st.markdown(f'<div style="{num_style};color:#15803D;font-weight:600">{row["Tỷ lệ giữ"]}</div>', unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.78rem;color:#94A3B8;margin-top:12px;line-height:1.6;font-style:italic">
            * Cột <em>"n hiệu dụng"</em> = tổng trọng số tin cậy — phản ánh lượng thông tin thực
            sự được dùng để phân tích, không phải số đầu đếm thô. Phản hồi <em>giảm trọng số</em>
            (54%) là đặc trưng tâm lý lực lượng lao động trực tiếp (trả lời nhanh, đồng thuận),
            không phải dữ liệu rác — nên được giảm trọng số chứ không loại bỏ.
        </p>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Two validation points callout
        st.markdown(f"""
        <div style="background:#FFFBEB;border:1px solid #FDE68A;border-left:4px solid #F59E0B;
                    border-radius:10px;padding:20px 24px;margin-top:12px">
            <div style="font-size:0.9rem;font-weight:700;color:#0A1F44;margin-bottom:14px;
                        display:flex;align-items:center;gap:8px">
                <img src="{_AI_LOGO_B64}" style="width:16px;height:16px">
                Hai điểm cần xác nhận trước khi trình chính thức
            </div>
            <div style="font-size:0.85rem;color:#475569;line-height:1.75">
                <strong>(1)</strong> File nhóm 2B chứa một bảng "test" 223 phản hồi không trùng
                điểm với 425 phản hồi chính; nếu gộp sẽ vượt quá tỷ lệ tham gia nhân sự thực
                của nhóm — cần xác minh nguồn gốc.<br><br>
                <strong>(2)</strong> So sánh với baseline 2025 (Engagement 8.02/10; eNPS +33.61%)
                cần thận trọng: thang đo đổi từ 1–10 sang 1–5 và cơ cấu nhóm khác nhau. Con số
                2026 không nên đọc là "sụt giảm" mà là một điểm khởi đầu mới trên thước đo mới.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # TAB 3: THANG ĐO & CRONBACH ALPHA
    # ═══════════════════════════════════════════════════
    with tab3:
        st.markdown(_sec("Độ tin cậy thang đo & Cảnh báo"), unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.88rem;color:#475569;line-height:1.75">
            Hệ số Cronbach Alpha của bộ 22 câu Likert đạt <strong>0.94–0.99</strong> ở cả 6 nhóm —
            thang đo nhất quán nội tại ở mức rất cao. Tuy nhiên hệ số quá cao (&gt;0.95) kèm tỷ
            lệ trả lời đồng nhất lớn cũng là tín hiệu của một số câu hỏi trùng lặp và/hoặc xu
            hướng trả lời đồng thuận — do đó báo cáo này luôn đọc kèm <em>phân phối điểm</em>
            và <em>phản hồi mở</em>, không chỉ dựa vào điểm trung bình.
        </p>
        """, unsafe_allow_html=True)

        # Alpha table
        alpha_data = {
            "Nhóm": ["1A - Shipper", "1B - Tài xế", "2A - NV Kho",
                     "2B - QL tuyến đầu", "3A - NV Văn phòng", "3B - Manager HO"],
            "Cronbach α": [0.97, 0.96, 0.98, 0.95, 0.94, 0.99],
            "Số câu Likert": [22, 22, 22, 22, 22, 22],
            "Đánh giá": ["Rất cao", "Rất cao", "Rất cao", "Cao", "Cao", "Cực cao — theo dõi"],
        }
        alpha_df = pd.DataFrame(alpha_data)

        eval_color = {
            "Rất cao": ("#15803D", "#F0FDF4"),
            "Cao": ("#1D4ED8", "#EFF6FF"),
            "Cực cao — theo dõi": ("#D97706", "#FFFBEB"),
        }

        header_cols2 = st.columns([2.5, 1.2, 1.5, 2])
        for col, h, bg in zip(
            header_cols2,
            ["Nhóm", "Cronbach α", "Số câu Likert", "Đánh giá"],
            ["#0A1F44", "#0A1F44", "#0A1F44", "#0A1F44"]
        ):
            with col:
                st.markdown(
                    f'<div style="background:{bg};color:white;padding:10px 14px;'
                    f'border-radius:8px 8px 0 0 ;font-size:0.78rem;font-weight:700">{h}</div>',
                    unsafe_allow_html=True
                )

        for i, row in alpha_df.iterrows():
            bg = "#FFFFFF" if i % 2 == 0 else "#F8FAFC"
            ev_color, ev_bg = eval_color.get(row["Đánh giá"], ("#475569", "#F8FAFC"))
            row_cols2 = st.columns([2.5, 1.2, 1.5, 2])
            cell = f"background:{bg};padding:9px 14px;font-size:0.84rem;border-bottom:1px solid #F1F5F9"
            with row_cols2[0]:
                st.markdown(f'<div style="{cell};font-weight:600;color:#0A1F44">{row["Nhóm"]}</div>', unsafe_allow_html=True)
            with row_cols2[1]:
                st.markdown(f'<div style="{cell};text-align:center;font-weight:700;color:#0A1F44">{row["Cronbach α"]:.2f}</div>', unsafe_allow_html=True)
            with row_cols2[2]:
                st.markdown(f'<div style="{cell};text-align:center;color:#475569">{row["Số câu Likert"]}</div>', unsafe_allow_html=True)
            with row_cols2[3]:
                st.markdown(
                    f'<div style="{cell}"><span style="background:{ev_bg};color:{ev_color};'
                    f'padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:700">'
                    f'{row["Đánh giá"]}</span></div>',
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(_callout(
            "Hệ số quá cao cần đọc kèm phân phối",
            "Cronbach α > 0.95 ở nhóm kho và shipper có thể phản ánh hiệu ứng halo "
            "(người trả lời đồng ý hoặc không đồng ý với toàn bộ bộ câu hỏi theo xu hướng chung), "
            "không hẳn là sự nhất quán tâm lý thực sự. "
            "Đây là lý do báo cáo <strong>luôn đính kèm biểu đồ phân phối điểm</strong> và "
            "<strong>phân tích phản hồi mở định tính</strong> để tam giác hóa với điểm trung bình.",
            color="#F59E0B", bg="#FFFBEB"
        ), unsafe_allow_html=True)

        # Pillar reliability breakdown
        st.markdown(_sec("Độ tin cậy theo từng Trụ cột"), unsafe_allow_html=True)

        pillar_alpha = {
            "Trụ cột": [
                "TC1 · Gắn kết Tổ chức",
                "TC2 · Quản lý Trực tiếp",
                "TC3 · Môi trường & Điều kiện",
                "TC4 · Thu nhập & Phúc lợi",
                "TC5 · Phát triển & Cơ hội",
            ],
            "Số câu": [7, 5, 4, 3, 3],
            "α trung bình": [0.93, 0.91, 0.89, 0.87, 0.88],
            "Ghi chú": [
                "Nhất quán cao — đọc kèm eNPS",
                "Nhất quán cao — kiểm tra gap Q9 vs Q12",
                "Nhất quán — xem phân phối tầng lớp",
                "Cảnh báo: 2 câu tương quan rất cao (r=0.91)",
                "Ổn định — nhưng câu Q19 có phân kỳ tenure",
            ]
        }

        pillar_alpha_df = pd.DataFrame(pillar_alpha)
        for i, row in pillar_alpha_df.iterrows():
            bg = "#FFFFFF" if i % 2 == 0 else "#F8FAFC"
            p_cols = st.columns([3, 1, 1.2, 3])
            cell_s = f"background:{bg};padding:8px 12px;font-size:0.83rem;border-bottom:1px solid #F1F5F9"
            with p_cols[0]:
                st.markdown(f'<div style="{cell_s};font-weight:600;color:#0A1F44">{row["Trụ cột"]}</div>', unsafe_allow_html=True)
            with p_cols[1]:
                st.markdown(f'<div style="{cell_s};text-align:center;color:#64748B">{row["Số câu"]}</div>', unsafe_allow_html=True)
            with p_cols[2]:
                alpha_val = row["α trung bình"]
                a_color = "#15803D" if alpha_val >= 0.90 else "#D97706"
                st.markdown(f'<div style="{cell_s};text-align:center;font-weight:700;color:{a_color}">{alpha_val:.2f}</div>', unsafe_allow_html=True)
            with p_cols[3]:
                st.markdown(f'<div style="{cell_s};color:#64748B;font-style:italic">{row["Ghi chú"]}</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # TAB 4: LƯU Ý SỬ DỤNG KẾT QUẢ
    # ═══════════════════════════════════════════════════
    with tab4:
        st.markdown(_sec("Lưu ý khi đọc và sử dụng kết quả"), unsafe_allow_html=True)

        notes = [
            (
                "Không so sánh trực tiếp với 2025",
                "#EF4444", "#FEF2F2",
                "Thang đo 2026 (1–5) khác với 2026 (1–10). Điểm Engagement 2026 = 3.8/5 "
                "<strong>không phải</strong> sụt giảm từ 8.02/10 — đây là hai thước đo độc lập. "
                "Cần quy đổi cùng thang hoặc dùng %Favorable thay vì điểm tuyệt đối để so sánh.",
            ),
            (
                "Đọc phân phối, không chỉ điểm trung bình",
                "#D97706", "#FFFBEB",
                "Với nhóm có trả lời đồng nhất cao (1A), điểm trung bình 3.9 có thể che khuất "
                "bimodal distribution (rất nhiều người 4–5 VÀ một nhóm nhỏ 1–2). "
                "Luôn xem biểu đồ phân phối Likert trước khi kết luận.",
            ),
            (
                "Lát cắt nhỏ cần biên tin cậy",
                "#3B82F6", "#EFF6FF",
                "Các đơn vị con (section) có n < 30 cần thêm biên tin cậy ±. "
                "Sự khác biệt 0.1–0.2 điểm ở nhóm nhỏ thường không có ý nghĩa thống kê. "
                "Dashboard chỉ hiển thị lát cắt khi n ≥ 15, nhưng tốt nhất nên n ≥ 30.",
            ),
            (
                "Nhóm 2B cần xác minh dữ liệu",
                "#8B5CF6", "#F5F3FF",
                "File 2B có bảng 'test' 223 phản hồi chưa được xác nhận nguồn gốc. "
                "Kết quả 2B trong dashboard hiện <strong>chưa bao gồm</strong> 223 phản hồi này. "
                "Cần xác nhận từ nhóm HR trước khi dùng cho quyết định cấp cao.",
            ),
            (
                "Câu hỏi mở là tam giác hóa định tính",
                "#10B981", "#F0FDF4",
                "Kết quả Likert phản ánh xu hướng tổng thể; câu hỏi mở Q34 (mong muốn thay đổi) "
                "cung cấp context định tính. Hai nguồn nên đọc <strong>song song</strong> — "
                "không nên dùng một nguồn để bác bỏ nguồn kia.",
            ),
        ]

        for title, color, bg, body in notes:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {color}33;border-left:4px solid {color};
                        border-radius:10px;padding:18px 22px;margin-bottom:16px;">
                <div style="font-size:0.88rem;font-weight:700;color:#0A1F44;margin-bottom:8px">{title}</div>
                <div style="font-size:0.84rem;color:#475569;line-height:1.7">{body}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0A1F44;border-radius:12px;padding:24px 28px;color:white">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
                <img src="{_AI_LOGO_B64}" style="width:20px;height:20px">
                <span style="font-size:0.9rem;font-weight:700;color:#F8FAFC">
                    Tóm tắt độ tin cậy tổng thể
                </span>
            </div>
            <p style="font-size:0.85rem;color:#94A3B8;line-height:1.75;margin:0">
                Dữ liệu EES 2026 có <strong style="color:white">độ tin cậy cao</strong> ở cấp độ tổng thể và đủ đại diện
                cho toàn bộ lực lượng lao động GHN. Các kết luận cấp công ty và cấp nhóm lớn
                (n &gt; 500) có thể được đọc trực tiếp. Lát cắt nhỏ (phòng ban, section)
                cần thêm bước xác nhận định tính. Phân tích AI trong dashboard
                <strong style="color:white">không thay thế phán đoán của HR/người quản lý</strong> —
                đây là công cụ hỗ trợ nhận diện tín hiệu, không phải kết luận cuối cùng.
            </p>
        </div>
        """, unsafe_allow_html=True)
