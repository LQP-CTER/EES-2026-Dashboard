"""Static analyst intelligence blocks sourced from docs/analyst.

These blocks intentionally render pre-curated findings instead of running
expensive analysis at page load. The goal is to align the dashboard narrative
with the analyst PDF/XLSX pack while keeping Streamlit fast.
"""

from __future__ import annotations

import html
from textwrap import dedent
from typing import Optional

import pandas as pd
import streamlit as st

from shared.plotly_theme import section_header


GROUP_INSIGHTS = {
    "1A": {
        "title": "Nhóm 1A - Nhân viên giao nhận",
        "source": "EES2026_1A1B_Analysis + EES2026_ThuNhap_NVPTTT_Full",
        "headline": "Không phải câu chuyện lương thấp đơn thuần. Rủi ro chính nằm ở biến động thu nhập, phạt/truy thu, minh bạch đơn giá và công bằng tuyến.",
        "metrics": [
            ("Mẫu hợp lệ 1A", "12,262", "DeepDive v13"),
            ("EI 1A", "73.5", "toàn nhóm"),
            ("Straight-line", "52.3%", "rủi ro im lặng"),
            ("Flight Risk", "5.5%", "toàn nhóm"),
        ],
        "cards": [
            ("Thu nhập & minh bạch là chủ đề số 1", "Q34 nhóm NVPTTT cho thấy Thu nhập/Minh bạch chiếm 44.7% phản hồi có nội dung. Cơ chế nổi bật: thu nhập giảm theo thời gian, AOV/đơn giá khó hiểu, tuyến dài nhưng bù đắp chưa tương xứng."),
            ("Phạt và xử lý công bằng là điểm mù cũ", "Nhóm phạt/xử lý công bằng chiếm khoảng 10% phản hồi, nổi bật ở XBG, ĐCL và DBB. Đây là lớp vấn đề dễ bị che nếu chỉ nhìn EI tổng."),
            ("Vùng cần ưu tiên", "ĐCL và XBG là hai vùng cần đọc sâu: EI thấp hơn mặt bằng, MEI yếu hơn, và phản hồi mở tập trung vào thu nhập, phạt, route/fare. HCM có số Flight Risk tuyệt đối lớn nên cần retention interview có chọn lọc."),
        ],
        "actions": [
            "Audit cơ chế đơn giá/tuyến dài và nhóm tỉnh có năng suất cao nhưng thu nhập thấp.",
            "Tách lỗi cá nhân khỏi lỗi hệ thống trong cơ chế phạt/truy thu.",
            "Đưa lý do phạt, COD clawback và công thức thu nhập lên App Driver theo hướng dễ kiểm tra.",
            "Close-the-loop riêng cho ĐCL, XBG, HCM với owner vùng và HRBP.",
        ],
    },
    "1B": {
        "title": "Nhóm 1B - Tài xế xe tải",
        "source": "EES2026_1A1B_Analysis",
        "headline": "1B có EI/eNPS tốt hơn 1A, nhưng rủi ro nằm ở công bằng chuyến, xe cũ, COD settlement và phụ cấp tuyến dài.",
        "metrics": [
            ("Mẫu hợp lệ 1B", "784", "DeepDive v13"),
            ("EI 1B", "75.9", "toàn nhóm"),
            ("eNPS", "+47.8", "toàn nhóm"),
            ("Leave intent", "2.1%", "thấp"),
        ],
        "cards": [
            ("Hưng Yên", "Vấn đề nổi bật là công bằng tuyến và xe cũ. Tài liệu analyst gợi ý cần kiểm tra khả năng thiên vị/không minh bạch trong điều phối chuyến."),
            ("M12", "COD settlement kéo dài, xe cũ và tải lịch chạy tạo áp lực vận hành. Đây là nhóm cần ưu tiên cải thiện quy trình thanh toán và phương tiện."),
            ("Xuyên Á", "Phản hồi nhấn mạnh phụ cấp Bắc-Nam, thu nhập giảm và cảm giác mất chuyến vào xe ngoài. Cần rà lại unit economics của tuyến dài."),
        ],
        "actions": [
            "Công khai nguyên tắc phân chuyến/tuyến tốt và log điều phối.",
            "Rút COD settlement về mốc vận hành rõ ràng hơn.",
            "Rà phụ cấp tuyến dài, xăng/dầu và tình trạng xe cũ theo đội xe.",
        ],
    },
    "2A": {
        "title": "Nhóm 2A - Nhân viên vận hành kho",
        "source": "EES2026_KTC_NVPH_Analysis + EES2026_KTC_Master_Analysis + DeepDive v13",
        "headline": "2A không chỉ là câu chuyện thu nhập. Các điểm vật lý như nóng, quạt, nhà vệ sinh, bữa ăn và thiết bị là tín hiệu rất thật trong open-text.",
        "metrics": [
            ("Mẫu hợp lệ 2A", "4,819", "DeepDive v13"),
            ("EI 2A", "72.4", "toàn nhóm"),
            ("MEI 2A", "78.8", "toàn nhóm"),
            ("Trapped Worker", "5.6%", "~268 người"),
        ],
        "cards": [
            ("Hưng Yên là ưu tiên số 1", "EI 67.9, MEI 71.2, eNPS +12.5. Phản hồi mở tập trung mạnh vào quạt/làm mát, nóng, bữa ăn và thu nhập."),
            ("M12 bị bỏ sót trong báo cáo cũ", "Master Analysis xác nhận M12 có tín hiệu vật lý rõ: nhà vệ sinh, thiết bị/PDA/băng tải, quạt/nóng và bụi. Không nên kết luận M12 chỉ có vấn đề thu nhập."),
            ("Xuyên Á là benchmark vận hành", "Xuyên Á có EI/MEI tốt nhất trong 5 KTC, nhưng vẫn có issue về canteen, NVS, xăng/đi lại. Điểm mạnh nằm ở MEI bảo vệ trải nghiệm."),
        ],
        "actions": [
            "Can thiệp Hưng Yên trong 30 ngày: đo nhiệt, bổ sung quạt/làm mát, rà bữa ăn/OT.",
            "M12: sửa NVS, thiết bị, PDA/băng tải và phân tách vấn đề theo ca/khu vực.",
            "Không bỏ quên Kho Vùng/GXT: 2,219 nhân sự kho vùng là gần một nửa workforce 2A.",
        ],
    },
    "2B": {
        "title": "Nhóm 2B - Quản lý vận hành tuyến đầu",
        "source": "EES2026_2B_Analysis + DeepDive v13",
        "headline": "2B là nhóm 'Proud but Pressured': EI/eNPS cao nhưng đang hấp thụ áp lực từ nhân viên tuyến dưới, thiếu công cụ và thiếu chuẩn vận hành.",
        "metrics": [
            ("Mẫu hợp lệ 2B", "425", "toàn nhóm"),
            ("EI 2B", "78.9", "cao nhất"),
            ("eNPS", "+59.6", "cao nhất"),
            ("Uncertain stay", "36.5%", "cần pulse"),
        ],
        "cards": [
            ("Áp lực quản trị bị che bởi EI cao", "Open-text cho thấy nhu cầu lớn về công cụ quản lý, data/reporting, chuẩn hóa quy trình và staffing. EI cao không đồng nghĩa đã hết rủi ro."),
            ("ĐCL là hotspot", "ĐCL 2B có EI 68.3, MEI 77.5 và nhiều phản hồi về thu nhập, nhân sự, chính sách NVPTTT. Đây là tín hiệu hệ thống, không chỉ cá nhân quản lý."),
            ("Manager gap cần được đọc cùng 1A", "DeepDive ghi nhận tương quan EI 2B vs 1A theo vùng có thể lệch chiều. Nơi quản lý thấy ổn nhưng nhân viên tuyến dưới thấp là vùng cần kiểm tra 'manager bubble'."),
        ],
        "actions": [
            "Pulse 5 câu cho 2B trong 2 tuần để đo áp lực giữ chân.",
            "Xây dashboard realtime/công cụ báo cáo cho AM/TBC/Supervisor.",
            "Rà KPI và chuẩn SOP địa phương hóa trước khi yêu cầu quản lý truyền thông xuống đội ngũ.",
        ],
    },
    "3A": {
        "title": "Nhóm 3A - Nhân viên văn phòng",
        "source": "DeepDive v13",
        "headline": "3A là rủi ro chiến lược ở khối văn phòng: eNPS thấp, burnout cao và TC5 là driver mạnh nhất cho ý định ở lại.",
        "metrics": [
            ("Mẫu hợp lệ 3A", "822", "toàn nhóm"),
            ("EI 3A", "71.5", "thấp"),
            ("eNPS", "+16.3", "thấp nhất"),
            ("Burnout risk", "24.4%", "cao nhất"),
        ],
        "cards": [
            ("HR Division paradox", "HR n=151 có Stay 3.41, Leave 13.3%, eNPS +8.7. Đây là nghịch lý quan trọng vì nhóm thiết kế EX lại có trải nghiệm EX yếu."),
            ("Product và AI/Data cần đọc dù mẫu nhỏ", "Product n=12 eNPS -18.6, AI & Data n=15 eNPS -6.7. Mẫu nhỏ nhưng chiến lược, cần coi là early signal thay vì bỏ qua."),
            ("TC5 là driver giữ chân", "KDA trong DeepDive cho thấy TC5 liên quan mạnh nhất tới Stay của 3A. Cần ưu tiên văn hóa, ghi nhận, belonging và career/process."),
        ],
        "actions": [
            "Can thiệp HR Division trong 30 ngày bằng listening session kín và action owner rõ.",
            "Review process debt: phê duyệt chậm, cross-functional friction, thiếu SLA.",
            "Thiết kế lại career/promotion cho office group trước 31/10/2026.",
        ],
    },
    "3B": {
        "title": "Nhóm 3B - Quản lý HQ",
        "source": "DeepDive v13",
        "headline": "3B nhìn ổn ở Leave intent nhưng có rủi ro im lặng chiến lược: Q26 silence cao, TC3 thấp và nhóm Product/AI/Data có tín hiệu yếu dù mẫu nhỏ.",
        "metrics": [
            ("Mẫu hợp lệ 3B", "109", "toàn nhóm"),
            ("EI 3B", "73.6", "trung bình"),
            ("Leave intent", "0.9%", "rất thấp"),
            ("Q26 Silence", "69.7%", "defensive silence"),
        ],
        "cards": [
            ("Defensive silence", "Tỷ lệ không trả lời Q26 rất cao cho thấy quản lý có thể chọn im lặng ở các vấn đề nhạy cảm, dù khảo sát ẩn danh."),
            ("Chiến lược & công cụ", "Open-text tập trung vào strategy/clarity, tools/data, resources/staff và process/cross-functional. Đây là nhóm cần thông tin rõ để ra quyết định."),
            ("Low-sample strategic units", "Product và AI/Data có điểm thấp nhưng n nhỏ. Với nhóm quản lý, mẫu nhỏ vẫn đáng đọc như tín hiệu chiến lược cần phỏng vấn sâu."),
        ],
        "actions": [
            "Tổ chức manager forum kín để phá defensive silence.",
            "Làm rõ priority chiến lược và quyền ra quyết định theo cấp.",
            "Theo dõi Product/AI/Data bằng phỏng vấn định tính thay vì chỉ nhìn n.",
        ],
    },
}


