import sys
import os
from PySide2 import QtWidgets, QtGui
import pickle
from mfcc import mfcc, vad_thr, cmvn, writehtk
from accStat import test, test_decision
import numpy as numpy
from Play import start_play
from record import start_record


class MyWidget(QtWidgets.QWidget):
    nmix = 4
    ubmDir = 'GMM' + str(nmix)
    Tardest = 'MAP3_Tau10.0'

    with open(ubmDir + '/' + 'ubm') as f:
        print "load ubm .. %s" %(f)
        ubm_mu, ubm_cov, ubm_w = pickle.load(f)

    winlen, ovrlen, pre_coef, nfilter, nftt = 0.025, 0.02, 0.97, 26, 512
    opts = 1
    emotion = ""
    state = ""
    speaker = ""
    result = ""

    def center(self):
        qRect = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())

    def add_files(self):
        self.files.clear()
        for f in os.listdir("Test/"):
            if f.endswith(".wav"):
                print(f)
                self.files.addItem(f)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        font = QtGui.QFont("Cursive", 18, QtGui.QFont.Bold)
        painter.setFont(font)
        painter.drawText(15, 230, self.result+self.emotion)
        painter.drawText(15, 280, self.state)

    def record(self,button):
        text, ok = QtWidgets.QInputDialog().getText(self, "Emotion Recognition", "Enter Your Name:")

        if ok and text:
            self.speaker = text
            print "Speaker: "+self.speaker
            wFile = "Test/"+self.speaker+".wav"
            start_record(self, wFile, 5, self.state)
            state = "File saved as "+self.speaker
            self.repaint()
            print 'File saved as '+self.speaker+".wav"
            self.add_files()
            fFile = "feat/Test/"+self.speaker+".htk"
            try:
                # call MFCC feature extraction subroutine
                f, E, fs = mfcc(wFile, self.winlen, self.ovrlen, self.pre_coef, self.nfilter, self.nftt)
                # VAD part
                if self.opts == 1:
                    f = vad_thr(f, E)
                    # Energy threshold based VAD [comment this  line if you would like to plugin the rVAD labels]
                elif self.opts == 0:
                    l = numpy.loadtxt('..corresponding vad label file')
                    # [Plugin the VAD label generated by rVAD matlab]

                    if (len(f) - len(l)) == 1:
                        # 1-[end-frame] correction [matlab/python]
                        l = numpy.append(l, l[-1:, ])
                    elif (len(f) - len(l)) == -1:
                        l = numpy.delete(l, -1)

                    if (len(l) == len(f)) and (len(numpy.argwhere(l == 1)) != 0):
                        idx = numpy.where(l == 1)
                        f = f[idx]
                    else:
                        print "mismatch frames between: label and feature files or no voice-frame in VAD"
                        exit()
                    # Zero mean unit variance  normalize after VAD
                f = cmvn(f)

                # write the VAD+normalized features  in file
                if not os.path.exists(os.path.dirname(fFile)):
                    # create director for the feature file
                    os.makedirs(os.path.dirname(fFile))

                writehtk(fFile, f, 0.01)

            except:
                print("Fail1..%s ---> %s\n" % (wFile, fFile))

            if button.text() == "Live Detection":
                self.test_emotion(name=self.speaker)
        else:
            self.state = "Not valid Name"
            self.repaint()

        return

    def test_emotion(self, name):
        if name:
            value = name
        else:
            file = self.files.currentItem()
            print file.text()
            value = file.text().split(".")[0]
        fFile = "feat/Test/"+value+".htk"
        self.emotion=test(fFile, self.Tardest, self.ubm_mu, self.ubm_cov, self.ubm_w)
        self.result = "Detected as: "
        self.repaint()
        start_play(self.emotion+"_dec.wav")
        self.state = "Say Yes or No"
        self.repaint()

        wFile = "Test_dec.wav"
        start_record(self, wFile, 3, self.state)
        fFile= "feat/Test/"+wFile+".htk"

        try:

            # call MFCC feature extraction subroutine
            f, E, fs = mfcc(wFile, self.winlen, self.ovrlen, self.pre_coef, self.nfilter, self.nftt)

            # VAD part
            if self.opts == 1:
                f = vad_thr(f, E)
                # Energy threshold based VAD [comment this  line if you would like to plugin the rVAD labels]
            elif self.opts == 0:
                l = numpy.loadtxt('..corresponding vad label file')
                # [Plugin the VAD label generated by rVAD matlab]

                if (len(f) - len(l)) == 1:
                    # 1-[end-frame] correction [matlab/python]
                    l = numpy.append(l, l[-1:, ])
                elif (len(f) - len(l)) == -1:
                    l = numpy.delete(l, -1)

                if (len(l) == len(f)) and (len(numpy.argwhere(l == 1)) != 0):
                    idx = numpy.where(l == 1)
                    f = f[idx]
                else:
                    print "mismatch frames between: label and feature files or no voice-frame in VAD"
                    exit()

        # Zero mean unit variance  normalize after VAD
            f = cmvn(f)

        # write the VAD+normalized features  in file
            if not os.path.exists(os.path.dirname(fFile)):
                # create director for the feature file
                os.makedirs(os.path.dirname(fFile))

        #print("%s --> %s\n" %(wFile,fFile))

            writehtk(fFile, f, 0.01)

        except:
            print("Fail ..%s ---> %s\n" %(wFile, fFile))

        decision = test_decision(fFile, 'DEC3_Tau10.0', self.ubm_mu, self.ubm_cov, self.ubm_w)

        if decision == "YES":
            start_play(self.emotion+".wav")

        self.result = ""
        self.emotion = ""
        self.state = ""
        self.repaint()
        return

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.setWindowTitle("Emotion Recognition")
        self.setGeometry(200, 100, 255, 400)
        self.center()

        self.files = QtWidgets.QListWidget(self)
        self.add_files()

        self.test = QtWidgets.QPushButton("Test Emotion", self)
        self.test.setGeometry(125, 310, 110, 30)
        self.test.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.test.clicked.connect(self.test_emotion)

        self.live = QtWidgets.QPushButton("Live Detection", self)
        self.live.setGeometry(125, 350, 110, 30)
        self.live.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.live.clicked.connect(lambda: self.record(button=self.live))

        self.record_button = QtWidgets.QPushButton("Record", self)
        self.record_button.setGeometry(20, 310, 100, 30)
        self.record_button.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.record_button.clicked.connect(lambda : self.record(button=self.record_button))

        self.play = QtWidgets.QPushButton("Play", self)
        self.play.setGeometry(20, 350, 100, 30)
        self.play.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.play.clicked.connect(lambda: start_play(file_play=self.files.currentItem().text(), choice=0))


app = QtWidgets.QApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec_())
