from PyQt5 import QtWidgets
from qline import Ui_main  # импорт нашего сгенерированного файла
import sys
from PyQt5.QtCore import QTimer
import socket
from pyModbusTCP.client import ModbusClient
import re


class mywindow(QtWidgets.QMainWindow):
    READ_CR = 0
    READ_DI = 1
    READ_HR = 2
    READ_IR = 3
    WRITE_MC = 4
    WRITE_MR = 5
    WRITE_SC = 6
    WRITE_SR = 7

    timer = QTimer()
    host = "192.168.10.201"
    unit_id = 2
    c = ModbusClient(host=host, unit_id=unit_id,
                     timeout=1, auto_open=True, auto_close=True)
    c.open()

    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_main()
        self.ui.setupUi(self)

    def test(self):
        """
        test foo with ip this pc
        """
        print(socket.gethostbyname(socket.gethostname()))
        self.send_cmd()

    def read_hr(self):
        """
        foo with reading hr
        """
        self.regs = self.c.read_holding_registers(0, 2)
        if self.regs:
            print(self.regs)
        else:
            print("read error")

    def send_cmd(self):
        """
        send modbus TCP command
        """
        buf = "Отправлено "
        choosed_fnct = self.ui.funct_cb.currentIndex()
        adr = self.ui.adr_sb.value()
        if choosed_fnct is self.READ_CR:
            buf += "Read Coil Register "
            self.regs = self.c.read_coils(adr, self.get_value())
        elif choosed_fnct is self.READ_DI:
            buf += "Read Digital Input "
            self.regs = self.c.read_discrete_inputs(adr, self.get_value())
        elif choosed_fnct is self.READ_HR:
            buf += "Read Holding Register "
            self.regs = self.c.read_holding_registers(adr, self.get_value())
        elif choosed_fnct is self.READ_IR:
            buf += "Read Input Register "
            self.regs = self.c.read_input_registers(adr, self.get_value())
        elif choosed_fnct is self.WRITE_MC:
            buf += "Write Multiple Coil "
            print(self.get_value())
            self.regs = self.c.write_multiple_coils(adr, self.get_value())
            print("read WRITE_MC")
        elif choosed_fnct is self.WRITE_MR:
            buf += "Write Multiple Register "
            print(self.get_value())
            self.regs = self.c.write_multiple_registers(adr, self.get_value())
            print("read WRITE_MR")
        elif choosed_fnct is self.WRITE_SC:
            buf += "Write Single Coil "
            self.regs = self.c.write_single_coil(adr, self.get_value())
        elif choosed_fnct is self.WRITE_SR:
            buf += "Write Single Register "
            self.regs = self.c.write_single_register(adr, self.get_value())

        buf += "по адресу " + str(adr)
        try:
            if choosed_fnct >= self.WRITE_MC:
                buf += " значения " +\
                       ",".join([str(i) for i in self.get_value()])
            else:
                buf += " " + str(self.get_value()) + " значений"
        except TypeError:
            buf += " значение "
            buf += str(self.get_value())

        self.ui.log_te.appendPlainText(buf)
        if self.regs:
            print(self.regs)
            if type(self.regs) != bool:
                for i in range(len(self.regs)):
                    if type(self.regs[i]) == bool:
                        data = 1 if self.regs[i] else 0
                        self.ui.data_tw.setItem(i, 2,
                                                QtWidgets.QTableWidgetItem(str(data)))
                    else:
                        self.ui.data_tw.setItem(i, 2, QtWidgets.QTableWidgetItem(str(self.regs[i])))

                buf = "Получено " + ",".join([str(i) for i in self.regs])
                self.ui.log_te.appendPlainText(buf)
            else:
                if self.regs:
                    self.ui.log_te.appendPlainText("Успешно записано")
                else:
                    self.ui.log_te.appendPlainText("Не записано")

        else:
            print("read error")
            self.ui.log_te.appendPlainText("Проблема с отправкой")

    def connect(self):
        """
        initialisation modbus TCP Client
        """
        self.c.host = self.ui.ip_le.text()
        if self.check_ip(self.ui.ip_le.text()):
            self.c = ModbusClient(host=self.host,
                                  unit_id=self.unit_id, timeout=1,
                                  auto_open=True, auto_close=True)
        else:
            print("ip кривой")
        print('id устройства', self.unit_id)
        self.c.open()
        print(self.ui.ip_le.text())

    def cntRow_changed(self, cnt):
        self.update_table(cnt)

    def update_table(self, cnt):
        """
        update table widget with data
        """
        if(self.ui.data_tw.rowCount() < cnt):
            for i in range(self.ui.data_tw.rowCount(), cnt):
                self.ui.data_tw.insertRow(i)
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(i))
                self.ui.data_tw.setItem(i, 1, item)
                self.ui.data_tw.setItem(i, 2,
                                        QtWidgets.QTableWidgetItem(str(0)))
        else:
            for i in range(cnt, self.ui.data_tw.rowCount()):
                self.ui.data_tw.removeRow(i)

        self.update_data_type_clmn()

    def get_value(self):
        """
        get value from tab widget
        """
        choosed_fnct = self.ui.funct_cb.currentIndex()

        if choosed_fnct is self.READ_CR or\
                choosed_fnct is self.READ_DI or\
                choosed_fnct is self.READ_HR or\
                choosed_fnct is self.READ_IR:
            return self.ui.cnt_sb.value()
        elif choosed_fnct is self.WRITE_MC:
            ret = [int(self.ui.data_tw.item(i, 2).text()) > 0
                   for i in range(self.ui.data_tw.rowCount())]
            return ret
        elif choosed_fnct is self.WRITE_MR:
            ret = [int(self.ui.data_tw.item(i, 2).text())
                   for i in range(self.ui.data_tw.rowCount())]
            return ret
        elif choosed_fnct is self.WRITE_SC:
            ret = int(self.ui.data_tw.item(0, 2).text()) > 0
            return ret
        elif choosed_fnct is self.WRITE_SR:
            ret = int(self.ui.data_tw.item(0, 2).text())
            return ret

    def update_data_type_clmn(self):
        choosed_fnct = self.ui.funct_cb.currentIndex()
        fnct_name = str()
        if choosed_fnct is self.READ_CR\
           or choosed_fnct is self.WRITE_MC\
           or choosed_fnct is self.WRITE_SC:
            fnct_name = "Coil register"
        elif choosed_fnct is self.READ_DI:
            fnct_name = "Discret input"
        elif choosed_fnct is self.READ_HR or\
            choosed_fnct is self.WRITE_SR\
                or choosed_fnct is self.WRITE_MR:
            fnct_name = "Holding Register"
        elif choosed_fnct is self.READ_IR:
            fnct_name = "Input Register"

        for i in range(self.ui.data_tw.rowCount()):
            self.ui.data_tw.setItem(i, 0,
                                    QtWidgets.QTableWidgetItem(fnct_name))

    def update_adrs(self):
        curr_adr = self.ui.adr_sb.value()
        for i in range(self.ui.data_tw.rowCount()):
            self.ui.data_tw.setItem(i, 1,
                                    QtWidgets.QTableWidgetItem(str(curr_adr)))
            curr_adr = curr_adr + 1

    def start_cyclic_cmd(self):
        if self.ui.cycle_sending_cb.isChecked():
            self.timer.start(self.ui.timeout_sb.value())
        else:
            self.timer.stop()

    def change_id(self, value):
        self.unit_id = value
        self.c = ModbusClient(host=self.host, unit_id=self.unit_id,
                              timeout=1, auto_open=True, auto_close=True)
        print(self.unit_id)

    def check_ip(self, inp_str):
        """
        check ip for correct IP
        """
        list_octets = re.findall(r"([0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3})", inp_str)
        try:
            if len(list_octets) > 0:
                list_octets = list_octets[0].split('.')
                for i in list_octets:
                    if int(i) > 255:
                        print("Октет ", i, " неправильный!")
                        buf = "Октет " + str(i) + " неправильный!"
                        self.ui.log_te.appendPlainText(buf)
                        return False

            if len(list_octets) != 4:
                print("Тоже лажа")
                self.ui.log_te.appendPlainText("Не верное количество октетов")
                return False
            else:
                self.host = inp_str
                return True
        except ValueError:
            print("Форма не верная")
            return False


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()
    application.timer.timeout.connect(application.test)
    application.ui.send_pb.released.connect(application.send_cmd)
    application.ui.connect_pb.released.connect(application.connect)
    application.ui.cnt_sb.valueChanged.connect(application.cntRow_changed)
    application.ui.adr_sb.valueChanged.connect(application.update_adrs)
    application.ui.funct_cb.currentIndexChanged.connect(application.update_data_type_clmn)
    application.ui.cycle_sending_cb.stateChanged.connect(application.start_cyclic_cmd)
    application.ui.id_sb.valueChanged.connect(application.change_id)
    application.ui.cnt_sb.setMinimum(1)
    application.ui.cnt_sb.setValue(1)
    sys.exit(app.exec())
