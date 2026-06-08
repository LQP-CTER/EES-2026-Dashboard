import os

file_path = 'views/overview_ees_2026.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Video playlist
target_videos = """    main_video_url  = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780389451/LOGO%20GHN/Action_video_dgq3f7.mp4"
    short_urls = [
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780395113/LOGO%20GHN/IMG_0734_nhqt02.mp4",   "Khoảnh khắc 1"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393976/LOGO%20GHN/IMG_1233_wgzajm.mp4",   "Khoảnh khắc 2"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393954/LOGO%20GHN/IMG_1232_ykz6pz.mp4",   "Khoảnh khắc 3"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393907/LOGO%20GHN/IMG_1723_gdh1gs.mp4",   "Khoảnh khắc 4"),
    ]"""

replacement_videos = """    main_video_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780395113/LOGO%20GHN/IMG_0734_nhqt02.mp4"
    highlight_url = "https://res.cloudinary.com/dd7gti2kn/video/upload/v1780389451/LOGO%20GHN/Action_video_dgq3f7.mp4"
    playlist = [
        (main_video_url, "Nhìn lại EES 2025"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393976/LOGO%20GHN/IMG_1233_wgzajm.mp4", "Giới thiệu EES 2026"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393954/LOGO%20GHN/IMG_1232_ykz6pz.mp4", "EES Race 2026"),
        (highlight_url, "Highlight"),
        ("https://res.cloudinary.com/dd7gti2kn/video/upload/v1780393907/LOGO%20GHN/IMG_1723_gdh1gs.mp4", "EES 2026 Vinh danh")
    ]"""

text = text.replace(target_videos, replacement_videos)

# 2. Update Playlist reference
target_ref = """    # Playlist = main highlight reel + 4 shorts. The main reel is the first item.
    playlist = [(main_video_url, "Highlight Reel")] + short_urls"""

replacement_ref = """    # Playlist is defined above"""

text = text.replace(target_ref, replacement_ref)

# 3. Update Radar UI - orbit pills
target_orbit = """                    <div class="ed-orbit">
                        <div class="ed-orbit-ring"></div>
                        <div class="ed-orbit-ring"></div>
                        <div class="ed-orbit-core"></div>
                        <span class="ed-orbit-pill p1">Lãnh đạo</span>
                        <span class="ed-orbit-pill p2">MEI</span>
                        <span class="ed-orbit-pill p3">Công việc</span>
                        <span class="ed-orbit-pill p4">Thu nhập</span>
                        <span class="ed-orbit-pill p5">Môi trường</span>
                    </div>"""

replacement_orbit = """                    <div class="ed-orbit">
                        <div class="ed-orbit-ring"></div>
                        <div class="ed-orbit-ring"></div>
                        <div class="ed-orbit-core"></div>
                        <span class="ed-orbit-pill p1">Niềm tin lãnh đạo</span>
                        <span class="ed-orbit-pill p2">Quản lý trực tiếp</span>
                        <span class="ed-orbit-pill p3">Công việc &amp; phát triển</span>
                        <span class="ed-orbit-pill p4">Thu nhập &amp; minh bạch</span>
                        <span class="ed-orbit-pill p5">Môi trường &amp; phát triển</span>
                    </div>"""

text = text.replace(target_orbit, replacement_orbit)

# 4. Update Radar UI - desc text
target_desc = """<div class="jt-stat-desc">Lãnh đạo · MEI · Công việc · Thu nhập · Môi trường</div>"""
replacement_desc = """<div class="jt-stat-desc">Niềm tin lãnh đạo · Quản lý trực tiếp · Công việc &amp; phát triển · Thu nhập &amp; minh bạch · Môi trường &amp; phát triển</div>"""
text = text.replace(target_desc, replacement_desc)

# 5. Comment out Map
target_map = """st.plotly_chart(create_vietnam_map(), use_container_width=True)"""
replacement_map = """# st.plotly_chart(create_vietnam_map(), use_container_width=True)"""
text = text.replace(target_map, replacement_map)

# 6. Remove Taglines
text = text.replace('<span class="ed-team-badge">Survey Design &amp; Ops</span>', '')
text = text.replace('<span class="ed-team-badge">Internal Comms · Engagement Push</span>', '')
text = text.replace('<span class="ed-team-badge">System & Infrastructure</span>', '')
text = text.replace('<span class="ed-team-badge">Data Engineering</span>', '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacement done")
