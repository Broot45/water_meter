# water_meter
Программное обеспечения для первичной настройки и штатной калибровки теплосчётчиков модели КАРАТ-Компакт 2-213

В процессе разработки также был реализован опрос единичного счётчика исходя из номера квартиры/адреса, а так-же алгоритм смены краткого адреса

Данное ПО использует протокол передачи MODBUS

Исключением для этого правила является алгоритм смены краткого адреса, использующий модификацию, схожую с M-BUS

Все сеансы общения приходятся на первый COM-порт, установленный на устройство операционной системы Linyx (Эту настройку можно изменить в глобальной переменной PORT в каждом файле индивидуально)
