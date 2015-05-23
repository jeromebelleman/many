#! /usr/bin/env python

import sys, os, subprocess
from PyQt4 import QtCore, QtGui

FIELDS = ['Scale:', 'Width:', 'Height:']
PERCENTS = ['', '10%', '20%', '50%', '75%', '120%']
PIXELS = ['', '320', '640', '1024', '1280', '1600']
VALUES = [PERCENTS, PIXELS, PIXELS]

CHOOSEORIG = "Choose original photos folder"
CHOOSEMOD = "Choose modified photos folder"

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Many")
        self.srcpath, self.dstpath = None, None
        self.msg = QtGui.QErrorMessage()

        # Central layout
        central = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(central)
        self.setCentralWidget(central)

        self.dirbox(layout)
        self.modbox(layout)

    def dirbox(self, layout):
        # Directory box
        dirbox = QtGui.QGroupBox("Choose Folders")
        layout.addWidget(dirbox)
        dirlayout = QtGui.QVBoxLayout(dirbox)

        # Source button
        self.src = QtGui.QPushButton(CHOOSEORIG)
        self.src.clicked.connect(self.setsrc)
        dirlayout.addWidget(self.src)

        # Destination button
        self.dst = QtGui.QPushButton(CHOOSEMOD)
        self.dst.clicked.connect(self.setdst)
        dirlayout.addWidget(self.dst)

    def modbox(self, layout):
        # Modification box
        modbox = QtGui.QGroupBox("Make Modifications")
        layout.addWidget(modbox)
        modlayout = QtGui.QVBoxLayout(modbox)

        # Dimensions
        self.dimbox(modlayout)

        # Run button
        self.run = QtGui.QPushButton("Run modifications over all photos")
        self.run.clicked.connect(self.setrun)
        self.run.setEnabled(False)
        modlayout.addWidget(self.run)

        # Progress bar
        self.bar = QtGui.QProgressBar()
        modlayout.addWidget(self.bar)

    def dimbox(self, layout):
        # Dimensions
        dimbox = QtGui.QGroupBox("Modify Dimensions")
        layout.addWidget(dimbox)
        dimlayout = QtGui.QGridLayout(dimbox)

        # Fields
        self.combos = []
        for i, (field, values) in enumerate(zip(FIELDS, VALUES)):
            label = QtGui.QLabel(field)
            dimlayout.addWidget(label, i, 0)

            self.combos.append(QtGui.QComboBox())
            self.combos[i].setEditable(True)
            dimlayout.addWidget(self.combos[i], i, 1)

            self.combos[i].addItems(values)

    def setsrc(self):
        self.srcpath = str(QtGui.QFileDialog().getExistingDirectory())
        if self.srcpath:
            self.src.setText('%s: %s' % (CHOOSEORIG, self.srcpath))
            if self.dstpath:
                self.run.setEnabled(True)

    def setdst(self):
        self.dstpath = str(QtGui.QFileDialog().getExistingDirectory())
        if self.dstpath:
            self.dst.setText('%s: %s' % (CHOOSEMOD, self.dstpath))
            if self.srcpath:
                self.run.setEnabled(True)

    def setrun(self):
        files = os.listdir(self.dstpath)
        if files and files[0] != ['.DS_Store']:
            self.msg.showMessage('''
                The folder you chose (%s) to write your modified photos to
                has already some files in it.  Please choose another one
                which is empty.
                ''' % self.dstpath)
        else:
            self.bar.setMaximum(self.walk(True))
            self.walk(False)

    def walk(self, scout):
        filec = 0
        for root, _, files in os.walk(self.srcpath):
            for filename in files:
                filec += 1
                if not scout:
                    inpath = '%s/%s' % (root, filename)
                    outdir = '%s/%s' % \
                        (self.dstpath,
                         os.path.dirname(inpath[len(self.srcpath) + 1:]))
                    try:
                        os.makedirs(outdir)
                    except OSError:
                        pass

                    scale = str(self.combos[0].currentText())
                    width = str(self.combos[1].currentText())
                    height = str(self.combos[2].currentText())

                    if scale:
                        args = ['gm', 'convert', '-geometry', scale, inpath,
                                '%s/%s' % (outdir, filename)]
                    elif width or height:
                        args = ['gm', 'convert', '-geometry',
                                '%sx%s' % (width, height), inpath,
                                '%s/%s' % (outdir, filename)]

                    if args:
                        self.bar.setValue(filec)
                        subprocess.call(args)

        return filec

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
