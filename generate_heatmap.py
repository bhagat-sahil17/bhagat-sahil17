import json
import datetime
import os

# Define a minimal SVG stylesheet for consistency across GitHub's themes
STYLESHEET = """
<style>
  rect { rx: 2px; ry: 2px; }
  text {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 9px;
    fill: #57606a;
  }
  .month-label { font-weight: 600; font-size: 10px; }
  .day-marker { font-size: 8px; font-weight: 200;}
</style>
"""

# Load habit data from growth.json
DATA_FILE = 'growth.json'
OUTPUT_FILE = 'heatmap.svg'

def generate_svg():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {DATA_FILE}")
            return

    categories = list(data.get('categories', {}).keys())
    total_categories = len(categories)
    history = data.get('history', {})

    # Heatmap Layout Configuration
    SQUARE_SIZE = 12
    GAP = 3
    HEADER_HEIGHT = 30 # Taller header for month labels
    LEFT_MARGIN = 35   # Wide left margin for day markers
    WEEKS = 52
    DAYS_PER_WEEK = 7

    width = LEFT_MARGIN + WEEKS * (SQUARE_SIZE + GAP) + 10
    height = HEADER_HEIGHT + DAYS_PER_WEEK * (SQUARE_SIZE + GAP) + 10

    # Calculate date ranges ending today
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=(WEEKS * 7 - 1))

    # Fallback to none_color if not provided in JSON
    none_color = data.get('none_color', '#ebedf0')
    all_done_color = data.get('all_done_color', '#ffd700')

    def get_color(date_str):
        completed = history.get(date_str, [])
        if not completed:
            return none_color
        
        # Check if ALL active habits were completed
        unique_completed = set(completed)
        if len(unique_completed) >= total_categories:
            return all_done_color
        
        # Return the color of the first completed task logged
        primary_cat = completed[0]
        cat_info = data.get('categories', {}).get(primary_cat, {})
        return cat_info.get('color', none_color)

    # Build SVG nodes
    svg_nodes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        STYLESHEET,
        f'<rect width="{width}" height="{height}" fill="#ffffff" />'
    ]

    # --- 1. Draw Month Labels (Along the top) ---
    current_date = start_date
    last_month = None
    for week in range(WEEKS):
        # Calculate the start date of this week column
        week_start_date = start_date + datetime.timedelta(days=week * 7)
        month_name = week_start_date.strftime('%b') # E.g., 'Jul'

        if month_name != last_month:
            x_pos = LEFT_MARGIN + week * (SQUARE_SIZE + GAP)
            svg_nodes.append(f'<text x="{x_pos}" y="20" class="month-label">{month_name}</text>')
            last_month = month_name

    # --- 2. Draw Day Markers (Along the left) ---
    # We label key days: Mon, Wed, Fri
    day_labels = {0: "Mon", 2: "Wed", 4: "Fri"}
    for day_index, label in day_labels.items():
        y_pos = HEADER_HEIGHT + day_index * (SQUARE_SIZE + GAP) + (SQUARE_SIZE / 2) + 3 # Center text
        svg_nodes.append(f'<text x="5" y="{y_pos}" class="day-marker">{label}</text>')

    # --- 3. Draw the Heatmap Squares ---
    for week in range(WEEKS):
        for day in range(DAYS_PER_WEEK):
            date_str = current_date.strftime('%Y-%m-%d')
            color = get_color(date_str)
            
            x = LEFT_MARGIN + week * (SQUARE_SIZE + GAP)
            y = HEADER_HEIGHT + day * (SQUARE_SIZE + GAP)
            
            # Draw the simple square (interactive hover/title are stripped by GitHub)
            svg_nodes.append(
                f'<rect x="{x}" y="{y}" width="{SQUARE_SIZE}" height="{SQUARE_SIZE}" fill="{color}" />'
            )
            current_date += datetime.timedelta(days=1)

    svg_nodes.append('</svg>')

    # Save SVG
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_nodes))
        print(f"{OUTPUT_FILE} successfully generated with date labels!")
    except IOError as e:
        print(f"Error saving {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    generate_svg()
