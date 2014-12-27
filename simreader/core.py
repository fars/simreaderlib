#!/usr/bin/env python3
#Based on: pySIM Copyright (C) 2005, Todd Whiteman
#Licensed under GNU GPL v2 see LICENCE for more.
import time
import binascii
import serial
import traceback

import simreader.constants
import simreader.utils


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
        self.chv1 = ""
        self.chv1_enabled = 0
        self.chv1_tries_left = 0
        self.chv2 = ""
        self.chv2_enabled = 0
        self.chv2_tries_left = 0

    def open_session(self):
        self.setRTS(1)
        self.setDTR(1)
        time.sleep(0.01)
        self.flushInput()
        self.setRTS(0)
        self.setDTR(0)

        ts = self.read()
        if ts == "":
            return -2  # no card probably
        elif ord(ts) != 0x3B:
            return -3  # got bad ATR byte
        else:
            self.response_atr["TS"] = ord(ts)  # OK we have 0x3B

        t0 = chr(0x3B)  # Lot of unnecessary ord and chars everywhere, should probably change everything to bytes
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
            historical.append(ord(x))
        self.response_atr["Historical"] = historical

        while self.read().decode("ascii") != "":  # Ugly as hell
            pass

        return 0

    def close_session(self):
        self.close()
        return 0

    def select_file(self, file_ids):
        """
        Select file or directory from SIM
        :param file_ids: list of files (path) ["3F00", "7F20", "6F07"]
        :return: nothing
        """
        for i in file_ids:
            self.send_apdu("A0A4000002%s" % i)
            #data, sw = self.send_apdu("A0A4000002%s" % i)
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
        #print("reply:", reply)
        #print(ord(reply))
        #print(int(command[2] + command[3], 16))
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

    def send_apdu_match_sw(self, command, expected_sw):
        """sendAPDUmatchSW(pdu)

            command : string of hexadecimal characters (ex. "A0A40000023F00")
            matchSW : string of 4 hexadecimal characters (ex. "9000")
            result  : tuple(data, sw), where
                      data : string (in hex) of returned data (ex. "074F4EFFFF")
                      sw   : string (in hex) of status word (ex. "9000")
        """

        data, sw = self.send_apdu(command)
        if sw != expected_sw:
            raise RuntimeError("Status words do not match. Result: %s, Expected: %s" % (sw, expected_sw))
        return data, sw

    def check_chv1(self):
        """
        Check card holder verification info.
        Sets: simreader.core.SIMReader.chv1_enabled - is CHV1 enabled
              simreader.core.SIMReader.chv1_tries_left - number of PIN code verification tries left
        :return:
        """
        #Check Card holder verification, returns if is set and number of tries remaining
        try:
            self.select_file(["3F00"])
            data, sw = self.send_apdu_match_sw("A0F200000D", simreader.constants.SW_OK)
            l = 0x0D + int(data[24:26], 16)
            data, sw = self.send_apdu_match_sw("A0F20000%s" % simreader.utils.int_to_hex(l), simreader.constants.SW_OK)
            s = binascii.unhexlify(data)

            # Check whether CHV1 is enabled
            chv1_enabled = 1
            if s[13] & 0x80:
                chv1_enabled = 0

            # Get number of CHV1 attempts left (0 means blocked, oh crap!)
            chv1_tries_left = s[18] & 0x0F
            self.chv1_enabled = chv1_enabled
            self.chv1_tries_left = chv1_tries_left
        except:  # Too broad should fix this
            traceback.print_exc()

    def check_chv2(self):
        try:
            self.select_file(["3F00"])
            data, sw = self.send_apdu_match_sw("A0F200000D", simreader.constants.SW_OK)
            l = 0x0D + int(data[24:26], 16)
            data, sw = self.send_apdu_match_sw("A0F20000%s" % simreader.utils.int_to_hex(l), simreader.constants.SW_OK)
            s = binascii.unhexlify(data)

            # 0000000C3F000100000000030A93070A0400838A838A00
            if len(s) >= 22:
                # Get number of CHV2 attempts left (0 means blocked, oh crap!)
                chv2_enabled = 1
                chv2_tries_left = s[20] & 0x0F
                self.chv2_enabled = chv2_enabled
                self.chv2_tries_left = chv2_tries_left
        except:
            traceback.print_exc()

    def check_and_verify_chv1(self, pin="", checktype=simreader.constants.CHV_UPDATE, data=None):
        """
        Checks what access is required and checks PIN is valid
        :param pin: PIN number
        :param checktype: type of access
        :param data:
        :return: 0 if OK
        """
        if self.chv1_enabled == 0:
            # No PIN set on this card
            return 1
        if self.chv1 != "":
            # Must have verified successfully already
            return 1

        # Issue the status command if we don't already have the data
        if not data:
            data, sw = self.send_apdu_match_sw("A0C000000F", simreader.constants.SW_OK)

        # Check if CHV1 is needed for this function (read / write)
        # 000007DF3F000100 00 444401071302
        if checktype == simreader.constants.CHV_ALWAYS:
            val = 1
        elif checktype & simreader.constants.CHV_UPDATE:
            val = int(data[17], 16)
        else:  # Must be checking for read access
            val = int(data[16], 16)

        if val == 0:  # means we don't need chv1, always access is set
            return 1
        elif val == 1:  # means chv1 is needed, try and verify it
            # Have not verified yet, try now, ask for the PIN number
            if pin == -1:
                return 1  # No pin set
            else:
                self.chv1 = pin
                ok = True
                for i in self.chv1:
                    if i not in "0123456789":
                        ok = False
                if len(self.chv1) < 4 or len(self.chv1) > 8:
                    ok = False

                if not ok:
                    raise RuntimeError("Invalid PIN! Must be 4 to 8 digits long\n\nDigits are: 0123456789")
                try:
                    self.send_apdu_match_sw("A020000108%s" % simreader.utils.ascii_to_pin(self.chv1),
                                            simreader.constants.SW_OK)
                    return 1
                except:
                    self.chv1 = ""
                    raise RuntimeError("Incorrect PIN!")

        # Must need CHV2 or ADM access, foo-ey!
        return 0
