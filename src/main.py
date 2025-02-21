import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from apify import Actor

url = "https://thealamo-keywest.com/wp-json/tribe/views/v2/html"

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Content-Length": "275", 
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://thealamo-keywest.com",
    "Referer": "https://thealamo-keywest.com/events/month/2025-01/",
    "Sec-CH-UA": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

cookies = {
    "sbjs_migrations": "1418474375998%3D1",
    "sbjs_first_add": "fd%3D2025-02-19%2017%3A47%3A57%7C%7C%7Cep%3Dhttps%3A%2F%2Fthealamo-keywest.com%2Fevents%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F",
    "sbjs_current": "typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29",
    "sbjs_first": "typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29",
    "sbjs_udata": "vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F133.0.0.0%20Safari%2F537.36",
    "sbjs_current_add": "fd%3D2025-02-19%2017%3A48%3A10%7C%7C%7Cep%3Dhttps%3A%2F%2Fthealamo-keywest.com%2Fevents%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com%2F",
    "sbjs_session": "pgs%3D11%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fthealamo-keywest.com%2Fevents%2Fmonth%2F"
}

data = {
    "view_data[tribe-bar-date]": "2025-02",
    "url": "https://thealamo-keywest.com/events/month/2025-01/",
    "prev_url": "https://thealamo-keywest.com/events/month/2024-12/",
    "should_manage_url": "true",
    "_tec_view_rest_nonce_primary": "3e0a7a3144",
    "_tec_view_rest_nonce_secondary": ""
}

response = requests.post(url, headers=headers, cookies=cookies, data=data)

async def main():
    async with Actor:
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            ld_json_script = soup.find("script", type="application/ld+json")

            if ld_json_script:
                ld_json_data = json.loads(ld_json_script.string)

                event_data = []
                for event in ld_json_data:
                    start_time = datetime.fromisoformat(event.get("startDate", "")).time().strftime('%H:%M:%S')  
                    end_time = datetime.fromisoformat(event.get("endDate", "")).time().strftime('%H:%M:%S')  
                    date = datetime.fromisoformat(event.get("startDate", "")).date().strftime('%Y-%m-%d')

                    event_info = {
                        "name": event.get("name", ""),
                        "date": date,
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                    event_data.append(event_info)
                for row in event_data:
                    await Actor.push_data(
                        {
                            "name": row.get('name'),
                            "date": row.get('date'),
                            "start_time": row.get('start_time'),
                            "end_time": row.get('end_time'),
                        }
                    )

        else:
            print("Failed to retrieve the page. Status code:", response.status_code)
