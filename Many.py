#! /usr/bin/env python

import sys, os, subprocess
import logging
import ConfigParser
from PyQt4 import QtCore, QtGui

FIELDS = ['Scale:', 'Width:', 'Height:']
PERCENTS = ['', '10%', '20%', '50%', '75%', '120%']
PIXELS = ['', '320', '640', '1024', '1280', '1600']
VALUES = [PERCENTS, PIXELS, PIXELS]

CHOOSEORIG = "Choose original photos folder"
CHOOSEMOD = "Choose modified photos folder"
RUNDIR = os.path.expanduser('~/.many')

class MainWindow(QtGui.QMainWindow):
    def __init__(self, cfg):
        super(MainWindow, self).__init__()

        self.cfg = cfg

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
        logging.info("Set source path to %s", self.srcpath)
        if self.srcpath:
            self.src.setText('%s: %s' % (CHOOSEORIG, self.srcpath))
            if self.dstpath:
                self.run.setEnabled(True)

    def setdst(self):
        self.dstpath = str(QtGui.QFileDialog().getExistingDirectory())
        logging.info("Set destination path to %s", self.dstpath)
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
            logging.info("Scouting for files")
            self.bar.setMaximum(self.walk(True))

            logging.info("Starting processing")
            self.walk(False)
            logging.info("Ending processing")

    def walk(self, scout):
        filec = 0
        for root, _, files in os.walk(self.srcpath):
            # Don't use output files as input files
            if self.dstpath == root:
                continue

            for filename in files:
                filec += 1
                if not scout:
                    inpath = '%s/%s' % (root, filename)
                    outdir = '%s/%s' % \
                        (self.dstpath,
                         os.path.dirname(inpath[len(self.srcpath) + 1:]))
                    try:
                        os.makedirs(outdir)
                        logging.info("Made directory %s", outdir)
                    except OSError:
                        pass

                    scale = str(self.combos[0].currentText())
                    width = str(self.combos[1].currentText())
                    height = str(self.combos[2].currentText())

                    if scale:
                        args = [self.cfg.get('many', 'gm'),
                                'convert', '-geometry', scale, inpath,
                                '%s/%s' % (outdir, filename)]
                    elif width or height:
                        args = [self.cfg.get('many', 'gm'),
                                'convert', '-geometry',
                                '%sx%s' % (width, height), inpath,
                                '%s/%s' % (outdir, filename)]

                    if args:
                        self.bar.setValue(filec)
                        logging.info("Running %s", ' '.join(args))
                        subprocess.call(args)

        return filec

def excepthook(type, value, tback):
    logging.error('Line %d, %s: %s', tback.tb_lineno, type, value)
    sys.__excepthook__(type, value, tback)

if __name__ == '__main__':
    # Create runtime directory
    try:
        os.mkdir(RUNDIR)
    except OSError:
        pass

    # Load config
    cfg = ConfigParser.RawConfigParser()
    cfg.read(RUNDIR + '/many.cfg')

    # Set up logging
    logging.basicConfig(filename=RUNDIR + '/log',
                        format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    logging.info("Starting run")
    sys.excepthook = excepthook

    # Run application
    app = QtGui.QApplication(sys.argv)
    win = MainWindow(cfg)
    win.show()

    excode = app.exec_()
    logging.info("Ending run")
    sys.exit(excode)
