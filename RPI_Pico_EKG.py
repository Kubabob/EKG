import network
import socket
from utime import sleep, time, sleep_ms
import machine
from machine import ADC, Pin


ssid = #podaj nazwe sieci wifi
password = #podaj haslo sieci wifi

def connect():
    '''
    Retruns connected IP address
    Connects to predefined ssid port with predefined password
    '''
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip
    


def reScale(value, min, max, nMin, nMax):
    return int(((value - min)/(max - min)) * (nMax-nMin) + nMin)

try:
    ip = connect()
    connection = socket.socket()
    connection.connect(socket.getaddrinfo('ip', 80)[0][-1])
 
    adc = ADC(26)
    while True:
        heartValue = reScale(adc.read_u16(), 0, 65535, 1000, 9999)
        connection.send(str(heartValue).encode())
        sleep_ms(15)

except KeyboardInterrupt:
    connection.close()
    machine.reset()    
