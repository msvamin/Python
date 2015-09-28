__author__ = 'Amin'

import sys
from PyQt4 import QtGui, QtCore


class drtWindow(QtGui.QWidget):

    def __init__(self):
        super(drtWindow, self).__init__()

        self.initUI()

    def initUI(self):

        betalayout = QtGui.QGridLayout()
        runtablayout = QtGui.QGridLayout()

        leftpart = QtGui.QFrame(self)
        leftpart.setFrameShape(QtGui.QFrame.StyledPanel)

        rightpart = QtGui.QFrame(self)
        rightpart.setFrameShape(QtGui.QFrame.StyledPanel)

        tabs	= QtGui.QTabWidget(self)
        runTab	= QtGui.QWidget()
        dataTab	= QtGui.QWidget()
        configTab	= QtGui.QWidget()

        betaNames = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', \
                     'B09', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16', \
                     'B17', 'B18', 'B19', 'B20', 'B21', 'B22', 'B23', 'B24', \
                     'B25', 'B26', 'B27', 'B28', 'B29', 'B30', 'B31', 'B32', \
                     'B33', 'B34', 'B35', 'B36', 'B37', 'B38', 'B39', 'B40']

        numBetas = len(betaNames)

        positions = [(i,j) for i in range(20) for j in range(2)]

        cb = []
        for position, name in zip(positions, betaNames):
            b = QtGui.QCheckBox(name, self)
            betalayout.addWidget(b, *position)
            cb.append(b)

        leftpart.setLayout(betalayout)
        leftpart.resize(250, 250)
        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(leftpart)
        splitter1.addWidget(rightpart)
        splitter1.setStretchFactor(1, 1)
        runtablayout.addWidget(splitter1)
        tabs.resize(750, 550)
        #tabs.move(300, 300)

        tabs.addTab(runTab,"Run Selection")
        tabs.addTab(dataTab,"Data Selection")
        tabs.addTab(configTab,"Configuration")

        runTab.setLayout(runtablayout)
        #tabs.show()

        self.setGeometry(300, 300, 750, 550)
        self.setWindowTitle('DRT')
        self.show()

    #def changeTitle(self, state):

     #   if state == QtCore.Qt.Checked:
      #      self.setWindowTitle('QtGui.QCheckBox')
       # else:
        #    self.setWindowTitle('')

def main():

    app = QtGui.QApplication(sys.argv)
    ex = drtWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()