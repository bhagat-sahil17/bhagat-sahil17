import json
import datetime

# Load habit data from growth.json
with open('growth.json', 'r') as f:
    data = json.load(f)

categories = list(data['categories'].keys())
total_categories = len(categories)
history = data.get('history', {})

# Layout Config
SQUARE_SIZE = 12
GAP = 3
HEADER_HEIGHT = 25
LEFT_MARGIN = 20
WEEKS = 52
DAYS_PER_WEEK = 7

width = LEFT_MARGIN + WEEKS * (SQUARE_SIZE + GAP) + 10
height = HEADER_HEIGHT + DAYS_PER_WEEK * (SQUARE_SIZE + GAP) + 10

today = datetime.date.today()
start_date = today - datetime.timedelta(days=(WEEKS * 7 - 1))

def get_color(date_str):
    completed = history.get(date_str, [])
    if not completed:
        return data['none_color']
    unique_completed = set(completed)
    if len(unique_completed) >= total_categories:
        return data['all_done_color']
    primary_cat = completed[0]
    return data['categories'].get(primary_cat, {}).get('color', data['none_color'])

# Build SVG
svg_nodes = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<style>rect { rx: 2px; ry: 2px; } text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 9px; fill: #57606a; }</style>',
    f'<rect width="{width}" height="{height}" fill="#ffffff" />'
]

# Add Month Labels above the heatmap
current_date = start_date
last_month = None
for week in range(WEEKS):
    week_start_date = start_date + datetime.timedelta(days=week * 7)
    month_name = week_start_date.strftime('%b')
    if month_name != last_month:
        x_pos = LEFT_MARGIN + week * (SQUARE_SIZE + GAP)
        svg_nodes.append(f'<text x="{x_pos}" y="15">{month_name}</text>')
        last_month = month_name

# Add Squares
for week in range(WEEKS):
    for day in range(DAYS_PER_WEEK):
        date_str = current_date.strftime('%Y-%m-%d')
        color = get_color(date_str)
        x = LEFT_MARGIN + week * (SQUARE_SIZE + GAP)
        y = HEADER_HEIGHT + day * (SQUARE_SIZE + GAP)
        
        svg_nodes.append(f'<rect x="{x}" y="{y}" width="{SQUARE_SIZE}" height="{SQUARE_SIZE}" fill="{color}" />')
        current_date += datetime.timedelta(days=1)

svg_nodes.append('</svg>')

with open('heatmap.svg', 'w') as f:
    f.write('\n'.join(svg_nodes))
