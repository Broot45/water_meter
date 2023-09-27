import struct

#print(struct.pack(">hh", 10, 12))
#print((str(struct.pack("h", 1022))[4:-1:]).split("\\x"))
#struct.unpack('!f', bytes.fromhex('470FC614'))[0]

    

##print(struct.unpack(">f", b"\x41\x41\x00\x00"))
##print(struct.pack(">f", 12.0625))
##print(b"\x41\x20")
##print(b"\x41")
#print(type(hex(10)))
#print(hex(0x6) + hex(0x6))
#print(hex(0x4073D70A) + )

##mas = []
##a = None
##print(struct.pack(">f", 12.0625))
##for byte in struct.pack(">f", 12.0625):
##    mas.append(byte)
##    print(byte)
    #print(Bipac[byte], end = ', ')
##ngh = []
##print(mas)
##for n in mas: 
##    ngh.append(struct.pack("b", n))
##    for m in struct.pack("b", n): print(m, "fuck")
##print(ngh)
#print(Bipac)
#print(struct.unpack(">f", b"\x41\x41\x00\x00"))

#mas = [1, 2, 3] #>>> [1, 2, 3]

#mas.extend([4, 5, 6]) #>>> [1, 2, 3, 4, 5, 6]
#mas.reverse() #>>> [6, 5, 4, 3, 2, 1]
#print(mas)

oldSet2 = [45, 3, 4, 65, 96, 101, 60, 40, 146]

def CRC16(data: list): # Функция, вычисляющая контрольную сумму по методу CRC16, контрольная сумма идёт в конце каждого пакета
    poly = 0xa001 # На вход подаётся массив байт прямого порядка
    xor1 = 0x0000
    crc = 0xffff
    len_ = len(data)
    i = 0

    while len_: 
        len_ -= 1
        crc ^= (data[i])
        i += 1        
        
        for j in range(0, 8):    
            if crc & 0x0001:
                crc = (crc >> 1) ^ poly
            else:
                crc = crc >> 1
            
    crc ^= xor1
    return crc # На выход получаем число, пе

print(CRC16(oldSet2))

test = [64, 115, 215, 10]