COMPANY_FINDINGS = [
    ("Rủi ro im lặng ở 1A", "1A có tỷ lệ silence/straight-line rất cao. Đây là rủi ro mất tín hiệu cảnh báo sớm, không nên chỉ đọc EI tổng."),
    ("2B tự hào nhưng chịu áp lực", "2B EI/eNPS cao nhất nhưng 36.5% chưa chắc ở lại. Nhóm này đang hấp thụ áp lực vận hành và thiếu công cụ quản trị."),
    ("Rủi ro chiến lược ở 3A", "3A có eNPS thấp nhất và burnout cao nhất. TC5 là driver chính cho Stay, nên rủi ro nằm ở văn hóa, ghi nhận, belonging và career process."),
    ("Điều kiện cơ bản tại KTC", "2A KTC/TTTC có nhiều vấn đề rất cụ thể: nóng, quạt, NVS, bữa ăn, thiết bị. Đây là tầng hygiene cần xử lý trước truyền thông gắn kết."),
    ("Biến động thu nhập NVPTTT", "Với NVPTTT, thu nhập trung bình không phải toàn bộ câu chuyện. Biến động, phạt/truy thu và minh bạch quyết định cảm nhận công bằng."),
]

EXECUTIVE_DECISIONS = [
    ("Phản hồi vòng lặp - Close the Loop", "30/07/2026", "Phản hồi kết quả và hành động tới lực lượng tuyến đầu, ưu tiên 1A/2A."),
    ("Khung KPI cho 2B", "30/09/2026", "Rà KPI và công cụ quản trị cho AM/TBC/Supervisor."),
    ("Hiệu suất & thăng tiến cho 3A", "31/10/2026", "Làm rõ career path, promotion và process/cross-functional friction."),
    ("Minh bạch App Driver", "31/08/2026", "Minh bạch thu nhập, phạt/truy thu, COD clawback cho 1A/1B."),
    ("Can thiệp XBG/ĐCL", "15/08/2026", "Can thiệp trực tiếp hai vùng rủi ro trong vận hành tuyến đầu."),
]


