from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

app = QApplication([])

window = QWidget()
window.setWindowTitle("Image Uploader")
window.resize(400, 350)

layout = QVBoxLayout()

# button
upload_btn = QPushButton("Upload Image")

# image preview label
image_label = QLabel("No image selected")
image_label.setAlignment(Qt.AlignCenter)

layout.addWidget(upload_btn)
layout.addWidget(image_label)

window.setLayout(layout)


# 📂 open file dialog and show image
def upload_image():
    file_path, _ = QFileDialog.getOpenFileName(
        window,
        "Select Image",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp)"
    )

    if file_path:
        pixmap = QPixmap(file_path)
        image_label.setPixmap(
            pixmap.scaled(
                300, 250,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )


upload_btn.clicked.connect(upload_image)


# ✨ simple modern styling
window.setStyleSheet("""
QWidget {
    background-color: #f5f6fa;
    font-size: 14px;
}

QPushButton {
    background-color: #4078ff;
    color: white;
    padding: 10px;
    border-radius: 10px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2f6be6;
}

QLabel {
    border: 2px dashed #bbb;
    background: white;
    border-radius: 10px;
}
""")

window.show()
app.exec()

