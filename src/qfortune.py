#!/usr/bin/python3

import os
import random
import gettext

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QRect, QSettings, QSize,
                          Qt, QTextStream, QT_VERSION_STR)
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtWidgets import (QWidget, QDialog, QAction, QApplication,
                             QFileDialog, QMainWindow, QLabel, QLineEdit,
                             QTabWidget, QGridLayout, QVBoxLayout,
                             QHBoxLayout, QMessageBox, QTextEdit, QPushButton)


PROGRAM_NAME = "qfortune"
DESCRIPTION = "A pyQt5 interface for reading fortune cookies"
VERSION = "0.2a"
AUTHOR = "Manuel Domínguez López"  # See AUTHORS file
MAIL = "mdomlop@gmail.com"
LICENSE = "GPLv3+"  # Read LICENSE file.

fortunes = "/usr/share/qfortune/fortunes"
fortunes_off = "/usr/share/qfortune/fortunes/off"
custom_fortunes = os.path.join(os.getenv("HOME"), ".config/qfortune/fortunes")
custom_fortunes_off = os.path.join(os.getenv("HOME"),
                                   ".config/qfortune/fortunes/off")
savefile = os.path.join(os.getenv("HOME"),
                        ".config/qfortune/favorites.cookies")


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        font = QFont()
        font.setPointSize(18)
        font.setBold(False)
        labelIcon = QLabel()
        pixmap = QIcon.fromTheme('qfortune').pixmap(QSize(64, 64))
        labelIcon.setPixmap(pixmap)
        labelText = QLabel("QFortune")
        labelText.setFont(font)

        tabWidget = QTabWidget()
        tabWidget.addTab(AboutTab(), "About")
        tabWidget.addTab(VersionTab(), "Version")
        tabWidget.addTab(AuthorsTab(), "Authors")
        tabWidget.addTab(ThanksTab(), "Thanks")
        tabWidget.addTab(TranslationTab(), "Translation")

        btn = QPushButton("Close", self)
        btn.setIcon(QIcon.fromTheme("window-close"))
        btn.setToolTip("Close this dialog")
        btn.clicked.connect(self.close)

        labelLayout = QHBoxLayout()
        labelLayout.addWidget(labelIcon)
        labelLayout.addWidget(labelText, Qt.AlignLeft)

        mainLayout = QGridLayout()
        mainLayout.addLayout(labelLayout, 0, 0)
        mainLayout.addWidget(tabWidget, 1, 0)
        mainLayout.addWidget(btn, 2, 0, Qt.AlignRight)
        self.setLayout(mainLayout)

        self.setWindowTitle("About QFortune")
        self.setWindowIcon(QIcon.fromTheme('qfortune'))


class AboutTab(QWidget):
    def __init__(self, parent=None):
        super(AboutTab, self).__init__(parent)

        blank = QLabel()
        description = QLabel("A pyQt5 interface for reading fortune cookies")
        copyright = QLabel("© 2017, Manuel Domínguez López")
        source = QLabel("<a href='https://github.com/mdomlop/qfortune'>"
                        "github</a>")
        license = QLabel("<a href='https://www.gnu.org/licenses/"
                         "gpl-3.0.en.html'>GPLv3+</a>")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(blank)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(description)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(copyright)
        mainLayout.addWidget(license)
        mainLayout.addStretch()
        self.setLayout(mainLayout)


