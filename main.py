import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt, QFileInfo, QAbstractTableModel, QModelIndex, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QFileDialog, QToolBar, QMessageBox, QStyle, QLabel, QAction, QStatusBar, QAbstractItemView, QTableView, QMenu, QHeaderView, QSizePolicy
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QFont
from imgPDF import GetImagesInFolder, Convert, ParseBytes
from math import ceil

class FilesModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data[index.row()][index.column()]
                return str(value)

    def getPath(self, index):
        if index.isValid():
            value = self._data[index.row()][2]
            return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True
        return False

    def addData(self, data):
        self._data += data
    
    def fillTable(self, data):
        self._data = data

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled 

    def removeData(self, index):
        row = (index.row())
        self._data.pop(row)

    def clearData(self):
        self._data = []

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        headers= ["Filename", "Size", "Path"]

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return '{}'.format(headers[section])
        return super().headerData(section, orientation, role)

    def MenuEvent(self, pos):
        self.mymenu = QMenu(self)
        removeAction = QAction('Remove')
        removeAction.triggered.connect(lambda: print("hello"))
        self.mymenu.addAction(removeAction)
        self.mymenu.popup(QCursor.pos())
        self.mymenu.exec_()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(800,600)
        frame =QtWidgets.QFrame()
        self.setCentralWidget(frame)

        layout = QtWidgets.QGridLayout()
        frame.setLayout(layout)
        # layout.setContentsMargins(10,10,10,10)

        # Toolbar
        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(40, 40))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        button_action = QAction(icon,"Add Files", self)
        button_action.setStatusTip("Add Image To Your Convertion list")
        button_action.triggered.connect(self.openFileNameDialog)
        toolbar.addAction(button_action)
        
        toolbar.addSeparator()
        
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        button_action = QAction(icon,"Add Folder", self)
        button_action.setStatusTip("Add Every Image In Folders to Your Convertion list")
        button_action.triggered.connect(self.openFolderNameDialog)
        toolbar.addAction(button_action)
        toolbar.setMovable(False)


        #Buttons
        self.ConvertButton = QtWidgets.QPushButton('Create PDF',self)
        self.ConvertButton.clicked.connect(self.StartConvertion)
        self.ClearButton = QtWidgets.QPushButton('Clear',self)
        self.ClearButton.clicked.connect(self.Clear)
        layout.addWidget(self.ConvertButton, 0, 0)
        layout.addWidget(self.ClearButton, 0, 1)

        #Table
        self.files = []
        model = FilesModel(self.files)
        self.tv = QTableView()
        self.tv.setShowGrid(False)
        self.tv.setModel(model)
        self.tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tv.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tv.setFocusPolicy(Qt.NoFocus)
        self.tv.clicked.connect(self.fileClicked)
        # self.tv.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.tv.customContextMenuRequested.connect(self.MenuEvent)
        self.tv.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tv.customContextMenuRequested.connect(self.MenuEvent)
        layout.addWidget(self.tv,1,0,1,2)
        
        # Preview Image
        self.preview = QPixmap(int(self.width()/3), 400)
        self.painter = QPainter()
        self.painter.begin(self.preview)
        self.painter.setPen(Qt.white)
        font = QFont()
        font.setPointSize(15)
        self.painter.setFont(font)
        self.painter.drawText(QRect(0,0,int(self.width()/3),400), Qt.AlignCenter, "Preview")
        self.painter.end()
        self.lbl = QLabel(self)                                                                                                                 
        self.lbl.setPixmap(self.preview)
        # self.lbl.setMargin(20)
        layout.addWidget(self.lbl, 1, 2, Qt.AlignHCenter | Qt.AlignTop)

        statusBar = QStatusBar()
        self.setStatusBar(statusBar)

    def fileClicked(self, index: QModelIndex):
        img_path = self.tv.model().getPath(index)
        self.setPreview(img_path)

    def setPreview(self, img_path):
        self.preview = QPixmap(img_path).scaledToWidth(int(self.width()/4))
        self.lbl.setPixmap(self.preview)

    #TODO FIX
    def resizeEvent(self, event):
        self.tv.setColumnWidth(0, ceil(1/3 * self.tv.width()))
        self.tv.setColumnWidth(1, ceil(1/3 * self.tv.width()))
        self.tv.setColumnWidth(2, ceil(1/3 * self.tv.width()))

        self.preview = self.preview.scaledToWidth(int(self.width()/4))

        self.lbl.setPixmap(self.preview)
        # self.tv.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def StartConvertion(self):
        images = [self.myList.item(x).text() for x in range(self.myList.count())]
        save_name, _ = QFileDialog.getSaveFileName(self,"Choose File", "","pdf (*.pdf)"); 
        if save_name:
            if save_name.split('.')[-1].lower() != 'pdf':
                print()
                save_name = save_name.rstrip() + '.pdf'
            Convert(images, save_name)
            self.ShowOkDialog()

    def Clear(self):
        self.tv.model().clearData()
        self.tv.model().modelReset.emit()

    def MenuEvent(self, pos):
        
        index = self.tv.indexAt(pos)
        data = self.tv.model().data(index)
        
        if data: 
            self.mymenu = QMenu(self)
            removeAction = QAction('Remove')
            removeAction.triggered.connect(lambda: self.removeData(index))
            self.mymenu.addAction(removeAction)
            self.mymenu.popup(QCursor.pos())
            self.mymenu.exec_()
        
    def removeData(self, index):
        # self.tv.model().fillTable([["0"],["0"]])
        self.tv.model().removeData(index)
        self.tv.model().modelReset.emit()

    def AddListToTable(self, file_list):

        files = []

        for file in file_list:
            info = QFileInfo(file)
            files.append([info.fileName(), ParseBytes(info.size()) ,info.filePath()])

        self.tv.model().addData(files)
        self.tv.model().modelReset.emit()

    def ShowOkDialog(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Completed")
        dlg.setText("PDF Generated Succesfully!")
        button = dlg.exec_()
        if button == QMessageBox.Ok:
            print("OK!")

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileNames(self,"Choose File", "","jpg (*.jpg)", options=options)
        self.AddListToTable(fileName)
    
    def openFolderNameDialog(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setWindowTitle('Choose Directories')
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        for view in dialog.findChildren(
            (QtWidgets.QListView, QtWidgets.QTreeView)):
            if isinstance(view.model(), QtWidgets.QFileSystemModel):
                view.setSelectionMode(
                    QtWidgets.QAbstractItemView.ExtendedSelection)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            path = dialog.selectedFiles()
            images = GetImagesInFolder(path)
            self.AddListToTable(images)
        dialog.deleteLater()

def main():

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()