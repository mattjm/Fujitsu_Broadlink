import broadfromhexcode as broad
import json
# REMEMBER TO CALC THE CHECK BIT


#1-8:  same
#9: temp and change or on.   least significant bit needs to be 1 for the machine to turn on.  example.  11100000 = E0.  No turn on.  11100001=E1.  Turns on.  
#10: mode hot/cold.  and timer.  Timer not implemented--always disabled.  
#11: swing and fan
#12:                                30    01 04 00 00 00
#heat high 60: 14 63 00 10 10 fe 09 30 || 00 04 01 00 00 00 20 ab
#               1  2  3  4  5  6  7  8  || 9 10 11 12 13 14 15 16

existing_codes = [
'28c60008087f900c80200000000004d5',
'28c60008087f900c88200000000004d9', # heat auto 60
'28c60008087f900c00208000000004d5', # heat high 60
'28c60008087f900c08208000000004d9', # heat high 62
'28c60008087f900c04208000000004d1', # heat high 64
'28c60008087f900c0280800000000476', #cool high 68
'28c60008087f900c07800000000004f3',# cool auto 88
'28c60008087f900c8780000000000473'# cool ON
]

new_codes = [
#'1463001010FE09 30 31 0B 00 0000002074
#'1463001010fe09 30 41 03 13 0000002059
#'1463001010fe09 30 41 03 14 0000002058
'1463001010fe093001040000000020ab',
'1463001010fe0930110400000000209b',
'1463001010fe093000040100000020ab',
'1463001010fe0930100401000000209b',
'1463001010fe0930200401000000208b',
'1463001010fe0930400101000000206e',
'1463001010fe0930e0010000000020cf',
'1463001010fe0930e1010000000020ce'
]


#for code in existing_codes:
#    print(broad.to_little_endian(code).hex())


M_HEAT = 0x04 
M_FAN_ONLY = 0x03
M_DRY = 0x02
M_COOL = 0x01
M_HEAT_COOL = 0x00

F_AUTO = 0x00
F_HIGH = 0x01
F_MEDIUM = 0x02
F_LOW = 0x03
F_QUIET = 0x04

S_OFF = 0x00
S_VERTICAL = 0x01 


#always the same as far as we know
FIRST_HALF = '1463001010fe0930'


#match HA names for these things:  https://developers.home-assistant.io/docs/core/entity/climate/
modes = ['heat', 'dry', 'cool', 'heat_cool', 'fan_only']
#for speeds and swing modes HA gives you a list from the names you provide
speeds = ['auto', 'high', 'medium', 'low', 'quiet']
temps_heat = range(16, 31) #temp goes to 30 but python range() is not inclusive so we need to go to 31
# "other" is auto, cool, dry, and fan
temps_other = range(18, 31) #note temp is sent for dry but not shown on remote
swings = ['off', 'vertical'] 


def temp_hex(decimaltemp):
    #temp in c
    encodedTemp = ((decimaltemp-16)*16) # we can get away with this because there are only 15 temperatures
    # adding 1 makes sure we always send the "turn on the device" signal.  Otherwise it only sends the temp and won't turn on the device if it's off.  
    encodedTemp = hex(encodedTemp + 1)
    if len(encodedTemp) == 3:
        return '0' + encodedTemp[2]
    else:
        return encodedTemp[2:]

    
    
def mode_hex(mode):
    modeVar = 'M_' + mode.upper()
    modeHex = hex(eval(modeVar))
    if len(modeHex) == 3:
        return '0' + modeHex[2]
    else:
        return modeHex[2:]

def fan_swing_hex(fan, swing):
    fanVar = 'F_' + fan.upper()
    fanHex = eval(fanVar)
    swingVar = 'S_' + swing.upper()
    swingHex = eval(swingVar)
    fanSwingHex = hex(swingHex * 16 + fanHex)
    if len(fanSwingHex) == 3:
        return '0' + fanSwingHex[2]
    else:
        return fanSwingHex[2:]



def checksum(controlString):
    verifyBytes = controlString[14:]#[14:26]
    sumBytes = 0
    for x in range(0, len(verifyBytes), 2):
        hexVal = verifyBytes[x:x+2]
        mybytes= bytes.fromhex(hexVal)
        sumBytes += int.from_bytes(mybytes)
    checksumVal = 0
    remainder = sumBytes % 256
    if remainder == 0:
        checksumVal = hex(0)
    else:
        checksumVal = hex(256 - remainder)
    if len(checksumVal) == 3:
        return '0' + checksumVal[2]
    else:
        return checksumVal[2:]

    






def build_control_string(mode, speed, swing, temp):
    controlString = FIRST_HALF
    controlString += temp_hex(temp)
    controlString += mode_hex(mode)
    controlString += fan_swing_hex(speed, swing)
    controlString += '00000020' #12, 13, and 14 are used for the timer (which we don't implement).  15 is always 0x20
    controlString+= checksum(controlString)
    return controlString
    

commandList = {}
if __name__ == "__main__": 
    for mode in modes:
        commandList[mode] = {}
        if (mode == 'heat'):
            temps = temps_heat
        else:
            temps = temps_other
        for speed in speeds:
            commandList[mode][speed] = {}
            for swing in swings:
                commandList[mode][speed][swing] = {}
                for temp in temps:
                    #print(mode, speed, swing, temp)
                    controlString = build_control_string(mode, speed, swing, temp)
                    #print(controlString)
                    encodedCommand = broad.broadlink_packet_from_hex(controlString)
                    commandList[mode][speed][swing][temp] = encodedCommand
                    
                
#print(commandList['heat']['fan_auto']['swing_off'][28])
smartIRList = {}
smartIRList['commands'] = commandList
smartIRList['commands']['economy'] = broad.broadlink_packet_from_hex('146300101009F6')
smartIRList['commands']['min_heat'] = broad.broadlink_packet_from_hex('1463001010FE0930310B000000002074')
smartIRList['commands']['off'] = broad.broadlink_packet_from_hex('146300101002fd') # special short string for off
#print(commandList)
#jsonExport = json.dumps(smartIRList, indent=2)
#print(jsonExport)                
# print(broad.broadlink_packet_from_hex('1463001010fe0930e1031300000020b9'))

with open('smartircommands.json', 'w') as file:
    json.dump(smartIRList, file, indent=2)
    print("wrote file")








#preset:
#eco = min_heat