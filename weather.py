import requests
import json
import smtplib
import imghdr
from email.message import EmailMessage
import sys

api_configfile_path, email_configfile_path = sys.argv[1:]

with open(api_configfile_path) as data:
    payload = json.loads(data.read())

r = requests.get('https://api.openweathermap.org/data/2.5/forecast', params=payload)
forcast_5day = r.json()
forcast_15hour = forcast_5day['list'][:5] #weather data is in 3 hour incriments, 3hours *5 data points = 15 hours

temps = []
rain_or_snow = []
rain_or_snow_icons = ['09d', '09n', '10d', '10n', '11d', '11n', '13d', '13n']
for forcast_3hour in forcast_15hour:
    temps.append(forcast_3hour['main']['temp'])
    if forcast_3hour['weather'][0]['icon'] in rain_or_snow_icons:
        rain_or_snow.append(forcast_3hour['weather'][0]['icon'])
    
min_temp = min(temps)
if min_temp > 60:
    clothes_style = 'summer'
elif min_temp > 30:
    clothes_style = 'fall/spring'
else:
    clothes_style = 'winter'

with open(email_configfile_path) as data:
    email_config = json.loads(data.read())

msg = EmailMessage()
msg.set_content(clothes_style)
msg['From'] = email_config['from']
msg['To'] = email_config['to']
if rain_or_snow:
    storm_picture_url = 'http://openweathermap.org/img/w/'+rain_or_snow[0]+'.png'
    r2 = requests.get(storm_picture_url)
    img_data = r2.content
    msg.add_attachment(img_data, maintype='image', subtype=imghdr.what(None, img_data))

with smtplib.SMTP('smtp.gmail.com', 587) as s:
    s.ehlo()
    s.starttls()
    s.login(email_config['from'],email_config['pwd'])
    s.send_message(msg)