def _metric_card(label: str, value: str, sub: str) -> str:
    return f"""
    <div class="aiq-metric">
        <div class="aiq-metric-label">{html.escape(label)}</div>
        <div class="aiq-metric-value">{html.escape(value)}</div>
        <div class="aiq-metric-sub">{html.escape(sub)}</div>
    </div>
    """


def _ensure_css():
    st.markdown(
        """
        <style>
        .aiq-shell {
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:18px;
            padding:22px;
            margin:18px 0 26px;
            box-shadow:0 16px 34px rgba(10,31,68,.07);
        }
        .aiq-top {
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:18px;
            margin-bottom:16px;
        }
        .aiq-kicker {
            color:#FF5200;
            font-size:.68rem;
            font-weight:850;
            letter-spacing:.13em;
            text-transform:uppercase;
            margin-bottom:6px;
        }
        .aiq-title {
            color:#0A1F44;
            font-size:1.2rem;
            font-weight:900;
            letter-spacing:-.02em;
            margin:0 0 6px;
        }
        .aiq-headline {
            color:#475569;
            font-size:.88rem;
            line-height:1.65;
            font-weight:560;
            margin:0;
            max-width:940px;
        }
        .aiq-source {
            color:#64748B;
            background:#F8FAFC;
            border:1px solid #E2E8F0;
            border-radius:999px;
            padding:6px 10px;
            font-size:.68rem;
            font-weight:750;
            white-space:nowrap;
        }
        .aiq-metrics {
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:12px;
            margin:16px 0;
        }
        .aiq-metric {
            background:#F8FAFC;
            border:1px solid #E2E8F0;
            border-radius:14px;
            padding:14px 15px;
            min-width:0;
        }
        .aiq-metric-label {
            color:#64748B;
            font-size:.66rem;
            font-weight:850;
            letter-spacing:.09em;
            text-transform:uppercase;
            margin-bottom:8px;
        }
        .aiq-metric-value {
            color:#0A1F44;
            font-size:1.45rem;
            font-weight:950;
            letter-spacing:-.035em;
            line-height:1;
        }
        .aiq-metric-sub {
            color:#94A3B8;
            font-size:.72rem;
            font-weight:650;
            margin-top:7px;
        }
        .aiq-card-grid {
            display:grid;
            grid-template-columns:repeat(3,minmax(0,1fr));
            gap:14px;
        }
        .aiq-card {
            border:1px solid #E2E8F0;
            border-top:3px solid #FF5200;
            border-radius:14px;
            padding:16px;
            background:#FFFFFF;
            min-height:145px;
        }
        .aiq-card-title {
            color:#0A1F44;
            font-size:.9rem;
            font-weight:850;
            margin-bottom:8px;
            letter-spacing:-.01em;
        }
        .aiq-card-body {
            color:#64748B;
            font-size:.82rem;
            line-height:1.62;
            font-weight:520;
        }
        .aiq-actions {
            margin:14px 0 0;
            padding:14px 16px;
            border-radius:14px;
            background:#FFF7ED;
            border:1px solid #FED7AA;
        }
        .aiq-actions-title {
            color:#C2410C;
            font-size:.72rem;
            font-weight:900;
            letter-spacing:.1em;
            text-transform:uppercase;
            margin-bottom:8px;
        }
        .aiq-actions ul {
            margin:0;
            padding-left:18px;
            color:#475569;
            font-size:.84rem;
            line-height:1.65;
            font-weight:540;
        }
        @media (max-width: 1080px) {
            .aiq-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .aiq-card-grid { grid-template-columns:1fr; }
            .aiq-top { flex-direction:column; }
            .aiq-source { white-space:normal; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_group_analyst_intelligence(group_id: Optional[str]):
    """Render analyst-backed narrative for a survey group."""
    if not group_id or group_id not in GROUP_INSIGHTS:
        return

    _ensure_css()
    item = GROUP_INSIGHTS[group_id]
    group_title = html.escape(item["title"])
    headline = html.escape(item["headline"])
    source = html.escape(item["source"])
    metric_html = "".join(_metric_card(*m) for m in item["metrics"])
    card_html = "".join(
        f"""
        <div class="aiq-card">
            <div class="aiq-card-title">{html.escape(card_title)}</div>
            <div class="aiq-card-body">{html.escape(body)}</div>
        </div>
        """
        for card_title, body in item["cards"]
    )
    actions = "".join(f"<li>{html.escape(a)}</li>" for a in item["actions"])

    st.markdown(section_header("Phân tích chuyên sâu từ tài liệu analyst", "Các insight đã đối chiếu từ bộ tài liệu trong docs/analyst"), unsafe_allow_html=True)
    st.html(
        dedent(
            f"""
            <div class="aiq-shell">
                <div class="aiq-top">
                    <div>
                        <div class="aiq-kicker">Bộ phân tích đã thẩm định</div>
                        <h3 class="aiq-title">{group_title}</h3>
                        <p class="aiq-headline">{headline}</p>
                    </div>
                    <div class="aiq-source">{source}</div>
                </div>
                <div class="aiq-metrics">{metric_html}</div>
                <div class="aiq-card-grid">{card_html}</div>
                <div class="aiq-actions">
                    <div class="aiq-actions-title">Hành động nên đưa vào dashboard</div>
                    <ul>{actions}</ul>
                </div>
            </div>
            """
        )
    )


def render_company_analyst_intelligence(all_data):
    """Render company-level analyst narrative."""
    from utils.data_loader import compute_kpis
    
    # Tính toán các chỉ số động
    silence_1a = "rất cao"
    if "1A" in all_data:
        kpis_1a = compute_kpis(all_data["1A"][0])
        silence_1a = f"{kpis_1a.get('silence_rate', 0):.1f}%"
        
    stay_risk_2b = "36.5%"
    if "2B" in all_data:
        kpis_2b = compute_kpis(all_data["2B"][0])
        risk = kpis_2b.get('stay_flight_pct', 0) + kpis_2b.get('stay_atrisk_pct', 0)
        stay_risk_2b = f"{risk:.1f}%"
        
    enps_3a = "thấp nhất"
    burnout_3a = "cao nhất"
    if "3A" in all_data:
        kpis_3a = compute_kpis(all_data["3A"][0])
        enps_3a = f"{kpis_3a.get('enps_score', 0):.0f}"
        burnout_3a = f"{kpis_3a.get('burnout_pct', 0):.1f}%"

    dynamic_findings = [
        ("Rủi ro im lặng ở 1A", f"1A có tỷ lệ silence/straight-line lên tới {silence_1a}. Đây là rủi ro mất tín hiệu cảnh báo sớm, không nên chỉ đọc EI tổng."),
        ("2B tự hào nhưng chịu áp lực", f"2B EI/eNPS cao nhưng {stay_risk_2b} chưa chắc ở lại. Nhóm này đang hấp thụ áp lực vận hành và thiếu công cụ quản trị."),
        ("Rủi ro chiến lược ở 3A", f"3A có eNPS ở mức {enps_3a} và tỷ lệ burnout lên tới {burnout_3a}. TC5 là driver chính cho Stay, nên rủi ro nằm ở văn hóa, ghi nhận, belonging và career process."),
        ("Điều kiện cơ bản tại KTC", "2A KTC/TTTC có nhiều vấn đề rất cụ thể: nóng, quạt, NVS, bữa ăn, thiết bị. Đây là tầng hygiene cần xử lý trước truyền thông gắn kết."),
        ("Biến động thu nhập NVPTTT", "Với NVPTTT, thu nhập trung bình không phải toàn bộ câu chuyện. Biến động, phạt/truy thu và minh bạch quyết định cảm nhận công bằng."),
    ]

    _ensure_css()
    finding_html = "".join(
        f"""
        <div class="aiq-card">
            <div class="aiq-card-title">{html.escape(finding_title)}</div>
            <div class="aiq-card-body">{html.escape(body)}</div>
        </div>
        """
        for finding_title, body in dynamic_findings
    )
    decisions_df = pd.DataFrame(EXECUTIVE_DECISIONS, columns=["Quyết định", "Mốc đề xuất", "Ý nghĩa triển khai"])

    st.markdown(section_header("Phân tích chuyên sâu từ tài liệu analyst", "Những điểm cần bổ sung để dashboard khớp với bộ tài liệu analyst"), unsafe_allow_html=True)
    st.html(
        dedent(
            f"""
            <div class="aiq-shell">
                <div class="aiq-top">
                    <div>
                        <div class="aiq-kicker">Tổng hợp điều hành</div>
                        <h3 class="aiq-title">Các phát hiện chiến lược từ bộ analyst</h3>
                        <p class="aiq-headline">
                            Lớp này gom các insight từ DeepDive v13, báo cáo 1A/1B, 2B, KTC và thu nhập NVPTTT.
                            Mục tiêu là giúp trang Tổng quan GHN không chỉ hiển thị KPI, mà còn nói đúng câu chuyện phân tích phía sau.
                        </p>
                    </div>
                    <div class="aiq-source">docs/analyst · PDF/XLSX pack</div>
                </div>
                <div class="aiq-card-grid">{finding_html}</div>
            </div>
            """
        )
    )
    st.dataframe(decisions_df, width="stretch", hide_index=True)
