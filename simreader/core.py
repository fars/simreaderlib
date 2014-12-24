#!/usr/bin/env python3
#Based on # Copyright (C) 2005, Todd Whiteman
import time

import serial

import simreader.constants


class SIMReader(serial.Serial):
    def __init__(self, port, baudrate):
        super().__init__(port,
                         baudrate,
                         serial.EIGHTBITS,
                         serial.PARITY_EVEN,
                         serial.STOPBITS_TWO,
                         1,
                         0,
                         0)
        self.response_atr = dict(TS=0, T0=0, TAi=0, TBi=0, TCi=0, TDi=0, Historical=[])

    def open_session(self):
        self.setRTS(1)
        self.setDTR(1)
        time.sleep(0.01)
        self.flushInput()
        self.setRTS(0)
        self.setDTR(0)

        ts = self.read().decode("ascii")
        if ts == "":
            return -2  # no card probably
        elif ord(ts) != 0x3B:
            return -3  # got bad ATR byte
        else:
            self.response_atr["TS"] = ord(ts)  # OK we have 0x3B

        t0 = chr(0x3B)
        while ord(t0) == 0x3B:
            t0 = self.read()

        if t0 == "":
            return -2  # something went wrong here
        self.response_atr["T0"] = ord(t0)

        #now read interface bytes
        if ord(t0) & 0x10:
            self.response_atr["TAi"] = ord(self.read())
        if ord(t0) & 0x20:
            self.response_atr["TBi"] = ord(self.read())
        if ord(t0) & 0x40:
            self.response_atr["TCi"] = ord(self.read())
        if ord(t0) & 0x80:
            self.response_atr["TDi"] = ord(self.read())

        historical = []
        for i in range(0, ord(t0) & 0xF):
            x = self.read()
            historical.append(x)
        self.response_atr["Historical"] = historical

        while self.read().decode("ascii") != "":  # Ugly as hell
            pass

        return 0

    def close_session(self):
        self.close()
        return 0

    def select_file(self, file_ids):
        for i in file_ids:
            #self.send_apdu("A0A4000002%s" % i)
            data, sw = self.send_apdu("A0A4000002%s" % i)
            #print(str(data) + " " + str(sw))

    def send_apdu(self, command):
        """sendAPDU(pdu)

            command : string of hexadecimal characters (ex. "A0A40000023F00")
            result  : tuple(data, sw), where
                      data : string (in hex) of returned data (ex. "074F4EFFFF")
                      sw   : string (in hex) of status word (ex. "9000")
        """
        # send first 5 'header' bytes
        for i in range(5):
            s = int(command[i*2] + command[i*2+1], 16)
            #print("0x%x" % s)
            self.write(s.to_bytes(1, "big"))
            # because rx and tx are tied together, we will read an echo
            self.read()
            #print("0x%x" % ord(self.read()))

        reply = self.read()
        while ord(reply) != int(command[2] + command[3], 16):
            if ord(reply) != simreader.constants.ACK_NULL:
                return 0, 0  # bad response
            reply = self.read()

        data = ''
        if len(command) == 10:
            # read data
            datalength = int(command[8] + command[9], 16)
            #print ("reading %d bytes" % datalen)
            for i in range(datalength):
                s = ord(self.read())
                hexed = "%02X" % s
                #print(hexed)
                data += hexed[0]
                data += hexed[1]
                #print(data)
        else:
            # time to send command
            datalength = int(command[8] + command[9], 16)
            #print("writing %d bytes" % datalength)
            for i in range(datalength):
                s = int(command[10 + i*2]+command[11 + i*2], 16)
                #print("%x" % s)
                self.write(s.to_bytes(1, "big"))
                # because rx and tx are tied together, we will read an echo
                self.read()

        # look for the ack word, but ignore a ACK_NULL (0x60)
        sw1 = self.read()
        #print(sw1)
        while ord(sw1) == simreader.constants.ACK_NULL:
            self.read()
            #print(sw1)

        sw2 = self.read()
        sw = "%02x%02x" % (ord(sw1), ord(sw2))
        #print("Status word: " + sw)
        if data:
            #print("Out: " + data)
            return data, sw
        else:
            return '', sw