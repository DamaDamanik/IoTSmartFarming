from tkinter import *
import random
import queue
import threading
import time
import json
import datetime
import sqlite3
from paho.mqtt import client as mqtt_client

broker 		= '0.tcp.ap.ngrok.io'
port 		= 15380
topic 		= "/FarmTech"
client_id 	= f'python-mqtt-{random.randint(0, 100)}'

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password) #auth service
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

window = Tk()
window.title("MQTT Dashboard")
window.geometry('1000x750') # Width, Height
window.resizable(False,False) # Width, Height
window.configure(bg="white")

# Header image
canvas = Canvas(window, width=1000,height=240)
canvas.place(x=0,y=0)
img = PhotoImage(file="banner.png")
canvas.create_image(0,0,anchor=NW,image=img)

# Display "Temperature" image
canvas2 = Canvas(window,width=500,height=250)
canvas2.place(x=0,y=241)
img2 = PhotoImage(file="temp_img.png")
canvas2.create_image(0,0,anchor=NW,image=img2)
# Label Temperature
temp_label = Label(window,
                 text="",
                 bg="white",
                 fg="black",
                 font=("Helvetica", 55))

# Display "Moisture" image
canvas3 = Canvas(window,width=500,height=250)
canvas3.place(x=501,y=241)
img3 = PhotoImage(file="soil_img.png")
canvas3.create_image(0,0,anchor=NW,image=img3)
# Label Moisture
moist_label = Label(window,
                 text="",
                 bg="white",
                 fg="black",
                 font=("Helvetica", 55))

# Label °C dan %
tempC_label = Label(window, text=" °C", bg="white", fg="black", font=("Helvetica", 55))
tempC_label.place(x=310,y=330)
moistP_label = Label(window, text=" %", bg="white", fg="black", font=("Helvetica", 55))
moistP_label.place(x=810,y=330)

# Display "Kipas" image
canvas4 = Canvas(window,width=500,height=250)
canvas4.place(x=0,y=492)
img4 = PhotoImage(file="kipas_img.png")
canvas4.create_image(0,0,anchor=NW,image=img4)

# Label Kipas
kipas_label = Label(window,
                text="",bg="white",fg="black", font=("Helvetica", 70))
kipas_label.place(x=300, y=620, anchor=CENTER)

# Display "keran" image
canvas5 = Canvas(window,width=500,height=250)
canvas5.place(x=501,y=492)
img5 = PhotoImage(file="keran_img.png")
canvas5.create_image(0,0,anchor=NW,image=img5)

# Label Keran
keran_label = Label(window,
                text="",bg="white",fg="black", font=("Helvetica", 70))
keran_label.place(x=800, y=620, anchor=CENTER)

current_time = datetime.datetime.now()

con = sqlite3.connect("data.sqlite", check_same_thread=False)
cur = con.cursor()

buat_tabel = '''CREATE TABLE IF NOT EXISTS data_farm_tech(
                        time TEXT NOT NULL,
                        temperature TEXT NOT NULL,
                        moisture TEXT NOT NULL,
                        fan TEXT NOT NULL,
                        water_irigration TEXT NOT NULL);'''
try:
    cur.execute(buat_tabel)
    con.commit()
    print("Table created successfully")
except Exception as e:
    print("Error creating table:", e)
    con.rollback()

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global temp_label
        global moist_label
        global kipas_label
        global keran_label
        try:
            _data = json.loads(msg.payload.decode())
            temp = str(_data["parameters"]["temp"])
            temp_label.place(x=250, y=370, anchor=CENTER)
            temp_label.config(text=temp)

            moist = str(_data["parameters"]["moisture"])
            moist_label.place(x=750, y=370, anchor=CENTER)
            moist_label.config(text=moist)
            
            kipas = str(_data["status"]["kipas"])
            kipas_label.config(text=kipas)
            
            keran = str(_data["status"]["keran"])
            keran_label.config(text=keran)
            
            data_sensor_val = (temp, moist, kipas, keran)
            cur.execute(
                "INSERT INTO data_farm_tech ('time',temperature,moisture,fan,water_irigration) VALUES ('{}',?, ?, ?, ?);".format(current_time), data_sensor_val)
            con.commit()
            
        except json.decoder.JSONDecodeError as e:
            print("Error parsing JSON:", e)
        except KeyError as e:
            print("Error accessing data:", e)
            print("Make sure the data has the correct structure: {'parameters': {'temp': <value>}}")
        except Exception as e:
            print("Unexpected error:", e)

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()
    time.sleep(1)  # add delay here
    window.mainloop()
    client.loop_stop()

if __name__ == '__main__':
    run()