import base64

BIT_MARK = 420#420
ONE_SPACE = 1210#1210
ZERO_SPACE = 420 #420
TICK = 32.84 # broadlink tick
IR_TOKEN = 0x26

# test codes
fujitsuHex = '1463001010fe0930110400000000209b'
hex2 = '1463001010fe093000040100000020ab'

#example broken down
#auto fan, 60F, heat
#Hex: 1463001010FE093000040000000020AC
#Binary:
#00010100 01100011 00000000 00010000
#00010000 11111110 00001001 00110000
#00000000 00000100 00000000 00000000
#00000000 00000000 00100000 10101100

#thanks chatgpt
def reverse_bits(byte):
    return int(f'{byte:08b}'[::-1], 2)

def to_big_endian(hexString):
    bigBytes = bytearray()
    littleBytes = bytes.fromhex(hexString)

    for littlebyte in littleBytes:
        original_byte = littlebyte
        reversed_byte = reverse_bits(original_byte)
        bigBytes.append(reversed_byte)
    return bigBytes

# just for testing
# sometimes when you read a code in from something else it will have the wrong byte order.  This can switch it 
# back so you can compare it to known values.  This isn't used for the conversion to broadlink.  
def to_little_endian (big):
    bigBytes = bytearray()
    littleBytes = bytes.fromhex(big)
    for littlebyte in littleBytes:
        original_byte = littlebyte
        reversed_byte = reverse_bits(original_byte)
        bigBytes.append(reversed_byte)
    return bigBytes
# print(to_little_endian('28c60008087f900c88200000000004d9').hex())
#end testing
    




def calc_microsecond_timings(timings):
    timings_out = []
    for byte in timings:
        singleBits = f'{byte:08b}'
        for oneBit in singleBits:
           timings_out.append(BIT_MARK)
           if oneBit == '1':
            timings_out.append(ONE_SPACE) 
           else:
            timings_out.append(ZERO_SPACE)
    return timings_out


    


# mostly borrowed from broadlink CLI
def durations_to_broadlink(durations):
    result = bytearray()
    result.append(IR_TOKEN)
    result.append(0)
    result.append(len(durations) % 256)
    result.append(len(durations) // 256) # this is different than what I got from the CLI--works for this length--maybe not others
    for dur in durations:
        num = int(round(dur / TICK))
        if num > 255:
            result.append(0)
            result.append(num / 256)
        result.append(num % 256)
    result.append(0x0d)
    result.append(0x05)
    return result
    


def broadlink_packet_from_hex(myhex):

    bigendhex = to_big_endian(myhex)
    # print(bigendhex.hex())
    microsecond_timings = calc_microsecond_timings(bigendhex)
    # print(microsecond_timings)
    # fujitsu headers
    microsecond_timings.insert(0,1631)
    microsecond_timings.insert(0,3288)
    # fujitsu trailer
    microsecond_timings.insert(len(microsecond_timings), BIT_MARK)
    microsecond_timings.insert(len(microsecond_timings), 8022) # it will work intermittently without the explicit silence at the end
    # print(microsecond_timings)
    broadlink_packet = durations_to_broadlink(microsecond_timings)
    #print(broadlink_packet.hex())
    return base64.b64encode(broadlink_packet).decode('utf-8')
    




if __name__ == "__main__":
    print(broadlink_packet_from_hex(hex2))
