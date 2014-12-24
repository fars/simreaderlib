#!/usr/bin/env python3
import simreader.core

reader = simreader.core.SIMReader("/dev/ttyUSB0", 9600)
reader.open_session()
print(reader.response_atr)
print("TS:0x%x" % reader.response_atr.get("TS"))
print("T0:0x%x" % reader.response_atr.get("T0"))
print("TAi:0x%x" % reader.response_atr.get("TAi"))
reader.select_file(["3F00"])  # Master File directory
reader.close_session()