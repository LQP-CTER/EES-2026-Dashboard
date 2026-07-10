import json
import pandas as pd
import plotly.express as px

def create_vietnam_map():
    # Load GeoJSON
    with open('data/vn-provinces.json', 'r', encoding='utf-8') as f:
        vn_geojson = json.load(f)

    # Extract all province names
    provinces = []
    for feature in vn_geojson['features']:
        provinces.append(feature['properties']['Ten'])

    df = pd.DataFrame({'province_name': provinces})

    # List of merged provinces to highlight
    merged_provinces = [
        'Tỉnh Nam Định', 'Tỉnh Hà Nam', 'Tỉnh Ninh Bình', 'Tỉnh Thanh Hóa',
        'Tỉnh Nghệ An', 'Tỉnh Hà Tĩnh', 'Tỉnh Thừa Thiên Huế', 'Thành phố Đà Nẵng',
        'Tỉnh Quảng Nam', 'Tỉnh Khánh Hòa', 'Tỉnh Bình Thuận', 'Tỉnh Tây Ninh',
        'Tỉnh Đồng Tháp', 'Tỉnh Bắc Giang', 'Tỉnh Quảng Ninh', 'Thành phố Hồ Chí Minh',
        'Tỉnh Tiền Giang', 'Tỉnh Bến Tre', 'Tỉnh Kiên Giang', 'Tỉnh Cà Mau'
    ]

    # Assign colors: Highlight merged ones, others are standard
    def get_color(prov):
        return 1 if prov in merged_provinces else 0

    def get_status(prov):
        return "Đã Sáp Nhập" if prov in merged_provinces else "Khu Vực Chuẩn"

    df['is_merged'] = df['province_name'].apply(get_color)
    df['Trạng thái'] = df['province_name'].apply(get_status)
    df['Tỉnh/Thành'] = df['province_name'].str.replace('Tỉnh ', '').str.replace('Thành phố ', '')

    # Create Choropleth Map using plotly express
    fig = px.choropleth(
        df,
        geojson=vn_geojson,
        featureidkey="properties.Ten",
        locations="province_name",
        color="is_merged",
        color_continuous_scale=[(0, '#0A1F44'), (1, '#FF5200')],
        hover_name="Tỉnh/Thành",
        hover_data={"is_merged": False, "province_name": False, "Trạng thái": True},
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False, # Hide background map, country borders, oceans etc.
        bgcolor="rgba(0,0,0,0)"
    )

    fig.update_layout(
        height=700,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        dragmode=False,
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Exo 2, sans-serif"
        )
    )

    return fig
