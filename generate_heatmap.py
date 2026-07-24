import json
import datetime
import os

STYLESHEET = """
<style>
  rect { rx: 2px; ry: 2px; }
  text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 9px;
    fill: #57606a;
  }
  .month-label { font-weight: 600; font-size: 10px; }
</style>
"""

DATA_FILE = 'growth.json'
OUTPUT_FILE = 'heatmap.svg'

def generate_svg():
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    categories = list(data.get('categories', {}).keys())
    total_categories = len(categories)
    history = data.get('history', {})

    SQUARE_SIZE = 12
    GAP = 3
    HEADER_HEIGHT = 25
    LEFT_MARGIN = 10
    WEEKS = 52
    DAYS_PER_WEEK = 7

    width = LEFT_MARGIN + WEEKS * (SQUARE_SIZE + GAP) + 10
    height = HEADER_HEIGHT + DAYS_PER_WEEK * (SQUARE_SIZE + GAP) + 10

    today = datetime.date.today()
    
    # Sunday-indexed calendar alignment
    days_since_sunday = (today.weekday() + 1) % 7
    start_date = today - datetime.timedelta(days=days_since_sunday + (WEEKS - 1) * 7)

    none_color = data.get('none_color', '#ebedf0')
    all_done_color = data.get('all_done_color', '#ffd700')

    def get_color(date_str):
        completed = history.get(date_str, [])
        if not completed:
            return none_color
        if len(set(completed)) >= total_categories:
            return all_done_color
        primary_cat = completed[0]
        return data.get('categories', {}).get(primary_cat, {}).get('color', none_color)

    svg_nodes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        STYLESHEET,
        f'<rect width="{width}" height="{height}" fill="#ffffff" />'
    ]

    # --- Month Labels (Top) ---
    current_date = start_date
    last_month = None
    for week in range(WEEKS):
        week_start_date = start_date + datetime.timedelta(days=week * 7)
        month_name = week_start_date.strftime('%b')

        if month_name != last_month:
            x_pos = LEFT_MARGIN + week * (SQUARE_SIZE + GAP)
            svg_nodes.append(f'<text x="{x_pos}" y="15" class="month-label">{month_name}</text>')
            last_month = month_name

    # --- Draw Squares ---
    for week in range(WEEKS):
        for day in range(DAYS_PER_WEEK):
            date_str = current_date.strftime('%Y-%m-%d')
            color = get_color(date_str)
            
            x = LEFT_MARGIN + week * (SQUARE_SIZE + GAP)
            y = HEADER_HEIGHT + day * (SQUARE_SIZE + GAP)
            
            svg_nodes.append(
                f'<rect x="{x}" y="{y}" width="{SQUARE_SIZE}" height="{SQUARE_SIZE}" fill="{color}" />'
            )
            current_date += datetime.timedelta(days=1)

    svg_nodes.append('</svg>')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_nodes))

if __name__ == "__main__":
    generate_svg()
