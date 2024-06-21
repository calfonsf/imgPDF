from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QLabel

class Preview(QLabel):
    """Preview of the Selected Image"""
    def __init__(self, width: int):
        super().__init__()

        self.preview_path = ""
        self.preview = QPixmap(width, 400)
        self.painter = QPainter()
        self.painter.begin(self.preview)
        self.painter.setPen(Qt.white)
        font = QFont()
        font.setPointSize(15)
        self.painter.setFont(font)
        self.painter.drawText(QRect(0,0,width,400), Qt.AlignCenter, "Preview")
        self.painter.end()
        self.setPixmap(self.preview)
    
    def update(self, img_path, width):
        """Updates the Preview."""
        self.preview_path = img_path
        self.preview = QPixmap(img_path).scaledToWidth(int(width))
        self.setPixmap(self.preview)

    def rescale(self, width):
        """Uses width to rescale the preview."""
        if self.preview_path:
            self.preview = QPixmap(self.preview_path).scaledToWidth(int(width))
        else:
            self.preview = self.preview.scaledToWidth(int(width))
        self.setPixmap(self.preview)