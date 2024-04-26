# Authored by Anish Susarla

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import imaplib
import email
from email.header import decode_header
import ssl
import os
import serial
import openmeteo_requests
import requests
import requests_cache
import pandas as pd
from retry_requests import retry


if __name__ == '__main__':
    load_dotenv()
    ssl._create_default_https_context = ssl._create_unverified_context
    # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('clean-slates-fd056ca1fe08.json', scope)
    # client = gspread.authorize(creds)
    # sheet_url = 'https://docs.google.com/spreadsheets/d/11j3hRZytEQmprgiCXk_RkGsEUcFYFAieZd_rXW2ojNk/edit?usp=drive_link'
    # sheet = client.open_by_url(sheet_url).sheet1
    # values = sheet.get_all_values()

    ser = serial.Serial('/dev/cu.usbmodem1101', 9600) 
    ser.flushInput()
    ser2 = serial.Serial('/dev/cu.usbmodem101', 9600) 
    ser2.flushInput()
    min_energy_saved = 0
    IMAP_SERVER = 'imap.outlook.com'
    EMAIL = os.environ["FROM_EMAIL"]
    PASSWORD = os.environ["FROM_PWD"]
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('INBOX')
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    latitude = 40.72
    longitude = -74.00

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "precipitation", "rain"],
        "temperature_unit": "fahrenheit",
        "forecast_days": 1
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_precipitation = current.Variables(1).Value()
    current_rain = current.Variables(2).Value()
    idealTemp = 65

    current_time = datetime.now()
    curr_classroom = "KMC 5-90"
    day_of_week = current_time.weekday()
    days = ["M", "T", "W", "H", "F", "S", "U"]
    day_name = days[day_of_week]
    formatted_time = current_time.strftime("%H:%M")
    # MAKE EMPTY LATER
    dict_class_times = {'KMC 5-90': [('11:00', '12:15', 'M,T,H'), ('14:00', '15:15', 'M,W,F')]}

    # for row in values:
    #     tuple_vals = (row[1], row[2], row[3])
    #     if row[0] not in dict_class_times: dict_class_times[row[0]] = [tuple_vals]
    #     else: dict_class_times[row[0]].append(tuple_vals)

    while True:
        for key in dict_class_times:
            outer_break = False
            if key == curr_classroom:
                for val in dict_class_times[key]:
                    if formatted_time >= val[0] and formatted_time <= val[1]: # class in session
                        outer_break = True
                        break
                if outer_break == True: 
                    print("Class still in session! Lights will remain on.")
                    time.sleep(60)
                    break
        if outer_break == False: # class not in session. code logic can resume.
            # now, must check if there is motion (class can still be in use outside class times)
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                if "yes" in line.lower():
                    print("Motion Detected in classroom. Rechecking in 60 seconds.")
                    time.sleep(60)
                    break
                else: # classroom not in use, carry on with code logic.
                    ldrVal = int(line[line.find("ue:") + 4:line.find(";")])
                    if ldrVal < 300: # this most probably means that the light is already off, so no action needs to be taken
                        print("Looks like your light is already off!")
                        min_energy_saved += 1
                        time.sleep(60)
                        break
                    else: # continue with code logic:
                        indoorTemp = float(line[line.find("re:") + 4:line.find(",")])
                        if indoorTemp > current_temperature_2m and indoorTemp > idealTemp: # only close blinds if temperature outside above temperature inside
                            message = Mail(
                                from_email='flipprlights@outlook.com', # replace from_email asap
                                to_emails='anish.susarla@gmail.com', # who should email get sent to?
                                subject='Silver Shades Notification',
                                html_content='<strong>Your blinds are about to be rolled up. Please respond no to the subject line of this email within 60 seconds if you would like us to stop.</strong>')
                            try:
                                sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
                                response = sg.send(message)
                            except Exception as e:
                                print("An error occurred:", e)
                            print("sent email")

                            for i in range(5): # change to 60.
                                status, data = mail.search(None, 'ALL')
                                break_again = False
                                for num in data[0].split():
                                    status, raw_email = mail.fetch(num, '(RFC822)')
                                    email_message = email.message_from_bytes(raw_email[0][1])
                                    subject = decode_header(email_message['Subject'])[0][0]
                                    sender = email.utils.parseaddr(email_message['From'])[1]
                                    date_sent = email_message['Date']
                                    
                                    if "Silver Shades Notification" in subject and "no" in subject.lower():
                                        print("Blinds will not be rolled up.")
                                        # time.sleep(30)
                                        break_again = True
                                        break
                                if break_again == True: break 
                                ser.write(b'H')
                                message = Mail(
                                    from_email='flipprlights@outlook.com', # replace from_email asap
                                    to_emails='anish.susarla@gmail.com', # who should email get sent to?
                                    subject='Silver Shades Notification',
                                    html_content='<strong>Your blinds are now rolled up. Thank you for using Silver Shades.</strong>')
                                try:
                                    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
                                    response = sg.send(message)
                                except Exception as e:
                                    print("An error occurred:", e)
                                print("sent email")    
                                time.sleep(5)
                            
    # # print(dict_class_times)
