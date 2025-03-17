import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apify import Actor

def convert_time_format(time_str):
    try:
        if '@' in time_str:
            time_str = time_str.split('@')[1].strip()  # Extract just the time part
        time_obj = datetime.strptime(time_str, "%I:%M %p")
    except ValueError as e:
        print(f"Error parsing time: {e}")
        return None
    return time_obj.strftime("%H:%M:%S")

current_date = datetime.now()

current_month_year = current_date.strftime("%Y-%m")

url = f"https://thealamo-keywest.com/events/month/{current_month_year}/"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Referer": "https://thealamo-keywest.com/menu-full-menu/",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

async def main():
    async with Actor:
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        day_cells = soup.find_all("div", class_="tribe-events-calendar-month__day-cell")

        for day_cell in day_cells:
            date_tag = day_cell.find("time", class_="tribe-events-calendar-month__day-date-daynum")
            event_date = date_tag['datetime'] if date_tag else None

            events = day_cell.find_all("article", class_="tribe-events-calendar-month__calendar-event")
            if not events:
                print(f"Date: {event_date} - No events")
                continue

            for event in events:
                title_link = event.find("a", class_="tribe-events-calendar-month__calendar-event-title-link")
                event_name = title_link.text.strip() if title_link else None

                times = event.find_all("time")
                start_time = convert_time_format(times[0].text.strip()) if times and len(times) > 0 else None
                end_time = convert_time_format(times[1].text.strip()) if times and len(times) > 1 else None

                await Actor.push_data(
                    {
                        "name": event_name,
                        "date": event_date,
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )
