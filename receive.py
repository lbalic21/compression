import serial
import datetime
import pytz
import psycopg2
from time import sleep

serIn = serial.Serial(          
    port='COM17',
    baudrate = 230400,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=None
)

prefixTable = {
    "00": 0,
    "010": 1,
    "011": 2,
    "100": 3,
    "101": 4,
    "110": 5,
    "1110": 6,
    "11110": 7,
    "111110": 8,
    "1111110": 9,
    "11111110": 10,
    "111111110": 11,
    "1111111110": 12,
    "11111111110": 13,
    "111111111110": 14,
    "1111111111110": 15,
    "11111111111110": 16,
    "111111111111110": 17,
    "1111111111111110": 18,
    "11111111111111110": 19
}

def decodeValue(codedValue: int, numBits: int):

    val = 0

    if numBits > 0 :
        if codedValue >= pow(2, numBits - 1) :
            val = codedValue
        else :
            val = codedValue - (pow(2, numBits) - 1)

    return val


def getBits(byte, msbFirst=True):

    byte = int.from_bytes(byte, 'big')

    masks = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
    if not msbFirst :
        masks.reverse()

    for mask in masks:
        yield 1 if byte & mask else 0


def decodeBuff(buff):
    numMeasurements = int.from_bytes(buff[3] + buff[4], 'big', signed = False)
    packet = int.from_bytes(buff[2], 'big', signed = False)
    startingAcc = int.from_bytes(buff[5] + buff[6] + buff[7] + buff[8], 'big', signed=True)
    buff = buff[9:]
    #print(startingAcc)
    prefix = ""
    currCodeLen = 0
    lastCodeLen = 0
    currCode = 0
    accDiffs = []

    for byte in buff :
        for bit in getBits(byte) :
            if numMeasurements <= 0:
                break
            if currCodeLen == 0 :
                prefix += str(bit)
            else :
                currCode = currCode*2 + bit
                currCodeLen -= 1
                if currCodeLen == 0 :
                    accDiffs.append(decodeValue(currCode, lastCodeLen))
                    numMeasurements -= 1
                    currCode = 0
            if prefix in prefixTable :
                currCodeLen = prefixTable[prefix]
                if currCodeLen == 0:
                    accDiffs.append(int(0))
                    numMeasurements -= 1
                lastCodeLen = currCodeLen
                prefix = ""

    accs = [startingAcc]
    for diff in accDiffs :
        accs.append(accs[-1] + diff)
    accs.append(packet)
    return accs

def main():
    i = 0
    brojPaketa = 0
    TZ = pytz.timezone('Europe/Zagreb')

    try:
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="sensor_data")

        cursor = connection.cursor()
        # Executing a SQL query to insert datetime into table
       
        #print("1 item inserted successfully")

        serIn.set_buffer_size(rx_size=10000)
        if(serIn.is_open == 'false') :
            serIn.open()
        buff = []
        decodedData = []
        flag = 0
        packet = 0

        while(1):
            #print("A")
            data = serIn.read(size=1) 
            buff.append(data)
            if buff[0] != b"H" :
                buff = []

            if len(buff) > 1 and buff[1] != b"H" :
                buff = []

            if len(buff) == 2 and buff[0] == b"H" and buff[1] == b"H" :
                flag = 1

            if(flag == 1) :
                while(len(buff) < 244):
                    a = serIn.read(1)
                    buff.append(a)
                flag = 0
            dataG = 0
            if len(buff) == 244 :
                brojPaketa += 1
                flag = 0
                #print(buff)
                decodedData = decodeBuff(buff)
                packet = decodedData[-1]
                #print(packet)
                decodedData = decodedData[:-1]
                print("newPackage")
                print(brojPaketa)
                for data in decodedData :
                    i += 1
                    if packet == 1 or packet == 2 :
                        dataG = data / 1024
                    elif packet == 3 or packet == 4 :
                        dataG = data / 256000
                    #sleep(0.1)
                    #serOut.write(bytes(str(data).encode('utf-8')))
                    #serOut.write(bytes(str('\n').encode('utf-8')))
                    #point = (
                    #    Point("accelerometer")
                    #    .field("acceleration", data)
                    #)
                    if packet == 1 or packet == 3:
                        insert_query = """ INSERT INTO accelerometer1 (id, data, time) VALUES (%s, %s, %s)"""
                    elif packet == 2 or packet == 4:
                        insert_query = """ INSERT INTO accelerometer2 (id, data, time) VALUES (%s, %s, %s)"""
                    time = datetime.datetime.now(TZ)
                    #
                    # print(time)
                    acc_tuple = (i, dataG, time)
                    cursor.execute(insert_query, acc_tuple)
                    connection.commit()
                    #print(data)
                    #file.write(str(data) + "\n")       
                    #write_api.write(bucket=bucket, record=point)

                buff = []
                #print(decodedData)
                decodedData = []
                #print()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__" :
    main()
