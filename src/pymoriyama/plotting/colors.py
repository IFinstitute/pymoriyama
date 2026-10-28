#! python3
import math

import matplotlib.colors as mcolors


def oklch_to_hex(lightness, chroma, hue, alpha=1.):
    """
    OKLCH を HEX カラーコードに変換します。
    lightness (float): Lightness (0.0 - 1.0)
    chroma (float): Chroma (通常 0.0 - 0.4 程度)
    hue (float): Hue (0.0 - 360.0)
    alpha (float): Alpha (0.0 - 1.0)
    """

    # 1. OKLCH -> OKLAB 変換
    # h は度数法(degree)なのでラジアンに変換
    h_rad = hue * (math.pi / 180.0)
    
    L = lightness
    a = chroma * math.cos(h_rad)
    b = chroma * math.sin(h_rad)

    # 2. OKLAB -> Linear RGB 変換
    # OKLab の変換行列係数を使用
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l_ = l_**3
    m_ = m_**3
    s_ = s_**3

    # Linear RGB への変換行列
    r_linear = +4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_
    g_linear = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_
    b_linear = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_

    # 3. Linear RGB -> sRGB (ガンマ補正)
    # 値を 0.0-1.0 にクリップし、sRGB の転送関数を適用
    def transfer_function(x):
        if x <= 0.0031308:
            return 12.92 * x
        else:
            return 1.055 * (x ** (1.0 / 2.4)) - 0.055

    r = transfer_function(max(0.0, min(1.0, r_linear)))
    g = transfer_function(max(0.0, min(1.0, g_linear)))
    b = transfer_function(max(0.0, min(1.0, b_linear)))

    # 4. 0-255 の整数に変換して HEX 文字列化
    r_int = round(r * 255)
    g_int = round(g * 255)
    b_int = round(b * 255)
    a_int = round(alpha * 255)

    return f"#{r_int:02x}{g_int:02x}{b_int:02x}{a_int:02x}"

# ユニバーサルデザイン推奨配色セット
ud_accent = { # アクセントカラー
    "red":    "#ff2800",   # (255, 40, 0)
    "yellow": "#faf500",   # (250, 245, 0)
    "green":  "#35a16b",   # (53, 161, 107)
    "blue":   "#0041ff",   # (0, 65, 255)
    "skyblue":"#66ccff",   # (102, 204, 255)
    "pink":   "#ff99a0",   # (255, 153, 160)
    "orange": "#ff9900",   # (255, 153, 0)
    "purple": "#9a0079",   # (154, 0, 121)
    "brown":  "#663300",   # (102, 51, 0)
}
ud_base = {
    "pink":    "#ffd1d1",  # (255, 209, 209)
    "cream":   "#ffff99",  # (255, 255, 153)
    "lime":    "#cbf266",  # (203, 242, 102)
    "skyblue": "#b4ebfa",  # (180, 235, 250)
    "beige":   "#edc58f",  # (237, 197, 143)
    "green":   "#87e7b0",  # (135, 231, 176)
    "purple":  "#c7b2de",  # (199, 178, 222)
}
ud_achromatic = {
    "white":     "#ffffff",# (255, 255, 255)
    "lightgray": "#c8c8cb",# (200, 200, 203)
    "gray":      "#7f878f",# (127, 135, 143)
    "black":     "#000000",# (0, 0, 0)
}

