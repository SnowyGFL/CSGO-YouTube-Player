from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QSlider
from PyQt5.QtCore import pyqtSignal, QThread
import sys, pafy, threading, time, codecs, os
# https://git.botox.bz/CSSZombieEscape/Torchlight3/src/branch/master/Torchlight/Utils.py
from Utils import Utils, DataHolder
from os import chdir, getcwd
from vlc import Instance, State
from requests import get
from bs4 import BeautifulSoup

LOGFILE = "C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\gtts.log"
COMMAND = ".yt"
TIMEOUT = 5

# Don't touch below
TIME_LIMIT = True

# Redid SmolPlayer for this menu
class MainWindow(QMainWindow):
    stop_signal = pyqtSignal()
    threadCreated = False

    def __init__(self):
        super(MainWindow, self).__init__()
        directory = getcwd()
        chdir(directory)

        # Set values
        self.paused = False
        self.nowPlaying = ""
        self.player = ""
        self.timestamp = ""
        self.volume = 40
        self.songPosition = 0
        self.run = True
        self.threadLock = threading.Lock()

        # Set MainWindow attributes
        self.setObjectName("MainWindow")
        self.resize(710, 530)
        self.setMinimumSize(QtCore.QSize(700, 500))
        self.setWindowTitle("YouTube Player - v1.0")
        self.setupUI()

    def setupUI(self):
        self.centralwidget = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # About Label
        self.aboutLabel = QtWidgets.QLabel(self.centralwidget)
        self.aboutLabel.setObjectName("aboutLabel")
        self.gridLayout.addWidget(self.aboutLabel, 0, 0, 1, 2)

        # Layout 1 = timeSlider, currentTimeLabel, totalTimeLabel
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.currentTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.currentTimeLabel.setMinimumSize(QtCore.QSize(80, 0))
        self.currentTimeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.currentTimeLabel.setObjectName("currentTimeLabel")
        self.horizontalLayout.addWidget(self.currentTimeLabel)
        # self.timeSlider = QtWidgets.QSlider(self.centralwidget)
        self.timeSlider = DoubleSlider()
        self.timeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.timeSlider.setMaximum(1)
        self.timeSlider.setSingleStep(0.0001)
        self.timeSlider.setObjectName("timeSlider")
        self.horizontalLayout.addWidget(self.timeSlider)
        self.totalTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.totalTimeLabel.setMinimumSize(QtCore.QSize(80, 0))
        self.totalTimeLabel.setObjectName("totalTimeLabel")
        self.horizontalLayout.addWidget(self.totalTimeLabel)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 9)

        # Get icons
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/skip.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("assets/delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("assets/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("assets/gflze.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        # Layout 2 = playButton, pauseButton, skipButton, deleteButton, startButton, stopButton, volumeSlider, windowIcon
        self.playButton = QtWidgets.QPushButton(self.centralwidget)
        self.playButton.setMinimumSize(QtCore.QSize(0, 30))
        self.playButton.setIcon(icon2)
        self.playButton.setObjectName("playButton")
        self.gridLayout.addWidget(self.playButton, 6, 0, 1, 1)
        self.pauseButton = QtWidgets.QPushButton(self.centralwidget)
        self.pauseButton.setMinimumSize(QtCore.QSize(0, 30))
        self.pauseButton.setIcon(icon3)
        self.pauseButton.setObjectName("pauseButton")
        self.gridLayout.addWidget(self.pauseButton, 6, 1, 1, 1)
        self.skipButton = QtWidgets.QPushButton(self.centralwidget)
        self.skipButton.setMinimumSize(QtCore.QSize(0, 30))
        self.skipButton.setIcon(icon)
        self.skipButton.setIconSize(QtCore.QSize(16, 16))
        self.skipButton.setObjectName("skipButton")
        self.gridLayout.addWidget(self.skipButton, 6, 2, 1, 1)
        self.deleteButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteButton.setMinimumSize(QtCore.QSize(0, 30))
        self.deleteButton.setIcon(icon1)
        self.deleteButton.setObjectName("deleteButton")
        self.gridLayout.addWidget(self.deleteButton, 6, 3, 1, 1)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setMinimumSize(QtCore.QSize(0, 30))
        self.startButton.setObjectName("startButton")
        self.gridLayout.addWidget(self.startButton, 6, 4, 1, 1)
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setMinimumSize(QtCore.QSize(0, 30))
        self.stopButton.setObjectName("stopButton")
        self.gridLayout.addWidget(self.stopButton, 6, 5, 1, 1)
        self.volumeSlider = QtWidgets.QSlider(self.centralwidget)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setProperty("value", 40)
        self.volumeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout.addWidget(self.volumeSlider, 6, 6, 1, 3)
        self.setWindowIcon(icon4)

        # Layout 3 = listBox, logBrowser, urlBox, addButton, nowPlaying, checkBox
        self.listBox = QtWidgets.QListWidget(self.centralwidget)
        self.listBox.setAlternatingRowColors(True)
        self.listBox.setUniformItemSizes(True)
        self.listBox.setObjectName("listBox")
        self.gridLayout.addWidget(self.listBox, 1, 0, 1, 6)
        self.logBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.logBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.logBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.logBrowser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.logBrowser.setObjectName("logBrowser")
        self.gridLayout.addWidget(self.logBrowser, 1, 6, 1, 3)
        self.urlBox = QtWidgets.QLineEdit(self.centralwidget)
        self.urlBox.setObjectName("urlBox")
        self.gridLayout.addWidget(self.urlBox, 2, 0, 1, 8)
        self.addButton = QtWidgets.QPushButton(self.centralwidget)
        self.addButton.setObjectName("addButton")
        self.gridLayout.addWidget(self.addButton, 2, 8, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.nowPlayingLabel = QtWidgets.QLabel(self.centralwidget)
        self.nowPlayingLabel.setObjectName("nowPlaying")
        self.gridLayout.addWidget(self.nowPlayingLabel, 5, 0, 1, 9)
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 0, 2, 1, 1)

        # MenuBar, StatusBar, ErrorDialog
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.errorDialog = QtWidgets.QErrorMessage(self)

        # Re-translate the UI
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.refresh()

        # Connect events
        self.urlBox.returnPressed.connect(self.addButtonClicked)
        self.addButton.clicked.connect(self.addButtonClicked)
        self.deleteButton.clicked.connect(self.deleteButtonClicked)
        self.playButton.clicked.connect(self.playButtonClicked)
        self.pauseButton.clicked.connect(self.pauseButtonClicked)
        self.timeSlider.sliderReleased.connect(lambda: self.setSlider(self.timeSlider.value()))
        self.skipButton.clicked.connect(self.skipButtonClicked)
        self.volumeSlider.valueChanged[int].connect(self.volumeSliderChanged)
        self.startButton.clicked.connect(self.startButtonClicked)
        self.stopButton.clicked.connect(self.stopButtonClicked)
        self.checkBox.stateChanged.connect(self.checkBoxChanged)

    # Set the text for each element
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.aboutLabel.setText(_translate("MainWindow", "Made by Snowy"))
        self.currentTimeLabel.setText(_translate("MainWindow", "00:00:00"))
        self.totalTimeLabel.setText(_translate("MainWindow", "00:00:00"))
        self.skipButton.setText(_translate("MainWindow", "SKIP"))
        self.deleteButton.setText(_translate("MainWindow", "DEL"))
        self.startButton.setText(_translate("MainWindow", "START"))
        self.stopButton.setText(_translate("MainWindow", "STOP"))
        self.addButton.setText(_translate("MainWindow", "ADD"))
        self.playButton.setText(_translate("MainWindow", "PLAY"))
        self.pauseButton.setText(_translate("MainWindow", "PAUSE"))
        self.nowPlayingLabel.setText(_translate("MainWindow", "Now Playing:"))
        self.checkBox.setText(_translate("MainWindow", "Time limit"))

    # Connect "PLAY" button
    def playButtonClicked(self):
        if self.paused:
            self.paused = False
            self.player.set_pause(0)
            self.playButton.setEnabled(False)
        else:
            t1 = threading.Thread(target=self.play)
            t1.daemon = True
            t1.start()

    def play(self):
        with open("urllist.txt", "r") as f:
            url = f.readline().strip()
            link = url.split(";")
        if link[0]:
            try:
                self.threadLock.acquire()
                audio = pafy.new(link[0])
                best = audio.getbest()
                playurl = best.url
                vInstance = Instance("--novideo")
                self.player = vInstance.media_player_new()
                media = vInstance.media_new(playurl)
                self.player.set_media(media)

                if audio.duration == "00:00:00":
                    self.update()
                    self.logBrowser.append("Denied. Tried to play livestream video...")
                    self.threadLock.release()
                    return

                self.player.play()
                self.player.audio_set_volume(int(self.volume))
                self.nowPlaying = audio.title
                self.totalTimeLabel.setText(audio.duration)
                h, m, s = audio.duration.split(":")
                duration = int(h) * 3600 + int(m) * 60 + int(s)
                # print(duration)
                ticker = 1 / duration
                try:
                    self.nowPlayingLabel.setText(f"Now Playing: {self.nowPlaying}")
                    self.logBrowser.append(f"Now playing: {self.nowPlaying}")
                    with open("nowPlaying.txt", "w", encoding="utf-8") as f:
                        f.write(self.nowPlaying + '   ')
                except:
                    self.nowPlaying = self.nowPlayingLabel.encode("unicode_escape")
                    self.nowPlayingLabel.setText(f"Now Playing: {self.nowPlaying}")
                    self.logBrowser.append(f"Now playing: {self.nowPlaying}")
                    with open("nowPlaying.txt", "w", encoding="utf-8") as f:
                        f.write(str(self.nowPlaying) + '   ')
                self.playButton.setEnabled(False)
                self.threadLock.release()
                self.deleteButton.setEnabled(False)
                self.skipButton.setEnabled(False)
                try:
                    ticker2 = int(link[1]) / duration
                    self.songPosition = ticker2
                    self.player.set_position(ticker2)
                    self.timeSlider.setValue(self.songPosition)
                except IndexError:
                    pass
                # Redundant code, remove in future™
                for i in range(1):
                    self.songPosition += ticker
                    self.timeSlider.setValue(self.songPosition)
                    self.getTime()
                    time.sleep(1)
                if self.player.get_state() == State.Ended:
                    self.nowPlayingLabel.setText("RETRYING CONNECTION")
                    self.play()
                else:
                    self.update()
                self.skipButton.setEnabled(True)
                self.deleteButton.setEnabled(True)
                try:
                    self.songPosition = ticker2 + (1 * ticker)
                    self.timeSlider.setValue(ticker2 + (1 * ticker))
                except UnboundLocalError:
                    self.songPosition = ticker * 1
                    self.timeSlider.setValue(ticker * 1)
                timeout = time.time() + TIMEOUT
                while self.player.get_state() == State.Playing or self.player.get_state() == State.Paused:
                    if not self.paused:
                        self.songPosition += ticker
                        self.timeSlider.setValue(self.songPosition)
                        # print(self.songPosition)
                        # print(self.timeSlider.value())
                        self.getTime()
                        time.sleep(1)
                    if time.time() > timeout:
                        global TIME_LIMIT
                        if TIME_LIMIT:
                            break
                    if not self.run:
                        self.player.stop()
                        sys.exit()
                self.songPosition = 0
                self.timeSlider.setValue(0)
                self.player.stop()
                self.play()
            except Exception as e:
                self.threadLock.release()
                self.errorDialog.setWindowTitle("Warning")
                self.errorDialog.showMessage(str(e))
                self.update()
                self.play()
        else:
            self.playButton.setEnabled(True)
            self.nowPlayingLabel.setText("Now Playing:")
            self.currentTimeLabel.setText("00:00:00")
            self.totalTimeLabel.setText("00:00:00")
            with open("nowPlaying.txt", "w", encoding="utf-8") as f:
                f.write("No songs playing currently.   ")

    # Connect "START" button
    def startButtonClicked(self):
        if not self.threadCreated:
            self.thread = logToggle()
            self.logBrowser.append("Thread started")
            self.thread.writeLog.connect(self.appendText)
            self.thread.URLinput.connect(self.checkLogURL)
            print(self.thread)
            self.thread.start()
            self.threadCreated = True
        else:
            self.logBrowser.append("Thread already created")

    # Connect "STOP" button
    def stopButtonClicked(self):
        if not self.threadCreated:
            self.logBrowser.append("Thread already stopped")
            return
        self.logBrowser.append("Thread stopped & deleted")
        self.thread.stop()
        #self.thread.finished.connect(self.thread.stop)
        self.thread.quit()
        self.threadCreated = False
        print(self.thread)

    # Connect "SKIP" button
    def skipButtonClicked(self):
        try:
            self.player.stop()
            self.paused = False
            self.logBrowser.append("Skipped current track!")
        except AttributeError:
            pass

    # Connect "PAUSE" button
    def pauseButtonClicked(self):
        if not self.player:
            return
        if self.player.get_state() == State.Playing:
            self.player.set_pause(1)
            self.paused = True
            self.playButton.setEnabled(True)
        else:
            pass

    # Connect "ADD" button and fuctions
    def addButtonClicked(self):
        url = self.urlBox.text()
        self.urlBox.clear()
        if self.validURL(url):
            # print("ValidURL")
            pass
        else:
            self.errorDialog.setWindowTitle("Error - Invalid URL")
            self.errorDialog.showMessage("Seems like a non YouTube URL was entered or the urlBox was empty...")

    def checkLogURL(self, message):
        if self.validURL(message):
            try:
                if self.player.get_state() == State.Playing or self.player.get_state() == State.Paused:
                    return
                else:
                    self.playButtonClicked()
            except AttributeError:
                self.playButtonClicked()
        else:
            pass

    def validURL(self, url):
        if url.startswith("https://www.youtube.com/") or url.startswith("https://youtu.be") or url.startswith(
                "https://m.youtube.com"):
            if "playlist" in url:
                self.errorDialog.setWindowTitle("Error - Playlist URL")
                self.errorDialog.showMessage("Inputting playlist URL is not supported")
                self.refresh()
            else:
                url = self.checkURL(url)
                url2 = url.split(";")
                webpage = get(url2[0]).text
                soup = BeautifulSoup(webpage, 'lxml')
                title = soup.title.string
                with open("urllist.txt", "a") as f:
                    self.logBrowser.append(f"Added {url2} into the queue!")
                    f.write(f"{url}\n")
                with open("songlist.txt", "a", encoding="utf-8") as f:
                    try:
                        f.write(f"{title} - {url2[1]}s\n")
                    except IndexError:
                        f.write(f"{title}\n")
                self.refresh()
                return True
                # print(title)
                # print(soup)

    # Connect "DELETE" button
    def deleteButtonClicked(self):
        selected = self.listBox.currentRow()
        if selected == -1:
            self.logBrowser.append("No row selected in the list")
            return
        self.listBox.takeItem(self.listBox.currentRow())
        with open("songlist.txt", "r", encoding="utf-8") as f:
            line = f.readlines()
            try:
                self.logBrowser.append(f"Removed \"{line[selected]}\" from the list!")
                line.pop(selected)
                line = "".join(line)
            except IndexError:
                return
        with open("songlist.txt", "w", encoding="utf-8") as f:
            f.write(line)
        with open("urllist.txt", "r") as f:
            line = f.readlines()
            line.pop(selected)
            line = "".join(line)
        with open("urllist.txt", "w") as f:
            f.write(line)

    # Connect "checkBox" button
    def checkBoxChanged(self, state):
        global TIME_LIMIT
        if state == QtCore.Qt.Checked:
            TIME_LIMIT = True
            # print(TIME_LIMIT)
        else:
            TIME_LIMIT = False
            # print(TIME_LIMIT)

    # Functions
    def appendText(self, message):
        self.logBrowser.append(message)

    def setSlider(self, amount):
        try:
            self.player.set_position(amount)
            self.songPosition = amount
            # print(self.songPosition)
        except:
            self.timeSlider.setValue(0)

    def volumeSliderChanged(self, value):
        try:
            self.player.audio_set_volume(int(value))
            self.volume = value
            # print(value)
        except:
            self.volume = value

    def getTime(self):
        vTime = self.player.get_time() // 1000
        # print(vTime)
        vTime = time.strftime("%H:%M:%S", time.gmtime(vTime))
        # print(vTime)
        self.currentTimeLabel.setText(f"{vTime}")

    def update(self):
        with open("urllist.txt", "r") as f:
            line = f.readlines()
        with open("urllist.txt", "w") as f:
            f.writelines(line[1:])
        with open("songlist.txt", "r", encoding="utf-8") as f:
            line = f.readlines()
        with open("songlist.txt", "w", encoding="utf-8") as f:
            f.writelines(line[1:])
        self.refresh()

    def refresh(self):
        # Read from songlist.txt to update listBox
        with open("songlist.txt", "r", encoding="utf-8") as f:
            songlist = f.readlines()
            self.listBox.clear()
            for songs in songlist:
                try:
                    self.listBox.addItem(songs)
                    # print(songs)
                except:
                    song = songs.encode("unicode_escape")
                    self.listBox.addItem(f"{song}\n")

    def checkURL(self, url):
        # Check timestamp of YouTube URL
        # https://git.botox.bz/CSSZombieEscape/Torchlight3/src/branch/master/Torchlight/Commands.py#L611
        Temp = DataHolder()
        Time = None

        if Temp(url.find("&t=")) != -1 or Temp(url.find("?t=")) != -1 or Temp(url.find("#t=")) != -1:
            TimeStr = url[Temp.value + 3:].split('&')[0].split('?')[0].split('#')[0]
            if TimeStr:
                Time = Utils.ParseTime(TimeStr)
                url = url[:43] + ";" + str(Time)
                return url
                # print(url)
        elif len(url) <= 43:
            return url
        else:
            self.errorDialog.setWindowTitle("Error - Invalid URL")
            self.errorDialog.showMessage(f"Playlist URL is not supported currently. Trying to get the first 43 characters of the link instead. {url[:43]}")
            return url[:43]

        '''
        if len(url) <= 43:
            return url
        else:
            self.errorDialog.setWindowTitle("Error - Invalid URL")
            self.errorDialog.showMessage(f"Playlist URL is not supported currently. Trying to get the first 43 characters of the link instead. {url[:43]}")
            return url[:43]
        '''

    def raise_error(self):
        assert False


# Class for the START/STOP button
class logToggle(QThread):
    writeLog = pyqtSignal(str)
    URLinput = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.continue_run = True

    def splicer(self, mystr, sub):
        index = mystr.find(sub)
        if index != -1:
            return mystr[index:]
        else:
            pass

    def run(self):
        # print("run")
        with open(LOGFILE, "r", encoding="utf-8") as f:
            f.seek(0, 2)
            self.writeLog.emit("Reading file...")

            while self.continue_run:
                # print("test")
                logline = f.readline()
                if COMMAND in logline:
                    # STRIP NEW LINES AT START AND END
                    logline = logline.strip("\n")
                    logline = logline.strip('\t')
                    self.writeLog.emit(logline)
                    print(logline)
                    string = self.splicer(logline, COMMAND)
                    print(string)
                    string2 = string.split()
                    print(string2)

                    if string[len(string2[0]):].isspace():
                        print("No input found")

                    self.URLinput.emit(string[len(string2[0]):].lstrip())
                QThread.msleep(10)
            self.finished.emit()

    def stop(self):
        # print("stop")
        self.continue_run = False


# https://stackoverflow.com/a/50300848
class DoubleSlider(QSlider):

    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals=3, *args, **kargs):
        super(DoubleSlider, self).__init__( *args, **kargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value())/self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self._multi)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(int(value * self._multi))

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))







def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()


if __name__ == "__main__":
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


