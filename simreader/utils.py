#!/usr/bin/env python3
#Based on: pySIM Copyright (C) 2005, Todd Whiteman
#Licensed under GNU GPL v2 see LICENCE for more.
import binascii


def int_to_hex(i, padchar='0', padlength=2):
    """ converts an integer to a hex string with padding
        sample : integer 12 is converted to string "0C"
    """
    res = hex(i).upper()[2:]
    while len(res) < padlength:
        res = "0" + res
    return res


def ascii_to_pin(sPIN):
    """ converts a PIN code string to a hex string with padding
        The PIN code string is padded with 'FF' until (8 - lg_sPIN).
        sample : "0000" is converted to "30303030FFFFFFFF"
        Input :
            - sPIN     = string containing the  cardholder code (PIN)

        Return a hex string of the PIN with FF padding.
    """
    return (binascii.hexlify(sPIN.encode("ascii")) + (8 - len(sPIN)) * b'FF').decode("ascii")


def remove_padding(s, padding="FF"):
    i = len(padding)
    while s[-i:] == padding:
        s = s[:-i]
    return s


def swap_nibbles(hex_string, padding_nibble='F'):
    """ converts a string in a buffer with swap of each character
        If odd number of characters, the paddingNibble is concatenated to the result string
        before swap.
        sample : "01396643721" is converted to "1093663427F1"
        Input :
            - hexString     = string containing data to swap
            - paddingNibble = value of the padd (optional parameter, default value is 'F')

        Return a list of bytes.
    """
    remove_pad = 0
    length = len(hex_string)
    if length >= 2 and hex_string[-2] == padding_nibble:
        remove_pad = 1

    if length % 2:       # need padding
        hex_string += padding_nibble

    res = ''
    for i in range(0, length, 2):
        res += "%s%s" % (hex_string[i+1], hex_string[i])

    if remove_pad:
        res = res[:-1]
    return res


def gsm_phone_number_to_str(phone_string, replaceTonNPI=0):
    """ converts a GSM string number to a normal string representation
        If the second last character is 'F', the F is removed from the result string.
        sample : "10936634F7"  is converted to "013966437"
        Input :
            - phoneString    = GSM phone string (data to swap)
        Returns a normal number string.
    """
    if not phone_string:
        return ''

    res = ""
    if replaceTonNPI:
        if phone_string[:2] == "91":
            res = "+"
        phone_string = phone_string[2:]

    i = 0
    while i < len(phone_string):
        res += '%s%s' % (phone_string[i+1], phone_string[i])
        i += 2

    if res and res[-1].upper() == 'F':
        res = res[:-1]

    return res


def str_to_gsm_phone_number(phoneString):
    """ converts a number string to a GSM number string representation
        Input :
            - phoneString    = phone string (data to swap)
        Returns a GSM number string.
    """
    if not phoneString:
        return ''

    if phoneString[0] == '+':
        res = "91"
        phoneString = phoneString[1:]
    else:
        res = "81"

    if len(phoneString) % 2:
        phoneString += "F"

    i = 0
    while i < len(phoneString):
        res += '%s%s' % (phoneString[i+1], phoneString[i])
        i += 2

    return res