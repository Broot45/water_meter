import struct # Для работы с байтами
import serial # Для работы с портами
import time # КД запросов

PORT = '/dev/ttyUSB0' # Порт общения с платой

fullAddr = int(input("Полный адрес: ")) # Полный адрес счётчика, 8 цифр
shortAddr = int(input("Краткое обращение: ")) # Краткий адрес, по которому общаются остальные программы, 0-247

#ser = serial.Serial(PORT, baudrate=2400, timeout = 0.5) # Открытие порта с частотой и таймаутом

C_OpenFullAddr = [16, 64, 253, 61, 22, 104, 11, 11, 104] # 10 40 FD 3D 16 68 0B 0B 68
C_FullAddrPre = [67, 253, 82]
C_FullAddrPost = [255, 255, 255, 255]
C_Term = [22]

# Скопированный блок, в данном случае в качестве параметра lenght передаётся int длины, поскольку автовычисление не сработает
def read_from_port(lenght): # Ахтунг, в функции не предусмотрена защита от некорректных данных
            global ser
            
            if (not (type(lenght) is int) and (lenght != None)): return [None] # Отсев некорректных значений

            mas = [] # Массив первичных значений, содержит элементы типа byte, обращаться с сторожностью, поскольку питон любит их переводить в хуйню без спросу
            
            if lenght == None: # Если значение не установлено (по умолчанию None), функция сама из содержания вычислит, сколько нужно прочесть
                for n in "12345": mas.append(ser.read()) # Читаем первые пять байт, которые гарантированно будут присутствовать в корректном ответе
                if struct.unpack('<B', mas[1])[0] == 16: lenght = 3 # Если ответ на команду записи, то мы читаем 5 + 3 байта, сообщение об успешной записи
                elif struct.unpack('<B', mas[1])[0] == 3: lenght = struct.unpack('<B', mas[2])[0] # Если ответ на команду чтения, то мы читаем 5 байт системной информации (адрес, команда, $Количество и два байта CRC16), + $Количество
                else: # Если ответ не стандартен
                    lenght = 0
                    ser.close()
                    ser = serial.Serial(PORT, 2400, timeout = 0.5)


            while lenght > 0: # Дочитываем $Оставшееся количество байт (если число было фиксированным, то $Оставшееся = $Необходимое)
                mas.append(ser.read())
                lenght -= 1
            
            ans = [] # Массив вторичных, готовых к отправке значений
            for n in mas:
                try:
                    ans.append(struct.unpack('<B', n)[0]) # Перевод первичного значения во вторичное
                except:
                    ans.append(255)
            return ans


def toHumanHex(trans: list): # Перевод последовательности десятичных байт в шестнадцатеричные

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
        #temp = CRC16(msg) # Вычисление контрольной суммы
        #temp = CRC16_to_send(temp)
        msg.extend(temp)
        print("Master >>", toHumanHex(msg))
    
        

        ser.write(msg)

        ans = []
        ans = read_from_port(lenght)

        print("Slave  >>", toHumanHex(ans))
        time.sleep(0.5)
        return ans

def Checksum(line: list): # В данном случае используется примитивная контрольная сумма, 
    summ = int(0)  
    for n in line:
          summ += n
    
    summ %= 256
    
    return summ

def HumanDecInHex(decmas: list):
    hexmas = []
    for dec in decmas:
        digit = 0
        hehex = 0
        while dec > 0:
            chr = dec % 10
            dec = dec // 10
            hehex += chr * (16 ** digit)
            digit += 1
        hexmas.append(hehex)

    return hexmas
      

# Обращение по первому адресу

SendedFullAddr = [] # Преобразование полного адреса в готовый к отправке вид
while fullAddr > 0:
    SendedFullAddr.append(fullAddr % 100)
    fullAddr //= 100


Control = [] # Сбор последовательности, к которой будет применима контрольная сумма
Control.extend(C_FullAddrPre) 
Control.extend(HumanDecInHex(SendedFullAddr))
Control.extend(C_FullAddrPost)
Control.append(Checksum(Control))

Send = []
Send.extend(C_OpenFullAddr)
Send.extend(Control)
Send.extend(C_Term)
print(toHumanHex(Send))

