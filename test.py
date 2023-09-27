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
import csv

