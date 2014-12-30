#!/usr/bin/env python3
#Based on: pySIM Copyright (C) 2005, Todd Whiteman
#Licensed under GNU GPL v2 see LICENCE for more.
import binascii
import simreader.utils
import simreader.constants
import traceback


def get_provider(reader):
    """
    Read provider name from SIM, PIN si not required
    :param reader: simreader.core.SIMReader object
    :return: ASCII string of provider name
    """
    try:
        reader.select_file([simreader.constants.MF, simreader.constants.DF_GSM, simreader.constants.EF_SPN])
        reader.check_and_verify_chv1(reader.chv1, simreader.constants.CHV_READ)
        data, sw = reader.send_apdu_match_sw("A0B0000009", simreader.constants.SW_OK)
        s = binascii.unhexlify((simreader.utils.remove_padding(data[1:]))[1:]).decode("ascii")
        return s
    except:
        traceback.print_exc()


def get_loci(reader, pin):
    """
    Returns location information from SIM card
    (MCC(3digits)-MNC(3digits)-LAC(2bytes))
    e.g. 231F02XXXX
    231 = MCC (SR)
    F02 = MNC (T-Mobile) Europe uses 2 digits (ignore F) USA 3
    XXXX = LAC (Location Area Code) - LCID in G-MoN
    :param reader: simreader.core.SIMReader object
    :param pin: pin code
    :return: Location information
    """
    reader.select_file(["3F00", simreader.constants.DF_GSM, simreader.constants.EF_LOCI])
    reader.check_and_verify_chv1(pin, simreader.constants.CHV_READ)
    data, sw = reader.send_apdu_match_sw("A0B000000B", simreader.constants.SW_OK)
    print(data)
    s = simreader.utils.swap_nibbles(simreader.utils.remove_padding(data))
    s = s[8:18]
    return s


def get_serial_number(reader):
    """
    Returns SIM card serial number (last digit is not always printed on the card)
    :param reader: simreader.core.SIMReader object
    :return: string containing SIM serial number
    """
    reader.select_file([simreader.constants.MF, simreader.constants.EF_ICCID])
    data, sw = reader.send_apdu_match_sw("A0B000000A", simreader.constants.SW_OK)
    s = simreader.utils.swap_nibbles(simreader.utils.remove_padding(data))
    return s


def get_msisdn(reader):
    """
    Actually this is pretty useless data in EF_MSISDN is optional, and I haven't found one SIM that
    had the real phone number stored there.
    :param reader: simreader.core.SIMReader object
    :return: Raw hex data stored in EF_MSISDN still have to call simreader.utils.gsm_phone_number_to_str
    """
    reader.select_file([simreader.constants.MF, simreader.constants.DF_TELECOM, simreader.constants.EF_MSISDN])
    data, sw = reader.send_apdu_match_sw("A0C000000F", simreader.constants.SW_OK)
    #data, sw = self.SIM.sendAPDUmatchSW("A0B000000B", SW_OK)
    return data

def get_imsi_raw(reader, pin=""):#broken do not use
    """
    Read IMSI from SIM card, PIN required
    :param reader: simreader.core.SIMReader object
    :return: Raw hex IMSI value
    """
    #if reader.chv1 == "" and pin != "":
    #    reader.chv1 = pin
    #else:
    #    return 1
    # IMSI: i.e. 505084000052282
    try:
        reader.select_file([simreader.constants.MF, simreader.constants.DF_GSM, simreader.constants.EF_IMSI])
        reader.check_and_verify_chv1(pin, simreader.constants.CHV_READ)  # When using reader.chv1 exception occurs???
        data, sw = reader.send_apdu_match_sw("A0B0000009", simreader.constants.SW_OK)
        return data
        #s = simreader.utils.swap_nibbles(simreader.utils.remove_padding(data[2:]))[1:]
        #print(s)
    except:
        traceback.print_exc()