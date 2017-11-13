#!/usr/bin/python3

import os
import random
import gettext

from PyQt5.QtCore import (QSettings, QSize,
                          Qt, QT_VERSION_STR)
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtWidgets import (QWidget, QAction, QApplication, QComboBox,
                             QMainWindow, QLabel,
                             QTabWidget, QGridLayout, QVBoxLayout,
                             QHBoxLayout, QMessageBox, QTextEdit, QPushButton)

PROGRAM_NAME = "QFortune"
EXECUTABLE_NAME = "qfortune"

gettext.translation("qfortune", localedir="/usr/share/locale",
                    fallback=True).install()

DESCRIPTION = _("A pyQt5 interface for reading fortune cookies")
VERSION = "0.5a"
AUTHOR = "Manuel Domínguez López"  # See AUTHORS file
MAIL = "mdomlop@gmail.com"
SOURCE = "https://github.com/mdomlop/qfortune"
LICENSE = "GPLv3+"  # Read LICENSE file.

COPYRIGHT = '''
Copyright: 2017 Manuel Domínguez López <mdomlop@gmail.com>
License: GPL-3.0+

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
'''


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.epigrams = {}  # Database containing all fortune cookies
        self.elist = []  # Only a list for random access to epigrams dict.
        self.saved = []  # Saved cookies merged from savefile and fortune.
        self.statics = {}
        self.cookie_files = []  # All cookie files

        self.loadDir()
        self.elist = list(self.epigrams.keys())
        self.nepigrams = len(self.elist)
        random.shuffle(self.elist)

        self.statusOrigin = QLabel()
        self.statusOffensive = QLabel()
        self.statusSaved = QLabel()
        self.statusCopied = QLabel()

        self.comboGoTo = QComboBox()
        for i in range(self.nepigrams):
            self.comboGoTo.addItem(str(i + 1))
        self.comboGoTo.setEditable(True)
        self.comboGoTo.currentIndexChanged[str].connect(self.goToComboIndex)
        # self.comboGoTo.setValidator('#')

        self.index = -1

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.setCentralWidget(self.textEdit)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        self.nextCookie()  # Starts showing a cookie

        self.readSettings()

    def decrypt(self, s):  # Unix offensive fortunes are rot13 encoded
        rot13 = str.maketrans(
            "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
            "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
        return(str.translate(s, rot13))

    def loadDir(self):
        ''' Only returns a list of found cookie files. '''
        app_fortunes = "/usr/share/" + EXECUTABLE_NAME + "/fortunes"
        custom_fortunes = os.path.join(os.getenv("HOME"),
                                       ".config/" + EXECUTABLE_NAME
                                       + "/fortunes")
        fortunes = [app_fortunes, custom_fortunes]

        for base in fortunes:
            if os.path.isdir(base):
                try:
                    langs = os.listdir(base)
                except:
                    next  # Skip empty directory
                for lang in langs:
                    path = os.path.join(base, lang)
                    cdir = (path, lang, False)
                    path = os.path.join(path, 'off')  # Check if offensive
                    ocdir = (path, lang, True)

                    for i in cdir, ocdir:
                        try:
                            l = os.listdir(i[0])
                        except:
                            l = []
                        for f in l:
                            f = os.path.join(i[0], f)
                            if os.path.isfile(f):
                                self.loadFile(f, i[1], i[2])

    def loadFile(self, path, lang, decode):
        ''' Adds a cookie file to the epigrams DB '''
        n = 0  # Count entries
        try:  # Populate epigrams with a fortune database file
            with open(path, "r") as f:
                text = f.read()
        except:
            text = None
        f.close()
        if text:
            for line in text.split("\n%\n"):
                if line:
                    n += 1
                    if decode:
                        line = self.decrypt(line)
                    self.epigrams.update({line: (line, path, lang, decode)})
            self.statics.update({path: (n, decode)})

    def goToComboIndex(self):
        i = self.comboGoTo.currentIndex()
        if i >= 0 and i < self.nepigrams:
            self.index = i
        self.showCookie()

    def firstCookie(self):
        self.index = 0
        self.showCookie()

    def lastCookie(self):
        self.index = self.nepigrams - 1
        self.showCookie()

    def nextCookie(self):
        self.index += 1
        if self.index >= self.nepigrams:
            self.index = 0  # Go to the beginning
        self.showCookie()

    def prevCookie(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.nepigrams - 1  # Go to the end
        self.showCookie()

    def saveCookie(self):
        formatcookie = self.cookie + "\n%\n"
        savename = "favorites.cookies"
        savebase = os.path.join(os.getenv("HOME"), ".config", EXECUTABLE_NAME)
        savefile = os.path.join(savebase, savename)
        if self.cookie not in self.saved:
            try:
                os.makedirs(savebase, exist_ok=True)
            except:
                QMessageBox.warning(self, _("Warning"),
                                    _("I can not create the directory"))
                return(1)
            try:
                with open(savefile, 'a') as f:
                    f.write(formatcookie)
            except PermissionError:
                QMessageBox.warning(self, _("Warning"),
                                    _("I have no permission to write the file"))
                f.close()
                return(1)
            except:
                QMessageBox.warning(self, _("Warning"),
                                    _("I can not write the file"))
                f.close()
                return(1)
            f.close()
            self.saved.append(self.cookie)
        self.updateInterface()

    def copyCookie(self):
        self.textEdit.selectAll()
        self.textEdit.copy()
        self.textEdit.clearFocus()
        self.updateInterface()

    def about(self):
        aboutdialog.show()

    def isSaved(self):
        ''' Returns status, text and abbreviation '''
        if self.cookie in self.saved:
            return((False, _("Saved")))
        return((True, _("Unsaved")))

    def isOffensive(self):
        ''' Returns status, text and abbreviation '''
        if self.epigrams[self.elist[self.index]][3]:  # 3 is true if offensive
            return((True, _("Offensive")))
        return((False, ""))

    def isCopied(self):
        if QApplication.clipboard().text() == self.cookie:
            return((True, _("Copied")))
        return((False, ""))

    def isFirst(self):
        if self.index == 0:
            return(True)
        return(False)

    def isLast(self):
        if self.index == self.nepigrams - 1:
            return(True)
        return(False)

    def updateStatus(self):
        path = self.epigrams[self.elist[self.index]][1]  # 1 is path
        origin = _("From:") + " " + os.path.basename(path)
        offensive = self.isOffensive()[1]
        saved = self.isSaved()[1]
        copied = self.isCopied()[1]
        self.statusOrigin.setText(origin)
        self.statusOffensive.setText(offensive)
        self.statusSaved.setText(saved)
        self.statusCopied.setText(copied)

    def updateInterface(self):
        self.comboGoTo.setCurrentIndex(self.index)
        self.firstAct.setEnabled(not self.isFirst())
        self.prevAct.setEnabled(not self.isFirst())

        self.lastAct.setEnabled(not self.isLast())
        self.nextAct.setEnabled(not self.isLast())

        self.copyAct.setEnabled(not self.isCopied()[0])
        self.saveAct.setEnabled(self.isSaved()[0])

        self.updateStatus()

    def noCookies(self):
            QMessageBox.critical(self, _("Critical error"),
                                 _("There is no cookies!"))
            return(1)

    def showCookie(self):
        if len(self.elist) == 0:
            self.noCookies()
        self.cookie = self.epigrams[self.elist[self.index]][0]  # 0 is text
        self.textEdit.setText(self.cookie)
        self.updateInterface()

    def createActions(self):
        self.firstAct = QAction(QIcon.fromTheme('go-first'),
                                _("&First"),
                                self, shortcut=QKeySequence.MoveToStartOfLine,
                                statusTip=_("Show first cookie"),
                                triggered=self.firstCookie)

        self.lastAct = QAction(QIcon.fromTheme('go-last'),
                               _("&Last"),
                               self, shortcut=QKeySequence.MoveToEndOfLine,
                               statusTip=_("Show last cookie"),
                               triggered=self.lastCookie)

        self.nextAct = QAction(QIcon.fromTheme('go-next'),
                               _("&Next"),
                               self, shortcut=QKeySequence.MoveToNextPage,
                               statusTip=_("Show next cookie"),
                               triggered=self.nextCookie)

        self.prevAct = QAction(QIcon.fromTheme('go-previous'),
                               _("&Previous"),
                               self, shortcut=QKeySequence.MoveToPreviousPage,
                               statusTip=_("Show previous cookie"),
                               triggered=self.prevCookie)

        self.saveAct = QAction(QIcon.fromTheme('document-save'), _("&Save"),
                               self, shortcut=QKeySequence.Save,
                               statusTip=_("Save cookie to favorites"),
                               triggered=self.saveCookie)

        self.exitAct = QAction(QIcon.fromTheme('window-close'), _("E&xit"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Exit the application"),
                               triggered=self.close)

        self.copyAct = QAction(QIcon.fromTheme('edit-copy'),
                               _("&Copy"),
                               self, shortcut=QKeySequence.Copy,
                               statusTip=_("Copy cookie to the clipboard"),
                               triggered=self.copyCookie)

        self.aboutAct = QAction(QIcon.fromTheme(EXECUTABLE_NAME),
                                _("&About") + " " + PROGRAM_NAME, self,
                                statusTip=_("Information about"
                                            " this application"),
                                triggered=self.about)

        self.aboutQtAct = QAction(QIcon.fromTheme('help-about'),
                                  _("About &Qt"), self,
                                  statusTip=_("Show information about"
                                              " the Qt library"),
                                  triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(_("&File"))
        self.fileMenu.addAction(self.copyAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu(_("&Navigation"))
        self.editMenu.addAction(self.prevAct)
        self.editMenu.addAction(self.nextAct)
        self.editMenu.addAction(self.firstAct)
        self.editMenu.addAction(self.lastAct)

        self.helpMenu = self.menuBar().addMenu(_("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar(_("File"))
        self.fileToolBar.addAction(self.firstAct)
        self.fileToolBar.addAction(self.prevAct)
        self.fileToolBar.addAction(self.nextAct)
        self.fileToolBar.addAction(self.lastAct)
        self.fileToolBar.addWidget(self.comboGoTo)

        self.editToolBar = self.addToolBar(_("Navigation"))
        self.editToolBar.addAction(self.saveAct)
        self.editToolBar.addAction(self.copyAct)

    def createStatusBar(self, message=None):
        if not message:
            message = str(self.nepigrams)
        self.statusBar().addWidget(self.statusOrigin, Qt.AlignLeft)
        self.statusBar().addWidget(self.statusOffensive, Qt.AlignRight)
        self.statusBar().addWidget(self.statusSaved, Qt.AlignRight)
        self.statusBar().addWidget(self.statusCopied, Qt.AlignRight)

    def readSettings(self):
        settings = QSettings(PROGRAM_NAME, _("Settings"))
        size = settings.value("size", QSize(400, 300))
        self.setWindowTitle(PROGRAM_NAME)
        self.setWindowIcon(QIcon.fromTheme(EXECUTABLE_NAME))
        self.resize(size)


class AboutDialog(QWidget):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        font = QFont()
        font.setPointSize(18)
        font.setBold(False)
        labelIcon = QLabel()
        pixmap = QIcon.fromTheme(EXECUTABLE_NAME).pixmap(QSize(64, 64))
        labelIcon.setPixmap(pixmap)
        labelText = QLabel(PROGRAM_NAME)
        labelText.setFont(font)

        tabWidget = QTabWidget()
        tabWidget.addTab(AboutTab(), _("About"))
        tabWidget.addTab(VersionTab(), _("Version"))
        tabWidget.addTab(AuthorsTab(), _("Authors"))
        tabWidget.addTab(ThanksTab(), _("Thanks"))
        tabWidget.addTab(TranslationTab(), _("Translation"))

        btn = QPushButton(_("Close"), self)
        btn.setIcon(QIcon.fromTheme("window-close"))
        btn.setToolTip(_("Close this window"))
        btn.clicked.connect(self.close)

        labelLayout = QHBoxLayout()
        labelLayout.addWidget(labelIcon)
        labelLayout.addWidget(labelText, Qt.AlignLeft)

        mainLayout = QGridLayout()
        mainLayout.addLayout(labelLayout, 0, 0)
        mainLayout.addWidget(tabWidget, 1, 0)
        mainLayout.addWidget(btn, 2, 0, Qt.AlignRight)
        self.setLayout(mainLayout)

        self.setWindowTitle(_("About") + " " + PROGRAM_NAME)
        self.setWindowIcon(QIcon.fromTheme(EXECUTABLE_NAME))


class AboutTab(QWidget):
    def __init__(self, parent=None):
        super(AboutTab, self).__init__(parent)

        blank = QLabel()
        description = QLabel(DESCRIPTION)
        copyright = QLabel("© 2017, " + AUTHOR)
        source = QLabel(_("Source:") + " "
                        + "<a href='" + SOURCE + "'>" + SOURCE + "</a>")
        license = QLabel(_("License:") + " "
                         + "<a href='https://www.gnu.org/licenses/"
                         "gpl-3.0.en.html'>"
                         + _("GNU General Public License, version 3") + "</a>")

        source.setTextInteractionFlags(Qt.TextBrowserInteraction)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(blank)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(description)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(copyright)
        mainLayout.addWidget(source)
        mainLayout.addWidget(license)
        mainLayout.addStretch()
        self.setLayout(mainLayout)


class VersionTab(QWidget):
    def __init__(self, parent=None):
        super(VersionTab, self).__init__(parent)

        version = QLabel("<b>" + _("Version") + " " + VERSION + "<b>")
        using = QLabel(_("Using:") + " ")
        pyver = ".".join((
            str(sys.version_info[0]),
            str(sys.version_info[1]),
            str(sys.version_info[2])))
        python = QLabel("<ul><li>Python " + pyver)
        pyqt = QLabel("<ul><li>PyQt " + QT_VERSION_STR)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(version)
        mainLayout.addWidget(using)
        mainLayout.addWidget(python)
        mainLayout.addWidget(pyqt)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class AuthorsTab(QWidget):
    def __init__(self, parent=None):
        super(AuthorsTab, self).__init__(parent)

        blank = QLabel()
        notice = QLabel(_("Mail me if you found bugs."))
        name1 = QLabel("<b>" + AUTHOR + "<b>")
        task1 = QLabel("<i>" + _("Principle author") + "</i>")
        mail1 = QLabel("<pre>" + MAIL + "</pre>")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(notice)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(name1)
        mainLayout.addWidget(task1)
        mainLayout.addWidget(mail1)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class ThanksTab(QWidget):
    def __init__(self, parent=None):
        super(ThanksTab, self).__init__(parent)

        blank = QLabel()
        notice = QLabel(_("Thank you for using my program."))

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(blank)
        mainLayout.addWidget(notice)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class TranslationTab(QWidget):
    def __init__(self, parent=None):
        super(TranslationTab, self).__init__(parent)

        blank = QLabel()
        notice = QLabel(_("Please, mail me if you want to") + " "
                        + _("improve the translation."))
        name1 = QLabel("<b>" + AUTHOR + "<b>")
        task1 = QLabel("<i>" + _("Spanish and english translation") + "</i>")
        mail1 = QLabel("<pre>" + MAIL + "</pre>")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(notice)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(name1)
        mainLayout.addWidget(task1)
        mainLayout.addWidget(mail1)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    aboutdialog = AboutDialog()
    mainWin.show()
    sys.exit(app.exec_())
