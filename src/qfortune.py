#!/usr/bin/env python3
# QFortune: A pyQt5 interface for reading fortune cookies.
# License: GPLv3+
# Author: Manuel Domínguez López
# Date: 2017


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import gettext
import random
import functools

PROGRAM_NAME = 'qfortune'
DESCRIPTION = 'A pyQt5 interface for reading fortune cookies'
VERSION = '0.2a'
AUTHOR = 'Manuel Domínguez López'  # See AUTHORS file
MAIL = 'mdomlop@gmail.com'
LICENSE = 'GPLv3+'  # Read LICENSE file.

savefile = os.path.join(os.getenv('HOME'), '.config/qfortune/qfortune.cookies')
epigrams = {}  # Database containing all fortune cookies
elist = []  # Only a list for random access to epigrams dict.
saved = []  # Saved cookies merged from savefile and fortune.
statics = {}

fortunes = '/usr/share/qfortune/fortunes'
fortunes_off = '/usr/share/qfortune/fortunes/off'
custom_fortunes = os.path.join(os.getenv("HOME"), '.config/qfortune/fortunes')
custom_fortunes_off = os.path.join(os.getenv("HOME"),
                        '.config/qfortune/fortunes/off')

'''
~/.config/qfortune/fortunes/off/
~/.config/qfortune/fortunes/
~/.config/qfortune/qfortune.cookies
~/.config/qfortune/qfortunerc

off
'''

def decrypt(s):  # Unix offensive fortunes are rot13 encoded
    rot13 =str.maketrans(
        'ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz',
        'NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm')
    return(str.translate(s, rot13))

def loaddb(directory, offensive=False):
    try:
        files = os.listdir(directory)
    except:
        files = []

    if files:  # Not empty
        files = list(map(lambda x: os.path.join(directory, x), files))
    for f in files:  # Loads to epigrams
        if os.path.isfile(f):
            if offensive:
                loadfile(f, True)
            else:
                loadfile(f)
        elif os.path.isdir(f):
            pass
        else:
            print(f, _('is not a regular file.'))

def loadfile(path, decode=False):
    n = 0  # Count entries
    try:  # Populate epigrams with a fortune database file
        with open(path, 'r') as f:
            text = f.read()

        for line in text.split('\n%\n'):
            if line:
                n += 1
                if decode:
                    line = decrypt(line)
                epigrams.update({line: (line, path, decode)})
        f.close()
        statics.update({path: (n, decode)})
    except PermissionError:
        fixpermissions()


def fixpermissions():
    buttonReply = QMessageBox.question(w, _('QFortune: Question'),
                            _('The database file: <p><pre>')
                            + savefile
                            + _('</pre><p>has incorrect permissions.<p>')
                            + _('It will be a read/write file.<p>')
                            + _('Do you want me to try to fix them?'),
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.Yes)
    if buttonReply == QMessageBox.Yes:
        try:
            os.chmod(savefile, 0o644)
            QMessageBox.information(w, _('QFortune: Information'),
                                    _('Permissions fixed successfully'))
        except Exception as e:
            QMessageBox.warning(w, _('QFortune: Warning'),
                                    _('I can not fix permissions.')
                                    + _('<p>Error: <b>') + str(e.errno)
                                    + _('</b><p>(<i>') + e.strerror
                                    + _('</i>)<p><b>You must fix it manually.</b>')
                                    + _("<p><p>You can't save the cookie."))
            btnSave.setEnabled(False)


def showCookie():
    global cookie
    global index
    global statics
    cookie = epigrams[elist[index]][0]
    path = epigrams[elist[index]][1]
    off = epigrams[elist[index]][2]
    if off:
        off = _('(Offensive) ')
    else:
        off = ''
    txt.setText(cookie)
    disablebuttons()
    settitle()
    sb.showMessage(off + os.path.basename(path) + ': ' + str(index + 1) + '/' + str(len(elist)) + ' ' + str(statics[path][0]))

def funcBtnNext():
    global index
    index += 1
    if index >= len(elist):
        index = 0  # Go to the beginning
    showCookie()

def funcBtnPrev():
    global index
    index -= 1
    if index < 0:
        index = len(elist) - 1  # Go to the end
    showCookie()

def funcBtnSave():
    formatcookie = cookie + '\n%\n'
    if cookie not in saved:
        try:
            with open(savefile, 'a') as f:
                f.write(formatcookie)
        except PermissionError:
            fixpermissions()
        except Exception as e:
            fatal_exception(e.errno, e.strerror)
        f.close()
        saved.append(cookie)
        btnSave.setEnabled(False)

def fatal_exception(errorcode, errortext):
    QMessageBox.critical(w, _('QFortune: Critical error'),
                            _('An unexpected error has happened.<p>')
                            + _('Error code: <b>') + str(errorcode)
                            + _('</b><p>')
                            + _('Error message: <i>') + errortext
                            + _('</i><p><p>The program will close.'))
    sys.exit(exitcode)

def funcBtnExit():
    QCoreApplication.instance().quit()

def settitle():
    title = _('QFortune:') + ' ' + str(index + 1)
    w.setWindowTitle(title)

def disablebuttons():
    # Save button:
    if cookie in saved:
        btnSave.setEnabled(False)
    else:
        btnSave.setEnabled(True)

def center_window(w):
    # get screen width and height

    resolution = QDesktopWidget().screenGeometry()
    w.move((resolution.width() / 2) - (w.frameSize().width() / 2),
           (resolution.height() / 2) - (w.frameSize().height() / 2))

def switchVisibility(widget):
    if widget.isVisible():
        widget.hide()
    else:
        widget.show()

