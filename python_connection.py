import serial
import time
import os
from dotenv import load_dotenv
from openai import OpenAI

def gpt_normalize(values):
    prompt = f"""I am going to provide a list of sensor values that were returned from an Arduino.

    I want you to return a score from 0-100; with 0 representing if less energy was saved, and 100 
    representing if more energy was saved. Do NOT return any extraneous text, just simply a number from 0-100.

    {values}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages = [{
            "role": "system",
            "content": prompt,
        }],
    )

    llm_response = response.choices[0].message.content
    return llm_response

if __name__ == '__main__':
    load_dotenv()
    client = OpenAI(os.environ['OPENAI_API_KEY'])
    # Configure the serial connection to the Arduino
    ser = serial.Serial('/dev/cu.usbmodem2101', 9600)  # Update this to match your device
    ser.flushInput()

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Received line: {line}")
            
            # Split the line into parts assuming the format "Photoresistor Value, Motion Sensor Value, Temperature In, Temperature Out"
            parts = line.split(", ")
            dict_vals = dict()
            dict_vals["photoresistor"] = int(parts[0])
            dict_vals["motion_detected"] = int(parts[1])
            dict_vals["temperature_inside"] = int(parts[2])
            dict_vals["temperature_outside"] = int(parts[3])
            
            violet_score = gpt_normalize(dict_vals)
            print(violet_score) # display on LCD
            # Delay for 5 seconds before the next read
            time.sleep(60)