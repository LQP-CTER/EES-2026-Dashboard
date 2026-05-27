import streamlit as st
import pandas as pd

def render(df=None, cfg=None, **kwargs):
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="color: #0A1F44; font-size: 1.8rem; margin-bottom: 8px;">Phụ lục & Giải thích Chỉ số</h2>
        <p style="color: #475569; font-size: 1.05rem;">
            Tài liệu tham khảo chi tiết về ý nghĩa và công thức tính toán của các chỉ số quan trọng được sử dụng trong Dashboard EES 2026.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Khung tổng quan
    st.markdown("""
    <div style="background-color: #FFF3EE; border-left: 4px solid #FF5200; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        <h3 style="color: #FF5200; font-size: 1.2rem; margin-top: 0;">Tại sao cần các chỉ số này?</h3>
        <p style="color: #334155; margin-bottom: 0; line-height: 1.6;">
            Các chỉ số EES không chỉ đơn thuần là điểm trung bình của khảo sát. Chúng được thiết kế dựa trên các mô hình 
            tâm lý học tổ chức (như <i>Job Demands-Resources Model</i>) để đo lường không chỉ <b>mức độ hài lòng</b> 
            mà còn cả <b>sự gắn kết sâu sắc</b>, <b>mức độ kiệt sức</b> và <b>rủi ro biến động nhân sự</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Chi tiết từng chỉ số
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; height: 100%; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
                <div style="background: #E0E7FF; color: #4F46E5; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;">EI</div>
                <h3 style="margin: 0; color: #0A1F44;">Engagement Index<br><span style="font-size: 0.85rem; color: #64748B; font-weight: 400;">Chỉ số Gắn kết Tổ chức</span></h3>
            </div>
            <p><b>Ý nghĩa:</b> Thước đo tổng thể về mức độ gắn kết của nhân viên với công ty, được tổng hợp từ 5 trụ cột cốt lõi: <i>Niềm tin & Định hướng, Quản lý trực tiếp, Môi trường & Công cụ, Đãi ngộ & Công bằng, Văn hóa & Tự hào.</i></p>
            <p><b>Công thức tính:</b></p>
            <div style="background: #F8FAFC; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.9rem; margin-bottom: 10px;">
                EI = Σ (Tỷ lệ tích cực của Trụ cột <i>i</i> × Trọng số <i>i</i>)
            </div>
            <ul style="color: #475569; font-size: 0.9rem;">
                <li><i>Tỷ lệ tích cực:</i> % người chọn mức 4 (Đồng ý) và 5 (Hoàn toàn đồng ý) trong các câu hỏi Likert 5 điểm.</li>
                <li><i>Trọng số:</i> Mỗi trụ cột có một trọng số (tổng = 100%) tùy thuộc vào định hướng chiến lược.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; height: 100%; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
                <div style="background: #FCE7F3; color: #DB2777; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;">MEI</div>
                <h3 style="margin: 0; color: #0A1F44;">Manager Effectiveness Index<br><span style="font-size: 0.85rem; color: #64748B; font-weight: 400;">Chỉ số Năng lực Quản lý</span></h3>
            </div>
            <p><b>Ý nghĩa:</b> Đánh giá mức độ hiệu quả, sự hỗ trợ và năng lực lãnh đạo của Quản lý trực tiếp từ góc nhìn của nhân viên cấp dưới.</p>
            <p><b>Công thức tính:</b></p>
            <div style="background: #F8FAFC; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.9rem; margin-bottom: 10px;">
                MEI = Tỷ lệ % trả lời Tích cực cho nhóm câu hỏi về Quản lý (Q11, Q12, Q14, Q15)
            </div>
            <p style="color: #475569; font-size: 0.9rem; margin-bottom: 0;">
                Gồm các khía cạnh: Ghi nhận năng lực, Đối xử công bằng, Hỗ trợ khi gặp khó khăn, và Lắng nghe ý kiến.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; height: 100%; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
                <div style="background: #DCFCE7; color: #16A34A; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;">eNPS</div>
                <h3 style="margin: 0; color: #0A1F44;">Employee Net Promoter Score<br><span style="font-size: 0.85rem; color: #64748B; font-weight: 400;">Chỉ số Sẵn sàng Giới thiệu</span></h3>
            </div>
            <p><b>Ý nghĩa:</b> Đo lường mức độ trung thành của nhân viên. Dựa trên câu hỏi duy nhất: <i>"Bạn có sẵn sàng giới thiệu GHN là một nơi làm việc tốt cho bạn bè/người thân không?"</i> (Thang 0-10).</p>
            <p><b>Công thức tính:</b></p>
            <div style="background: #F8FAFC; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.9rem; margin-bottom: 10px;">
                eNPS = % Promoter (Điểm 9-10) - % Detractor (Điểm 0-6)
            </div>
            <ul style="color: #475569; font-size: 0.9rem;">
                <li><b>Promoter (Đại sứ):</b> Điểm 9-10. Trung thành, nhiệt huyết.</li>
                <li><b>Passive (Thụ động):</b> Điểm 7-8. Hài lòng nhưng dễ bị thu hút bởi offer khác (không đưa vào công thức).</li>
                <li><b>Detractor (Bất mãn):</b> Điểm 0-6. Không hài lòng, có khả năng lan truyền tiêu cực.</li>
            </ul>
            <p style="color: #475569; font-size: 0.9rem; margin-bottom: 0;"><i>Lưu ý: Điểm eNPS chạy từ -100 đến +100. >0 là Tốt, >30 là Tuyệt vời.</i></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; height: 100%; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
                <div style="background: #FEF2F2; color: #DC2626; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;">BR</div>
                <h3 style="margin: 0; color: #0A1F44;">Burnout Risk & Flight Risk<br><span style="font-size: 0.85rem; color: #64748B; font-weight: 400;">Rủi ro Kiệt sức & Nghỉ việc</span></h3>
            </div>
            <p><b>Nguy cơ Kiệt sức (Burnout Risk):</b></p>
            <div style="background: #F8FAFC; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.9rem; margin-bottom: 10px;">
                Burnout Score = [Áp lực Công việc (Q18, Q29)] - [Nguồn lực Hỗ trợ (Q11, Q16)]
            </div>
            <p style="color: #475569; font-size: 0.9rem; margin-bottom: 15px;">Dựa trên mô hình JD-R (Job Demands-Resources). Nếu Áp lực liên tục lớn hơn Nguồn lực, nhân viên sẽ rơi vào trạng thái kiệt quệ.</p>
            
            <p><b>Tỷ lệ Muốn nghỉ (Turnover Intent / Flight Risk):</b></p>
            <div style="background: #F8FAFC; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.9rem; margin-bottom: 10px;">
                % Muốn nghỉ = Tỷ lệ chọn mức Thấp (1-2) ở câu hỏi "Ý định gắn bó"
            </div>
            <p style="color: #475569; font-size: 0.9rem; margin-bottom: 0;">Nhóm này có nguy cơ rời tổ chức trong vòng 6 tháng tới rất cao, cần can thiệp giữ chân (Retention Plan).</p>
        </div>
        """, unsafe_allow_html=True)