blue = {
    50:  "#edf0fc",
    100: "#dce0f9",
    200: "#bdc5f4",
    300: "#9aa7ee",
    400: "#7c8ce9",
    500: "#596de3",
    600: "#3a52de",
    700: "#223bce",
    800: "#1c31ab",
    900: "#17288b", # uec_blue
    950: "#0c1446",
}
sky = {
    50:  "#e7f3f8",
    100: "#cbe4f1",
    200: "#9bcce3",
    300: "#67b1d5",
    400: "#3797c6", # sky_blue
    500: "#2d7da4",
    600: "#256484",
    700: "#1c4c64",
    800: "#133444",
    900: "#091820",
    950: "#040c10",
}
cyan = {
    50:  "#dbf8ff",
    100: "#b8f0ff",
    200: "#70e1ff",
    300: "#29d2ff",
    400: "#00afdd", # uec_sub_blue
    500: "#0091b8",
    600: "#007594",
    700: "#005970",
    800: "#003947",
    900: "#001c24",
    950: "#001014",
}
green = {
    50:  "#eefcf5",
    100: "#d9f7e9",
    200: "#b3efd2",
    300: "#8de8bc",
    400: "#67e0a5",
    500: "#45d991",
    600: "#29c77a",
    700: "#21a163",
    800: "#197a4b",
    900: "#0c3b24",
    950: "#061e12",
}
lime = {
    50:  "#ecfbd6",
    100: "#d7f6a8",
    200: "#b1ed55",
    300: "#84cc16",
    400: "#71af13",
    500: "#5f9310",
    600: "#4a730c",
    700: "#395709",
    800: "#273c06",
    900: "#121c03",
    950: "#090e01",
}
yellow = {
    50:  "#fff7db",
    100: "#ffeeb3",
    200: "#ffdf6b",
    300: "#ffce1f",
    400: "#d2a400",
    500: "#ad8700",
    600: "#8a6c00",
    700: "#6b5400",
    800: "#473800",
    900: "#241c00",
    950: "#0f0c00",
}
orange = {
    50:  "#fff3e5",
    100: "#ffe7cc",
    200: "#ffce94",
    300: "#ffb661",
    400: "#ff9f2e",
    500: "#f58400",
    600: "#c16800", #primary
    700: "#8f4d00",
    800: "#613400",
    900: "#2e1900",
    950: "#1a0e00",
}
rust = {
    50:  "#fef3f0",
    100: "#fee3dd",
    200: "#fdc6ba",
    300: "#fbaa98",
    400: "#fa8e75",
    500: "#f97558",
    600: "#f85935",
    700: "#f63c13",
    800: "#dd2f08",
    900: "#6c1704",
    950: "#360c02",
}
red = {
    50:  "#fff0f0",
    100: "#ffdbdb",
    200: "#ffbdbd",
    300: "#ff9999",
    400: "#ff7575",
    500: "#ff5252",
    600: "#ff3333",
    700: "#ff0f0f",
    800: "#ec0000", # primary
    900: "#750000",
    950: "#3d0000",
}
magenta = {
    50:  "#ffe5ff",
    100: "#ffccff",
    200: "#ff94ff",
    300: "#ff61ff",
    400: "#ff29ff",
    500: "#f500f5",
    600: "#c000c0",
    700: "#8f008f",
    800: "#610061",
    900: "#2e002e",
    950: "#1a0019",
}
purple = {
    50:  "#f5f2fc",
    100: "#e8e2f9",
    200: "#d2c6f3",
    300: "#bca9ed",
    400: "#a88ce7",
    500: "#956ee0",
    600: "#824fd7",
    700: "#6c37bb",
    800: "#532992",
    900: "#2e1455",
    950: "#1d0a39",
}


# 色テーマ
white = "#FFFFFF"
uec_blue = blue[900] #17288B
sky_blue = sky[400] #00afdd
uec_skyb = cyan[400]
if_orange = "#C16800"
international_orange = "#ff7500"
my_orange = "#E18F5F"
rose_pink = "#F97B5F"
pptx_purple = "#532992"
digital_primary_black = "#252020"

cmap_blue = mcolors.LinearSegmentedColormap.from_list("UEC", [white, sky_blue, uec_blue])
cmap_orange = mcolors.LinearSegmentedColormap.from_list("IF", [white, if_orange])
cmap_OrWBu = mcolors.LinearSegmentedColormap.from_list("OrWBu", [if_orange, my_orange, white, sky_blue, uec_blue])
colors = ["lightsteelblue", "deepskyblue","royalblue","blue","darkblue"]
cmap_orate = mcolors.ListedColormap(colors)

if __name__ == "__main__":
    # --- 使用例 ---
    hex_val = oklch_to_hex(0.342, 0.163, 267.91)
    print(f"oklch(0.7 0.15 200) -> {hex_val}") 
