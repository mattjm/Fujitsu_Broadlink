import broadfromhexcode as broad

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
'1463001010fe093001040000000020ab',
'1463001010fe0930110400000000209b',
'1463001010fe093000040100000020ab',
'1463001010fe0930100401000000209b',
'1463001010fe0930200401000000208b',
'1463001010fe0930400101000000206e',
'1463001010fe0930e0010000000020cf',
'1463001010fe0930e1010000000020ce'
]


for code in existing_codes:
    print(broad.to_little_endian(code).hex())


M_HEAT = 0x04 
M_FAN = 0x03
M_DRY = 0x02
M_COOL = 0x01
M_AUTO = 0x00
M_MIN_HEAT = 0x0B

F_AUTO = 0x00
F_HIGH = 0x01
F_MEDIUM = 0x02
F_LOW = 0x03
F_QUIET = 0x04

S_OFF = 0x00
S_VERTICAL = 0x01 


#always the same as far as we know
FIRST_HALF = '1463001010fe0930'



modes = ['heat', 'dry', 'cool', 'auto', 'min_heat', 'fan']
speeds = ['auto', 'high', 'medium', 'low', 'quiet']
temps_heat = range(16, 31) #temp goes to 30 but python range() is not inclusive so we need to go to 31
# "other" is auto, cool, dry, and fan
temps_other = range(18, 31) #temp is sent for dry but not shown on remote
swing = ['off', 'vertical'] 


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

# https://gist.github.com/GeorgeDewar/11171561
# https://stackoverflow.com/questions/48531654/fujitsu-ir-remote-checksum-calculation
def checksum(controlString):
    controlString = broad.to_little_endian(controlString).hex()
    print(controlString)
    verifyBytes = controlString[14:26]#[14:26]
    print(verifyBytes)
    sum = 0
    for x in range(0, len(verifyBytes), 2):
        print("hex")
        print(verifyBytes[x:x+2])
        hexVal = verifyBytes[x:x+2]
        #print("binary")
        #print(f'{int(hexVal):08b}')
        #print("reversed")
        #print(f'{int(hexVal):08b}'[::-1], 2)
        reversedDecimalVal = int(f'{int(hexVal):08b}'[::-1], 2)
        print(reversedDecimalVal)
        sum += reversedDecimalVal
    print("sum")
    print(sum)
    checksum = (208-sum) % 256

    print(int(checksum))
    print(f'{checksum:08b}')
    reversedChecksum = hex(int(f'{checksum:08b}'[::-1], 2))
    print(f'{checksum:08b}'[::-1], 2)
    print(reversedChecksum)
    if len(reversedChecksum) == 3:
        return '0' + reversedChecksum[2]
    else:
        return reversedChecksum[2:]

def checksum2(controlString):
    #controlString = broad.to_little_endian(controlString).hex()
    print(controlString)
    verifyBytes = controlString[14:]#[14:26]
    print(verifyBytes)
    sumBytes = 0
    for x in range(0, len(verifyBytes), 2):
        hexVal = verifyBytes[x:x+2]
        mybytes= bytes.fromhex(hexVal)
        print(int.from_bytes(mybytes))
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
    

    
    if len(reversedChecksum) == 3:
        return '0' + reversedChecksum[2]
    else:
        return reversedChecksum[2:]

        
 #= f'{int(verifyBytes):08b}'
  #  print(byte)
    
    
    #print(verifyBytes)
    #print(type(verifyBytes))
    #print(f'{int(verifyBytes):08b}')

    



#testing only
for temp in temps_heat:
    print(temp_hex(temp))
    

for mode in modes:
    print("mode")
    print(mode_hex(mode))

print(fan_swing_hex('high', 'off'))


def build_control_string(mode, temp, fan, swing):
    controlString = FIRST_HALF
    print(controlString)
    controlString += temp_hex(temp)
    print(controlString)
    controlString += mode_hex(mode)
    print (controlString)
    controlString += fan_swing_hex(fan, swing)
    print(controlString)
    controlString += '00000020' #12, 13, and 14 are used for the timer.  15 is always 0x20
    controlString+= checksum2(controlString)
    print(controlString)
    
build_control_string('heat', 17, 'auto', 'off')

