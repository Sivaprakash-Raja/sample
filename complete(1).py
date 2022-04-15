from tkinter import *
from tkinter import ttk  
import tkinter as tk
import mysql.connector as msql
import serial
import math
from numpy import log as ln
import serial.tools.list_ports
import functools
import random

ports =serial.tools.list_ports.comports()
serialobj = serial.Serial()
connection = msql.connect(host="localhost", user="root", database="test")
cursor = connection.cursor()
print("db connected")

def calculate(rawtemp,rawhumi):
	
    humi = ((rawhumi/pow(2,16))*125)
    temp = ((rawtemp/pow(2,16))*175.72)

    #print(humi)
    #print(pow(2,16))
    #print(temp)

    cal_hum = 10.3884593392 + ((-0.0001812953*pow(humi,3))+(0.0296632331*pow(humi,2))+(-0.4432939368*humi))
    temp_kelvin = temp + 273.15
    altitude = 300
    pressure_at_station =1031.25 * math.exp((-9.80665*0.0289644*(altitude-0))/(8.31432*temp_kelvin))
    dewpoint = 243.04*(ln(humi/100)+((17.625*temp)/(243.04+temp)))/(17.625-ln(humi/100)-((17.625*temp)/(243.04+temp)))
    vapour_pressure = 6.11*pow(10,((7.5*dewpoint)/(237.3+dewpoint)))*100
    Actual_mixing_ratio = (621.97*(vapour_pressure/100))/(pressure_at_station-vapour_pressure/100)
    saturated_vapour_pressure = 6.11*pow(10,((7.5*temp)/(237.7+temp)))
    saturated_mixing_ratio = 621.97*saturated_vapour_pressure/(pressure_at_station-saturated_vapour_pressure)
    RH = Actual_mixing_ratio/saturated_mixing_ratio *100
    RH_standard = 100*(math.exp((17.625*dewpoint)/(243.04+dewpoint))/math.exp((17.625*25)/(243.04+25)))
    dewpoint_RH = 243.04*(ln(rawhumi/100)+((17.625*temp)/(243.04+temp)))/(17.625-ln(rawhumi/100)-((17.625*temp)/(243.04+temp)))
    RH_standard_raw = 100*(math.exp((17.625*dewpoint_RH)/(243.04+dewpoint_RH))/math.exp((17.625*25)/(243.04+25)))

    value = f'\n Temperature – {temp} \n Humidity Raw - {humi} \n Humidity @ 25°C – {cal_hum}% \n Actual Vapour Pressure – {vapour_pressure}\n RH% - {RH}% \n RH %@ 25°C – {RH_standard}%'

    #print(value)
    return value




window = Tk()
print(type(window))

window.title("HUMIDIFY")
window.configure(width=1700, height=400)
window.configure(bg='lightgray')
window.geometry("800x350")
 

Tx = Text(window, height = 15, width = 45, padx = 10, pady = 10)
Ty = Text(window, height = 15, width = 45, padx = 10, pady = 10)


l1 = Label(window, text = "SENSOR 1 Calculated output")
l1.config(font =("Courier", 11))

l2 = Label(window, text = "SENSOR 2 Calculated output")
l2.config(font =("Courier", 11))
 
# Create an Exit button.
b2 = Button(window, text = "Exit",
            command = window.destroy)

Tx.grid(row=1,column=0)
Ty.grid(row=1,column=1)
l1.grid(row=0,column=0)
l2.grid(row=0,column=1)
b2.grid(row=2,column=1)

'''
def initcomPort(index):
    currentPort = str(ports[index])
    comPortVar = str(currentPort.split(' ')[0])
    print(comPortVar)
    serialobj.port = comPortVar
    serialobj.baudrate = 9600
    serialobj.open()
    
for onePort in ports:
    comButton = Button(window, text=onePort, font=('calibri','13'), height=1, width=45, command = functools.partial(initcomPort, index = ports.index(onePort)))
    comButton.grid(row = 0,column=ports.index(onePort))
'''    
try:
    ser1 = serial.Serial()
    ser1.baudrate = 9600
    ser1.port = 'COM8'
    print(ser1)
    ser1.open()
    
    ser2 = serial.Serial()
    ser2.baudrate = 9600
    ser2.port = 'COM9'
    print(ser2)
    ser2.open()
except:
    print("pass")


def checkserialport():
    if serialobj.isOpen() and serialobj.in_waiting:
        recentPacket = serialobj.readline()
        recentPacketString = recentPacket.decode('utf').rstrip('\n')
        #print(recentPacketString)
        a1=  recentPacketString[:3]
        b1 = recentPacketString[3:]
        print(a1,b1)
        value = calculate(int(a1),int(b1))
        Tx.delete('1.0', END)
        Tx.insert(tk.END, value)

def checkserialport2():
    if serialobj.isOpen() and serialobj.in_waiting:
        recentPacket = serialobj.readline()
        recentPacketString = recentPacket.decode('utf').rstrip('\n')
        a2=  recentPacketString[:3]
        b2 = recentPacketString[3:]
        value2 = calculate(int(a2),int(b2))
        query = "INSERT INTO `sen` (`temp1`, `humn1`,`temp2`, `humn2`) VALUES ('{0}','{1}','{2}','{3}');".format(a1,b1,a2,b2)
        
        cursor.execute(query)
        connection.commit()
        #print("done")
        Ty.delete('1.0', END)
        
        Ty.insert(tk.END, value2)
        
while (ser1.is_open and ser2.is_open ):
    window.update()
    line1 = ser1.readline()
    line1 = line1.decode('utf')
    a1=  line1[:2]
    b1 = line1[2:]
    print(a1,b1)
    
    line2 = ser2.readline()
    line2 = line2.decode('utf')
    a2= line2[:2]
    b2 = line2[2:]

    value1 = calculate(int(a1),int(b1))
    value2 = calculate(int(a2),int(b2))
    query = "INSERT INTO `sen` (`temp1`, `humn1`,`temp2`, `humn2`) VALUES ('{0}','{1}','{2}','{3}');".format(a1,b1,a2,b2)
    cursor.execute(query)
    connection.commit()
    Tx.delete('1.0', END)
    Tx.insert(tk.END, value1)
    Ty.delete('1.0', END)
    Ty.insert(tk.END, value2)

    #value = calculate(int(a1),int(b1))
    
    
else:
    print("pass")



window.mainloop()



