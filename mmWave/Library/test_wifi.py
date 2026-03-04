from ksoc_wifi_connection import ConnectionOfWebsocket
import time

HOST = '192.168.2.1'
PORT = 80

if __name__ == '__main__':
    connection = ConnectionOfWebsocket()
    connection.connectDevice()
    # print(f'Chirp ID : {connection.getChipID()[1]}')
    print(f'read reg ({hex(0x50000504)}) : {hex(connection.readHWRegister(0x50000530)[1])}')
    print(f'write reg ({hex(0x50000504)}) : {connection.writeHWRegister(0x50000504, 0x00000000)}')
    print(f'read reg ({hex(0x50000504)}) : {hex(connection.readHWRegister(0x50000504)[1])}')
    # connection.setPowerSavingMode(2)
    # print(f'power saving mode: {connection.getPowerSavingMode()[1]}')
    connection.switchCollectionOfMultiResults(actions=0b1, read_interrupt=0, clear_interrupt=0, raw_size=(8192+2)*2, ch_of_RBank=1, reg_address=[])
    s = time.time_ns()
    for i in range(20):
        print(f'=================={i}==================')
        data = connection.getMultiResults()[1]
        # print(f'getMultiResults : {data}')
        # print(f'getMultiResults length : {data}')
        print(f'getMultiResults time : {(time.time_ns()-s)/1000000} ms')
        s = time.time_ns()


    connection.switchCollectionOfMultiResults(actions=0b0, read_interrupt=0, clear_interrupt=0, raw_size=(8192 + 2) * 2,
                                              ch_of_RBank=1, reg_address=[])

    connection.switchCollectionOfMultiResults(actions=0b0, read_interrupt=0, clear_interrupt=0, raw_size=(8192 + 2) * 2,
                                              ch_of_RBank=1, reg_address=[])
    connection.disconnectDevice()
