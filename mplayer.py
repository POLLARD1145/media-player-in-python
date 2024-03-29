# Form implementation generated from reading ui file 'mplayer.ui'
#
# Created by: PyQt6 UI code generator 6.2.2
# DEVELOPER: POLLARD SAMBA
# GITHUB: POLLARD1145
# EMAIL: POLLADSAMBA1@GMAIL.COM
#######################################################################################
##TASKS TO BE DONE //This has to be edited everytime changes are made to track progress!!!
#Improve the folders function to avoid listing the media documents in the folders nav
#improve the video playing function to be able to resize the window and other functions related
#

from turtle import *
from PyQt6 import QtCore, QtGui, QtWidgets
import os
from moviepy.editor import *
from moviepy.video.fx import *
import tkinter as tk

import pygame
import re; import numpy as np
root = tk.Tk()
screen_height = root.winfo_screenheight()
screen_width = root.winfo_screenwidth()

#User Interface building starts here
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        pygame.init()
        pygame.mixer.init()
        
       
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        MainWindow.resize(screen_width, screen_height)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../Pictures/pollard.jpg"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhSensitiveData)
        MainWindow.setDockNestingEnabled(True)
        MainWindow.setProperty("start", QtCore.QTime(-1, -1, -1))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMouseTracking(True)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(10, 30, 221, 321))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 219, 319))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.listWidget = QtWidgets.QListWidget(self.scrollAreaWidgetContents)
        self.listWidget.setGeometry(QtCore.QRect(0, 0, 221, 321))
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.adjustSize()
        self.graphicsView.acceptDrops()
        self.graphicsView.setGeometry(QtCore.QRect(10, 380, 231, 221))
        self.graphicsView.setObjectName("graphicsView")
        self.playButton = QtWidgets.QToolButton(self.centralwidget)
        self.playButton.setGeometry(QtCore.QRect(10, 640, 41, 31))
        self.playButton.setObjectName("playButton")
        self.previousButton = QtWidgets.QToolButton(self.centralwidget)
        self.previousButton.setGeometry(QtCore.QRect(74, 650, 31, 20))
        self.previousButton.setObjectName("previousButton")
        self.stopButton = QtWidgets.QToolButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(110, 650, 25, 19))
        self.stopButton.setObjectName("stopButton")
        self.nextButton = QtWidgets.QToolButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(140, 650, 31, 19))
        self.nextButton.setObjectName("nextButton")
        self.loopButton = QtWidgets.QToolButton(self.centralwidget)
        self.loopButton.setGeometry(QtCore.QRect(200, 650, 25, 19))
        self.loopButton.setObjectName("loopButton")
        self.repeatButton = QtWidgets.QToolButton(self.centralwidget)
        self.repeatButton.setGeometry(QtCore.QRect(230, 650, 25, 19))
        self.repeatButton.setObjectName("repeatButton")
        self.shuffleButton = QtWidgets.QToolButton(self.centralwidget)
        self.shuffleButton.setGeometry(QtCore.QRect(300, 650, 25, 19))
        self.shuffleButton.setObjectName("shuffleButton")
        self.equalizerButton = QtWidgets.QToolButton(self.centralwidget)
        self.equalizerButton.setGeometry(QtCore.QRect(330, 650, 25, 19))
        self.equalizerButton.setObjectName("equalizerButton")
        self.toolButton_9 = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_9.setGeometry(QtCore.QRect(360, 650, 25, 19))
        self.toolButton_9.setObjectName("toolButton_9")

        self.vol = QtWidgets.QLabel(self.centralwidget)
        self.vol.setGeometry(QtCore.QRect(1312,650,90,22))
        self.vol.setText(str(int(100*pygame.mixer.music.get_volume())) + "%")

        self.volumeslider = QtWidgets.QSlider(self.centralwidget)
        self.volumeslider.setGeometry(QtCore.QRect(1200, 650, 111, 10))
        self.volumeslider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.volumeslider.setObjectName("volumeslider")
        self.volumeslider.setRange(0,100)
        self.volumeslider.setValue(int(100*pygame.mixer.music.get_volume()))
        
        #The funtion to control volume when the slider is moved 
        def voluMe():
            svol = float(self.volumeslider.value()/100) #get slider value and convert it to a float between the range of 0 to 1.0
            pygame.mixer.music.set_volume(svol) #set slider value to be volume
            vtxt = str(int(100*pygame.mixer.music.get_volume())) + "%" #get volume value and convert it to a string and an in
            self.vol.setText(vtxt) #change the displayed volume to the new volume
            nh = int(22*pygame.mixer.music.get_volume())
            self.volumeslider.setGeometry(QtCore.QRect(1200, 650, 111, nh+11))
            pass
        self.volumeslider.valueChanged.connect(voluMe)

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(250, 30, 1091, 571))
        self.widget.setAcceptDrops(True)
        self.widget.setStyleSheet("QPushButton{\n"
"background-color: qconicalgradient(cx:0.5, cy:0.5, angle:0, stop:0 rgba(35, 40, 3, 255), stop:0.16 rgba(136, 106, 22, 255), stop:0.225 rgba(166, 140, 41, 255), stop:0.285 rgba(204, 181, 74, 255), stop:0.345 rgba(235, 219, 102, 255), stop:0.415 rgba(245, 236, 112, 255), stop:0.52 rgba(209, 190, 76, 255), stop:0.57 rgba(187, 156, 51, 255), stop:0.635 rgba(168, 142, 42, 255), stop:0.695 rgba(202, 174, 68, 255), stop:0.75 rgba(218, 202, 86, 255), stop:0.815 rgba(208, 187, 73, 255), stop:0.88 rgba(187, 156, 51, 255), stop:0.935 rgba(137, 108, 26, 255), stop:1 rgba(35, 40, 3, 255));\n"
"}")
        self.widget.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhSensitiveData)
        self.widget.setObjectName("widget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.widget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 1091, 571))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.playlistView = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.playlistView.setObjectName("playlistView")

        def loadPlaylist():
            path = QtWidgets.QFileDialog.getExistingDirectory(None,"Select Folder Containing Media")
            files = os.listdir(path)
            mp4s = re.compile(".*.mp4"); mp4 = list(filter(mp4s.match,files))
            mp3s = re.compile(".*.mp3"); mp3 = list(filter(mp3s.match,files))
            mediafiles = mp4 + mp3
            self.playlistView.clear()
            for i in mediafiles:
                self.playlistView.addItem(i)
        


       #Getting song when user clicks on it 
        def loadSong(item):
            global pina_song
            pina_song = item.text()
            songtracs = os.listdir()
            
            mp4s = re.compile(".*.mp4"); mp4 = list(filter(mp4s.match,songtracs))
            if item.text() in mp4:
                #creaating an alternative to handle videos
                
                video = VideoFileClip(item.text(),False,True,200000,(screen_height,screen_width),'bicubic',44100,2,False,'tbr')
                video.preview()
                video.close()
                
            else:
                pina = os.path.abspath(item.text()) #getting the path name of the selected item from the list of songs
                ppina = pina.replace('\\','/') #removing the backslash and replacing it with a frontslash to avoid escapes
                pygame.mixer.music.load(ppina) #loading a song to be able to play it once the playSong function is called
                self.playButton.setText("Play") #wheneve a song is loaded it sets button to play
                #duration = pygame.mixer.Sound(ppina).get_length()
                #minutes= duration/60
                #minutes_int = int(minutes)
                #seconds = int((minutes-minutes_int)*60)
                #hours = int(duration/3600)
                #formatted string value
                #fhours = "{:02d}".format(hours)
                #fminutes_int = "{:02d}".format(minutes_int)
                #fseconds = "{:02d}".format(seconds)
                #endtime = fhours+":"+fminutes_int+":"+fseconds
                #self.endtime.setText(endtime)
                #print(pygame.mixer.music.get_endevent())
                

            
                  
            pass
        self.playlistView.itemClicked.connect(loadSong)

        #playing by doubleclicking on song
        def pauto(item):
            pat = os.path.abspath(item.text())
            songtracs = os.listdir()
            
            mp4s = re.compile(".*.mp4"); mp4 = list(filter(mp4s.match,songtracs))
            pina = os.path.abspath(item.text())
            ppina = pina.replace('\\','/')
            if item.text() in mp4:
                #creaating an alternative to handle videos
                
                video = VideoFileClip(ppina)
                video.resize(height=screen_height)
                video.preview()
                video.close()
            else:
                pygame.mixer.music.load(ppina)
                pygame.mixer.music.play()
                self.playButton.setText("Pause")
        self.playlistView.itemDoubleClicked.connect(pauto)


        
        
        
        
        self.verticalLayout.addWidget(self.playlistView)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 6, 71, 20))
        self.label.setObjectName("label")
        self.toolButton_10 = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton_10.setGeometry(QtCore.QRect(1200, 0, 25, 19))
        self.toolButton_10.setObjectName("toolButton_10")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(1230, 0, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.durationslider = QtWidgets.QSlider(self.centralwidget)
        self.durationslider.setGeometry(QtCore.QRect(80, 615, 1211, 11))
        
        self.durationslider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.durationslider.setObjectName("durationslider")
        self.starttime = QtWidgets.QLabel(self.centralwidget)
        self.starttime.setGeometry(QtCore.QRect(30, 610, 61, 22))
        self.starttime.setText("00:00:00")
        self.starttime.setObjectName("starttime")

        self.endtime = QtWidgets.QLabel(self.centralwidget)
        self.endtime.setGeometry(QtCore.QRect(1293, 610, 61, 22))
        self.endtime.setText("00:00:00")
        self.endtime.setObjectName("endtime")
        

        self.scrollArea.raise_()
        self.graphicsView.raise_()
        self.playButton.raise_()
        self.previousButton.raise_()
        self.stopButton.raise_()
        self.nextButton.raise_()
        self.loopButton.raise_()
        self.repeatButton.raise_()
        self.shuffleButton.raise_()
        self.equalizerButton.raise_()
        self.toolButton_9.raise_()
        self.volumeslider.raise_()
        self.label.raise_()
        self.toolButton_10.raise_()
        self.lineEdit.raise_()
        self.widget.raise_()
        self.durationslider.raise_()
        self.starttime.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 560, 21))
        self.menubar.setObjectName("menubar")
        self.menuMedia = QtWidgets.QMenu(self.menubar)
        self.menuMedia.setObjectName("menuMedia")
        self.menuPlayback = QtWidgets.QMenu(self.menubar)
        self.menuPlayback.setObjectName("menuPlayback")
        self.menuAudio = QtWidgets.QMenu(self.menubar)
        self.menuAudio.setObjectName("menuAudio")
        self.menuVideo = QtWidgets.QMenu(self.menubar)
        self.menuVideo.setObjectName("menuVideo")
        self.menuSubtitle = QtWidgets.QMenu(self.menubar)
        self.menuSubtitle.setObjectName("menuSubtitle")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setMouseTracking(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionnew = QtGui.QAction(MainWindow)
        self.actionnew.setObjectName("actionnew")
        self.actionCurrent_playlistView = QtGui.QAction(MainWindow)
        self.actionCurrent_playlistView.setCheckable(True)
        self.actionCurrent_playlistView.setWhatsThis("")
        

        
        self.actionCurrent_playlistView.setObjectName("actionCurrent_playlistView")
        self.actionShow_Subtitles = QtGui.QAction(MainWindow)
        self.actionShow_Subtitles.setObjectName("actionShow_Subtitles")
        self.actionAdd_subtitles = QtGui.QAction(MainWindow)
        self.actionAdd_subtitles.setObjectName("actionAdd_subtitles")
        self.load_Playlist = QtGui.QAction(MainWindow)
        self.load_Playlist.setObjectName("load_Playlist")
        self.menuSubtitle.addAction(self.actionShow_Subtitles)
        self.menuSubtitle.addAction(self.actionAdd_subtitles)
        self.menuMedia.addAction(self.load_Playlist)
        self.load_Playlist.triggered.connect(loadPlaylist)
        
        

        self.menubar.addAction(self.menuMedia.menuAction())
        self.menubar.addAction(self.menuPlayback.menuAction())
        self.menubar.addAction(self.menuAudio.menuAction())
        self.menubar.addAction(self.menuVideo.menuAction())
        self.menubar.addAction(self.menuSubtitle.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        
        
      


        self.retranslateUi(MainWindow)
        self.listWidget.itemClicked['QListWidgetItem*'].connect(self.playlistView.update) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        def showFolders(item):
            user = os.getlogin()
            userfolder = "C:/Users/"+user+"/"
            os.chdir(userfolder)
                        
            if item.text() == "Media Library":
                self.listWidget.addItem("Music")
                self.listWidget.addItem("Videos")                      
        
            elif item.text() == "Drives":
                os.getcwd()
                os.chdir("F:")
                folders = os.listdir()
                mp4s = re.compile(".*.mp4"); mp4 = list(filter(mp4s.match,folders))
                mp3s = re.compile(".*.mp3"); mp3 = list(filter(mp3s.match,folders))
                accs = re.compile(".*.acc"); acc = list(filter(accs.match,folders))
                media = acc+mp3+mp4
                for i in media:
                    self.playlistView.addItem(i)
                if item.text() not in media:
                    path1 = os.path.abspath(item.text())
                    
                    folders1 = os.listdir()
                    for i in folders1:
                        self.listWidget.addItem(i)

                    for i in media:
                        self.playlistView.addItem(i)
                    pass

            else:
                path1 = os.path.abspath(item.text())
                os.chdir(path1)
                folders = os.listdir()
                mp4s = re.compile(".*.mp4"); mp4 = list(filter(mp4s.match,folders))
                mp3s = re.compile(".*.mp3"); mp3 = list(filter(mp3s.match,folders))
                accs = re.compile(".*.acc"); acc = list(filter(accs.match,folders))
                media = acc+mp3+mp4

                for i in folders:
                                   
                    if i not in media:
                        self.listWidget.addItem(i)
                    else:
                        self.playlistView.addItem(i)
                   
                pass
        self.listWidget.itemDoubleClicked.connect(showFolders)

    

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Pd Music Player"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "Current Playlist"))
        item = self.listWidget.item(1)
        item.setText(_translate("MainWindow", "Media Library"))
        item = self.listWidget.item(2)
        item.setText(_translate("MainWindow", "Drives"))
        item = self.listWidget.item(3)
        item.setText(_translate("MainWindow", ""))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.playButton.setText(_translate("MainWindow", "Play"))
        self.playButton.clicked.connect(self.playSong)
        self.previousButton.setText(_translate("MainWindow", "prev"))
        #self.previousButton.clicked.connect(self.previousSong)
        self.stopButton.setText(_translate("MainWindow", "stop"))
        self.stopButton.clicked.connect(self.stopSong)
        self.nextButton.setText(_translate("MainWindow", "next"))
        self.nextButton.clicked.connect(self.nextSong)
        self.loopButton.setText(_translate("MainWindow", "loop"))
        self.repeatButton.setText(_translate("MainWindow", "repeat"))
        self.shuffleButton.setText(_translate("MainWindow", "shuffle"))
        self.equalizerButton.setText(_translate("MainWindow", "equalizer"))
        self.toolButton_9.setText(_translate("MainWindow", "..."))
        self.label.setText(_translate("MainWindow", "PLAYLISTS"))
        self.toolButton_10.setText(_translate("MainWindow", "go"))
        self.menuMedia.setTitle(_translate("MainWindow", "Media"))
        self.menuPlayback.setTitle(_translate("MainWindow", "Playback"))
        self.menuAudio.setTitle(_translate("MainWindow", "Audio"))
        self.menuVideo.setTitle(_translate("MainWindow", "Video"))
        self.menuSubtitle.setTitle(_translate("MainWindow", "Subtitle"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionnew.setText(_translate("MainWindow", "New playlistView"))
        self.actionCurrent_playlistView.setText(_translate("MainWindow", "Current Playlist"))
        self.actionShow_Subtitles.setText(_translate("MainWindow", "Show Subtitles"))
        self.actionAdd_subtitles.setText(_translate("MainWindow", "Add subtitles"))
        self.load_Playlist.setText(_translate("MainWindow", "Load New Playlist"))
#creating our playlist combination of all multimedia formats
        
        user = str(os.getlogin())
        musicFolder = "C:/Users/"+user+"/Music"
        songtracs = os.listdir(musicFolder)
        os.chdir(musicFolder)

        mp3s = re.compile(".*.mp3"); mp3 = list(filter(mp3s.match,songtracs))
        accs = re.compile(".*.acc"); acc = list(filter(accs.match,songtracs))
        mp4s = re.compile(".*.mp4"); mp4 = list(filter(mp4s.match,songtracs))
        wavs = re.compile(".*.wav"); wav = list(filter(wavs.match,songtracs))
        songs = mp3+acc+mp4+wav
        songtracks = list(songs)
        
        for trac in songtracks:
            self.playlistView.addItem(trac)
            print(trac)
            
#Function to play loaded audio, pause and unpause it
    def playSong(self):
        if self.playButton.text()=="Play":
            pygame.mixer.music.play()
            self.playButton.setText("Pause") #changes button name to pause so that when clicked again
        elif self.playButton.text()=="Pause": #it moves to the pause section 
            pygame.mixer.music.pause()
            self.playButton.setText("Unpause") #sets button name to Unpause so that when clicked again 
        else:                                   #moves to the unpause section instead of play
            pygame.mixer.music.unpause()
            self.playButton.setText("Pause") #this allows to go back to the pause function when clicked
        pass
            
    def nextSong(self,item):
        user = str(os.getlogin())
        musicFolder = "C:/Users/"+user+"/Music"
        songtracs = os.listdir(musicFolder)
        os.chdir(musicFolder)
        current_list = []

        mp3s = re.compile(".*.mp3"); mp3 = list(filter(mp3s.match,songtracs))
        accs = re.compile(".*.acc"); acc = list(filter(accs.match,songtracs))
        mp4s = re.compile(".*.mp4"); mp4 = list(filter(mp4s.match,songtracs))
        wavs = re.compile(".*.wav"); wav = list(filter(wavs.match,songtracs))
        songs = mp3+acc+mp4+wav
        songtracks = list(songs)
        
        for trac in songtracks:
            current_list.append(trac)
        print(pina_song)
        current_song = str(pina_song)
        current_song_position = current_list.index(current_song)
        next_song_position = current_song_position+1
        next_song = str(current_list[next_song_position])
        print(next_song)
                
        if pina_song == current_song:
            current_song = next_song
            current_song_position = current_list.index(current_song)
            next_song_position = current_song_position+1
            next_song = str(current_list[next_song_position])
            pygame.mixer.music.load(next_song)
            pygame.mixer.music.play()
        else:    
            pygame.mixer.music.load(next_song)
            pygame.mixer.music.play()


#Function to stop playing an audio
    def stopSong(self):
        
        pygame.mixer.music.stop()
    def pauseSong(self):
    
        pygame.mixer.music.pause()
    def unpauseSong(self):
        
        pygame.mixer.music.unpause()
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