class VersionTab(QWidget):
    def __init__(self, parent=None):
        super(VersionTab, self).__init__(parent)

        version = QLabel("<b>Version 0.1a<b>")
        using = QLabel("Usando:")
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
        notice = QLabel("Mail me if you found bugs.")
        name1 = QLabel("<b>Manuel Domínguez López<b>")
        task1 = QLabel("<i>Principle author</i>")
        mail1 = QLabel("<pre>mdomlop@gmail.com</pre>")

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
        notice = QLabel("Thank you for using my program.")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(blank)
        mainLayout.addWidget(notice)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class TranslationTab(QWidget):
    def __init__(self, parent=None):
        super(TranslationTab, self).__init__(parent)

        blank = QLabel()
        notice = QLabel("Please, mail me if you want to"
                        " improve the translation.")
        name1 = QLabel("<b>Manuel Domínguez López<b>")
        task1 = QLabel("<i>Spanish and english translation</i>")
        mail1 = QLabel("<pre>mdomlop@gmail.com</pre>")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(notice)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(name1)
        mainLayout.addWidget(task1)
        mainLayout.addWidget(mail1)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.epigrams = {}  # Database containing all fortune cookies
        self.elist = []  # Only a list for random access to epigrams dict.
        self.saved = []  # Saved cookies merged from savefile and fortune.
        self.statics = {}

        self.loadDir(fortunes)
        self.loadDir(custom_fortunes)
        self.loadDir(fortunes_off, True)
        self.loadDir(custom_fortunes_off, True)
        self.elist = list(self.epigrams.keys())
        self.nepigrams = len(self.elist)
        # random.shuffle(elist)
        self.cookie = 'unix'

        self.index = -1

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.setCentralWidget(self.textEdit)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.nextFile()
        self.createStatusBar('unix')

        self.readSettings()

    def decrypt(self, s):  # Unix offensive fortunes are rot13 encoded
        rot13 = str.maketrans(
            "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
            "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
        return(str.translate(s, rot13))

    def loadDir(self, directory, offensive=False):
        try:
            files = os.listdir(directory)
        except:
            files = []

        if files:  # Not empty
            files = list(map(lambda x: os.path.join(directory, x), files))
        for f in files:  # Loads to epigrams
            if os.path.isfile(f):
                if offensive:
                    self.loadFile(f, True)
                else:
                    self.loadFile(f)
            elif os.path.isdir(f):
                pass
            else:
                print(f, _("is not a regular file."))

    def loadFile(self, path, decode=False):
        n = 0  # Count entries
        try:  # Populate epigrams with a fortune database file
            with open(path, "r") as f:
                text = f.read()

            for line in text.split("\n%\n"):
                if line:
                    n += 1
                    if decode:
                        line = self.decrypt(line)
                    self.epigrams.update({line: (line, path, decode)})
            f.close()
            self.statics.update({path: (n, decode)})
        except PermissionError:
            print('PermissionError')
            self.close()

    def nextFile(self):
        self.index += 1
        if self.index >= self.nepigrams:
            self.index = 0  # Go to the beginning
        self.showCookie()

    def prevFile(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.nepigrams - 1  # Go to the end
        self.showCookie()

    def save(self):
        formatcookie = self.cookie + "\n%\n"
        if self.cookie not in self.saved:
            try:
                with open(savefile, 'a') as f:
                    f.write(formatcookie)
            except PermissionError:
                print('PermissionError at save')
                sys.exit()
            except:
                print('Exception at save')
                sys.exit()
            f.close()
            self.saved.append(self.cookie)
            self.saveAct.setEnabled(False)

    def about(self):
        aboutdialog.show()

    def setTitle(self):
        title = _("QFortune:") + " " + str(self.index + 1)
        self.setWindowTitle(title)

    def disableSave(self):
        # Save button:
        if self.cookie in self.saved:
            self.saveAct.setEnabled(False)
        else:
            self.saveAct.setEnabled(True)

    def showCookie(self):
        if len(self.elist) == 0:
            noCookiesDialog()
        self.cookie = self.epigrams[self.elist[self.index]][0]
        path = self.epigrams[self.elist[self.index]][1]
        off = self.epigrams[self.elist[self.index]][2]
        if off:
            off = _("(Offensive) ")
        else:
            off = ""
        self.textEdit.setText(self.cookie)
        self.disableSave()
        self.setTitle()
        txt = 'READY'
        self.createStatusBar(txt)

    def createActions(self):
        root = QFileInfo(__file__).absolutePath()

        self.nextAct = QAction(QIcon.fromTheme('go-next'),
                               _("&Next cookie"),
                               self, shortcut=QKeySequence.MoveToNextPage,
                               statusTip=_("Show next cookie"),
                               triggered=self.nextFile)

        self.prevAct = QAction(QIcon.fromTheme('go-previous'),
                               _("&Previous cookie"),
                               self, shortcut=QKeySequence.MoveToPreviousPage,
                               statusTip=_("Show previous cookie"),
                               triggered=self.prevFile)

        self.saveAct = QAction(QIcon.fromTheme('document-save'), _("&Save"),
                               self, shortcut=QKeySequence.Save,
                               statusTip=_("Save cookie to favorites"),
                               triggered=self.save)

        self.exitAct = QAction(QIcon.fromTheme('window-close'), _("E&xit"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Exit the application"),
                               triggered=self.close)

        self.copyAct = QAction(QIcon.fromTheme('edit-copy'), _("&Copy"),
                               self, shortcut=QKeySequence.Copy,
                               statusTip=_("Copy cookie to the clipboard"),
                               triggered=self.textEdit.copy)

        self.aboutAct = QAction(QIcon.fromTheme('help-about'),
                                _("&About QFortune"), self,
                                statusTip=_("Information about"
                                            " this application"),
                                triggered=self.about)

        self.aboutQtAct = QAction(QIcon.fromTheme('help-about'),
                                  _("About &Qt"), self,
                                  statusTip=_("Show information about"
                                              " the Qt library"),
                                  triggered=QApplication.instance().aboutQt)

        self.copyAct.setEnabled(False)
        self.textEdit.copyAvailable.connect(self.copyAct.setEnabled)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(_("&File"))
        self.fileMenu.addAction(self.prevAct)
        self.fileMenu.addAction(self.nextAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu(_("&Edit"))
        self.editMenu.addAction(self.copyAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(_("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar(_("File"))
        self.fileToolBar.addAction(self.prevAct)
        self.fileToolBar.addAction(self.nextAct)
        self.fileToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar(_("Edit"))
        self.editToolBar.addAction(self.copyAct)

    def createStatusBar(self, message):
        self.statusBar().showMessage(message)

    def readSettings(self):
        settings = QSettings("QFortune", _("Settings"))
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.setWindowIcon(QIcon.fromTheme("qfortune"))
        self.resize(size)
        self.move(pos)


if __name__ == '__main__':

    import sys

    gettext.translation("qfortune", localedir="/usr/share/locale",
                        fallback=True).install()

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    aboutdialog = AboutDialog()
    mainWin.show()
    sys.exit(app.exec_())
