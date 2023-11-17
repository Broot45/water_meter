import struct
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', baudrate=2400, timeout = 0.5)

adress = int(input("Адрес устройства: "))



C_Read = [3] # Код для чтения регистра
C_Write = [16] # Код для записи регистра

C_Key_adr = [0, 0, 0, 1] # Адрес ключа для записи показаний счётчиков (включая длину)
C_Key_len = [8] # Длина ключа для записи счётчиков (также это длина кода для записи показаний)

С_oldSet_adr_1 = [21, 126, 0, 2] # Адрес регистра (включая длину), в котором находятся старые показания счётчика №1 = 15 7E 00 02
С_oldSet_adr_2 = [21, 128, 0, 2] # Адрес регистра (включая длину), в котором находятся старые показания счётчика №2 = 15 8E 00 02
С_oldSet_adr_3 = [21, 130, 0, 2] # Адрес регистра (включая длину), в котором находятся старые показания счётчика №3 = 15 82 00 02

C_Write_open = [21, 73, 0, 1, 2, 83, 0] # Адрес, и значения, которые нужно установить перед началом сеанса записи = 15 49 00 01 02 53 00
C_Short_init = [22, 140, 0, 4] # Форма малой инициализации (та самая, что требует ключ и вводится перед каждой записью) = 16 8C 00 04
C_Write_close = [21, 73, 0, 1, 2, 0, 0] # 15 49 00 01 02 00 00  Закрытие сеанса записи

С_newSet_adr_1 = [22, 122, 0, 4] # Адрес, по которому будут записаны новые показания (разность) = 16 7A 00 04
С_newSet_adr_2 = [22, 124, 0, 4] # Адрес, по которому будут записаны новые показания (разность) = 16 7C 00 04
С_newSet_adr_3 = [22, 126, 0, 4] # Адрес, по которому будут записаны новые показания (разность) = 16 7E 00 04
Trm = [28, 247, 25, 0] # Терминатор, последовательность, обозначающая конец записи (используется только для записи показаний счётчиков) = 1C F7 19 00

C_sth = [1, 10, 215, 35, 60, 0, 0, 192, 64, 0, 0, 128, 63, 1, 0, 0, 128, 63, 6] # Последовательность неизвестного назначения, нужна при записи весов
C_open_weight = [1, 0, 0, 0, 0, 0, 36, 116, 73] # Открытие переменной, хранящей весы
C_close_weight = [3, 0, 0, 0, 0, 6] # Закрытие переменной, хранящей весы



def read_from_port(lenght: int):
    mas = []
    while lenght > 0:
        mas.append(ser.read())
        lenght -= 1
    
    ans = []
    for n in mas:
        ans.append(struct.unpack('<B', n)[0])
    
    return ans


def CRC16(data: list): # Функция, вычисляющая контрольную сумму по методу CRC16, контрольная сумма идёт в конце каждого пакета
    for n in range(len(data)):
        data[n] = int(data[n])
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
    return crc # На выход получаем число, перевод которого в шестнадцатеричное представление даст нам контрольную сумм в прямом порядке !!!ПЕРЕД ОТПРАВКОЙ ОБЯЗАТЕЛЬНО РАЗДЕЛИТЬ ПО БАЙТАМ И РАЗВЕРНУТЬ В ОБРАТНЫЙ ПОРЯДОК!!!

def CRC16_to_send(int_data: int): # Получая на вход контрольную сумму, возвращаемую функцией CRC16(), в виде числа int, переводит его в стандартную форму (массив байт), и разворачивает в обратную последовательность
    ret = []
    ret.append(int_data % 256)
    ret.append(int_data // 256)
    return ret # Результат работы этой функции можно отправлять вместе с остальными данными

def get_Read(data: list): # Сбор полезной нагрузки из ответа, отправленного устройством
    stop = 0
    stop = len(data) - 2
    return data[3:stop]

def toHumanHex(trans: list):

    dic = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "A", 11: "B", 12: "C", 13: "D", 14: "E", 15: "F"}
    line = ''

    for n in trans:
        two = dic[n % 16]
        n //= 16
        line += dic[n % 16]
        line += two
        line += " "

    return line




def Transmit(msg: list, lenght: int = 0): # Составление контрольной суммы и отправка пакета данных
    temp = [] # Временный массив
    temp = CRC16(msg) # Вычисление контрольной суммы
    temp = CRC16_to_send(temp)
    msg.extend(temp)
    print("Master >>", toHumanHex(msg))

    

    ser.write(msg)

    ans = []
    ans = read_from_port(lenght)

    print("Slave  >>", toHumanHex(ans))
    time.sleep(2)
    return ans

def HEXtoFloat(data: list): # Получая на вход массив байт в прямом порядке, переводит его во Float
    data.reverse() # Для удобства вычислений переводим в обратный
    
    merge: int = 0
    for frag in range(len(data)):
        merge += data[frag] * (256 ** frag) # Полученные байты переводим в UInt

    return struct.unpack("<f", struct.pack("<I", merge))[0] # UInt переводим в байты, удобные для понимания библиотекой, которые после этого переводим во Float

def FloatToHEX(num: float): # Получая на вход Float, возвращает масив байт
    merge = struct.unpack(">I", struct.pack("<f", num))[0] # Float -> Байты -> UInt

    data = []
    for n in range(4): # Разбиваем UInt на отдельные байты, записанные в обратном порядке
        data.append(merge % 256)
        merge = merge // 256

    data.reverse() # Переводим в прямой порядок (для удобства понимания)
    return data

send = []


send.append(adress)
send.extend(C_Read)
send.extend(С_oldSet_adr_1)

oldSet1 = []
oldSet1 = Transmit(send, 9)
send.clear()
oldSet1 = get_Read(oldSet1) # Собираем полезные данные (Старые показания счётчика №1)
oldSet1.reverse() # Поскольку они представлены в обратном порядке, возвращаем его к стандартному (в пределах этой программы)


send.append(adress)
send.extend(C_Read)
send.extend(С_oldSet_adr_2)

oldSet2 = []
oldSet2 = Transmit(send, 9)
send.clear()
oldSet2 = get_Read(oldSet2)
oldSet2.reverse()


send.append(adress)
send.extend(C_Read)
send.extend(С_oldSet_adr_3)

oldSet3 = []
oldSet3 = Transmit(send, 9)
send.clear()
oldSet3 = get_Read(oldSet3)
oldSet3.reverse()

oldSet1f = HEXtoFloat(oldSet1)
oldSet2f = HEXtoFloat(oldSet2)
oldSet3f = HEXtoFloat(oldSet3)

print()
print('Показания 1:', oldSet1f)
print('Показания 2:', oldSet2f)
print('Показания 3:', oldSet3f)
print()

send = [] #Чтение записи о весах
send.append(adress)
send.extend(C_Read)
send.extend([21, 7, 0, 1])
mas_wht = []
mas_wht = Transmit(send, 100)
oldWht1 = mas_wht[31:35]
oldWht2 = mas_wht[50:54]
oldWht3 = mas_wht[69:73]



oldWht1.reverse()
oldWht2.reverse()
oldWht3.reverse()


print("\n" + f'Старое значение весов 1: {HEXtoFloat(oldWht1)}')
print(f'Старое значение весов 2: {HEXtoFloat(oldWht2)}')
print(f'Старое значение весов 3: {HEXtoFloat(oldWht3)}')