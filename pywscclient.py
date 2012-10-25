#!/usr/bin/env python
from PySide.QtGui import QApplication, QMainWindow, QToolBox, QWidget, QTextBrowser,\
 QVBoxLayout, QPushButton, QFormLayout, QLabel, QLineEdit, QTabWidget,\
   QHBoxLayout, QStyleFactory, QDialog, QGroupBox, QDialogButtonBox


from suds.client import Client
from suds.transport.http import HttpAuthenticated

import sys,os

class Tab(QWidget):
    def __init__(self, client, method):
        super(Tab, self).__init__(None)

        self.client = client
        self.method = method

        horiz = QHBoxLayout(self)
        
        left = QWidget()
        
        horiz.addWidget(left)
        
        layout = QFormLayout(left)
        
        self.fields = []
        for param in method[1]:
            field = QLineEdit()
            self.fields.append(field)
            layout.addRow(param[0], field)

        button = QPushButton("Execute Web Service")
        button.clicked.connect(self.execute)
        layout.addWidget(button)
        
        display = QTabWidget()
        
        self.result = QTextBrowser()
        display.addTab(self.result, "Result")
        
        self.request = QTextBrowser()
        display.addTab(self.request, "Request", )
        
        self.response = QTextBrowser()
        display.addTab(self.response, "Response")
        
        horiz.addWidget(display)
        
    def execute(self):
        service_method = getattr(self.client.service, self.method[0])
        args = [field.text() for field in self.fields]
        result = service_method(*args)
        self.result.setText(str(result))
        self.request.setText(str(self.client.last_sent()))
        self.response.setText(str(self.client.last_received()))

class WSDLDialog(QDialog):
    def __init__(self, url="", parent=None):
        super(WSDLDialog, self).__init__()
        self.setWindowTitle("Select Web Service")
        layout = QVBoxLayout(self)
        
        form = QWidget(self)
        form_layout = QFormLayout(form)
        self.wsdl_field = QLineEdit()
        self.wsdl_field.setText(url)
        form_layout.addRow("WSDL Address:", self.wsdl_field)
        
        layout.addWidget(form)
        
        self.auth = QGroupBox("Use HTTP Basic Authentication")
        self.auth.setCheckable(True)
        self.auth.setChecked(False)
        
        auth_layout = QFormLayout(self.auth)
        
        self.user_field = QLineEdit()
        auth_layout.addRow("Username:", self.user_field)
        
        self.pass_field = QLineEdit()
        auth_layout.addRow("Pass:", self.pass_field)
        
        layout.addWidget(self.auth)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
    def get_url(self):
        return self.wsdl_field.text()
    
    def auth_enabled(self):
        return self.auth.isChecked()
        
    def get_user(self):
        return self.user_field.text()
    
    def get_pass(self):
        return self.pass_field.text()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QApplication.setStyle(QStyleFactory.create("Plastique"))
        QApplication.setPalette(QApplication.style().standardPalette())
        super(MainWindow, self).__init__(None)  
        centralwidget = QWidget(self)
        self.setCentralWidget(centralwidget)
        self.layout = QVBoxLayout(centralwidget)
        
        button = QPushButton("Set WSDL Address")
        button.clicked.connect(self.request_wsdl)
        self.layout.addWidget(button)
        
        self.toolbox = QToolBox()
        self.layout.addWidget(self.toolbox)
        self.url = ""
        
    def request_wsdl(self):
        dialog = WSDLDialog(self.url)
        if dialog.exec_() == dialog.Accepted:
            if dialog.auth_enabled():
                t = HttpAuthenticated(username=dialog.get_user(), password=dialog.get_pass())
                client = Client(dialog.get_url(), transport=t)
            else:
                client = Client(dialog.get_url())
            self.url = dialog.get_url()
            self.wsdl_change(client)
            
    def wsdl_change(self, client): 
        self.toolbox.hide()
        del self.toolbox
        self.toolbox = QToolBox()
        self.layout.addWidget(self.toolbox)
                
        for method in client.sd[0].ports[0][1]:
            tab = Tab(client, method)
            self.toolbox.addItem(tab, method[0])
            
            
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    os._exit(app.exec_())
