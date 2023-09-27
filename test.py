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

oldSet2 = [45, 3, 21, 7, 0, 76, 152, 1, 10, 215, 35, 60, 0, 0, 192, 64, 0, 0, 128, 63, 1, 0, 0, 128, 63, 6, 1, 0, 0, 0, 0, 0, 36, 116, 73, 64, 64, 0, 0, 3, 0, 0, 0, 0, 6, 1, 0, 0, 0, 0, 0, 36, 116, 73, 64, 160, 0, 0, 3, 0, 0, 0, 0, 6, 1, 0, 0, 0, 0, 0, 36, 116, 73, 65, 16, 0, 0, 3, 0, 0, 0, 0, 6, 1, 10, 215, 35, 60, 0, 0, 192, 64, 0, 0, 128, 63, 1, 0, 0, 128, 63, 6, 1, 0, 0, 0, 0, 0, 36, 116, 73, 64, 64, 0, 0, 3, 0, 0, 0, 
0, 6, 1, 0, 0, 0, 0, 0, 36, 116, 73, 64, 160, 0, 0, 3, 0, 0, 0, 0, 6, 1, 0, 0, 0, 0, 0, 36, 116, 73, 65, 16, 0, 0, 3, 0, 0, 0, 0, 6, 31, 14]

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

line = "03 00 00 00 00 06"
first = True
out = []
num = 0
abc = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15} #{"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15}

for n in line:
    if first and n != " ":
        num += (abc[n] * 16)
        first = False
    elif not first and n != " ":
        num += abc[n]
    elif n == " ":
        out.append(num)
        first = True
        num = 0

out.append(num)

print(out)

def FloatToHEX(num: float): # Получая на вход Float, возвращает масив байт
    merge = struct.unpack("<I", struct.pack(">f", num))[0] # Float -> Байты -> UInt

    data = []
    for n in range(4): # Разбиваем UInt на отдельные байты, записанные в обратном порядке
        data.append(merge % 256)
        merge = merge // 256

    data.reverse() # Переводим в прямой порядок (для удобства понимания)
    return data


newWht1f = float(3.0)



temp = FloatToHEX(newWht1f) # Вес №1
temp.reverse()


print(FloatToHEX(newWht1f))

print(struct.pack('<f', 3.0))