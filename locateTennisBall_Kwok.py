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
    self.setGeometry(200, 200, 400, 300)
    
    self.dock = QtGui.QDockWidget(self)
    self.gridLayout = QtGui.QGridLayout()
    
    self.rMin = 0
    self.rMax = 0
    self.gMin = 0
    self.gMax = 0
    self.bMin = 0
    self.bMax = 0
    
    self.fileInfoLabel = QtGui.QLabel()
    self.fileInfoLabel.setText('Choose your image file via file menu')
    self.gridLayout.addWidget(self.fileInfoLabel, 0, 0, 1, 2)
    
    self.fname = None
    self.fileChoiceLabel = QtGui.QLabel()
    if self.fname is None:
      self.fileChoiceLabel.setText('File chosen: None')
    else:
      self.fileChoiceLabel.setText('File chosen: ' + self.fname)
    self.gridLayout.addWidget(self.fileChoiceLabel, 1, 0, 1, 2)
    
    #Dictates which configuration gets used
    self.colorChoice_comboBox = QtGui.QComboBox()
    self.colorChoice_comboBox.addItem("Green")
    self.colorChoice_comboBox.addItem("Blue")
    self.gridLayout.addWidget(self.colorChoice_comboBox, 2, 0, 2, 1)
    
    #Load configuration from hardcoded default
    self.default_cfg_pb = QtGui.QPushButton("Load Default Configuration")
    self.default_cfg_pb.setCheckable(True)
    self.default_cfg_pb.toggle()
    self.default_cfg_pb.clicked.connect(self.set_default_config)
    self.gridLayout.addWidget(self.default_cfg_pb, 4, 0)
    
    #Load settings from respective configuration file
    self.custom_cfg_pb = QtGui.QPushButton("Load Custom Configuration")
    self.custom_cfg_pb.setCheckable(True)
    self.custom_cfg_pb.toggle()
    self.custom_cfg_pb.clicked.connect(self.set_custom_config)
    self.gridLayout.addWidget(self.custom_cfg_pb, 4, 1)
    
    redmin_label = QtGui.QLabel()
    redmin_label.setText("Red Minimum:")
    self.gridLayout.addWidget(redmin_label, 5, 0)
    
    self.rm_le = QtGui.QLineEdit()
    self.gridLayout.addWidget(self.rm_le, 5, 1)
    
    redmax_label = QtGui.QLabel()
    redmax_label.setText("Red Maximum:")
    self.gridLayout.addWidget(redmax_label, 6, 0)
    
    self.rM_le = QtGui.QLineEdit()
    self.gridLayout.addWidget(self.rM_le, 6, 1)
    
    greenmin_label = QtGui.QLabel()
    greenmin_label.setText("Green Minimum:")
    self.gridLayout.addWidget(greenmin_label, 7, 0)
    
    self.gm_le = QtGui.QLineEdit()
    self.gridLayout.addWidget(self.gm_le, 7, 1)
    
    greenmax_label = QtGui.QLabel()
    greenmax_label.setText("Green Maximum:")
    self.gridLayout.addWidget(greenmax_label, 8, 0)
    
    self.gM_le = QtGui.QLineEdit()
    self.gridLayout.addWidget(self.gM_le, 8, 1)
    
    bluemin_label = QtGui.QLabel()
    bluemin_label.setText("Blue Minimum:")
    self.gridLayout.addWidget(bluemin_label, 9, 0)
    
    self.bm_le = QtGui.QLineEdit()
    self.gridLayout.addWidget(self.bm_le, 9, 1)
    
    bluemax_label = QtGui.QLabel()
    bluemax_label.setText("Blue Maximum:")
    self.gridLayout.addWidget(bluemax_label, 10, 0)
    
    self.bM_le = QtGui.QLineEdit()
    self.gridLayout.addWidget(self.bM_le, 10, 1)
    
    #Provides a way to store input values
    self.save_pb = QtGui.QPushButton("Save/Overwrite Custom Configurations")
    self.save_pb.setCheckable(True)
    self.save_pb.toggle()
    self.save_pb.clicked.connect(self.save_func)
    self.gridLayout.addWidget(self.save_pb, 11, 0, 11, 1)
    
    #Begin detection button
    self.detect_pb = QtGui.QPushButton("Load Image and Detect")
    self.detect_pb.setCheckable(True)
    self.detect_pb.toggle()
    self.detect_pb.clicked.connect(self.detect_ball_func)
    self.gridLayout.addWidget(self.detect_pb, 14, 0, 14, 1)
    
    self.dockFrame = QtGui.QFrame()
    self.dockFrame.setLayout(self.gridLayout)
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
      
  #Sets line edits as default config values
  def set_default_config(self):
    if (self.colorChoice_comboBox.currentText()) == 'Green':
      self.rm_le.setText('20')
      self.rM_le.setText('160')
      self.gm_le.setText('130')
      self.gM_le.setText('255')
      self.bm_le.setText('70')
      self.bM_le.setText('100')
    if (self.colorChoice_comboBox.currentText()) == 'Blue':
      self.rm_le.setText('10')
      self.rM_le.setText('100')
      self.gm_le.setText('50')
      self.gM_le.setText('140')
      self.bm_le.setText('75')
      self.bM_le.setText('140')
      
  #Sets line edits as custom config values from respective (dictated by combobox) file
  def set_custom_config(self):
    if (self.colorChoice_comboBox.currentText()) == 'Green':
      with open("greenBallCfg.txt") as f:
        self.rm_le.setText(str(f.readline().split("= ")[1]))
        self.rM_le.setText(str(f.readline().split("= ")[1]))
        self.gm_le.setText(str(f.readline().split("= ")[1]))
        self.gM_le.setText(str(f.readline().split("= ")[1]))
        self.bm_le.setText(str(f.readline().split("= ")[1]))
        self.bM_le.setText(str(f.readline().split("= ")[1]))
    if (self.colorChoice_comboBox.currentText()) == 'Blue':
      with open("blueBallCfg.txt") as f:
        self.rm_le.setText(str(f.readline().split("= ")[1]))
        self.rM_le.setText(str(f.readline().split("= ")[1]))
        self.gm_le.setText(str(f.readline().split("= ")[1]))
        self.gM_le.setText(str(f.readline().split("= ")[1]))
        self.bm_le.setText(str(f.readline().split("= ")[1]))
        self.bM_le.setText(str(f.readline().split("= ")[1]))
  
  #Saves current line edit values into respective (dictated by combobox) config file
  def save_func(self):
    if (self.colorChoice_comboBox.currentText()) == 'Green':
      with open("greenBallCfg.txt", "r+") as f:
        f.write("rMin  = " + self.rm_le.text() + "\n")
        f.write("rMax  = " + self.rM_le.text() + "\n")
        f.write("gMin  = " + self.gm_le.text() + "\n")
        f.write("gMax  = " + self.gM_le.text() + "\n")
        f.write("bMin  = " + self.bm_le.text() + "\n")
        f.write("bMax  = " + self.bM_le.text() + "\n")
        
    if (self.colorChoice_comboBox.currentText()) == 'Blue':
      with open("blueBallCfg.txt", "r+") as f:
        f.write("rMin  = " + self.rm_le.text() + "\n")
        f.write("rMax  = " + self.rM_le.text() + "\n")
        f.write("gMin  = " + self.gm_le.text() + "\n")
        f.write("gMax  = " + self.gM_le.text() + "\n")
        f.write("bMin  = " + self.bm_le.text() + "\n")
        f.write("bMax  = " + self.bM_le.text() + "\n")
  
  def detect_ball_func(self):
    if self.detect_pb.isChecked():
      img = cv2.imread(str(self.fname))
      small_img = cv2.resize(img,(640,480))
      #Pull values from line edits - if not, throw error message
      try:
        self.rMin  = float(self.rm_le.text())
        self.rMax  = float(self.rM_le.text())
        self.gMin  = float(self.gm_le.text())
        self.gMax  = float(self.gM_le.text())
        self.bMin  = float(self.bm_le.text())
        self.bMax  = float(self.bM_le.text())
      except ValueError:
        QtGui.QMessageBox.critical(self, 'Input Error', 'Please input integers between 0 an 255 in all text fields.')
      
      # generate threshold array
      lower = np.array([self.bMin,self.gMin,self.rMin])
      upper = np.array([self.bMax,self.gMax,self.rMax])
      
      clone_img = copy.copy(small_img)
      
      #(Ideas derived from https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/)
      #gaussian blur to reduce high frequency noise (especially applicable when video functionality is implemented)
      blurred = cv2.GaussianBlur(clone_img, (11, 11), 0) 
      #converted to hsv color space
      hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
      
      #mask colors based on thresholds
      mask = cv2.inRange(hsv, lower, upper)
      
      #remove small blobs
      mask = cv2.erode(mask, None, iterations=2)
      mask = cv2.dilate(mask, None, iterations=2)
      
      cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
      cnts = imutils.grab_contours(cnts)
      center = None
      
      # only proceed if at least one contour was found
      if len(cnts) > 0:
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
          
          # Tell user coordinates:
          x_label = QtGui.QLabel()
          x_label.setText("x location: " + str(x))
          self.gridLayout.addWidget(x_label, 16, 0, 16, 1)
          y_label = QtGui.QLabel()
          y_label.setText("y location: " + str(y))
          self.gridLayout.addWidget(y_label, 18, 0, 18, 1)
      
      cv2.imshow('Result',clone_img)
    
def main():
  app = QtGui.QApplication(sys.argv)
  mainWindow = MainWindow()
  sys.exit(app.exec_())
  
if __name__ == '__main__':
  main()