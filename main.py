#!/usr/bin/env python3
import simreader.core
import simreader.constants
import simreader.utils
import simreader.extras

reader = simreader.core.SIMReader("/dev/ttyUSB0", 9600)
reader.open_session()
print(reader.response_atr)
print("TS:0x%x" % reader.response_atr.get("TS"))
print("T0:0x%x" % reader.response_atr.get("T0"))
print("TAi:0x%x" % reader.response_atr.get("TAi"))

reader.check_chv1()
print(reader.chv1_tries_left)
print(reader.chv2_tries_left)
print(simreader.extras.get_serial_number(reader))
print(simreader.extras.get_provider(reader))
print(simreader.extras.get_msisdn(reader))

#reader.check_chv1()
#print(reader.chv1_tries_left)
reader.close_session()