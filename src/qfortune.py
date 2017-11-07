#!/usr/bin/env python3
# QFortune: A pyQt5 interface for reading fortune cookies.
# License: GPLv3+
# Author: Manuel Domínguez López
# Date: 2017


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import subprocess
import os
import gettext

PROGRAM_NAME = 'qfortune'
DESCRIPTION = 'A pyQt5 interface for reading fortune cookies'
VERSION = '0.1b'
AUTHOR = 'Manuel Domínguez López'  # See AUTHORS file
MAIL = 'mdomlop@gmail.com'
LICENSE = 'GPLv3+'  # Read LICENSE file.

fortune = []  # Temp database containing fortune cookies
saved = []  # Saved cookies merged from savefile and fortune.
savefile = os.getenv("HOME") + '/qfortune.cookies'


def loaddb():
    try:  # Populate saved with
        with open(savefile, 'r') as loadsaved:
            text = loadsaved.read()

        for line in text.split('\n%\n'):
            saved.append(line)  # Do not line.strip() for match with original
        loadsaved.close()
    except FileNotFoundError:
        QMessageBox.information(w, _('QFortune: Information'),
                                _('No database file was found.<p>')
                                + _('A new one will be created at: <p><pre>')
                                + savefile
                                + '</pre>')
    except PermissionError:
        fixpermissions()
    except IsADirectoryError:
        QMessageBox.critical(w, _('QFortune: Critical error'),
                                _('The database file: <p><pre>')
                                + savefile
                                + _('</pre><p>is a directory.<p>')
                                + _('It will be a read/write file.'))
        sys.exit()
    except Exception as e:
        fatal_exception(e.errno, e.strerror)
    except AttributeError:
        fatal_exception(1, e.strerror)

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
            btn_save.setEnabled(False)


def printcookie(i=-1):
    txt.setText(fortune[i])

def func_btn_new():
    global current
    cookie = subprocess.getoutput('fortune')
    fortune.append(cookie)
    index = len(fortune) - 1
    current = index
    printcookie()
    settitle(current)
    disablebuttons(fortune[current])  # Prevent repetition

def func_btn_prev():
    global current
    if current == 0:
        current = len(fortune) - 1
    else:
        current = current - 1
    printcookie(current)
    settitle(current)
    disablebuttons(fortune[current])

def func_btn_next():
    global current
    if current == len(fortune) - 1:
        current = 0
    else:
        current = current + 1
    printcookie(current)
    settitle(current)
    disablebuttons(fortune[current])

def func_btn_save():
    cookie = fortune[current]
    formatcookie = fortune[current] + '\n%\n'
    if cookie not in saved:
        try:
            with open(savefile, 'a') as mysavefile:
                mysavefile.write(formatcookie)
            saved.append(cookie)
            disablebuttons(cookie)
        except PermissionError:
            fixpermissions()
        except Exception as e:
            fatal_exception(e.errno, e.strerror)

def fatal_exception(errorcode, errortext):
    QMessageBox.critical(w, _('QFortune: Critical error'),
                            _('An unexpected error has happened.<p>')
                            + _('Error code: <b>') + str(errorcode)
                            + _('</b><p>')
                            + _('Error message: <i>') + errortext
                            + _('</i><p><p>The program will close.'))
    sys.exit(exitcode)

def func_btn_exit():
    QCoreApplication.instance().quit()

def settitle(index):
    title = _('QFortune:') + ' ' + str(index + 1)
    w.setWindowTitle(title)

def disablebuttons(cookie):
    # Save button:
    if cookie in saved:
        btn_save.setEnabled(False)
    else:
        btn_save.setEnabled(True)
        btn_save.setIcon(QIcon.fromTheme('document-save'))
        btn_save.setToolTip(_('Save the cookie in your database file'))
        btn_save.setText(_('Save'))
    # Prev button:
    if len(fortune) == 1:
        btn_prev.setEnabled(False)
        btn_next.setEnabled(False)
    else:
        btn_prev.setEnabled(True)
        btn_next.setEnabled(True)

def center_window(w):
    # get screen width and height

    resolution = QDesktopWidget().screenGeometry()
    w.move((resolution.width() / 2) - (w.frameSize().width() / 2),
           (resolution.height() / 2) - (w.frameSize().height() / 2))

gettext.translation('qfortune', localedir='/usr/share/locale', fallback=True).install()

app = QApplication(sys.argv)
w = QWidget()

txt = QTextEdit()
txt.setReadOnly(True)

btn_new = QPushButton(_('New cookie'), w, default=True)
btn_new.setIcon(QIcon.fromTheme('document-new'))
btn_new.setToolTip(_('Show new cookie'))
btn_new.clicked.connect(func_btn_new)

btn_next = QPushButton(_('Next'), w)
btn_next.setIcon(QIcon.fromTheme('go-next'))
btn_next.setToolTip(_('Show next cookie if available'))
btn_next.clicked.connect(func_btn_next)

btn_prev = QPushButton(_('Previous'), w)
btn_prev.setIcon(QIcon.fromTheme('go-previous'))
btn_prev.setToolTip(_('Show previous cookie if available'))
btn_prev.clicked.connect(func_btn_prev)

btn_save = QPushButton(_('Save'), w)
btn_save.setIcon(QIcon.fromTheme('document-save'))
btn_save.setToolTip(_('Save the cookie in your database file'))
btn_save.clicked.connect(func_btn_save)

btn_exit = QPushButton(_('Exit'), w)
btn_exit.setIcon(QIcon.fromTheme('window-close'))
btn_exit.setToolTip(_('Exit program'))
btn_exit.clicked.connect(func_btn_exit)

grid = QGridLayout()
grid.addWidget(txt, 0, 0, 1, 5)
grid.addWidget(btn_new, 1, 0)
grid.addWidget(btn_prev, 1, 1)
grid.addWidget(btn_next, 1, 2)
grid.addWidget(btn_save, 1, 3)
grid.addWidget(btn_exit, 1, 4)


def main():
    global current
    loaddb()
    w.setWindowTitle('QFortune')
    w.setWindowIcon(QIcon.fromTheme('qfortune'))
    w.resize(500, 200)
    center_window(w)
    w.setLayout(grid)
    w.show()
    func_btn_new()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
