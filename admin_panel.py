import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
    QComboBox, QSpinBox, QTabWidget, QFormLayout, QGroupBox,
    QDialog, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap, QColor, QIcon
from database import Database
import sys
import os

def get_base_path():
    """Get the base path whether running as script or exe"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys._MEIPASS
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()


def resolve_resource(path: str | None) -> str | None:
    """Resolve a resource path to an existing file similar to home.resolve_resource."""
    if not path:
        return None
    if os.path.isabs(path) and os.path.exists(path):
        return path
    if os.path.exists(path):
        return path
    candidate = os.path.join(BASE_DIR, path)
    if os.path.exists(candidate):
        return candidate
    candidate = os.path.join(BASE_DIR, 'src', os.path.basename(path))
    if os.path.exists(candidate):
        return candidate
    return None

class ContactDialog(QDialog):
    """Dialog for editing contact information"""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.contact_info = self.db.get_contact_info()
        
        self.setWindowTitle("Edit Contact Information")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setText(self.contact_info['phone'])
        self.phone_input.setPlaceholderText("Enter phone number")
        self.phone_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("Phone Number:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setText(self.contact_info['email'])
        self.email_input.setPlaceholderText("Enter email address")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setText(self.contact_info['address'])
        self.address_input.setPlaceholderText("Enter full address")
        self.address_input.setMaximumHeight(100)
        self.address_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("Address:", self.address_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        save_btn.clicked.connect(self.save_contact)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_contact(self):
        """Save contact information"""
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.toPlainText().strip()
        
        if not phone or not email or not address:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return
        
        self.db.update_contact_info(phone, email, address)
        QMessageBox.information(self, "Success", "Contact information updated successfully!")
        self.accept()


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    def __init__(self, db, product_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.product_id = product_id
        self.image_path = ""
        
        self.setWindowTitle("Add New Product" if product_id is None else "Edit Product")
        self.setMinimumSize(500, 550)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Product Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("Product Name:", self.name_input)
        
        # Price per hour
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setStyleSheet(self.name_input.styleSheet())
        form_layout.addRow("Price per hour (₹):", self.price_input)
        
        # Stock quantity
        self.stock_input = QSpinBox()
        self.stock_input.setRange(1, 9999)
        self.stock_input.setValue(1)
        self.stock_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("Stock Quantity:", self.stock_input)
        
        # (category removed)
        
        # Image upload section
        image_group = QGroupBox("Product Image")
        image_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #1f2937;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        image_layout = QVBoxLayout(image_group)
        
        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(150)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                background-color: #f9fafb;
                color: #6b7280;
            }
        """)
        
        image_btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton("📁 Upload Image")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_image)
        
        self.clear_image_btn = QPushButton("🗑️ Clear")
        self.clear_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                border: none;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.clear_image_btn.clicked.connect(self.clear_image)
        
        image_btn_layout.addWidget(self.upload_btn)
        image_btn_layout.addWidget(self.clear_image_btn)
        
        image_layout.addWidget(self.image_label)
        image_layout.addLayout(image_btn_layout)
        
        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter product description...")
        self.desc_input.setMaximumHeight(100)
        self.desc_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
            }
        """)
        form_layout.addRow("Description:", self.desc_input)
        
        layout.addLayout(form_layout)
        layout.addWidget(image_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Product")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_product)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Load product data if editing
        if product_id is not None:
            self.load_product_data()
    
    def upload_image(self):
        """Open file dialog to select image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Product Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale and display the image
                scaled_pixmap = pixmap.scaled(
                    300, 150, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setText("")
    
    def clear_image(self):
        """Clear the selected image"""
        self.image_path = ""
        self.image_label.clear()
        self.image_label.setText("No image selected")
    
    def load_product_data(self):
        """Load existing product data into form"""
        product = self.db.get_product(self.product_id)
        if product:
            # Map product columns to fields for current schema:
            # id, name, description, price_per_hour, image_path, stock_quantity, is_available, created_at?
            self.name_input.setText(str(product[1]) if product[1] else "")
            self.desc_input.setText(str(product[2]) if product[2] else "")
            # Price at index 3
            self.price_input.setText(str(product[3]) if product[3] else "0")
            try:
                stock_value = int(product[5]) if len(product) > 5 and product[5] else 1
                self.stock_input.setValue(stock_value)
            except (ValueError, TypeError):
                self.stock_input.setValue(1)
            self.image_path = str(product[4]) if len(product) > 4 and product[4] else ""
            
            # Load image if exists
            if self.image_path:
                resolved = resolve_resource(self.image_path)
                if resolved:
                    pixmap = QPixmap(resolved)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            300, 150,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                        self.image_label.setText("")
    
    def save_product(self):
        """Save product to database"""
        # Validate inputs
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Product name is required!")
            return
        
        if not price_text:
            QMessageBox.warning(self, "Validation Error", "Price is required!")
            return
        
        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid price!")
            return
        
        description = self.desc_input.toPlainText().strip()
        stock = self.stock_input.value()  # This is already an int
        
        try:
            # Save or update product
            if self.product_id is None:
                # Add new product
                product_id = self.db.add_product(
                    name=name,
                    price=price,
                    description=description,
                    image_path=self.image_path,
                    stock=stock
                )
                if product_id:
                    QMessageBox.information(self, "Success", f"Product '{name}' added successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add product! Product ID is None.")
            else:
                # Update existing product
                success = self.db.update_product(
                    product_id=self.product_id,
                    name=name,
                    price=price,
                    description=description,
                    image_path=self.image_path,
                    stock=stock
                )
                if success:
                    QMessageBox.information(self, "Success", f"Product '{name}' updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update product!")
        except Exception as e:
            print(f"Error saving product: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error saving product: {str(e)}")


class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        """Setup the admin panel UI"""
        self.setWindowTitle("Admin Panel")
        self.resize(1300, 800)
        
        # Set application-wide text color
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f4f6;
            }
            QLabel {
                color: #1f2937;
            }
            QTableWidget {
                color: #1f2937;
                background-color: white;
            }
            QTableWidget::item {
                color: #1f2937;
            }
            QHeaderView::section {
                color: white;
                background-color: #3b82f6;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #1f2937;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #1f2937;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title = QLabel("🛠️Admin Panel")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        self.stats_label = QLabel("0 Products")
        self.stats_label.setFont(QFont("Segoe UI", 12))
        self.stats_label.setStyleSheet("color: #e2e8f0;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(header)
        
        # Content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Left sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                border-radius: 12px;
                padding: 20px;
            }
            QLabel {
                color: #1f2937;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(15)
        
        # Add Product Button
        add_btn = QPushButton("➕ Add New Product")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        add_btn.clicked.connect(self.add_product)
        
        # Edit Contact Button
        contact_btn = QPushButton("📞 Edit Contact Info")
        contact_btn.setCursor(Qt.PointingHandCursor)
        contact_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        contact_btn.clicked.connect(self.edit_contact)
        
        # Refresh Button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                border: none;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        refresh_btn.clicked.connect(self.load_products)
        
        sidebar_layout.addWidget(add_btn)
        sidebar_layout.addWidget(contact_btn)
        sidebar_layout.addWidget(refresh_btn)
        sidebar_layout.addStretch()
        
        # Contact info preview
        contact_preview = QGroupBox("Current Contact Info")
        contact_preview.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #1f2937;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #4b5563;
                font-size: 11px;
            }
        """)
        contact_layout = QVBoxLayout(contact_preview)
        
        contact_info = self.db.get_contact_info()
        self.phone_preview = QLabel(f"📞 {contact_info['phone']}")
        self.email_preview = QLabel(f"✉️ {contact_info['email']}")
        self.address_preview = QLabel(f"📍 {contact_info['address'][:30]}...")
        self.address_preview.setWordWrap(True)
        
        contact_layout.addWidget(self.phone_preview)
        contact_layout.addWidget(self.email_preview)
        contact_layout.addWidget(self.address_preview)
        
        sidebar_layout.addWidget(contact_preview)
        sidebar_layout.addStretch()
        
        # Right content - Products table
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)
        right_layout.setSpacing(15)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search products...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        self.search_input.textChanged.connect(self.search_products)
        
        search_layout.addWidget(self.search_input)
        right_layout.addLayout(search_layout)
        
        # Products table - 7 data columns + 3 action columns = 10 columns
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(10)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Name", "Description", "Price/Hour", "Stock", 
            "Status", "Image", "Edit", "Delete", "Toggle Status"
        ])
        
        # Set column resize modes
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Hide description column by default (too long)
        self.products_table.setColumnHidden(2, True)
        # Set fixed widths for action columns
        self.products_table.setColumnWidth(7, 80)   # Edit column
        self.products_table.setColumnWidth(8, 80)   # Delete column
        self.products_table.setColumnWidth(9, 100)  # Toggle Status column
        
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
                gridline-color: #e5e7eb;
                color: #1f2937;
            }
            QTableWidget::item {
                padding: 8px;
                color: #1f2937;
            }
            QHeaderView::section {
                background-color: #3b82f6;
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
            }
        """)
        
        right_layout.addWidget(self.products_table)
        
        content_layout.addWidget(sidebar)
        content_layout.addWidget(right_content)
        
        main_layout.addWidget(content_widget)
    
    def load_products(self):
        """Load all products into the table"""
        products = self.db.get_all_products()
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            if len(product) < 7:
                print(f"Warning: Product has fewer than 7 columns: {product}")
                continue
            
            # ID (index 0)
            id_item = QTableWidgetItem(str(product[0]))
            id_item.setForeground(QColor("#1f2937"))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 0, id_item)
            
            # Name (index 1)
            name_item = QTableWidgetItem(str(product[1]) if product[1] else "")
            name_item.setForeground(QColor("#1f2937"))
            self.products_table.setItem(row, 1, name_item)
            
            # Description (index 2) - hidden
            desc_item = QTableWidgetItem(str(product[2]) if product[2] else "")
            desc_item.setForeground(QColor("#1f2937"))
            self.products_table.setItem(row, 2, desc_item)
            
            # Price (index 3)
            try:
                price_value = float(product[3]) if product[3] else 0
                price_item = QTableWidgetItem(f"₹{price_value:,.2f}")
            except (ValueError, TypeError):
                price_item = QTableWidgetItem(f"₹{product[3]}")
            price_item.setForeground(QColor("#1f2937"))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 3, price_item)
            
            # Stock (index 5)
            try:
                stock_value = int(product[5]) if product[5] else 0
                stock_item = QTableWidgetItem(str(stock_value))
            except (ValueError, TypeError):
                stock_item = QTableWidgetItem(str(product[5]) if product[5] else "0")
            stock_item.setForeground(QColor("#1f2937"))
            stock_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 4, stock_item)
            
            # Status (index 6)
            try:
                is_available = bool(int(product[6])) if product[6] is not None else False
            except (ValueError, TypeError):
                is_available = False
            
            status = "✅ Available" if is_available else "❌ Unavailable"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#059669") if is_available else QColor("#dc2626"))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 5, status_item)
            
            # Image preview (index 4)
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            if len(product) > 4 and product[4]:
                resolved_path = resolve_resource(str(product[4]))
                if resolved_path:
                    pixmap = QPixmap(resolved_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                        image_label.setPixmap(scaled_pixmap)
                    else:
                        image_label.setText("📷")
                        image_label.setStyleSheet("color: #4b5563; font-size: 20px;")
                else:
                    image_label.setText("📷")
                    image_label.setStyleSheet("color: #4b5563; font-size: 20px;")
            else:
                image_label.setText("📷")
                image_label.setStyleSheet("color: #4b5563; font-size: 20px;")
            self.products_table.setCellWidget(row, 6, image_label)
            
            # Edit button column
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setToolTip("Edit Product")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fbbf24;
                    color: #78350f;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 12px;
                    border: none;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #f59e0b;
                }
            """)
            edit_btn.clicked.connect(lambda checked, p=product[0]: self.edit_product(p))
            self.products_table.setCellWidget(row, 7, edit_btn)
            
            # Delete button column
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setToolTip("Delete Product")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 12px;
                    border: none;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda checked, p=product[0]: self.delete_product(p))
            self.products_table.setCellWidget(row, 8, delete_btn)
            
            # Toggle Status button column
            status_btn = QPushButton("✅ Available" if is_available else "❌ Disable")
            status_btn.setCursor(Qt.PointingHandCursor)
            status_btn.setToolTip("Toggle Availability")
            if is_available:
                status_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #10b981;
                        color: white;
                        padding: 6px;
                        border-radius: 4px;
                        font-size: 12px;
                        border: none;
                        min-width: 90px;
                    }
                    QPushButton:hover {
                        background-color: #059669;
                    }
                """)
            else:
                status_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #9ca3af;
                        color: white;
                        padding: 6px;
                        border-radius: 4px;
                        font-size: 12px;
                        border: none;
                        min-width: 90px;
                    }
                    QPushButton:hover {
                        background-color: #6b7280;
                    }
                """)
            status_btn.clicked.connect(lambda checked, p=product[0], s=not is_available: self.toggle_availability(p, s))
            self.products_table.setCellWidget(row, 9, status_btn)
        
        # Update stats
        self.stats_label.setText(f"{len(products)} Products")
        
        # Update contact preview
        contact_info = self.db.get_contact_info()
        self.phone_preview.setText(f"📞 {contact_info['phone']}")
        self.email_preview.setText(f"✉️ {contact_info['email']}")
        self.address_preview.setText(f"📍 {contact_info['address'][:30]}...")
    
    def search_products(self):
        """Search products based on search text"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_products()
            return
        
        products = self.db.search_products(search_text)
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            if len(product) < 7:
                continue
                
            # ID
            id_item = QTableWidgetItem(str(product[0]))
            id_item.setForeground(QColor("#1f2937"))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(str(product[1]) if product[1] else "")
            name_item.setForeground(QColor("#1f2937"))
            self.products_table.setItem(row, 1, name_item)
            
            # Description (hidden)
            desc_item = QTableWidgetItem(str(product[2]) if product[2] else "")
            desc_item.setForeground(QColor("#1f2937"))
            self.products_table.setItem(row, 2, desc_item)
            
            # Price (index 3)
            try:
                price_value = float(product[3]) if product[3] else 0
                price_item = QTableWidgetItem(f"₹{price_value:,.2f}")
            except (ValueError, TypeError):
                price_item = QTableWidgetItem(f"₹{product[3]}")
            price_item.setForeground(QColor("#1f2937"))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 3, price_item)
            
            # Stock (index 5)
            try:
                stock_value = int(product[5]) if product[5] else 0
                stock_item = QTableWidgetItem(str(stock_value))
            except (ValueError, TypeError):
                stock_item = QTableWidgetItem(str(product[5]) if product[5] else "0")
            stock_item.setForeground(QColor("#1f2937"))
            stock_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 4, stock_item)
            
            # Status (index 6)
            try:
                is_available = bool(int(product[6])) if product[6] is not None else False
            except (ValueError, TypeError):
                is_available = False
            
            status = "✅ Available" if is_available else "❌ Unavailable"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#059669") if is_available else QColor("#dc2626"))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 5, status_item)
            
            # Image preview (index 4)
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            if len(product) > 4 and product[4]:
                resolved_path = resolve_resource(str(product[4]))
                if resolved_path:
                    pixmap = QPixmap(resolved_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        image_label.setPixmap(scaled_pixmap)
                    else:
                        image_label.setText("📷")
                        image_label.setStyleSheet("color: #4b5563; font-size: 20px;")
                else:
                    image_label.setText("📷")
                    image_label.setStyleSheet("color: #4b5563; font-size: 20px;")
            else:
                image_label.setText("📷")
                image_label.setStyleSheet("color: #4b5563; font-size: 20px;")
            self.products_table.setCellWidget(row, 6, image_label)
            
            # Disabled buttons for search results
            view_btn = QPushButton("🔍")
            view_btn.setEnabled(False)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9ca3af;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 12px;
                    border: none;
                    min-width: 60px;
                }
            """)
            self.products_table.setCellWidget(row, 7, view_btn)
            
            view_btn2 = QPushButton("🔍")
            view_btn2.setEnabled(False)
            view_btn2.setStyleSheet("""
                QPushButton {
                    background-color: #9ca3af;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 12px;
                    border: none;
                    min-width: 60px;
                }
            """)
            self.products_table.setCellWidget(row, 8, view_btn2)
            
            view_btn3 = QPushButton("🔍")
            view_btn3.setEnabled(False)
            view_btn3.setStyleSheet("""
                QPushButton {
                    background-color: #9ca3af;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 12px;
                    border: none;
                    min-width: 90px;
                }
            """)
            self.products_table.setCellWidget(row, 9, view_btn3)
    
    def add_product(self):
        """Open dialog to add new product"""
        dialog = ProductDialog(self.db)
        if dialog.exec():
            self.load_products()
    
    def edit_product(self, product_id):
        """Open dialog to edit product"""
        print(f"Editing product with ID: {product_id}")
        dialog = ProductDialog(self.db, product_id)
        if dialog.exec():
            self.load_products()
    
    def edit_contact(self):
        """Open dialog to edit contact information"""
        dialog = ContactDialog(self.db)
        if dialog.exec():
            self.load_products()  # Refresh to update preview
    
    def delete_product(self, product_id):
        """Delete a product with confirmation"""
        product = self.db.get_product(product_id)
        if not product:
            QMessageBox.warning(self, "Error", "Product not found!")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{product[1]}'?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_product(product_id):
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                self.load_products()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete product!")
    
    def toggle_availability(self, product_id, new_status):
        """Toggle product availability"""
        product = self.db.get_product(product_id)
        if product:
            if self.db.update_product(product_id, available=new_status):
                self.load_products()
            else:
                QMessageBox.warning(self, "Error", "Failed to update product status!")


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f3f4f6;
        }
        QLabel {
            color: #1f2937;
        }
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            color: #1f2937;
        }
        QDialog {
            background-color: white;
        }
    """)
    
    window = AdminPanel()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()