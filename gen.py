from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SIZE = 1024
MARGIN = 24
CONTENT = SIZE - 2 * MARGIN
PAPER = (246, 241, 229)
INK = (23, 35, 59)
NAVY = (22, 50, 79)
RED = (179, 32, 44)
SLATE = (52, 61, 78)
GOLD = (198, 158, 66)
SEA = (203, 221, 228)
TAN = (226, 210, 175)
WHITE = (255, 255, 255)
GREY = (118, 122, 130)

FONT_PATHS = {
    "serif_cond_bold": [
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBold.ttf",
    ],
    "serif_cond_bitalic": [
        "/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBoldItalic.ttf",
    ],
    "serif_bold": ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"],
    "sans_bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}


def font(kind, size):
    for path in FONT_PATHS[kind]:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    raise FileNotFoundError(f"No installed font available for {kind}")


def text_width(draw, text, face):
    return draw.textlength(text, font=face)


def wrap_text(draw, text, face, width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if text_width(draw, candidate, face) <= width:
            current = candidate
        else:
            if not current:
                raise ValueError(f"Word does not fit text box: {word!r}")
            lines.append(current)
            current = word
            if text_width(draw, current, face) > width:
                raise ValueError(f"Word does not fit text box: {word!r}")
    if current:
        lines.append(current)
    return lines


def draw_block(draw, text, xy, width, height, face, color, leading, align="left"):
    lines = wrap_text(draw, text, face, width)
    line_boxes = [draw.textbbox((0, 0), line, font=face, anchor="lt") for line in lines]
    measured_width = max((box[2] - box[0] for box in line_boxes), default=0)
    measured_height = sum(max(leading, box[3] - box[1]) for box in line_boxes)
    if measured_width > width or measured_height > height:
        raise ValueError(
            f"Text block does not fit: {text!r} is {measured_width}x{measured_height}, "
            f"box is {width}x{height}"
        )
    x, y = xy
    for line, box in zip(lines, line_boxes):
        line_width = box[2] - box[0]
        line_x = x + (width - line_width) / 2 if align == "center" else x
        draw.text((line_x, y), line, font=face, fill=color, anchor="lt")
        y += leading
    return len(lines), measured_height


def draw_centered(draw, text, center_x, y, face, color):
    bounds = draw.textbbox((0, 0), text, font=face, anchor="lt")
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if width > CONTENT:
        raise ValueError(f"Centered text is too wide: {text!r}")
    draw.text((center_x - width / 2, y), text, font=face, fill=color, anchor="lt")
    return y + height


def panel_bounds(panel):
    x, y, width, height = panel
    return x + 8, y + 8, x + width - 8, y + height - 8


def check_art_bounds(panel, bounds):
    left, top, right, bottom = panel_bounds(panel)
    x1, y1, x2, y2 = bounds
    if x1 < left or y1 < top or x2 > right or y2 > bottom:
        raise ValueError(f"Illustration element {bounds} crosses panel clearance {panel_bounds(panel)}")


def art_rect(draw, panel, box, fill, outline=INK, width=1):
    check_art_bounds(panel, box)
    draw.rectangle(box, fill=fill, outline=outline, width=width)


def art_ellipse(draw, panel, box, fill, outline=INK, width=1):
    check_art_bounds(panel, box)
    draw.ellipse(box, fill=fill, outline=outline, width=width)


def art_polygon(draw, panel, points, fill, outline=INK, width=1):
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    check_art_bounds(panel, (min(xs), min(ys), max(xs), max(ys)))
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=width, joint="curve")


def art_line(draw, panel, points, fill=INK, width=1):
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    pad = (width + 1) / 2
    check_art_bounds(panel, (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad))
    draw.line(points, fill=fill, width=width, joint="curve")


def art_arc(draw, panel, box, start, end, fill=INK, width=2):
    pad = (width + 1) / 2
    check_art_bounds(panel, (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad))
    draw.arc(box, start, end, fill=fill, width=width)


def begin_panel(draw, panel, interior):
    x, y, width, height = panel
    draw.rectangle((x, y, x + width - 1, y + height - 1), fill=interior, outline=INK, width=1)


def draw_hero_art(draw, panel):
    x, y, width, height = panel
    left, top, right, bottom = panel_bounds(panel)
    horizon = y + int(height * 0.68)
    art_rect(draw, panel, (left, top, right, bottom), (213, 178, 157))
    art_rect(draw, panel, (left + 1, top + 1, right - 1, y + int(height * 0.53)), (236, 177, 139))
    art_ellipse(draw, panel, (x + width - 156, y + 22, x + width - 108, y + 70), GOLD)
    skyline = [
        (x + 38, horizon - 33, x + 102, horizon),
        (x + 111, horizon - 52, x + 171, horizon),
        (x + 180, horizon - 27, x + 251, horizon),
        (x + width - 254, horizon - 45, x + width - 188, horizon),
        (x + width - 178, horizon - 29, x + width - 111, horizon),
        (x + width - 103, horizon - 38, x + width - 39, horizon),
    ]
    for box in skyline:
        art_rect(draw, panel, box, NAVY)
    for center_x, base in ((x + 292, horizon), (x + width - 302, horizon)):
        trunk = [
            (center_x - 3, base), (center_x + 3, base),
            (center_x + 10, y + 34), (center_x + 5, y + 31),
        ]
        art_polygon(draw, panel, trunk, INK)
        crown = (center_x + 7, y + 34)
        for dx, dy in ((-27, -13), (-17, -22), (-4, -24), (12, -22), (25, -13)):
            art_line(draw, panel, [crown, (center_x + dx, y + 25 + dy // 3)], INK, 4)
    road_top = horizon + 3
    art_rect(draw, panel, (left + 1, road_top, right - 1, bottom), (48, 54, 68))
    for lane_x in (x + 110, x + 318, x + 548, x + 784):
        art_rect(draw, panel, (lane_x, road_top + 13, lane_x + 56, road_top + 15), TAN, TAN)
    car_y = y + height - 50
    car = [
        (x + 438, car_y + 13), (x + 458, car_y - 2), (x + 516, car_y - 2),
        (x + 540, car_y + 13), (x + 560, car_y + 17), (x + 560, car_y + 27),
        (x + 432, car_y + 27), (x + 432, car_y + 18),
    ]
    art_polygon(draw, panel, car, RED)
    art_ellipse(draw, panel, (x + 451, car_y + 21, x + 469, car_y + 39), INK)
    art_ellipse(draw, panel, (x + 523, car_y + 21, x + 541, car_y + 39), INK)
    art_polygon(
        draw, panel,
        [(x + 463, car_y + 10), (x + 472, car_y + 1), (x + 510, car_y + 1), (x + 523, car_y + 10)],
        SEA,
    )


def draw_court_art(draw, panel):
    x, y, width, height = panel
    mid = x + width // 2
    floor = y + height - 13
    for column_x in (x + 38, x + width - 61):
        art_rect(draw, panel, (column_x, y + 22, column_x + 22, floor - 12), TAN)
        art_rect(draw, panel, (column_x - 6, y + 17, column_x + 28, y + 22), WHITE)
        art_rect(draw, panel, (column_x - 5, floor - 12, column_x + 27, floor - 7), WHITE)
        for groove in (column_x + 7, column_x + 14):
            art_line(draw, panel, [(groove, y + 27), (groove, floor - 17)], GOLD)
    art_rect(draw, panel, (mid - 4, y + 25, mid + 4, floor - 7), NAVY)
    art_rect(draw, panel, (mid - 72, y + 21, mid + 72, y + 27), GOLD)
    art_ellipse(draw, panel, (mid - 5, y + 17, mid + 5, y + 27), GOLD)
    for pan_x in (mid - 52, mid + 52):
        art_line(draw, panel, [(pan_x, y + 27), (pan_x - 12, y + 48)], INK)
        art_line(draw, panel, [(pan_x, y + 27), (pan_x + 12, y + 48)], INK)
        art_line(draw, panel, [(pan_x - 12, y + 48), (pan_x + 12, y + 48)], INK)
        art_polygon(
            draw, panel,
            [(pan_x - 22, y + 49), (pan_x + 22, y + 49), (pan_x + 16, y + 59), (pan_x - 16, y + 59)],
            GOLD,
        )
    art_rect(draw, panel, (mid - 41, floor - 7, mid + 41, floor - 2), NAVY)


def draw_summit_art(draw, panel):
    x, y, width, height = panel
    left, top, right, bottom = panel_bounds(panel)
    water_top = y + height - 22
    art_rect(draw, panel, (left, water_top, right, bottom), SEA)
    for offset, building_width, building_height in ((82, 30, 27), (124, 24, 36), (157, 35, 22), (300, 29, 31), (344, 31, 25)):
        bx = x + offset
        art_rect(draw, panel, (bx, water_top - building_height, bx + building_width, water_top), (83, 112, 130))
        for window_y in range(water_top - building_height + 6, water_top - 5, 8):
            art_rect(draw, panel, (bx + 6, window_y, bx + building_width - 6, window_y + 2), GOLD, GOLD)
    flag_y = y + 10
    flag_h = 31
    pole_bottom = bottom - 4
    flags = ((x + 49, "china"), (x + width // 2 - 29, "us"), (x + width - 106, "russia"))
    for flag_x, kind in flags:
        art_line(draw, panel, [(flag_x, flag_y + 1), (flag_x, pole_bottom)], INK, 2)
        if kind == "china":
            flag_w = 50
            art_rect(draw, panel, (flag_x + 2, flag_y, flag_x + flag_w, flag_y + flag_h), RED)
            art_ellipse(draw, panel, (flag_x + 8, flag_y + 6, flag_x + 15, flag_y + 13), GOLD, GOLD)
            for sx, sy in ((21, 5), (25, 10), (24, 17), (18, 20)):
                art_ellipse(draw, panel, (flag_x + sx, flag_y + sy, flag_x + sx + 3, flag_y + sy + 3), GOLD, GOLD)
        elif kind == "us":
            flag_w = 56
            art_rect(draw, panel, (flag_x + 2, flag_y, flag_x + flag_w, flag_y + flag_h), WHITE)
            stripe_h = flag_h / 7
            for stripe in range(0, 7, 2):
                sy = flag_y + int(stripe * stripe_h)
                ey = flag_y + int((stripe + 1) * stripe_h)
                art_rect(draw, panel, (flag_x + 2, sy, flag_x + flag_w, ey), RED, RED)
            art_rect(draw, panel, (flag_x + 2, flag_y, flag_x + 25, flag_y + 16), NAVY)
            for sy in (flag_y + 4, flag_y + 9, flag_y + 13):
                for sx in (flag_x + 7, flag_x + 14, flag_x + 20):
                    art_ellipse(draw, panel, (sx, sy, sx + 2, sy + 2), WHITE, WHITE)
        else:
            flag_w = 52
            art_rect(draw, panel, (flag_x + 2, flag_y, flag_x + flag_w, flag_y + 10), WHITE)
            art_rect(draw, panel, (flag_x + 2, flag_y + 10, flag_x + flag_w, flag_y + 21), (48, 91, 155))
            art_rect(draw, panel, (flag_x + 2, flag_y + 21, flag_x + flag_w, flag_y + flag_h), RED)


def draw_capitol_art(draw, panel):
    x, y, width, height = panel
    mid = x + width // 2
    base = y + height - 10
    dome_cx = mid
    dome_cy = y + 28
    radius_x = 62
    radius_y = 19
    points = [(dome_cx - radius_x, dome_cy)]
    for step in range(13):
        angle = pi - pi * step / 12
        points.append((dome_cx + radius_x * cos(angle), dome_cy - radius_y * sin(angle)))
    points.append((dome_cx + radius_x, dome_cy))
    art_polygon(draw, panel, points, TAN)
    art_rect(draw, panel, (mid - 5, y + 8, mid + 5, y + 13), GOLD)
    art_rect(draw, panel, (mid - 54, dome_cy + radius_y - 1, mid + 54, dome_cy + radius_y + 5), WHITE)
    for column_x in (mid - 48, mid - 24, mid, mid + 24, mid + 48):
        art_rect(draw, panel, (column_x - 3, dome_cy + radius_y + 6, column_x + 3, base - 15), NAVY)
    art_rect(draw, panel, (mid - 67, base - 15, mid + 67, base - 10), TAN)
    art_rect(draw, panel, (mid - 80, base - 10, mid + 80, base - 5), NAVY)
    art_rect(draw, panel, (mid - 96, base - 5, mid + 96, base), INK)


def draw_cyclone_art(draw, panel):
    x, y, width, height = panel
    left, top, right, bottom = panel_bounds(panel)
    sea_top = y + height - 22
    art_rect(draw, panel, (left, sea_top, right, bottom), SEA)
    cx, cy = x + width // 2, y + 35
    spiral = []
    for step in range(97):
        angle = step * (4 * pi / 96)
        radius = 2 + step * (20 / 96)
        spiral.append((cx + radius * cos(angle), cy + radius * sin(angle)))
    art_line(draw, panel, spiral, NAVY, 2)
    art_ellipse(draw, panel, (cx - 3, cy - 3, cx + 3, cy + 3), RED)
    for dx in (-122, -76, -30, 24, 78, 124):
        start_x = cx + dx
        art_line(draw, panel, [(start_x, y + 10), (start_x - 18, sea_top - 4)], NAVY, 2)
    wave = [
        (x + 40, sea_top + 11), (x + 126, sea_top + 11), (x + 196, sea_top + 10),
        (x + 218, sea_top + 7), (x + 238, sea_top + 4), (x + 258, sea_top + 7),
        (x + 278, sea_top + 10), (x + 356, sea_top + 11), (x + 418, sea_top + 11),
    ]
    art_line(draw, panel, wave, NAVY, 2)


STORIES = [
    {
        "num": "1", "region": "NORTH AMERICA", "beat": "GAMES",
        "headline": "Grand Theft Auto VI launches worldwide",
        "deck": "After a 13-year wait, Grand Theft Auto VI begins its global rollout; players return to Vice City.",
        "art": draw_hero_art,
    },
    {
        "num": "2", "region": "THE HAGUE", "beat": "WORLD COURT",
        "headline": "World Court rules on Myanmar genocide case",
        "deck": "The world court delivers its judgment today on whether Myanmar committed genocide against the Rohingya.",
        "art": draw_court_art,
    },
    {
        "num": "3", "region": "ASIA", "beat": "DIPLOMACY",
        "headline": "Trump, Xi and Putin meet in Shenzhen",
        "deck": "Trump, Xi and Putin meet in Shenzhen on the sidelines of the APEC summit; nuclear cuts and the US war with Iran on the agenda.",
        "art": draw_summit_art,
    },
    {
        "num": "4", "region": "UNITED STATES", "beat": "POLITICS",
        "headline": "Democrats nominate Jeffries for Speaker",
        "deck": "Democrats nominate Hakeem Jeffries for Speaker of the House; he would be the first African-American Speaker.",
        "art": draw_capitol_art,
    },
    {
        "num": "5", "region": "SOUTH ASIA", "beat": "WEATHER",
        "headline": "Cyclone Akvan bears down on India's east coast",
        "deck": "Cyclone Akvan bears down on India's east coast, expected to cross between Machilipatnam and Puri.",
        "art": draw_cyclone_art,
    },
]


def measure_card(draw, story, width, panel_height, headline_size, deck_size, heading_leading, deck_leading):
    heading_font = font("serif_cond_bold", headline_size)
    deck_font = font("sans", deck_size)
    heading_lines = wrap_text(draw, story["headline"], heading_font, width)
    deck_lines = wrap_text(draw, story["deck"], deck_font, width)
    heading_height = len(heading_lines) * heading_leading
    deck_height = len(deck_lines) * deck_leading
    content_height = 7 + 16 + 3 + heading_height + 3 + deck_height
    return panel_height + content_height, heading_lines, deck_lines


def draw_story(draw, story, x, y, width, panel_height, headline_size, deck_size, heading_leading, deck_leading):
    height, heading_lines, deck_lines = measure_card(
        draw, story, width, panel_height, headline_size, deck_size, heading_leading, deck_leading
    )
    panel = (x, y, width, panel_height)
    story["art"](draw, panel)
    kicker_y = y + panel_height + 7
    number_face = font("sans_bold", 13)
    number = f"{story['num']}"
    draw.text((x, kicker_y), number, font=number_face, fill=RED, anchor="lt")
    number_width = text_width(draw, number, number_face)
    kicker = f"{story['region']} · {story['beat']}"
    draw.text((x + number_width + 7, kicker_y), kicker, font=number_face, fill=INK, anchor="lt")
    kicker_bounds = draw.textbbox((0, 0), kicker, font=number_face, anchor="lt")
    if number_width + 7 + kicker_bounds[2] - kicker_bounds[0] > width:
        raise ValueError(f"Story kicker does not fit: {kicker!r}")
    heading_y = kicker_y + 19
    draw_block(
        draw, story["headline"], (x, heading_y), width, len(heading_lines) * heading_leading,
        font("serif_cond_bold", headline_size), INK, heading_leading,
    )
    deck_y = heading_y + len(heading_lines) * heading_leading + 3
    draw_block(
        draw, story["deck"], (x, deck_y), width, len(deck_lines) * deck_leading,
        font("sans", deck_size), SLATE, deck_leading,
    )
    return y + height


def render():
    image = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(image)
    center = SIZE / 2
    kicker_face = font("sans_bold", 13)
    kicker_y = 22
    draw.text((MARGIN, kicker_y), "THE DAY IN WORLD NEWS", font=kicker_face, fill=INK, anchor="lt")
    right_text = "ONE PAGE · FIVE STORIES"
    right_width = text_width(draw, right_text, kicker_face)
    draw.text((SIZE - MARGIN - right_width, kicker_y), right_text, font=kicker_face, fill=INK, anchor="lt")
    masthead_bottom = draw_centered(
        draw, "Thursday 19 November 2026", center, 38, font("serif_cond_bold", 68), INK
    )
    rule_y = masthead_bottom + 5
    draw.line((MARGIN, rule_y, SIZE - MARGIN, rule_y), fill=INK, width=3)
    draw.line((MARGIN, rule_y + 5, SIZE - MARGIN, rule_y + 5), fill=INK, width=1)
    standfirst_y = rule_y + 11
    standfirst_bottom = draw_centered(
        draw, "Every story on this page happened, or was first reported, on this day.",
        center, standfirst_y, font("serif_cond_bitalic", 19), NAVY,
    )
    header_bottom = max(kicker_y + 16, standfirst_bottom)

    hero_top = header_bottom + 7
    hero_bottom = draw_story(draw, STORIES[0], MARGIN, hero_top, CONTENT, 156, 36, 17, 40, 22)
    row1_top = hero_bottom + 11
    draw.line((MARGIN, row1_top - 5, SIZE - MARGIN, row1_top - 5), fill=INK, width=1)
    card_width = (CONTENT - 12) // 2
    row1_bottom = row1_top
    for index, x in ((1, MARGIN), (2, MARGIN + card_width + 12)):
        row1_bottom = max(
            row1_bottom,
            draw_story(draw, STORIES[index], x, row1_top, card_width, 116, 30, 16, 35, 21),
        )
    row2_top = row1_bottom + 11
    draw.line((MARGIN, row2_top - 5, SIZE - MARGIN, row2_top - 5), fill=INK, width=1)
    row2_bottom = row2_top
    for index, x in ((3, MARGIN), (4, MARGIN + card_width + 12)):
        row2_bottom = max(
            row2_bottom,
            draw_story(draw, STORIES[index], x, row2_top, card_width, 88, 28, 16, 33, 21),
        )
    footer_rule_y = row2_bottom + 8
    draw.line((MARGIN, footer_rule_y, SIZE - MARGIN, footer_rule_y), fill=INK, width=1)
    footer_text = "Five stories that defined Thursday 19 November 2026, as reported that day."
    footer_y = footer_rule_y + 7
    draw_block(draw, footer_text, (MARGIN, footer_y), CONTENT, 22, font("sans", 12), GREY, 14)
    footer_end = footer_y + 14

    measurements = {
        "header bottom": header_bottom,
        "hero bottom": hero_bottom,
        "row-2 bottom": row1_bottom,
        "row-3 bottom": row2_bottom,
        "footer end": footer_end,
    }
    budgets = {"header bottom": 175, "hero bottom": 470, "row-2 bottom": 760, "row-3 bottom": 962, "footer end": 1008}
    for label, value in measurements.items():
        if value > budgets[label]:
            raise ValueError(f"{label} {value} exceeds budget {budgets[label]}")
    image.save(ROOT / "entry.png", format="PNG", optimize=True)
    for label, value in measurements.items():
        print(f"{label}: {value}px (budget {budgets[label]}px)")


if __name__ == "__main__":
    render()
