#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import time
import logging
from PIL import Image, ImageDraw, ImageFont
import netifaces
import requests
import signal

def signal_handler(sig, frame):
    print('Gracefully shutting down')
    logging.info("Clear...")
    epd.init()
    epd.Clear()
    logging.info("Goto Sleep...")
    epd.sleep()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in7_V2

last_update_time = time.time()
last_ip_info = {}

def has_network_info_changed(current_info):
    global last_ip_info
    return current_info != last_ip_info

def update_display(ip_addresses, public_ip):
    global last_update_time, last_ip_info

    draw.rectangle((0, 0, epd.height, epd.width), fill=255)
    draw.text((10, 0), 'Pub: ' + public_ip, font=font, fill=0)

    y = 30
    for interface, ip in ip_addresses.items():
        draw.text((10, y), f'{interface}: {ip}', font=font, fill=0)
        y += 30

    rotated_Himage = Himage.rotate(180)
    epd.display(epd.getbuffer(rotated_Himage))

    last_update_time = time.time()
    last_ip_info = ip_addresses.copy()

def get_all_ip_addresses():
    ip_addresses = {}
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        logging.info(interface)
        if interface == "lo" or interface.startswith('v') or interface.startswith('docker'):
            continue
        addr = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addr:
            ip_addresses[interface] = addr[netifaces.AF_INET][0]['addr']
        else:
            ip_addresses[interface] = 'No IP'
    return ip_addresses

def get_public_ip():
    try:
        res = requests.get('https://ipinfo.io/ip')
        ip = res.text.strip()
    except:
        ip = 'Unavailable'
    return ip

try:
    logging.basicConfig(level=logging.DEBUG)
    logging.info("epd2in7 Demo")

    epd = epd2in7_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.height, epd.width), 255)  
    draw = ImageDraw.Draw(Himage)
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

    while True:
        current_time = time.time()
        ip_addresses = get_all_ip_addresses()
        public_ip = get_public_ip()

        if has_network_info_changed(ip_addresses) or (current_time - last_update_time) > 150:
            update_display(ip_addresses, public_ip)

        time.sleep(10)

except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    logging.info("Clear...")
    epd.init()   
    epd.Clear()
    logging.info("Goto Sleep...")
    epd.sleep()
    exit()