gettext.translation('qfortune', localedir='/usr/share/locale',
fallback=True).install()

aboutappstr = _('<b>QFortune:</b> ') + _(DESCRIPTION) + '<p>'
aboutappstr +=  _('<b>Version:</b> ') + VERSION + '<p>'
aboutappstr +=  _('<b>Author:</b> ') + AUTHOR
aboutappstr += " <a href='mailto:" + MAIL + "'>email</a>" + '<p>'
aboutappstr +=  _('<b>License:</b> ') + LICENSE

app = QApplication(sys.argv)
w = QWidget()

txt = QTextEdit()
txt.setReadOnly(True)

btnNext = QPushButton(_('Next'), w)
btnNext.setIcon(QIcon.fromTheme('go-next'))
btnNext.setToolTip(_('Show next cookie if available'))
btnNext.clicked.connect(funcBtnNext)

btnPrev = QPushButton(_('Previous'), w)
btnPrev.setIcon(QIcon.fromTheme('go-previous'))
btnPrev.setToolTip(_('Show previous cookie if available'))
btnPrev.clicked.connect(funcBtnPrev)

btnSave = QPushButton(_('Save'), w)
btnSave.setIcon(QIcon.fromTheme('document-save'))
btnSave.setToolTip(_('Save the cookie in your database file'))
btnSave.clicked.connect(funcBtnSave)

btnExit = QPushButton(_('Exit'), w)
btnExit.setIcon(QIcon.fromTheme('window-close'))
btnExit.setToolTip(_('Exit program'))
btnExit.clicked.connect(funcBtnExit)

sb = QStatusBar()
sb.hide()

mainMenu = QMenuBar()


grid = QGridLayout()
grid.addWidget(mainMenu, 0, 0, 1, 4)

grid.addWidget(txt, 1, 0, 1, 4)
grid.addWidget(btnPrev, 2, 0)
grid.addWidget(btnNext, 2, 1)
grid.addWidget(btnSave, 2, 2)
grid.addWidget(btnExit, 2, 3)
grid.addWidget(sb, 3, 0, 1, 4)

aa = QWidget()
aa.setWindowTitle(_('About QFortune'))
aa.setWindowIcon(QIcon.fromTheme('qfortune'))
aa.resize(400, 300)
center_window(aa)
aaTxt = QLabel()
aaTxt.setText(aboutappstr)
aaBtnExit = QPushButton(_('Exit'), aa)
aaBtnExit.setIcon(QIcon.fromTheme('window-close'))
aaBtnExit.setToolTip(_('Exit program'))
aaBtnExit.clicked.connect(aa.close)
aaGrid = QGridLayout()
aaGrid.addWidget(aaTxt, 0, 0, 1, 2)
aaGrid.addWidget(aaBtnExit, 1, 1)
aa.setLayout(aaGrid)


# MENU CONFIGURATION
fileMenu = mainMenu.addMenu(_('File'))
actNext = QAction(QIcon.fromTheme('go-next'), _('Next cookie'))
actNext.setShortcut('Ctrl+Right')
actNext.setStatusTip(_('Show next cookie if available'))
actNext.triggered.connect(funcBtnNext)
fileMenu.addAction(actNext)
actPrev = QAction(QIcon.fromTheme('go-previous'), _('Next cookie'))
actPrev.setShortcut('Ctrl+Left')
actPrev.setStatusTip(_('Show previous cookie if available'))
actPrev.triggered.connect(funcBtnPrev)
fileMenu.addAction(actPrev)
actSave = QAction(QIcon.fromTheme('document-save'), _('Save'))
actSave.setShortcut('Ctrl+S')
actSave.setStatusTip(_('Save epigram to database'))
actSave.triggered.connect(funcBtnSave)
fileMenu.addAction(actSave)

actExit = QAction(QIcon.fromTheme('window-close'), _('Exit'))
actExit.setShortcut('Ctrl+Q')
actExit.setStatusTip(_('Exit application'))
actExit.triggered.connect(funcBtnExit)
fileMenu.addAction(actExit)

editMenu = mainMenu.addMenu('Edit')
actEditSaved = QAction(QIcon.fromTheme('document-edit'), _('Edit saved database'))
actEditSaved.setShortcut('F2')
editMenu.addAction(actEditSaved)

viewMenu = mainMenu.addMenu('View')
actShowSB = QAction(QIcon.fromTheme('kt-show-statusbar'), _('Show/Hide status bar'))
actShowSB.setShortcut('F5')
actShowSB.triggered.connect(functools.partial(switchVisibility, sb))
viewMenu.addAction(actShowSB)

searchMenu = mainMenu.addMenu('Tools')
toolsMenu = mainMenu.addMenu('Preferences')

helpMenu = mainMenu.addMenu(_('Help'))
actShowAboutApp = QAction(QIcon.fromTheme('qfortune'), _('About QFortune'))
actShowAboutApp.setStatusTip(_('Show info about this program'))
actShowAboutApp.triggered.connect(aa.show)
helpMenu.addAction(actShowAboutApp)


def main():
    global index
    global elist
    global cookie

    index = -1

    for i in fortunes, custom_fortunes:
        loaddb(i)
    for i in fortunes_off, custom_fortunes_off:
        loaddb(i, True)

    elist = list(epigrams.keys())

    #random.shuffle(elist)

    w.setWindowTitle('QFortune')
    w.setWindowIcon(QIcon.fromTheme('qfortune'))
    w.resize(500, 200)
    center_window(w)
    w.addAction(actShowSB)
    w.setLayout(grid)
    w.show()
    funcBtnNext()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
