from PyQt5.QtCore import Qt, QAbstractTableModel, QFileInfo, QModelIndex
from PyQt5.QtWidgets import QAction, QAbstractItemView, QTableView, QMenu, QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import QDrag
from .imgPDF import ParseBytes, GetImagesInFolder, isImage

class myTable(QTableView):


    def __init__(self, parent=None):

        super(myTable, self).__init__(parent)
        self.setAcceptDrops(True)

        model = FilesModel([])

        self.setShowGrid(False)
        self.setModel(model)
        self.setSelectionBehavior(self.SelectRows)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menuEvent)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.setDragDropOverwriteMode(False)
        # self.verticalHeader().setVisible(False)
        # self.setFocusPolicy(Qt.NoFocus)

    def dropEvent(self, event):
     
        if event.source() is self:
            selection = self.selectedIndexes()
            
            # This crops the d&drop to single files instead of bulk
            from_index = selection[0].row() if selection else -1

            to_index = self.indexAt(event.pos()).row()

            if (0 <= from_index < self.model().rowCount() and
                0 <= to_index < self.model().rowCount() and
                from_index != to_index):
                self.model().relocateRow(from_index, to_index)
                event.accept()
                self.setCurrentIndex(self.indexAt(event.pos()))
            
            super().dropEvent(event)
             
        if event.mimeData().hasUrls:
            event.accept()
            invalid_files = False
            for url in event.mimeData().urls():
                # Fix Later if trouble
                info = QFileInfo(url.toLocalFile())

                if info.isDir():
                    images = GetImagesInFolder([info.filePath()])
                    for image in images:
                        file = QFileInfo(image)
                        self.model().addData([[file.fileName(), ParseBytes(file.size()) ,file.filePath()]])
                        self.model().modelReset.emit()

                elif isImage(info.filePath()):
                    self.model().addData([[info.fileName(), ParseBytes(info.size()) ,info.filePath()]])
                    self.model().modelReset.emit()
                else:
                    invalid_files = True

            if invalid_files == True:
                self.showInvalidFileDialog()
                print("invalid")
        else:
            event.ignore()

    def showInvalidFileDialog(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Invalid File")
        dlg.setText("Invalid files where skipped, only images files and directories are supported.")
        button = dlg.exec_()
        if button == QMessageBox.Ok:
            print("OK!")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            # event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def menuEvent(self, _):
        
        rows = self.selectionModel().selectedRows()

        if len(rows) == 1: 

            mymenu = QMenu(self)
            removeAction = QAction('Remove')
            removeAction.triggered.connect(lambda: self.removeData(rows))
            
            # Add Actions for Move Up and Move Down
            moveUpAction = QAction('Move Up')
            moveDownAction = QAction('Move Down')

            moveUpAction.triggered.connect(lambda: self.moveItemUp(rows[0]))
            moveDownAction.triggered.connect(lambda: self.moveItemDown(rows[0]))

            if rows[0].row() == 0:
                moveUpAction.setEnabled(False)

            if rows[0].row() == len(self.getData()) - 1:
                moveDownAction.setEnabled(False)

            # Adding Actions To menu
            mymenu.addAction(moveUpAction)
            mymenu.addAction(moveDownAction)
            mymenu.addAction(removeAction)

            mymenu.popup(QCursor.pos())
            mymenu.exec_()
        
        if len(rows) > 1:
            self.mymenu = QMenu(self)
            removeAction = QAction('Remove')
            removeAction.triggered.connect(lambda: self.removeData(rows))
            self.mymenu.addAction(removeAction)
            self.mymenu.popup(QCursor.pos())
            self.mymenu.exec_()

    def keyPressEvent(self, e):
        
        if self.hasFocus():
            if e.key() == Qt.Key.Key_Delete:
                rows = self.selectionModel().selectedRows()
                self.removeData(rows)

    def moveItemUp(self, index):
        self.model().moveItemUp(index.row())

    def moveItemDown(self, index):
        self.model().moveItemDown(index.row())

    def removeData(self, indexList):
        self.model().removeData(indexList)
        self.model().modelReset.emit()

    def clearData(self):
        self.model().clearData()

    def getData(self):
        return self.model().getData()
    
    def getDataSize(self):
        return [f[1] for f in self.model().getData()]
    
    def getDataPath(self):
        return [f[2] for f in self.model().getData()]

class FilesModel(QAbstractTableModel):

    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data[index.row()][index.column()]
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True
        return False
    
    def getData(self):
        return self._data

    def addData(self, data):
        self._data += data

    def removeData(self, indexList):

        rows = []
        new_data = []

        for i in indexList:
            rows.append(i.row())

        for i, j in enumerate(self._data):
            if i not in rows:
                new_data.append(j)

        self._data = new_data

    def clearData(self):
        self._data = []
        self.modelReset.emit()

    def getPath(self, index):
        if index.isValid():
            value = self._data[index.row()][2]
            return str(value)
    
    def fillTable(self, data):
        self._data = data

    def moveItemUp(self, index):
        tmp = self._data[index-1]
        self._data[index-1] = self._data[index]
        self._data[index] = tmp
        self.modelReset.emit()
        
    def moveItemDown(self, index):
        tmp = self._data[index+1]
        self._data[index+1] = self._data[index]
        self._data[index] = tmp
        self.modelReset.emit()

    def supportedDropActions(self) -> bool:
        return Qt.MoveAction | Qt.CopyAction

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsDropEnabled
        if index.row() < len(self._data):
            return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsEditable
    
    def relocateRow(self, row_source, row_target) -> None:
        row_a, row_b = max(row_source, row_target), min(row_source, row_target)
        self.beginMoveRows(QModelIndex(), row_a, row_a, QModelIndex(), row_b)
        self._data.insert(row_target, self._data.pop(row_source))
        self.endMoveRows()

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        headers= ["Filename", "Size", "Path"]

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return '{}'.format(headers[section])

        return super().headerData(section, orientation, role)