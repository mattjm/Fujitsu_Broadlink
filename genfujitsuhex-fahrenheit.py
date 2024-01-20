import broadfromhexcode as broad
import json
from pytemp import pytemp



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
#for speeds and swing modes HA make the list from the names you provide
speeds = ['auto', 'high', 'medium', 'low', 'quiet']
temps_heat = range(61, 87) 
# "other" is auto, cool, dry, and fan
temps_other = range(64, 87) 
swings = ['off', 'vertical'] 


def temp_hex(decimaltemp):
    #temp in c
    encodedTemp = ((decimaltemp-16)*16)
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
    verifyBytes = controlString[14:]
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
    controlString += '00000020' # 12, 13, and 14 are used for the timer (which we don't implement).  15 is always 0x20
    controlString+= checksum(controlString)
    return controlString
    
    
def freedomUnits(temp):
    # this actually converts FROM freedom units ¯\_(ツ)_/¯
    return round(pytemp(temp, 'f', 'c'))
    

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
                    #convert F temp to C for purposes of calculating the control string
                    controlString = build_control_string(mode, speed, swing, freedomUnits(temp))
                    #print(controlString)
                    encodedCommand = broad.broadlink_packet_from_hex(controlString)
                    #use the F temp here
                    commandList[mode][speed][swing][temp] = encodedCommand
                    
                

smartIRList = {}
smartIRList['commands'] = commandList
smartIRList['commands']['economy'] = broad.broadlink_packet_from_hex('146300101009F6') # short string
smartIRList['commands']['min_heat'] = broad.broadlink_packet_from_hex('1463001010FE0930310B000000002074') # special mode and temp
smartIRList['commands']['off'] = broad.broadlink_packet_from_hex('146300101002fd') # short string
smartIRList['commands']['step_vertical_vane'] = broad.broadlink_packet_from_hex('14630010107986') # short string


with open('smartircommands-fahrenheit.json', 'w') as file:
    json.dump(smartIRList, file, indent=2)
    print("wrote file")

