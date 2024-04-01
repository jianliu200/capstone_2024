import gpiod
import time
import signal
import sys

LED_PIN1 = 9
LED_PIN2 = 10
LED_PIN3 = 11

chip = gpiod.Chip('gpiochip4')

RED = chip.get_line(LED_PIN1)
YELLOW = chip.get_line(LED_PIN2)
GREEN = chip.get_line(LED_PIN3)


RED.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
YELLOW.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
GREEN.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

try:
   while True:
       RED.set_value(1)
       YELLOW.set_value(1)
       GREEN.set_value(1)
       time.sleep(1)
       RED.set_value(0)
       GREEN.set_value(0)
       YELLOW.set_value(0)
       time.sleep(1)
finally:
   RED.set_value(0)
   GREEN.set_value(0)
   YELLOW.set_value(0)
   RED.release()
   YELLOW.release()
   GREEN.release()
   
