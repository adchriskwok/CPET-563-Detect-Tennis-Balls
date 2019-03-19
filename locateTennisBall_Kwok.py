# Adam Kwok
# Lab 3 - ESDII
# First written: 3/5/2019 21:03
# Last modified: 3/6/2019 10:25
# This code:
# * shall be able to load in various images via a file menu
# * shall be able to select whether to detect a green or blue tennis ball
# * shall be able to save and load various parameters used for tennis ball detection from a configuration file
# * shall display the X and Y values of the centroid of the detected tennis ball

import cv2
import imutils
import numpy as np
import copy
import sys
from PyQt4 import QtCore, QtGui

class MainWindow(QtGui.QMainWindow):
  def __init__(self):
    super(MainWindow,self).__init__()
    self.statusBar().showMessage("ready")
    
    self.dock = QtGui.QDockWidget(self)
    self.vLayout = QtGui.QVBoxLayout()
    
    self.rMin = 0
    self.rMax = 0
    self.gMin = 0
    self.gMax = 0
    self.bMin = 0
    self.bMax = 0
    
    self.fileInfoLabel = QtGui.QLabel()
    self.fileInfoLabel.setText('Choose your image file via file menu')
    self.vLayout.addWidget(self.fileInfoLabel)
    
    self.fname = None
    self.fileChoiceLabel = QtGui.QLabel()
    if self.fname is None:
      self.fileChoiceLabel.setText('File chosen: None')
    else:
      self.fileChoiceLabel.setText('File chosen: ' + self.fname)
    self.vLayout.addWidget(self.fileChoiceLabel)
    
    self.colorChoice_comboBox = QtGui.QComboBox()
    self.colorChoice_comboBox.addItem("Green")
    self.colorChoice_comboBox.addItem("Blue")
    self.vLayout.addWidget(self.colorChoice_comboBox)
    
    self.detect_pb = QtGui.QPushButton("Load Image and Detect")
    self.detect_pb.setCheckable(True)
    self.detect_pb.toggle()
    self.detect_pb.clicked.connect(self.detect_ball_func)
    
    self.vLayout.addWidget(self.detect_pb)
    self.dockFrame = QtGui.QFrame()
    self.dockFrame.setLayout(self.vLayout)
    self.dock.setWidget(self.dockFrame)
    self.addDockWidget(QtCore.Qt.DockWidgetArea(4),self.dock)
    
    loadAction = QtGui.QAction(QtGui.QIcon('load.png'), '&Load', self)        
    loadAction.setShortcut('Ctrl+L')
    loadAction.setStatusTip('Loading File.....')
    loadAction.triggered.connect(self.loadFile)
    
    exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(QtGui.qApp.quit)
    
    self.statusBar()
    
    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(loadAction)    
    fileMenu.addAction(exitAction)    
    
    self.show()
  
  def loadFile(self):
    self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
            '/home')
            
    f = open(self.fname, 'r')
    
    self.fileChoiceLabel.setText('File chosen: ' + self.fname)
    
    with f:        
      data = f.read()
      
  
  def detect_ball_func(self):
    if self.detect_pb.isChecked():
      img = cv2.imread(str(self.fname))
      small_img = cv2.resize(img,(640,480))
    
      if (self.colorChoice_comboBox.currentText()) == 'Green':
          with open("greenBallCfg.txt") as f:
            self.rMin = int(f.readline().split("= ")[1])
            self.rMax = int(f.readline().split("= ")[1])
            self.gMin = int(f.readline().split("= ")[1])
            self.gMax = int(f.readline().split("= ")[1])
            self.bMin = int(f.readline().split("= ")[1])
            self.bMax = int(f.readline().split("= ")[1])
      if (self.colorChoice_comboBox.currentText()) == 'Blue':
          with open("blueBallCfg.txt") as f:
            self.rMin = int(f.readline().split("= ")[1])
            self.rMax = int(f.readline().split("= ")[1])
            self.gMin = int(f.readline().split("= ")[1])
            self.gMax = int(f.readline().split("= ")[1])
            self.bMin = int(f.readline().split("= ")[1])
            self.bMax = int(f.readline().split("= ")[1])
      
      # generate threshold array
      lower = np.array([self.bMin,self.gMin,self.rMin])
      upper = np.array([self.bMax,self.gMax,self.rMax])
      
      clone_img = copy.copy(small_img)
      
      blurred = cv2.GaussianBlur(clone_img, (11, 11), 0) #(Idea derived from https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/)
      hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
      
      mask = cv2.inRange(hsv, lower, upper)
      mask = cv2.erode(mask, None, iterations=2)
      mask = cv2.dilate(mask, None, iterations=2)
      
      cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
      cnts = imutils.grab_contours(cnts)
      center = None
      
      # only proceed if at least one contour was found
      if len(cnts) > 0:
        print "counts" + str(len(cnts))
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
      
        # only proceed if the radius meets a minimum size
        if radius > 10:
          # draw the circle and centroid on the frame,
          # then update the list of tracked points
          cv2.circle(clone_img, (int(x), int(y)), int(radius),(0, 255, 255), 2)
          cv2.circle(clone_img, center, 5, (0, 0, 255), -1)
      
      cv2.imshow('Result',clone_img)    
      k = cv2.waitKey(5) & 0xFF
      if k == 27:
          pass # break
    
def main():
  app = QtGui.QApplication(sys.argv)
  mainWindow = MainWindow()
  sys.exit(app.exec_())
  
if __name__ == '__main__':
  main()