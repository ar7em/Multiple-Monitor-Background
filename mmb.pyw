#!/usr/bin/env python

####################################################################
## This script is written for educational purposes by Molokov Artem,
## display icon kindly provided by Rimshotdesign: 
##   http://rimshotdesign.com (see icon/readme.txt for more info)
## Feel free to use any and all parts of this program (except icon).
####################################################################

import os.path
import tempfile
import pythoncom
from win32com.shell import shell, shellcon
from PyQt4 import QtCore, QtGui
import qrc_resources


class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Multiple Monitors Background")
        self.setWindowIcon(QtGui.QIcon(":/display.png"))

        # main widget
        grid = QtGui.QWidget()
        self.setCentralWidget(grid)

        # create window layout
        layout = QtGui.QGridLayout()
        self.detectDisplays()
        self.createModeGroupBox()
        self.createSingleGroupBox()
        self.createMultipleGroupBox()
        layout.addWidget(self.modeGroupBox, 0, 0)
        layout.addWidget(self.singleBox, 1, 0)
        layout.addWidget(self.multipleBox, 1, 0)
        applyButton = QtGui.QPushButton("Apply")
        applyButton.setFixedSize(100, applyButton.sizeHint().height())
        self.connect(applyButton, QtCore.SIGNAL("clicked()"),
            self.applyBackground)
        layout.addWidget(applyButton, 2, 0)
        layout.setRowStretch(4, 1)
        layout.setAlignment(applyButton, QtCore.Qt.AlignHCenter)
        grid.setLayout(layout)
        self.adjustSize()
        self.setMode(False)

    def detectDisplays(self):
        '''Get every monitor in system and keep its number and resolution'''
        self.resolutions = []
        numOfScreens = app.desktop().screenCount()
        for screen in range(numOfScreens):
            screenSize = app.desktop().screenGeometry(screen)
            self.resolutions.append((screenSize.width(), screenSize.height()))

    def setMode(self, singleMode):
        '''Show layout for single wallpaper across all displays if True
        is passed otherwise show layout that allows to set separate
        wallpaper for each display'''
        self.singleBox.setVisible(singleMode)
        self.multipleBox.setVisible(not singleMode)
        self.singleMode = singleMode

    def createModeGroupBox(self):
        self.modeGroupBox = QtGui.QGroupBox("Background mode")
        layout = QtGui.QVBoxLayout()
        self.modeGroupBox.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        multipleRButton = QtGui.QRadioButton("Set separate wallpaper "
                                             "for each display")
        multipleRButton.setChecked(True)
        self.connect(multipleRButton, QtCore.SIGNAL("toggled(bool)"),
                     lambda singleMode: self.setMode(not singleMode))        
        singleRButton = QtGui.QRadioButton("Stretch single wallpaper "
                                           "across all displays")
        self.connect(singleRButton, QtCore.SIGNAL("toggled(bool)"),
                     self.setMode)
        layout.addWidget(multipleRButton, 0)        
        layout.addWidget(singleRButton, 1)
        self.modeGroupBox.setLayout(layout)

    def createSingleGroupBox(self):
        self.singleBox = QtGui.QGroupBox("Single wallpaper")
        layout = QtGui.QGridLayout()
        displays = QtGui.QWidget()
        displaysLayout = QtGui.QHBoxLayout()

        # monitor image
        screenImage = QtGui.QLabel()
        image = QtGui.QPixmap(":/display.png")
        self.overallWidth = sum([width for (width, height) in self.resolutions])
        self.overallHeight = max([height for (width, height) in self.resolutions])
        widthStretch = self.overallWidth / image.size().width()
        heightStretch = self.overallHeight / image.size().height()
        screenImage.setPixmap(image.scaled(sum([width for (width, height)
                              in self.resolutions]) / heightStretch,
                              image.rect().height()))

        self.displayOrder = []
        displayList = ["{0} ({1}x{2})  ".format(i + 1, width, height)
                       for i, (width, height)
                       in zip(range(len(self.resolutions)), self.resolutions)]

        # displays number and resolution text
        for i, screen in zip(range(len(self.resolutions)), self.resolutions):
            j = i * 2
            displayLabel = QtGui.QLabel('Screens from left to right:'
                                        if i == 0 else ', ')
            displayBox = QtGui.QComboBox()
            displayBox.addItems(displayList)
            displayBox.setCurrentIndex(i)
            self.connect(displayBox,
                         QtCore.SIGNAL("highlighted(int)"),
                         self.prepareToSwapDisplays)
            self.connect(displayBox,
                         QtCore.SIGNAL("currentIndexChanged(int)"),
                         self.swapDisplays)
            self.displayOrder.append(displayBox)
            displaysLayout.addWidget(displayLabel, j)
            displaysLayout.addWidget(displayBox, j + 1)

        overallLabel = QtGui.QLabel('. Overall resolution: '
            '{0}x{1}.'.format(self.overallWidth, self.overallHeight))
        displaysLayout.addWidget(overallLabel, j)

        displays.setLayout(displaysLayout)

        layout.addWidget(screenImage, 0, 0, 1, 3)
        layout.addWidget(displays, 1, 0, 1, 3)
        layout.setAlignment(screenImage, QtCore.Qt.AlignHCenter)
        layout.setAlignment(displays, QtCore.Qt.AlignHCenter)
        openFileLabel = QtGui.QLabel("Background image:")
        openFileButton = QtGui.QPushButton("Browse...")
        self.singleBackgroundPath = QtGui.QLineEdit()
        setOpenFile = self.createOpenFileFunction(self.singleBackgroundPath)
        openFileButton.clicked.connect(setOpenFile)
        layout.addWidget(openFileLabel, 2, 0)
        layout.addWidget(self.singleBackgroundPath, 2, 1)
        layout.addWidget(openFileButton, 2, 2)
        self.singleBox.setLayout(layout)

    def prepareToSwapDisplays(self, num):
        '''Find the combobox that might swap it's value with active combobox'''
        for swapDisplay in self.displayOrder:
            if swapDisplay.currentIndex() == num:
                self.swap = swapDisplay
                return

    def swapDisplays(self, num):
        '''find missing index and assign it to combobox, which
        value now is set to active combobox'''
        if self.swap:
            for swapDisplay in self.displayOrder:
                if (swapDisplay.currentIndex() == num and
                        swapDisplay == self.swap):
                    self.swap = None
                    for i in range(len(self.displayOrder)):
                        flag = False
                        for missingDisplay in self.displayOrder:
                            if missingDisplay.currentIndex() == i:
                                flag = True
                        if not flag:
                            swapDisplay.setCurrentIndex(i)
                            return

    def createMultipleGroupBox(self):
        self.multipleBox = QtGui.QGroupBox("Separate wallpapers")
        layout = QtGui.QGridLayout()

        displays = QtGui.QWidget()
        displaysLayout = QtGui.QGridLayout()
        openFileLabel = QtGui.QLabel("Background images:")
        self.separateWallpapers = []
        displaysLayout.addWidget(openFileLabel, 2, 0)
        for i, screen in zip(range(len(self.resolutions)), self.resolutions):
            screenLabel = QtGui.QLabel("Screen {0} ({1}x{2})".format(i + 1,
                                                                    screen[0],
                                                                    screen[1]))
            screenImage = QtGui.QLabel()
            screenSize = app.desktop().screenGeometry(i)
            # calculate image stretch ratio
            image = QtGui.QPixmap(":/display.png")
            stratchRatio = screen[1] / image.size().height()
            screenImage.setPixmap(image.scaled(screen[0] / stratchRatio,
                                               image.size().height()))
            j = i * 3 + 1
            displaysLayout.addWidget(screenImage, 0, j, 1, 2)
            displaysLayout.addWidget(screenLabel, 1, j, 1, 2)
            displaysLayout.setAlignment(screenImage, QtCore.Qt.AlignHCenter)
            if i < (len(self.resolutions) - 1):
                displaysLayout.setColumnMinimumWidth(j + 2, 50)
            displaysLayout.setAlignment(screenLabel, QtCore.Qt.AlignHCenter)
            backgroundPath = QtGui.QLineEdit()
            openFileButton = QtGui.QPushButton("...")
            openFileButton.setFixedSize(30, backgroundPath.sizeHint().height())
            #return needed
            setOpenFile = self.createOpenFileFunction(backgroundPath)
            openFileButton.clicked.connect(setOpenFile)
            displaysLayout.addWidget(backgroundPath, 2, j)
            displaysLayout.addWidget(openFileButton, 2, j + 1)
            self.separateWallpapers.append(backgroundPath)

        displays.setLayout(displaysLayout)

        layout.addWidget(displays, 0, 0)

        self.multipleBox.setLayout(layout)

    def createOpenFileFunction(self, lineEdit):
        '''Open file dialog box'''
        def setOpenFile():
            fileName = QtGui.QFileDialog.getOpenFileName(self,
                "Select background image",
                lineEdit.text(),
                "Images (*.jpeg *.jpg *.png *bmp);;All Files (*)")
            if fileName:
                lineEdit.setText(fileName)
        return setOpenFile

    def applyBackground(self):
        '''Use IActiveDesktop to set wallpaper in Windows 7'''
        if self.singleMode:
            background = self.getSingleBackground()
        else:
            background = self.getMultipleBackgrounds()
        backgroundPath = tempfile.gettempdir() + 'background'
        background.save(backgroundPath, "JPG", 100)
        iad = pythoncom.CoCreateInstance(shell.CLSID_ActiveDesktop, None,
                  pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IActiveDesktop)
        iad.SetWallpaper(backgroundPath, 0)
        iad.ApplyChanges(shellcon.AD_APPLY_ALL)

    def getSingleBackground(self):
        '''Resize single image to fit all of screens'''
        imagePath = os.path.normpath(self.singleBackgroundPath.text())
        image = QtGui.QPixmap(imagePath)
        stretchFactor = self.overallWidth / image.size().width()
        newSize = QtCore.QSize(self.overallWidth,
                                      self.overallHeight * stretchFactor)
        background = QtGui.QPixmap(imagePath).scaled(newSize)
        return background

    def getMultipleBackgrounds(self):
        '''Paste together images for every screen into single background'''
        newSize = QtCore.QSize(self.overallWidth, self.overallHeight)
        background = QtGui.QImage(newSize, QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(background)
        xPos = 0.0
        yPos = 0.0
        for i in range(len(self.resolutions)):
            image = QtGui.QImage(self.separateWallpapers[i].text())
            sourceSize = QtCore.QRectF(0.0, 0.0, 
                                image.size().width(),
                                image.size().height())
            targetSize = QtCore.QRectF(xPos,
                                       yPos,
                                       self.resolutions[i][0],
                                       self.resolutions[i][1])
            painter.drawImage(targetSize, image, sourceSize)
            xPos += self.resolutions[i][0]
        return background

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)

    # get stylesheet
    with open('stylesheet.qss', 'r') as content_file:
        styleSheet = content_file.read()
    app.setStyleSheet(styleSheet)

    window = Window()
    window.show()
    sys.exit(app.exec_())
