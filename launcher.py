import sys
import os
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                               QVBoxLayout, QWidget, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Baskaran Events - Management System")
        self.setFixedSize(500, 400)
        
        # Set the window icon
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7fafc;
            }
            QLabel {
                color: #2d3748;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo
        logo_label = QLabel()
        logo_path = self.get_resource_path("src/logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("🎯")
            logo_label.setStyleSheet("font-size: 80px;")
            logo_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(logo_label)
        
        # Title
        title = QLabel("Baskaran Events")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2d3748; margin: 10px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Rental Management System")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #718096; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Admin Panel Button
        admin_btn = QPushButton("👤 Admin Panel")
        admin_btn.setCursor(Qt.PointingHandCursor)
        admin_btn.setMinimumHeight(50)
        admin_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        admin_btn.clicked.connect(self.launch_admin)
        layout.addWidget(admin_btn)
        
        # Customer Store Button
        customer_btn = QPushButton("🛒 Customer Store")
        customer_btn.setCursor(Qt.PointingHandCursor)
        customer_btn.setMinimumHeight(50)
        customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        customer_btn.clicked.connect(self.launch_customer)
        layout.addWidget(customer_btn)
        
        # Exit Button
        exit_btn = QPushButton("❌ Exit")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.setMinimumHeight(40)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                padding: 10px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def get_exe_path(self, exe_name):
        """Get the path to the executable"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Look in dist folder first
        dist_path = os.path.join(base_path, "dist", exe_name)
        if os.path.exists(dist_path):
            return dist_path
        
        # Then look in current directory
        current_path = os.path.join(base_path, exe_name)
        if os.path.exists(current_path):
            return current_path
        
        return None
    
    def launch_admin(self):
        """Launch admin panel"""
        exe_path = self.get_exe_path("BaskaranEventsAdmin.exe")
        
        if exe_path and os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path])
                QMessageBox.information(self, "Launched", "Admin Panel is starting...")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to launch Admin Panel: {str(e)}")
        else:
            # If exe not found, try running the Python script (for development)
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_panel.py")
            if os.path.exists(script_path):
                try:
                    subprocess.Popen(["python", script_path])
                    QMessageBox.information(self, "Launched", "Admin Panel is starting in development mode...")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to launch Admin Panel: {str(e)}")
            else:
                QMessageBox.warning(self, "Not Found", 
                                   "Admin Panel executable not found!\n"
                                   "Please make sure BaskaranEventsAdmin.exe is in the same folder.")
    
    def launch_customer(self):
        """Launch customer store"""
        exe_path = self.get_exe_path("BaskaranEventsStore.exe")
        
        if exe_path and os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path])
                QMessageBox.information(self, "Launched", "Customer Store is starting...")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to launch Customer Store: {str(e)}")
        else:
            # If exe not found, try running the Python script (for development)
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "home.py")
            if os.path.exists(script_path):
                try:
                    subprocess.Popen(["python", script_path])
                    QMessageBox.information(self, "Launched", "Customer Store is starting in development mode...")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to launch Customer Store: {str(e)}")
            else:
                QMessageBox.warning(self, "Not Found", 
                                   "Customer Store executable not found!\n"
                                   "Please make sure BaskaranEventsStore.exe is in the same folder.")

def main():
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()