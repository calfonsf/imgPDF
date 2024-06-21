import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSize, Qt, QFileInfo, QModelIndex
from PyQt5.QtWidgets import QApplication, QFileDialog, QToolBar, QStyle, QAction, QStatusBar, QMessageBox
from math import ceil

from modules.Preview import Preview
from modules.Table import myTable
from modules.imgPDF import GetImagesInFolder, Convert, ParseBytes

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(800,600)
        frame =QtWidgets.QFrame()
        self.setCentralWidget(frame)

        # Layout
        layout = QtWidgets.QGridLayout()
        frame.setLayout(layout)

        # Title
        self.setWindowTitle("imgPDF")

        # Table
        self.tv = myTable()
        self.tv.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.tv.clicked.connect(self.fileClicked)
        layout.addWidget(self.tv,1,0,1,2)

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
        button_action.setStatusTip("Add Every Image In Folders to your Convertion list")
        button_action.triggered.connect(self.openFolderNameDialog)
        toolbar.addAction(button_action)
        toolbar.setMovable(False)

        # Preview
        self.preview = Preview(width=int(self.width()/2))
        layout.addWidget(self.preview, 1, 2, Qt.AlignHCenter | Qt.AlignTop)

        # Status Bar
        self.statusBar = QStatusBar()
        # self.statusMsg = QLabel("Add files to your convertion list to begin")
        # self.statusMsg.setContentsMargins(QMargins(4, 0, 0, 0))
        # self.statusBar.addWidget(self.statusMsg)
        self.setStatusBar(self.statusBar)

        # Buttons
        self.convertButton = QtWidgets.QPushButton('Create PDF',self)
        self.convertButton.clicked.connect(self.startConvertion)
        self.clearButton = QtWidgets.QPushButton('Clear',self)
        self.clearButton.clicked.connect(self.tv.clearData)
        layout.addWidget(self.convertButton, 0, 0)
        layout.addWidget(self.clearButton, 0, 1)

        self.setFocus()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # self.size_lbl = QLabel("size")
        # self.size_lbl.setContentsMargins(QMargins(20, 0, 0, 0))
        # layout.addWidget(self.size_lbl, 2, 2)

    def fileClicked(self, index: QModelIndex):
        img_path = self.tv.model().getPath(index)
        self.preview.update(img_path, self.width()/4)

    def resizeEvent(self, event):
        self.tv.setColumnWidth(0, ceil(1/3 * self.tv.width()))
        self.tv.setColumnWidth(1, ceil(1/3 * self.tv.width()))
        self.tv.setColumnWidth(2, ceil(1/3 * self.tv.width()))
        self.preview.rescale(int(self.width()/4))
        # self.tv.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    
    def startConvertion(self):
        images = self.tv.getDataPath()
        save_name, _ = QFileDialog.getSaveFileName(self,"Choose File", "","pdf (*.pdf)"); 
        if save_name:
            if save_name.split('.')[-1].lower() != 'pdf':
                print()
                save_name = save_name.rstrip() + '.pdf'
            Convert(images, save_name)
            self.ShowOkDialog()

    def AddListToTable(self, file_list):

        files = []

        for file in file_list:
            info = QFileInfo(file)
            files.append([info.fileName(), ParseBytes(info.size()) ,info.filePath()])

        self.tv.model().addData(files)
        self.tv.model().modelReset.emit()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        
        # Add Extensions List Based on Supported Extensions Variable
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
    
    def ShowOkDialog(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Completed")
        dlg.setText("PDF Generated Succesfully!")
        button = dlg.exec_()
        if button == QMessageBox.Ok:
            print("OK!")

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()