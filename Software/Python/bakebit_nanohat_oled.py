#!/usr/bin/env python
#
# BakeBit example for the basic functions of BakeBit 128x64 OLED (http://wiki.friendlyarm.com/wiki/index.php/BakeBit_-_OLED_128x64)
#
# The BakeBit connects the NanoPi NEO and BakeBit sensors.
# You can learn more about BakeBit here:  http://wiki.friendlyarm.com/BakeBit
#
# Have a question about this example?  Ask on the forums here:  http://www.friendlyarm.com/Forum/
#
'''
## License

The MIT License (MIT)

BakeBit: an open source platform for connecting BakeBit Sensors to the NanoPi NEO.
Copyright (C) 2016 FriendlyARM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import bakebit_128_64_oled as oled
import bakebit_nanohat_pages as pages
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import time
import sys
import subprocess
import threading
import signal
import os
import socket
import fcntl
import struct
import datetime
import pihole
import current_device

global width
width=128
global height
height=64

global pageCount
pageCount=3
global pageIndex
pageIndex=0
global showPageIndicator
showPageIndicator=True

global pageSleep
pageSleep=120
global pageSleepCountdown
pageSleepCountdown=pageSleep

isPiholeInstalled=False

global enabledMarkerShownSeconds
enabledMarkerShownSeconds=5
global enabledCounter
enabledCounter=0

oled.init()  #initialze SEEED OLED display
oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setHorizontalMode()

global drawing 
drawing = False

image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

global lock
lock = threading.Lock()

def draw_page():
    global drawing
    global image
    global draw
    global oled
    global width
    global height
    global pageCount
    global pageIndex
    global showPageIndicator
    global width
    global height
    global lock
    global pageSleepCountdown
    global enabledMarkerShownSeconds
    global enabledCounter
    global isPiholeInstalled
    
    lock.acquire() # make this injected in the function
    is_drawing = drawing
    page_index = pageIndex
    lock.release()

    if is_drawing:
        return

    #if the countdown is zero we should be sleeping (blank the display to reduce screenburn)
    if pageSleepCountdown == 1:
        oled.clearDisplay()
        pageSleepCountdown = pageSleepCountdown - 1
        return

    if pageSleepCountdown == 0:
        return

    pageSleepCountdown = pageSleepCountdown - 1

    lock.acquire()
    drawing = True
    lock.release()

    # Draw a black filled box to clear the image.            
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    
    # Draw current page indicator
    if showPageIndicator: draw_page_indicator()

    if page_index == pages.CLOCK:
        pages.draw_clock(draw)
    elif page_index == pages.CPU_STATS:
        pages.draw_cpu_stats(draw)
    elif page_index == pages.PIHOLE_STATS:
        pages.draw_pihole_stats(draw)
    elif page_index == pages.REBOOT_YES:
        pages.draw_reboot_yes(draw, width)
    elif page_index == pages.REBOOT_NO:
        pages.draw_reboot_no(draw, width)
    elif page_index == pages.PIHOLE_YES:
        pages.draw_pihole_yes(draw, width)
    elif page_index == pages.PIHOLE_NO:
        pages.draw_pihole_no(draw, width)
    elif page_index == pages.PIHOLE_STATUS:
        pages.draw_pihole_status(draw)
    elif page_index == pages.REBOOTING:
        pages.draw_rebooting(draw)

    oled.drawImage(image)

    lock.acquire()
    drawing = False
    lock.release()

def is_showing_disable_msgbox():
    return pageIndex in pages.YES_PAGES + pages.NO_PAGES

def update_page_index(pi):
    if not isPiholeInstalled and pi in pages.PIHOLE_PAGES:
        pi = pages.CLOCK

    global pageIndex
    lock.acquire()
    pageIndex = pi
    lock.release()

def receive_signal(signum, stack):
    global pageIndex
    global pageSleepCountdown
    global isPiholeInstalled
    global pageSleep

    if pageSleepCountdown == 0:
        image1 = Image.open('pihole.png').convert('1')
        oled.drawImage(image1)
        time.sleep(0.5)

    pageSleepCountdown = pageSleep #user pressed a button, reset the sleep counter

    lock.acquire()
    isPiholeInstalled = pihole.is_installed()
    lock.release()

    if signum == signal.SIGUSR1: # K1 pressed
        if is_showing_disable_msgbox():
            if pageIndex in pages.YES_PAGES:
                update_page_index(pages.PIHOLE_NO if pageIndex == pages.PIHOLE_YES else pages.REBOOT_NO)
            else:
                update_page_index(pages.PIHOLE_YES if pageIndex == pages.PIHOLE_NO else pages.REBOOT_YES)
            # draw_page()
        else:
            update_page_index(pages.CLOCK)
            # draw_page()
    elif signum == signal.SIGUSR2: # K2 pressed
        if is_showing_disable_msgbox():
            if pageIndex == pages.PIHOLE_YES:
                if pihole.status() is pihole.ENABLE:
                    pihole.disable(str(pihole.DISABLE_TIME_SECONDS) + "s")
                else:
                    pihole.enable()
                update_page_index(pages.PIHOLE_STATUS)
                # draw_page()
            elif pageIndex == pages.REBOOT_YES:
                update_page_index(pages.REBOOTING) # restart is handled somewhere else
                # draw_page()
            else:
                update_page_index(pages.CLOCK)
                # draw_page()
        else:
            if isPiholeInstalled:
                if pageIndex == pages.PIHOLE_STATS:
                    update_page_index(pages.CPU_STATS)
                else:
                    update_page_index(pages.PIHOLE_STATS)
            else: update_page_index(pages.CPU_STATS)
            # draw_page()
    elif signum == signal.SIGALRM: # K3 pressed
        if is_showing_disable_msgbox():
            if pageIndex == pages.PIHOLE_NO:
                update_page_index(pages.REBOOT_NO)
            elif pageIndex == pages.REBOOT_NO:
                update_page_index(pages.PIHOLE_NO)
            else: update_page_index(pages.CLOCK)
            # draw_page()
        else:
            if isPiholeInstalled:
                update_page_index(pages.PIHOLE_NO)
            else:
                update_page_index(pages.REBOOT_NO)
            # draw_page()
    
    draw_page()

def draw_page_indicator():
    dotWidth, dotPadding = 4, 2
    dotX = width - dotWidth - 1
    dotTop = (height - pageCount * dotWidth - (pageCount - 1) * dotPadding) / 2
    for i in pages.INDICATOR_PAGES:
        if pageIndex in pages.INDICATOR_PAGES:
            if i == pageIndex:
                draw.rectangle((dotX, dotTop, dotX+dotWidth, dotTop+dotWidth), outline=255, fill=255)
            else:
                draw.rectangle((dotX, dotTop, dotX+dotWidth, dotTop+dotWidth), outline=255, fill=0)
        else:
            draw.rectangle((dotX, dotTop, dotX+dotWidth, dotTop+dotWidth), outline=0, fill=0)
        dotTop=dotTop+dotWidth+dotPadding

image0 = Image.open('pihole.png').convert('1')
oled.drawImage(image0)
time.sleep(2)

signal.signal(signal.SIGUSR1, receive_signal)
signal.signal(signal.SIGUSR2, receive_signal)
signal.signal(signal.SIGALRM, receive_signal)

isPiholeInstalled = pihole.is_installed()

while True:
    try:
        draw_page()

        lock.acquire()
        page_index = pageIndex
        lock.release()

        if page_index == pages.REBOOTING:
            time.sleep(2)
            while True:
                lock.acquire()
                is_drawing = drawing
                lock.release()
                if not is_drawing:
                    lock.acquire()
                    drawing = True
                    lock.release()
                    oled.clearDisplay()
                    break
                else:
                    time.sleep(.1)
                    continue
            time.sleep(1)
            os.system('systemctl reboot')
            break

        time.sleep(1)
    except KeyboardInterrupt:
        break
    except IOError:
        print ("Error")
