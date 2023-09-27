import csv
import struct
import serial
ser = serial.Serial('/dev/ttyUSBx', 2400)

with open('some.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)










adress = 45 # адрес

newSet1 = float(120.0) # новые показания счётчиков
newSet2 = float(40.0) # новые показания счётчиков
newSet3 = float(3.0) # новые показания счётчиков


#Данные, необходимые для записи
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


#=================================Тест на нескольких машинах=============================
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
    return crc # На выход получаем число, перевод которого в шестнадцатеричное представление даст нам контрольную сумм в прямом порядке !!!ПЕРЕД ОТПРАВКОЙ ОБЯЗАТЕЛЬНО РАЗДЕЛИТЬ ПО БАЙТАМ И РАЗВЕРНУТЬ В ОБРАТНЫЙ ПОРЯДОК!!!

def CRC16_to_send(int_data: int): # Получая на вход контрольную сумму, возвращаемую функцией CRC16(), в виде числа int, переводит его в стандартную форму (массив байт), и разворачивает в обратную последовательность
    ret = []
    ret.append(int_data % 256)
    ret.append(int_data // 256)
    return ret # Результат работы этой функции можно отправлять вместе с остальными данными
#======================================Тест на нескольких машинах================================
def get_Read(data: list): # Сбор полезной нагрузки из ответа, отправленного устройством
    stop = len(data) - 2
    return data[3:stop]

def Transmit(msg: list): # Составление контрольной суммы и отправка пакета данных
    temp = [] # Временный массив
    temp = CRC16(msg) # Вычисление контрольной суммы
    temp = CRC16_to_send(temp)
    msg.extend(temp)
    ser.writelines(send)
    ans = ser.readline()
    send.clear()
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


# Подготовка данных к записи ==============================

send = [] # Лист для отправки байт
# Сборка запроса на получение ключа
send.append(adress)
send.extend(C_Read)
send.extend(C_Key_adr)

Key = Transmit(send) # (адрес, команда, длина, сама инфа, CRC16, CRC16)
send.clear()
Key = get_Read(Key)


# Сбор старых показаний
send.append(adress)
send.extend(C_Read)
send.extend(С_oldSet_adr_1)

oldSet1 = Transmit(send)
send.clear()
oldSet1 = get_Read(oldSet1) # Собираем полезные данные (Старые показания счётчика №1)
oldSet1.reverse() # Поскольку они представлены в обратном порядке, возвращаем его к стандартному (в пределах этой программы)


send.append(adress)
send.extend(C_Read)
send.extend(С_oldSet_adr_2)

oldSet2 = Transmit(send)
send.clear()
oldSet2 = get_Read(oldSet2)
oldSet2.reverse()


send.append(adress)
send.extend(C_Read)
send.extend(С_oldSet_adr_3)

oldSet3 = Transmit(send)
send.clear()
oldSet3 = get_Read(oldSet3)
oldSet3.reverse()

oldSet1f = HEXtoFloat(oldSet1)
oldSet2f = HEXtoFloat(oldSet2)
oldSet3f = HEXtoFloat(oldSet3)


diffSet1 = FloatToHEX(newSet1 - oldSet1f) # В устройства подаётся разность старого и нового значений, в следствие чего этот фрагмент имеет место быть
diffSet2 = FloatToHEX(newSet2 - oldSet2f)
diffSet3 = FloatToHEX(newSet3 - oldSet3f)

diffSet1.reverse() # Перевод в обратный порядок
diffSet2.reverse()
diffSet3.reverse()

# Запись данных ==================================

send = [] # Обьявление начала сеанса записи
send.append(adress)
send.extend(C_Write)
send.extend(C_Write_open)
Transmit(send) # Принимать значение не требуется
send.clear()

send.append(adress) # Обьявление начала экземпляра записи
send.extend(C_Write)
send.extend(C_Short_init)
send.extend(C_Key_len)
send.extend(Key)
Transmit(send) # Принимать значение не требуется
send.clear()

send.append(adress) # Экземпляр записи
send.extend(C_Write)
send.extend(С_newSet_adr_1)
send.extend(C_Key_len)
send.extend(diffSet1)
send.extend(Trm)
Transmit(send)
send.clear()


send.append(adress) # Обьявление начала экземпляра записи
send.extend(C_Write)
send.extend(C_Short_init)
send.extend(C_Key_len)
send.extend(Key)
Transmit(send) # Принимать значение не требуется
send.clear()

send.append(adress) # Экземпляр записи
send.extend(C_Write)
send.extend(С_newSet_adr_2)
send.extend(C_Key_len)
send.extend(diffSet2)
send.extend(Trm)
Transmit(send)
send.clear()


send.append(adress) # Обьявление начала экземпляра записи
send.extend(C_Write)
send.extend(C_Short_init)
send.extend(C_Key_len)
send.extend(Key)
Transmit(send) # Принимать значение не требуется
send.clear()

send.append(adress) # Экземпляр записи
send.extend(C_Write)
send.extend(С_newSet_adr_3)
send.extend(C_Key_len)
send.extend(diffSet3)
send.extend(Trm)
Transmit(send)
send.clear()


send.append(adress)
send.extend(C_Write_close)
Transmit(send)
send.clear()

#=========================== Запись показаний завершена ===============================

# Изменение весов

# Базовые данные
newWht1f = float(10.0)
newWht2f = float(10.0)
newWht3f = float(10.0)

C_sth = [1, 10, 215, 35, 60, 0, 0, 192, 64, 0, 0, 128, 63, 1, 0, 0, 128, 63, 6] # Последовательность неизвестного назначения, нужна при записи весов
C_open_weight = [1, 0, 0, 0, 0, 0, 36, 116, 73] # Открытие переменной, хранящей весы
C_close_weight = [3, 0, 0, 0, 0, 6] # Закрытие переменной, хранящей весы



send = [] # Обьявление начала сеанса записи
send.append(adress)
send.extend(C_Write)
send.extend(C_Write_open)
Transmit(send) # Принимать значение не требуется
send.clear()


temp = []
send = [] # Обьявление начала сеанса записи
send.append(adress)
send.extend(C_Write)
send.extend([21, 7, 0, 76, 152]) #Адрес регистра, количество регистров, и количество байт, отправляемых для изменения весов
send.extend(C_sth)
send.extend(C_open_weight)

temp = FloatToHEX(newWht1f) # Вес №1
send.extend(temp)
temp.clear()

send.extend(C_close_weight)
send.extend(C_open_weight)

temp = FloatToHEX(newWht2f) # Вес №2
send.extend(temp)
temp.clear()

send.extend(C_close_weight)
send.extend(C_open_weight)

temp = FloatToHEX(newWht3f) # Вес №3
send.extend(temp)
temp.clear()

send.extend(C_close_weight)
send.extend(C_sth)
send.extend(C_open_weight)

temp = FloatToHEX(newWht1f) # Вес №1
send.extend(temp)
temp.clear()

send.extend(C_close_weight)
send.extend(C_open_weight)

temp = FloatToHEX(newWht2f) # Вес №2
send.extend(temp)
temp.clear()

send.extend(C_close_weight)
send.extend(C_open_weight)

temp = FloatToHEX(newWht3f) # Вес №3
send.extend(temp)
temp.clear()

send.extend(C_close_weight)
Transmit(send)
send.clear()


send.append(adress)
send.extend(C_Write)
send.extend(C_Write_close)
Transmit(send)
send.clear()
