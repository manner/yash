#!/usr/bin/env python2.7
from yeelight import *
from scapy.all import *
import signal
import device_config as dc

bulb = Bulb(dc.yeelightIP, auto_on=True)

def button_pressed_dash1():
  print("Somebody rang. Please get the door!")
  try:
      state=bulb.get_properties()["power"]
      if state=="on":
        action=Flow.actions.recover
      else:
        action=Flow.actions.off

      transitions = [
            HSVTransition(0, 100, duration=80),
            HSVTransition(240, 100, duration=80)
      ]

      flow = Flow(
        count=10,
        action=action,
        transitions=transitions
      )
      bulb.start_flow(flow)
  except BulbException as e:
      print(str(e))
      print("Please try again...")

def udp_filter(pkt):
  options = pkt[DHCP].options
  for option in options:
    if isinstance(option, tuple):
      if 'requested_addr' in option:
        mac_to_action[pkt.src]()
        break


def signal_handler(signal, frame):
  print("\nBye.")
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

mac_to_action = {dc.dashMAC : button_pressed_dash1}
mac_id_list = list(mac_to_action.keys())

print("Waiting for somebody to ring...")
sniff(prn=udp_filter, store=0, filter="udp", lfilter=lambda d: d.src in mac_id_list)

if __name__ == "__main__":
  main()
