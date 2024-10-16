# # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# # SPDX-License-Identifier: MIT

# # Quick test of TFT FeatherWing (ILI9341) with Feather M0 or M4
# # Will fill the TFT black and put a red pixel in the center, wait 2 seconds,
# # then fill the screen blue (with no pixel), wait 2 seconds, and repeat.
# import time
# import random
# import busio
# import digitalio
# import board
# import subprocess

# from PIL import Image, ImageDraw, ImageFont
# from adafruit_rgb_display.rgb import color565
# from adafruit_rgb_display import ili9341
# import adafruit_dht

# from datetime import datetime


# # Configuratoin for CS and DC pins (these are FeatherWing defaults on M0/M4):
# cs_pin = digitalio.DigitalInOut(board.CE0)
# dc_pin = digitalio.DigitalInOut(board.D22)
# rst_pin = digitalio.DigitalInOut(board.D27)
# temp_pin = digitalio.DigitalInOut(board.D23)
# temp_pin.direction = digitalio.Direction.INPUT
# temp_pin.pull = digitalio.Pull.DOWN

# temp_sensor = adafruit_dht.DHT11(board.D23)

# # Config for display baudrate (default max is 24mhz):
# # BAUDRATE = 24000000
# BAUDRATE = 64000000

# # Setup SPI bus using hardware SPI:
# spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# font = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnBatang.ttf", 24)
# font_title = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnGraphicBold.ttf", 18)

# # Create the ILI9341 display:
# disp = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=rst_pin, baudrate=BAUDRATE, rotation=90)

# if disp.rotation % 180 == 90:
#     height = disp.width  # we swap height/width to rotate it to landscape!
#     width = disp.height
# else:
#     width = disp.width  # we swap height/width to rotate it to landscape!
#     height = disp.height

# image = Image.new("RGB", (width, height))

# draw = ImageDraw.Draw(image)

# TITLE = "간식창고 by 승승장구"
# count = 1

# while True:
#   draw.rectangle((0, 0, width, height), outline=0, fill=0)

#   try:

#       # text_temperature = f"온도 : {temp_sensor.temperature}°C"
#       # text_humidity = f"습도 : {temp_sensor.humidity}%"

#       draw.text((0, 0), f"{TITLE}", font=font_title, fill="#FFFFFF")
#       #draw.text((0, 20), f"({datetime.now().strftime('%y%m%d.%H:%M:%S')})", font=font_title, fill="#FFFFFF")
#       #draw.rectangle((0, 20, (width, 20)), outline=0, fill=(255,255,255))
#       # draw.rectangle((0, 20, width, 40), outline=0, fill=(85,85,85))
#       # draw.text((0, 20), f"{datetime.now().strftime('%y%m%d.%H:%M:%S')}", font=font_title, fill="#FF0000")
#       # if temp_sensor.temperature is not None:
#       #     draw.text((0, 40), text_temperature, font=font, fill="#FFFFFF")
#       # if temp_sensor.humidity is not None:
#       #     draw.text((0, 65), text_humidity, font=font, fill="#FFFFFF")
#   except RuntimeError:
#       pass

#   count = count + 1

#   print("test")
#   # disp.image(image)
#   time.sleep(0.01)



# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Quick test of TFT FeatherWing (ILI9341) with Feather M0 or M4
# Will fill the TFT black and put a red pixel in the center, wait 2 seconds,
# then fill the screen blue (with no pixel), wait 2 seconds, and repeat.
import time
import random
import busio
import digitalio
import board
import subprocess

from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
from adafruit_rgb_display import ili9341
import adafruit_dht

from datetime import datetime


# Configuratoin for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D22)
rst_pin = digitalio.DigitalInOut(board.D27)
temp_pin = digitalio.DigitalInOut(board.D23)
temp_pin.direction = digitalio.Direction.INPUT
temp_pin.pull = digitalio.Pull.DOWN

temp_sensor = adafruit_dht.DHT11(board.D23)

# Config for display baudrate (default max is 24mhz):
# BAUDRATE = 24000000
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

font = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnBatang.ttf", 24)
font_title = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnGraphicBold.ttf", 18)

# Create the ILI9341 display:
disp = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=rst_pin, baudrate=BAUDRATE, rotation=90)

if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

draw = ImageDraw.Draw(image)

TITLE = "간식창고 by 승승장구"
count = 1

draw.rectangle((0, 0, width, height), outline=0, fill=0)
draw.text((0, 0), f"{TITLE}", font=font_title, fill="#FFFFFF")

while True:
  draw.rectangle((0, 20, width, height-20), outline=0, fill=0)

  try:
      text_temperature = f"온도 : {temp_sensor.temperature}°C"
      text_humidity = f"습도 : {temp_sensor.humidity}%"

      draw.text((0, 20), f"{datetime.now().strftime('%y%m%d.%H:%M:%S')}", font=font_title, fill="#FF0000")
      if temp_sensor.temperature is not None:
          draw.text((0, 40), text_temperature, font=font, fill="#FFFFFF")
      if temp_sensor.humidity is not None:
          draw.text((0, 65), text_humidity, font=font, fill="#FFFFFF")
  except RuntimeError:
      pass

  count = count + 1

  disp.image(image)
  time.sleep(0.01)