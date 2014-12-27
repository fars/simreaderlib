#!/usr/bin/env python3
#Based on # Copyright (C) 2005, Todd Whiteman
#add licence later

#pySIM constants useless probably
SCARD_PROTOCOL_T0 = 1
SCARD_PROTOCOL_T1 = 2
CHV_ALWAYS = 0
CHV_READ = 1
CHV_UPDATE = 2
SIM_STATE_DISCONNECTED = 0
SIM_STATE_CONNECTED = 1

#Status words
SW_OK = "9000"
SW_FOLDER_SELECTED_OK = "9F17"
SW_FILE_SELECTED_OK = "9F0F"

OFFSET_CDATA = 5
ACK_NULL = 0x60
ACK_OK = 0x90

ATTRIBUTE_ATR = 0x90303
ATTRIBUTE_VENDOR_NAME = 0x10100
ATTRIBUTE_VENDOR_SERIAL_NO = 0x10103

#Filesystem
#Every file is explained in GSM Technical Specification 11.11
#Specification of the Subscriber Identity Module - Mobile Equipment (SIM - ME) interface
#http://www.etsi.org/deliver/etsi_gts/11/1111/05.03.00_60/gsmts_1111v050300p.pdf
#Names are the same
MF = "3F00"
DF_TELECOM = "7F10"
DF_GSM = "7F20"
#ICCID is directly in MF
EF_ICCID = "2FE2"
#TELECOM directory:
EF_ADN = "6F3A"
EF_FDN = "6F3B"
EF_SMS = "6F3C"
EF_CCP = "6F3D"
EF_MSISDN = "6F40"
EF_SMSP = "6F42"
EF_SMSS = "6F43"
EF_LND = "6F44"
EF_SDN = "6F49"
EF_EXT1 = "6F4A"
EF_EXT2 = "6F4B"
EF_EXT3 = "6F4C"
#GSM_directory:
EF_LP = "6F05"
EF_IMSI = "6F07"
EF_KC = "6F20"
EF_PLMNsel = "6F30"
EF_HPLMN = "6F31"
EF_ACMmax = "6F37"
EF_SST = "6F38"
EF_ACM = "6F38"
EF_GID1 = "6F3E"
EF_GID2 = "6F3F"
EF_PUCT = "6F41"
EF_CBMI = "6F45"
EF_SPN = "6F46"
EF_BCCH = "6F74"
EF_ACC = "6F78"
EF_FPLMN = "6F7B"
EF_LOCI = "6F7E"
EF_AD = "6FAD"
EF_Phase = "6FAE"
