from PIL import ImageFont
import current_device
import pihole
import time

CLOCK           = 0
CPU_STATS       = 1
REBOOT_NO       = 2
REBOOT_YES      = 3
REBOOTING       = 4
PIHOLE_STATS    = 5
PIHOLE_YES      = 6
PIHOLE_NO       = 7
PIHOLE_STATUS   = 8

PIHOLE_PAGES = [PIHOLE_STATS, PIHOLE_STATUS, PIHOLE_YES, PIHOLE_NO]
INDICATOR_PAGES = [CLOCK, PIHOLE_STATS, CPU_STATS]
NUMBER_OF_PAGES = len(INDICATOR_PAGES)
YES_PAGES = [REBOOT_YES, PIHOLE_YES]
NO_PAGES = [REBOOT_NO, PIHOLE_NO]

font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14)
fontb14 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14)
fontb24 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24)
smartFont = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 10)

def draw_clock(draw):
    text = time.strftime("%A")
    draw.text((2,2),text,font=font14,fill=255)
    text = time.strftime("%e %b %Y")
    draw.text((2,18),text,font=font14,fill=255)
    text = time.strftime("%X")
    draw.text((2,40),text,font=fontb24,fill=255)

def draw_cpu_stats(draw):
    __draw_stats_screen(draw, [
        'IP: ' + current_device.ip_address(),
        current_device.cpu_load(),
        current_device.ram_usage(),
        current_device.disk_usage(),
        current_device.cpu_temperature()
    ])

def draw_reboot_yes(draw, width):
    __draw_enable_reboot_screen(draw, width, 'Reboot?', True)

def draw_reboot_no(draw, width):
    __draw_enable_reboot_screen(draw, width, 'Reboot?', False)

def draw_rebooting(draw):
    draw.text((2, 2), 'Rebooting', font=fontb14, fill=255)
    draw.text((2, 20), 'Please wait...', font=font11, fill=255)

# Pi-hole Screens
def draw_pihole_stats(draw):
    __draw_stats_screen(draw, [
        'IP: ' + current_device.ip_address(),
        pihole.dns_queries_today(),
        pihole.ads_blocked_today(),
        pihole.ads_percentage_today(),
        pihole.unique_clients()
    ])

def draw_pihole_yes(draw, width):
    title = __get_pihole_status_title()
    __draw_enable_reboot_screen(draw, width, title, True)

def draw_pihole_no(draw, width):
    title = __get_pihole_status_title()
    __draw_enable_reboot_screen(draw, width, title, False)

def draw_pihole_status(draw):
    status = pihole.status()
    if status == pihole.DISABLE:
        draw.text((2, 2), 'Disabled', font=fontb14, fill=255)
    elif status == pihole.ENABLE:
        draw.text((2, 2), 'Enabled', font=fontb14, fill=255)

# Private functions
def __draw_stats_screen(draw, rows):
    left, top = 2, 4
    for row in rows:
        draw.text((left, top), row, font=smartFont, fill=255)
        top += 12

def __draw_enable_reboot_screen(draw, width, title, yes):
    draw.text((2, 2), title, font=fontb14, fill=255)

    if yes: __draw_yes_section(draw, width)
    else:   __draw_no_section(draw, width)

def __draw_yes_section(draw, width):
    draw.rectangle((2,20,width-4,20+16), outline=0, fill=255)
    draw.text((4, 22),  'Yes',  font=font11, fill=0)

    draw.rectangle((2,38,width-4,38+16), outline=0, fill=0)
    draw.text((4, 40),  'No',  font=font11, fill=255)

def __draw_no_section(draw, width):
    draw.rectangle((2,20,width-4,20+16), outline=0, fill=0)
    draw.text((4, 22),  'Yes',  font=font11, fill=255)

    draw.rectangle((2,38,width-4,38+16), outline=0, fill=255)
    draw.text((4, 40),  'No',  font=font11, fill=0)

def __get_pihole_status_title():
    enableText = 'Enable Pihole?'
    disableText = 'Disable ' + str(pihole.DISABLE_TIME_SECONDS/60) + ' min?'
    return disableText if pihole.status() is pihole.ENABLE else enableText