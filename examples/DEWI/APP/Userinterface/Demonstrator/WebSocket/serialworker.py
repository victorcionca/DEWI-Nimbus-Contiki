import serial
import time
import multiprocessing
import dewi as DBConnection

## Change this to match your local settings
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 115200

class SerialProcess(multiprocessing.Process):

    dewi = DBConnection.dewi()
    addrMasterSlave = ""

    def __init__(self, input_queue, output_queue):
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)

    def close(self):
        self.sp.close()

    def writeSerial(self, data):
        self.sp.write(data.encode())
        # time.sleep(1)

    def readSerial(self):
        return self.sp.readline().replace("\n", "")

    def collectAddrMasterSlave(self,data):
        if 'MasterSlave_addr data:' in str(data):
            self.addrMasterSlave = data[data.index("'")+1:data.index("'",data.index("'")+1,len(data))]
            return True
        else:
            return False

    def toHex(self,s):
        return hex(int(s,16))[2:]

    def collectAddrM_addrS(self):
        self.addrM1 = self.addrMasterSlave[0:2]
        self.addrM1 = self.toHex(self.addrM1);
        self.addrM2 = self.addrMasterSlave[2:4]
        self.addrM2 = self.toHex(self.addrM2)
        self.addrM = self.addrM1+":"+self.addrM2;
        self.addrS1 = self.addrMasterSlave[4:6]
        self.addrS1 = self.toHex(self.addrS1)
        self.addrS2 = self.addrMasterSlave[6:8]
        self.addrS2 = self.toHex(self.addrS2)
        self.addrM = self.addrM1+":"+self.addrM2;
        self.addrS = self.addrS1+":"+self.addrS2;

    def handle_tab(self):
        self.order = 0
        self.dewi.save_node_details(self.addrS,self.addrM,self.order);

    def saveIntoDewiDB(self):
        self.collectAddrM_addrS();
        self.handle_tab();


    def sendSerialData(self,data):
        if self.collectAddrMasterSlave(data) == True:
            self.saveIntoDewiDB();

        if "Temperature" in data:
            T_addr = data[data.index("(")+1:data.index(")")]
            T_addr = T_addr[0:2]+":"+T_addr[2:4]
            temperature = data[data.index("'")+1:data.index("C")+1]
            self.dewi.add_temperature_data(T_addr, temperature)

        if "Battery" in data:
            B_addr = data[data.index("(")+1:data.index(")")]
            B_addr = B_addr[0:2]+":"+B_addr[2:4]
            temperature = data[data.index("'")+1:data.index("'",data.index("'")+1,len(data))]
            self.dewi.add_battery_stat(B_addr, temperature)

        if "colour" in data:
            C_addr = data[data.index("(")+1:data.index(")")]
            C_addr = C_addr[0:2]+":"+C_addr[2:4]
            colour = data[data.index("'")+1:data.index("'",data.index("'")+1,len(data))]
            self.dewi.add_colour_stat(C_addr, colour)

        if "Stats" in data:
            addr = data[data.index("(")+1:data.index(")")]
            addr = addr[0:2]+":"+addr[2:4]
            splitted = data.split("'");
            packets = splitted[1];
            latency = int(splitted[3]);
            self.dewi.add_statistics(addr, packets, latency)
            
    def sendToSerial(self,data):
        if "resetstatistics" in data:
            self.dewi.cleanStatsTable()
        if "topologyrefresh" in data:
            self.dewi.cleanNodeLinkTables()
            

    def run(self):

        self.sp.flushInput()

        while True:
            # look for incoming tornado request
            if not self.input_queue.empty():
                data = self.input_queue.get()
                self.sendToSerial(data)
                # send it to the serial device
                self.writeSerial(data)
                self.output_queue.put("writing to serial: " + data)
                print "writing to serial: " + data

            # look for incoming serial data
            if (self.sp.inWaiting() > 0):
                data = self.readSerial()
                self.sendSerialData(data)
                print "reading from serial: " + data
                # send it back to tornado
                self.output_queue.put(data)
