import csv
import struct
import serial
import time

log = open("log.txt", "w")
log.write("ID сеанса:" + str(int(time.time())%1000000) + "\n") #6-и значный ID генерируется из последних 6-и цифр текущего времени в секундах с начала эпохи (ID проходит один круг каждые ~11 дней)
log.write("Время сеанса:" + time.asctime() + "\n") # Часы могут быть неверными

#ser = serial.Serial('/dev/ttyUSB0', 2400)
PORT = '/dev/ttyUSB0' # Используемый порт, наименование порта для общения будет браться отсюда
csvPath = 'value.csv' # Путь к csv файлу со списком указываемых данных

with open(csvPath, newline='') as f: 
    reader = csv.reader(f)

    for base in reader:

        ser = serial.Serial(PORT, baudrate=2400, timeout = 0.5)

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

        C_sth = [1, 10, 215, 35, 60, 0, 0, 192, 64, 0, 0, 128, 63, 1, 0, 0, 128, 63, 6] # Последовательность неизвестного назначения, нужна при записи весов
        C_open_weight = [1, 0, 0, 0, 0, 0, 36, 116, 73] # Открытие переменной, хранящей весы
        C_close_weight = [3, 0, 0, 0, 0, 6] # Закрытие переменной, хранящей весы



        def read_from_port(lenght): # Ахтунг, в функции не предусмотрена защита от некорректных данных

            # Все условия подразумевают исправную работу счётчиков, сети, и самой программы в целом...
            # ...Если потребуется это исправить - можно засунуть всю функцию в try, и при любой ошибке, вместо чтения, просто... 
            # ...открывать и закрывать порт, понадеявшись, что в данный момент ответ был нам не сильно нужен

            if (not (type(lenght) is int) and (lenght != None)): return [None] # Отсев некорректных значений

            mas = [] # Массив первичных значений, содержит элементы типа byte, обращаться с сторожностью, поскольку питон любит их переводить в хуйню без спросу
            
            if lenght == None: # Если значение не установлено (по умолчанию None), функция сама из содержания вычислит, сколько нужно прочесть
                for n in "12345": mas.append(ser.read()) # Читаем первые пять байт, которые гарантированно будут присутствовать в корректном ответе
                if struct.unpack('<B', mas[1])[0] == 16: lenght = 3 # Если ответ на команду записи, то мы читаем 5 + 3 байта, сообщение об успешной записи
                elif struct.unpack('<B', mas[1])[0] == 3: lenght = struct.unpack('<B', mas[2])[0] # Если ответ на команду чтения, то мы читаем 5 байт системной информации (адрес, команда, $Количество и два байта CRC16), + $Количество

            while lenght > 0: # Дочитываем $Оставшееся количество байт (если число было фиксированным, то $Оставшееся = $Необходимое)
                mas.append(ser.read())
                lenght -= 1
            
            ans = [] # Массив вторичных, готовых к отправке значений
            for n in mas:
                ans.append(struct.unpack('<B', n)[0]) # Перевод первичного значения во вторичное
            
            return ans
            



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

        def get_Read(data: list): # Сбор полезной нагрузки из ответа, отправленного устройством
            stop = 0
            stop = len(data) - 2
            return data[3:stop]

        def toHumanHex(trans: list):

            if trans[0] == None: return "None"

            dic = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "A", 11: "B", 12: "C", 13: "D", 14: "E", 15: "F"}
            line = ''

            for n in trans:
                two = dic[n % 16]
                n //= 16
                line += dic[n % 16]
                line += two
                line += " "

            return line




        def Transmit(msg: list, lenght = None): # Составление контрольной суммы и отправка пакета данных
            temp = [] # Временный массив
            temp = CRC16(msg) # Вычисление контрольной суммы
            temp = CRC16_to_send(temp)
            msg.extend(temp)
            print("Master >>", toHumanHex(msg))
            log.write("Master >>" + toHumanHex(msg) + "\n")
	    
            

            ser.write(msg)

            ans = []
            ans = read_from_port(lenght)

            print("Slave  >>", toHumanHex(ans))
            log.write("Slave  >>" + toHumanHex(ans) + "\n")
            time.sleep(0.5)
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



        log.write("\n\n\n" + "Адрес: " + base[0] + "\n")
        print("\n\n\n", "Адрес:", base[0])


        log.write("Счётчики:" + "\n")
        print("Счётчики:")

        log.write("\t1: " + base[1] + "\n")
        print("\t1:", base[1])

        log.write("\t2: " + base[2] + "\n")
        print("\t2:", base[2])

        log.write("\t3: " + base[3] + "\n\n")
        print("\t3:", base[3], end = "\n\n")

        log.write("Веса импульсов: " + "\n")
        print("Веса импульсов: ")

        log.write("\t1: " + base[4] + "\n")
        print("\t1:", base[4])

        log.write("\t2: " + base[5] + "\n")
        print("\t2:", base[5])

        log.write("\t3: " + base[6] + "\n\n")
        print("\t3:", base[6], end = "\n\n")
        print ('base[0]', base[0]) 
        adress = int(base[0]) # адрес
        newSet1 = float(base[1]) # новые показания счётчиков
        newSet2 = float(base[2]) # новые показания счётчиков
        newSet3 = float(base[3]) # новые показания счётчиков


        log.write("\n\n\nНачало сеанса записи\n\n")


        # Подготовка данных к записи ==============================

        send = [] # Лист для отправки байт
        # Сборка запроса на получение ключа
        send.append(adress)
        send.extend(C_Read)
        send.extend(C_Key_adr)

        Key = []
        Key = Transmit(send) # (адрес, команда, длина, сама инфа, CRC16, CRC16)
        send.clear()
        Key = get_Read(Key)

        log.write("Ключ для записи значений: " + toHumanHex(Key) + "\n")
        print("Key =", Key)


        # Сбор старых показаний
        send.append(adress)
        send.extend(C_Read)
        send.extend(С_oldSet_adr_1)
        
        oldSet1 = []
        oldSet1 = Transmit(send)
        send.clear()
        oldSet1 = get_Read(oldSet1) # Собираем полезные данные (Старые показания счётчика №1)
        oldSet1.reverse() # Поскольку они представлены в обратном порядке, возвращаем его к стандартному (в пределах этой программы)
        

        send.append(adress)
        send.extend(C_Read)
        send.extend(С_oldSet_adr_2)

        oldSet2 = []
        oldSet2 = Transmit(send)
        send.clear()
        oldSet2 = get_Read(oldSet2)
        oldSet2.reverse()


        send.append(adress)
        send.extend(C_Read)
        send.extend(С_oldSet_adr_3)

        oldSet3 = []
        oldSet3 = Transmit(send)
        send.clear()
        oldSet3 = get_Read(oldSet3)
        oldSet3.reverse()

        oldSet1f = HEXtoFloat(oldSet1)
        oldSet2f = HEXtoFloat(oldSet2)
        oldSet3f = HEXtoFloat(oldSet3)
        
        log.write("Старые показания 1: " + str(oldSet1f) + "\n")
        log.write("Старые показания 2: " + str(oldSet2f) + "\n")
        log.write("Старые показания 3: " + str(oldSet3f) + "\n")
        print('Показания 1:', oldSet1f)
        print('Показания 2:', oldSet2f)
        print('Показания 3:', oldSet3f)

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
        send.extend(C_Key_len);diffSet1.reverse()
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
        send.extend(C_Key_len);diffSet2.reverse()
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
        send.extend(C_Key_len);diffSet3.reverse()
        send.extend(diffSet3)
        send.extend(Trm)
        Transmit(send)
        send.clear()


        send.append(adress)
        send.extend(C_Write)
        send.extend(C_Write_close)
        Transmit(send)
        send.clear()

        # #=========================== Запись показаний завершена ===============================

        log.write("\n\nЗапись показаний завершена\n\nНачинается запись весов" + "\n")

        # Изменение весов
        ser.close()
        ser = serial.Serial(PORT, 2400, timeout = 0.5)
        

        send = [] # Обьявление начала сеанса записи
        send.append(adress)
        send.extend(C_Write)
        send.extend(C_Write_open)
        Transmit(send)
        send.clear()

        send = [] #Чтение записи о весах
        send.append(adress)
        send.extend(C_Read)
        send.extend([21, 7, 0, 1])
        mas_wht = []
        mas_wht = Transmit(send)
        oldWht1 = mas_wht[31:35]
        oldWht2 = mas_wht[50:54]
        oldWht3 = mas_wht[69:73]



        oldWht1.reverse()
        oldWht2.reverse()
        oldWht3.reverse()

        if base[4] == None or base[4] == "" : newWht1f = HEXtoFloat(oldWht1); oldWht1.reverse()
        else: newWht1f = float(base[4])
        
        if base[5] == None or base[5] == "": newWht2f = HEXtoFloat(oldWht2); oldWht2.reverse()
        else: newWht2f = float(base[5]) 

        if base[6] == None or base[6] == "": newWht3f = HEXtoFloat(oldWht3); oldWht3.reverse()
        else: newWht3f = float(base[6])



        log.write(f'Старое значение весов 1: {HEXtoFloat(oldWht1)}' + "\n")
        log.write(f'Старое значение весов 2: {HEXtoFloat(oldWht2)}' + "\n")
        log.write(f'Старое значение весов 3: {HEXtoFloat(oldWht3)}' + "\n")

        oldWht1.reverse()
        oldWht2.reverse()
        oldWht3.reverse()

        print(f'Вес 1: {HEXtoFloat(oldWht1)}')
        print(f'Вес 2: {HEXtoFloat(oldWht2)}')
        print(f'Вес 3: {HEXtoFloat(oldWht3)}')

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

        # Очистка переменных
        del adress
        del newSet1
        del newSet2
        del newSet3
        del C_Read
        del C_Write
        del C_Key_adr
        del C_Key_len
        del С_oldSet_adr_1
        del С_oldSet_adr_2
        del С_oldSet_adr_3
        del C_Write_open
        del C_Short_init
        del C_Write_close
        del С_newSet_adr_1
        del С_newSet_adr_2
        del С_newSet_adr_3
        del Trm
        del send
        del Key
        del oldSet1
        del oldSet2
        del oldSet3
        del oldSet1f
        del oldSet2f
        del oldSet3f
        del diffSet1
        del diffSet2
        del diffSet3
        del temp
        del newWht1f

        ser.close()
        log.write("Сеанс записи завершен" + "-"*25 + "\n")


log.write("Все сеансы записи успешно завершены" + "\n" + "="*45 + "\n")
log.close()