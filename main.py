from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
from threading import Event
import re
from datetime import datetime
from datetime import timedelta
import sys

event = Event()

def get_publish_date(released_ago):
    timeNow = datetime.today()
    released_ago = released_ago.lower()
    intValue = int(re.sub("[^0-9]", "", released_ago))
    
    if "minute" in released_ago or "minutes" in released_ago:
        time = timeNow - timedelta(minutes=intValue)
    elif "hour" in released_ago or "hours" in released_ago:
        time = timeNow - timedelta(hours=intValue)
    elif "day" in released_ago or "days" in released_ago:
        time = timeNow - timedelta(days=intValue)
    elif "week" in released_ago or "weeks" in released_ago:
        time = timeNow - timedelta(days=(intValue*7))
    else:
        return timeNow.strftime("%m/%d/%Y, %H:%M:%S")
        
    return time.strftime("%m/%d/%Y, %H:%M:%S")

def get_videos_from_channel(link):
    session = HTMLSession()
    response = session.get(link)
    event.wait(1)
    response.html.render(scrolldown=1, sleep=1)
    page = bs(response.html.html, "html.parser")
    
    vids = page.findAll("a",{"id":"thumbnail"}, href=True)
    
    data = []
    i = 0
    for vid in vids:
        i = i+1
        
        obj = {
            'Title' : vid.parent.findNext("div", {"id" : "details"}).findChild("a", {"id" : "video-title"}).text,
            'Video ID' : vid['href'][9:],
            'Duration' : vid.findChild("span", {"class" : "ytd-thumbnail-overlay-time-status-renderer"}).text.replace('\n', '').replace(' ', ''),
            'Publish Date' : get_publish_date(vid.parent.findNext("div", {"id" : "details"}).findChild("div", {"id" : 'metadata-line'}).findChild("span").findNext("span").text),
            'Thumbnail' : vid.findChild("img", {"id" : "img"}).get('src')
            }
        data.append(obj)
        if i == 10: break
        #event.wait(2)
    
    jsonData = str(data)
    
    try:
        with open("json.txt", "w") as jsonFile:
            jsonFile.write(jsonData)
    except UnicodeEncodeError:
        print(jsonData)
        return
    print(jsonData)
    
if len(sys.argv) == 1:
    print("Please put a link!")
else:
    get_videos_from_channel(sys.argv[1])