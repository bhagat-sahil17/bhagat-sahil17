import json
import datetime

# Load habit data
with open('growth.json', 'r') as f:
    data = json.load(f)

categories = list(data['categories'].keys())
total_categories = len(categories)
history = data.get('history', {})

# Heatmap Layout Configuration
SQUARE_SIZE = 12
GAP = 3
HEADER_HEIGHT = 20
LEFT_MARGIN = 20
WEEKS = 52
DAYS_PER_WEEK = 7

width = LEFT_MARGIN + WEEKS * (SQUARE_SIZE + GAP) + 10
height = HEADER_HEIGHT + DAYS_PER_WEEK * (SQUARE_SIZE + GAP) + 10

# Calculate date ranges ending today
today = datetime.date.today()
start_date = today - datetime.timedelta(days=(WEEKS * 7 - 1))

def get_color(date_str):
    completed = history.get(date_str, [])
    if not completed:
        return data['none_color']
    
    # Check if ALL active habits were completed
    unique_completed = set(completed)
    if len(unique_completed) >= total_categories:
        return data['all_done_color']
    
    # Return the color of the first completed task logged
    primary_cat = completed[0]
    return data['categories'].get(primary_cat, {}).get('color', data['none_color'])

# Build SVG
svg_nodes = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<style>rect { rx: 2px; ry: 2px; }</style>',
    f'<rect width="{width}" height="{height}" fill="#ffffff" />'
]

current_date = start_date
for week in range(WEEKS):
    for day in range(DAYS_PER_WEEK):
        date_str = current_date.strftime('%Y-%m-%d')
        color = get_color(date_str)
        
        x = LEFT_MARGIN + week * (SQUARE_SIZE + GAP)
        y = HEADER_HEIGHT + day * (SQUARE_SIZE + GAP)
        
        svg_nodes.append(
            f'<rect x="{x}" y="{y}" width="{SQUARE_SIZE}" height="{SQUARE_SIZE}" fill="{color}">'
            f'<title>{date_str}: {", ".join(history.get(date_str, ["Rest Day"]))}</title>'
            '</rect>'
        )
        current_date += datetime.timedelta(days=1)

svg_nodes.append('</svg>')

# Save SVG
with open('heatmap.svg', 'w') as f:
    f.write('\n'.join(svg_nodes))

print("heatmap.svg successfully generated!")
