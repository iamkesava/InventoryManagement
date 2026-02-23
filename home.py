import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QListWidget, QListWidgetItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect,
    QDialog, QSpinBox, QMessageBox, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QGroupBox, QGridLayout, QLineEdit,
    QSizePolicy, QFileDialog, QInputDialog, QFormLayout,
    QTextEdit, QComboBox, QDoubleSpinBox, QDateEdit,
    QTabWidget
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont, QColor, QPixmap

from database import Database  # Import the database module
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import reportlab.lib.fonts

# Import admin panel
from admin_panel import AdminPanel

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
    """Resolve a resource path to an existing file.
    Tries the given path, then paths relative to BASE_DIR and BASE_DIR/src.
    Returns the first existing path or None.
    """
    if not path:
        return None
    # Absolute path exists
    if os.path.isabs(path) and os.path.exists(path):
        return path

    # Try as given (relative to cwd)
    if os.path.exists(path):
        return path

    # Try inside packaged base dir (sys._MEIPASS when frozen)
    candidate = os.path.join(BASE_DIR, path)
    if os.path.exists(candidate):
        return candidate

    # Try inside BASE_DIR/src with basename
    candidate = os.path.join(BASE_DIR, 'src', os.path.basename(path))
    if os.path.exists(candidate):
        return candidate

    return None

# ======================================================
# Modern Button
# ======================================================
class ModernButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self.setStyleSheet("""
            QPushButton {
                background:#667eea;
                color:white;
                padding:10px 22px;
                border-radius:10px;
                font-weight:bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background:#5a67d8;
            }
        """)


# ======================================================
# Modern Search Bar
# ======================================================
class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("🔍 Search products by name or description...")
        self.setClearButtonEnabled(True)
        
        # Base styling without fixed padding values that will be overridden
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                background-color: white;
                color: #2d3748;
                selection-background-color: #667eea;
                selection-color: white;
                padding-left: 40px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
            QLineEdit:hover {
                border-color: #cbd5e0;
            }
        """)
    
    def resizeEvent(self, event):
        """Update font size based on widget height"""
        font_size = max(10, int(self.height() * 0.35))
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)
        super().resizeEvent(event)


# ======================================================
# Product Card
# ======================================================
class ProductWidget(QWidget):
    def __init__(self, product_data, cart_callback=None):
        super().__init__()
        self.setStyleSheet("""
            background-color: white;
            color: #333333;
        """)

        self.product_id = product_data[0]
        self.name = product_data[1]
        self.description = product_data[2] if product_data[2] else ""
        
        # Convert price to float (price at index 3)
        try:
            self.price = float(product_data[3])  # price_per_hour
        except (ValueError, TypeError):
            self.price = 0.0

        self.image_path = product_data[4] if len(product_data) > 4 and product_data[4] else ""  # image_path (index 4)

        # Convert stock to int (index 5)
        try:
            self.stock = int(product_data[5]) if len(product_data) > 5 and product_data[5] else 0  # stock_quantity
        except (ValueError, TypeError):
            self.stock = 0

        # Convert is_available to boolean (index 6)
        try:
            # Handle both integer (0/1) and boolean values
            if len(product_data) > 6 and isinstance(product_data[6], bool):
                self.is_available = product_data[6]
            else:
                self.is_available = bool(int(product_data[6])) if len(product_data) > 6 and product_data[6] is not None else False
        except (ValueError, TypeError):
            self.is_available = False
        
        self.cart_callback = cart_callback

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        container.setGraphicsEffect(shadow)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Image or Icon section
        resolved = resolve_resource(self.image_path)
        if resolved and os.path.exists(resolved):
            # Display actual product image
            image_label = QLabel()
            image_label.setFixedSize(80, 80)
            pixmap = QPixmap(resolved)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.setStyleSheet("""
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                """)
            else:
                # Fallback to simple icon
                image_label = QLabel("📦")
                image_label.setStyleSheet("font-size: 36px; color: #4a5568;")
                image_label.setAlignment(Qt.AlignCenter)
        else:
            # Display default icon
            image_label = QLabel("📦")
            image_label.setStyleSheet("font-size: 36px; color: #4a5568;")
            image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(image_label)

        # ===== INFO SECTION =====
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        # Product Name
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        name_label.setStyleSheet("color: #2d3748;")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)

        # Description (truncated if too long)
        if self.description:
            desc_text = self.description[:80] + "..." if len(self.description) > 80 else self.description
            desc_label = QLabel(desc_text)
            desc_label.setFont(QFont("Segoe UI", 11))
            desc_label.setStyleSheet("color: #718096;")
            desc_label.setWordWrap(True)
            info_layout.addWidget(desc_label)

        # Price
        price_label = QLabel(f"₹{self.price:,.2f}")
        price_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        price_label.setStyleSheet("color: #2d3748;")

        # Stock/Availability indicator
        if self.is_available:
            if self.stock > 0:
                availability = QLabel(f"✅ {self.stock} in stock")
                availability.setStyleSheet("""
                    color: #38a169;
                    font-size: 12px;
                    font-weight: 500;
                """)
            else:
                availability = QLabel("⏳ Out of Stock")
                availability.setStyleSheet("""
                    color: #e53e3e;
                    font-size: 12px;
                    font-weight: 500;
                """)
        else:
            availability = QLabel("❌ Not Available")
            availability.setStyleSheet("""
                color: #e53e3e;
                font-size: 12px;
                font-weight: 500;
            """)

        # Add to layout
        info_layout.addWidget(price_label)
        info_layout.addWidget(availability)
        info_layout.addStretch()

        layout.addLayout(info_layout)
        layout.addStretch()

        # Add to Cart button (disabled if not available or out of stock)
        self.add_to_cart_btn = ModernButton("🛒 Add to Cart")
        self.add_to_cart_btn.clicked.connect(self.add_to_cart_clicked)
        
        if not self.is_available or self.stock <= 0:
            self.add_to_cart_btn.setEnabled(False)
            self.add_to_cart_btn.setStyleSheet("""
                QPushButton {
                    background:#cbd5e0;
                    color:#718096;
                    padding:10px 22px;
                    border-radius:10px;
                    font-weight:bold;
                    font-size: 13px;
                }
            """)

        layout.addWidget(self.add_to_cart_btn)

        main_layout.addWidget(container)

    def add_to_cart_clicked(self):
        """Add product to cart"""
        if self.cart_callback:
            self.cart_callback(self.product_id, self.name, self.price, self.stock)

    def update_cart_status(self, is_in_cart):
        """Update button based on cart status"""
        if is_in_cart:
            self.add_to_cart_btn.setText("✅ In Cart")
            self.add_to_cart_btn.setEnabled(False)
            self.add_to_cart_btn.setStyleSheet("""
                QPushButton {
                    background:#48bb78;
                    color:white;
                    padding:10px 22px;
                    border-radius:10px;
                    font-weight:bold;
                    font-size: 13px;
                }
            """)
        else:
            self.add_to_cart_btn.setText("🛒 Add to Cart")
            self.add_to_cart_btn.setEnabled(self.is_available and self.stock > 0)
            self.add_to_cart_btn.setStyleSheet("""
                QPushButton {
                    background:#667eea;
                    color:white;
                    padding:10px 22px;
                    border-radius:10px;
                    font-weight:bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background:#5a67d8;
                }
                QPushButton:disabled {
                    background:#cbd5e0;
                    color:#718096;
                }
            """)


# ======================================================
# Advance Payment Dialog
# ======================================================
class AdvancePaymentDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.total_amount = total_amount
        self.advance_amount = 0
        self.balance_amount = total_amount
        self.payment_method = "Cash"
        self.due_date = QDate.currentDate().addDays(7)  # Default due date 7 days from now
        
        self.setWindowTitle("Advance Payment")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2d3748;
            }
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border-color: #667eea;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("💰 Advance Payment")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Total Amount Display
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background-color: #ebf4ff;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        total_layout = QHBoxLayout(total_frame)
        
        total_label = QLabel("Total Amount:")
        total_label.setFont(QFont("Segoe UI", 14))
        total_label.setStyleSheet("color: #2d3748;")
        
        self.total_value_label = QLabel(f"₹{self.total_amount:,.2f}")
        self.total_value_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.total_value_label.setStyleSheet("color: #667eea;")
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_value_label)
        layout.addWidget(total_frame)
        
        # Payment Method
        method_group = QGroupBox("Payment Method")
        method_layout = QVBoxLayout(method_group)
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer"])
        self.payment_combo.currentTextChanged.connect(self.on_payment_method_changed)
        method_layout.addWidget(self.payment_combo)
        
        layout.addWidget(method_group)
        
        # Advance Payment Section
        advance_group = QGroupBox("Advance Payment Details")
        advance_layout = QFormLayout(advance_group)
        advance_layout.setSpacing(10)
        
        # Advance Amount
        self.advance_spin = QDoubleSpinBox()
        self.advance_spin.setRange(0, self.total_amount)
        self.advance_spin.setSingleStep(100)
        self.advance_spin.setPrefix("₹ ")
        self.advance_spin.setDecimals(2)
        self.advance_spin.valueChanged.connect(self.on_advance_changed)
        advance_layout.addRow("Advance Amount:", self.advance_spin)
        
        # Balance Amount (read-only)
        self.balance_label = QLabel(f"₹{self.total_amount:,.2f}")
        self.balance_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.balance_label.setStyleSheet("color: #e53e3e;")
        advance_layout.addRow("Balance Due:", self.balance_label)
        
        # Due Date
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setDate(self.due_date)
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setMinimumDate(QDate.currentDate())
        self.due_date_edit.setDisplayFormat("dd MMM yyyy")
        advance_layout.addRow("Due Date:", self.due_date_edit)
        
        layout.addWidget(advance_group)
        
        # Payment Status Note
        note_label = QLabel("Note: The products will be reserved until the due date.")
        note_label.setStyleSheet("color: #718096; font-size: 11px; font-style: italic; padding: 5px;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        proceed_btn = QPushButton("✅ Process Advance Payment")
        proceed_btn.setCursor(Qt.PointingHandCursor)
        proceed_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
            QPushButton:disabled {
                background-color: #cbd5e0;
                color: #718096;
            }
        """)
        
        full_payment_btn = QPushButton("💳 Pay Full Amount")
        full_payment_btn.setCursor(Qt.PointingHandCursor)
        full_payment_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5a67d8;
            }
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #a0aec0;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #718096;
            }
        """)
        
        button_layout.addWidget(proceed_btn)
        button_layout.addWidget(full_payment_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect buttons
        proceed_btn.clicked.connect(self.accept_advance)
        full_payment_btn.clicked.connect(self.accept_full)
        cancel_btn.clicked.connect(self.reject)
    
    def on_payment_method_changed(self, method):
        self.payment_method = method
    
    def on_advance_changed(self, value):
        self.advance_amount = value
        self.balance_amount = self.total_amount - value
        self.balance_label.setText(f"₹{self.balance_amount:,.2f}")
        
        # Update balance color based on amount
        if self.balance_amount > 0:
            self.balance_label.setStyleSheet("color: #e53e3e; font-weight: bold;")
        else:
            self.balance_label.setStyleSheet("color: #38a169; font-weight: bold;")
    
    def accept_advance(self):
        if self.advance_amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Please enter an advance amount greater than 0!")
            return
        
        self.due_date = self.due_date_edit.date()
        self.payment_type = "advance"
        self.accept()
    
    def accept_full(self):
        self.advance_amount = self.total_amount
        self.balance_amount = 0
        self.payment_type = "full"
        self.accept()


# ======================================================
# PDF Generator Class (Updated with Logo and No GST)
# ======================================================
class PDFGenerator:
    @staticmethod
    def generate_invoice(cart_items, total_amount, payment_type="full", 
                        advance_amount=0, balance_amount=0, due_date=None,
                        customer_name="Customer", customer_address="", 
                        customer_phone="", customer_email="", payment_method="Cash",
                        file_path=None):
        """Generate a PDF invoice for the cart items with advance payment details"""
        
        if file_path is None:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"invoice_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_LEFT  # Changed to LEFT alignment
        )
        
        right_align_style = ParagraphStyle(
            'RightAlign',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_RIGHT
        )
        
        left_align_style = ParagraphStyle(
            'LeftAlign',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_LEFT
        )
        
        # Get store contact info from database
        db = Database()
        contact_info = db.get_contact_info()
        
        # Create header with logo and seller address in top right
        logo_path = resolve_resource(os.path.join('src', 'logoforbill.webp'))
        logo_element = Paragraph("", styles['Normal'])  # Default empty paragraph
        
        if logo_path and os.path.exists(logo_path):
            try:
                logo_element = Image(logo_path, width=1.5*inch, height=1.5*inch)
            except:
                logo_element = Paragraph("", styles['Normal'])
        
        header_data = [[
            # Left side - Logo
            logo_element,
            
            # Right side - Seller Address
            Paragraph(
                f"<b>ADDRESS:</b><br/>"
                f"<b>Baskaran Events</b><br/>"
                f"{contact_info['address']}<br/>"
                f"Phone: {contact_info['phone']}<br/>"
                f"Email: {contact_info['email']}",
                right_align_style
            )
        ]]
        
        header_table = Table(header_data, colWidths=[3*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Invoice Details
        invoice_date = datetime.now().strftime("%d %B %Y, %I:%M %p")
        invoice_no = datetime.now().strftime("INV-%Y%m%d-%H%M%S")
        
        payment_status = "Partially Paid" if payment_type == "advance" and balance_amount > 0 else "Paid"
        status_color = "orange" if payment_status == "Partially Paid" else "green"
        
        details_text = f"""
        <b>Invoice Number:</b> {invoice_no}<br/>
        <b>Date:</b> {invoice_date}<br/>
        <b>Payment Status:</b> <font color="{status_color}">{payment_status}</font><br/>
        <b>Payment Method:</b> {payment_method}<br/>
        """
        
        if payment_type == "advance" and balance_amount > 0:
            due_date_str = due_date.toString("dd MMM yyyy") if due_date else "Not specified"
            details_text += f"<b>Due Date:</b> {due_date_str}<br/>"
        
        details = Paragraph(details_text, left_align_style)  # Changed to left align
        elements.append(details)
        elements.append(Spacer(1, 30))
        
        # Create table for items
        table_data = [['#', 'Item Description', 'Qty', 'Unit Price (₹)', 'Total (₹)']]
        
        # Add items to table
        for idx, item in enumerate(cart_items, 1):
            quantity = item.get('quantity', 1)
            unit_price = item['price'] / quantity if quantity > 0 else item['price']
            table_data.append([
                str(idx),
                item['name'],
                str(quantity),
                f"{unit_price:,.2f}",
                f"{item['price']:,.2f}"
            ])
        
        # Add subtotal
        subtotal = total_amount
        table_data.append(['', '', '', '', ''])
        table_data.append(['', '', '', 'Subtotal:', f"{subtotal:,.2f}"])
        
        # Add grand total (no GST)
        grand_total = subtotal
        table_data.append(['', '', '', 'GRAND TOTAL:', f"{grand_total:,.2f}"])
        
        # Add payment details if advance payment
        if payment_type == "advance" and balance_amount > 0:
            table_data.append(['', '', '', '', ''])
            table_data.append(['', '', '', 'Advance Paid:', f"-₹{advance_amount:,.2f}"])
            table_data.append(['', '', '', 'Balance Due:', f"₹{balance_amount:,.2f}"])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 0.5*inch, 1.2*inch, 1.3*inch])
        
        # Calculate row indices based on payment type
        if payment_type == "advance" and balance_amount > 0:
            # With advance payment rows
            item_end_row = -8  # Excluding empty row, subtotal, grand total, empty, advance, balance
            summary_start_row = -7
        else:
            # Without advance payment rows
            item_end_row = -5  # Excluding empty row, subtotal, grand total
            summary_start_row = -4
        
        # Add style to table
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Item rows
            ('BACKGROUND', (0, 1), (-1, item_end_row), colors.HexColor('#f7fafc')),
            ('ALIGN', (0, 1), (0, item_end_row), 'CENTER'),
            ('ALIGN', (1, 1), (1, item_end_row), 'LEFT'),
            ('ALIGN', (2, 1), (2, item_end_row), 'CENTER'),
            ('ALIGN', (3, 1), (4, item_end_row), 'RIGHT'),
            
            # Summary rows (subtotal and grand total)
            ('BACKGROUND', (0, summary_start_row), (-1, -1), colors.HexColor('#edf2f7')),
            ('FONTNAME', (0, summary_start_row), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2d3748')),
            ('ALIGN', (3, summary_start_row), (4, -1), 'RIGHT'),
            
            # Grid and borders
            ('GRID', (0, 0), (-1, item_end_row), 1, colors.HexColor('#cbd5e0')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#667eea')),
            ('LINEBELOW', (0, item_end_row), (-1, item_end_row), 1, colors.HexColor('#cbd5e0')),
        ])
        
        # Add specific styling for advance payment rows
        if payment_type == "advance" and balance_amount > 0:
            # Style for Advance Paid row
            table_style.add('BACKGROUND', (0, -3), (-1, -3), colors.HexColor('#fed7d7'))
            table_style.add('TEXTCOLOR', (0, -3), (-1, -3), colors.HexColor('#9b2c2c'))
            table_style.add('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold')
            
            # Style for Balance Due row
            table_style.add('BACKGROUND', (0, -2), (-1, -2), colors.HexColor('#fef3c7'))
            table_style.add('TEXTCOLOR', (0, -2), (-1, -2), colors.HexColor('#92400e'))
            table_style.add('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold')
            
            # Style for Grand Total row (now at -1)
            table_style.add('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#cbd5e0'))
            table_style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
        
        table.setStyle(table_style)
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Amount in words
        if payment_type == "advance" and balance_amount > 0:
            amount_in_words = PDFGenerator.number_to_words(advance_amount)
            amount_text = Paragraph(
                f"<b>Advance amount in words:</b> {amount_in_words} only",
                left_align_style  # Changed to left align
            )
            elements.append(amount_text)
            
            # Balance due note
            balance_text = Paragraph(
                f"<b>Balance due:</b> ₹{balance_amount:,.2f} to be paid by {due_date.toString('dd MMM yyyy') if due_date else 'due date'}",
                left_align_style  # Changed to left align
            )
            elements.append(balance_text)
            elements.append(Spacer(1, 10))
        else:
            amount_in_words = PDFGenerator.number_to_words(grand_total)
            amount_text = Paragraph(
                f"<b>Amount in words:</b> {amount_in_words} only",
                left_align_style  # Changed to left align
            )
            elements.append(amount_text)
            elements.append(Spacer(1, 20))
        
        # Buyer Information at the bottom - left aligned
        buyer_info = Paragraph(
            f"<b>CLIENT INFORMATION</b><br/>"
            f"<b>Name:</b> {customer_name}<br/>"
            f"<b>Address:</b> {customer_address}<br/>"
            f"<b>Phone:</b> {customer_phone if customer_phone else 'Not provided'}<br/>"
            f"<b>Email:</b> {customer_email if customer_email else 'Not provided'}",
            left_align_style  # Changed to left align
        )
        elements.append(buyer_info)
        elements.append(Spacer(1, 20))
        
        # Footer with thank you message - left aligned
        footer_text = """
        <br/>
        """
        
        footer = Paragraph(footer_text, left_align_style)  # Changed to left align
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        return file_path
    
    @staticmethod
    def number_to_words(n):
        """Convert number to words (for amount in words)"""
        if n == 0:
            return "Zero"
        
        # This is a simplified version - you can expand it for more accuracy
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", 
                 "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_two_digits(num):
            if num < 10:
                return units[num]
            elif num < 20:
                return teens[num - 10]
            else:
                ten = num // 10
                unit = num % 10
                if ten < len(tens):
                    return tens[ten] + (" " + units[unit] if unit > 0 else "")
                else:
                    return str(num)
        
        rupees = int(n)
        paise = int(round((n - rupees) * 100))
        
        if rupees == 0:
            result = ""
        elif rupees < 100:
            result = convert_two_digits(rupees)
        elif rupees < 1000:
            result = units[rupees // 100] + " Hundred " + convert_two_digits(rupees % 100)
        elif rupees < 100000:
            result = convert_two_digits(rupees // 1000) + " Thousand " + convert_two_digits(rupees % 1000)
        else:
            result = convert_two_digits(rupees // 100000) + " Lakh " + convert_two_digits(rupees % 100000)
        
        result = result.strip() + " Rupees"
        
        if paise > 0:
            result += " and " + convert_two_digits(paise) + " Paise"
        
        return result


# ======================================================
# Cart Widget with Headers and PDF Export (Updated)
# ======================================================
class CartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background-color: white;
            color: #333333;
        """)
        
        self.cart_items = []  # List of product data
        self.db = Database()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Cart title with limit indicator
        title_layout = QHBoxLayout()
        title = QLabel("🛒 Your Cart")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #2d3748; margin: 5px 0;")
        title_layout.addWidget(title)
        
        # Add limit indicator
        limit_label = QLabel("(One product type only)")
        limit_label.setFont(QFont("Segoe UI", 10))
        limit_label.setStyleSheet("color: #718096; margin-left: 10px;")
        title_layout.addWidget(limit_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Cart table with headers
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(3)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Action"])
        
        # Set header styles
        self.cart_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #667eea;
                color: white;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-right: 1px solid #5a67d8;
            }
        """)
        
        # Set column widths
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #e2e8f0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
                color: #4a5568;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidget::item:selected {
                background-color: #e2e8f0;
                color: #2d3748;
            }
        """)
        
        # Connect cell click for removal
        self.cart_table.cellClicked.connect(self.on_cell_clicked)
        
        layout.addWidget(self.cart_table)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setSpacing(8)
        
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.total_label.setStyleSheet("color: #2d3748;")
        
        self.items_count_label = QLabel("Items: 0 units")
        self.items_count_label.setFont(QFont("Segoe UI", 12))
        self.items_count_label.setStyleSheet("color: #4a5568;")
        
        summary_layout.addWidget(self.items_count_label)
        summary_layout.addWidget(self.total_label)
        
        layout.addWidget(summary_frame)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Clear cart button
        clear_btn = QPushButton("🗑️ Clear Cart")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #fed7d7;
                color: #9b2c2c;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #feb2b2;
            }
        """)
        clear_btn.clicked.connect(self.clear_cart)
        buttons_layout.addWidget(clear_btn)
        
        # Advance Payment Button
        advance_btn = QPushButton("💰 Pay Advance")
        advance_btn.setCursor(Qt.PointingHandCursor)
        advance_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed8936;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #dd6b20;
            }
        """)
        advance_btn.clicked.connect(self.process_advance_payment)
        buttons_layout.addWidget(advance_btn)
        
        # Full Checkout button
        checkout_btn = ModernButton("💳 Full Payment")
        checkout_btn.clicked.connect(self.checkout)
        buttons_layout.addWidget(checkout_btn)
        
        layout.addLayout(buttons_layout)
        
        self.update_summary()
    
    def add_to_cart(self, product_id, product_name, price, stock_available):
        """Add a product to the cart - only one product type allowed, but multiple quantities"""
        
        # Check if cart already has an item
        if len(self.cart_items) >= 1:
            current_item = self.cart_items[0] if self.cart_items else None
            
            if current_item and current_item['id'] == product_id:
                # Same product - increase quantity if stock available
                current_quantity = current_item.get('quantity', 1)
                unit_price = price  # Original unit price
                
                if current_quantity >= stock_available:
                    QMessageBox.warning(
                        self,
                        "Stock Limit Reached",
                        f"Sorry, only {stock_available} units of {product_name} are available in stock!"
                    )
                    return
                
                # Increase quantity
                new_quantity = current_quantity + 1
                current_item['quantity'] = new_quantity
                current_item['price'] = unit_price * new_quantity  # Update total price
                
                self.update_cart_display()
                self.update_summary()
                
                QMessageBox.information(
                    self,
                    "Quantity Updated",
                    f"{product_name} quantity increased to {new_quantity}\n"
                    f"Total: ₹{unit_price * new_quantity:,.2f}"
                )
                return
                
            else:
                # Different product - show option to replace
                reply = QMessageBox.question(
                    self,
                    "Replace Cart Item",
                    f"Your cart already contains:\n"
                    f"'{current_item['name'] if current_item else 'an item'}'\n\n"
                    f"Do you want to replace it with:\n"
                    f"'{product_name}'?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Store old product ID to update its button status
                    old_product_id = current_item['id'] if current_item else None
                    
                    # Check stock availability for new item
                    if stock_available <= 0:
                        QMessageBox.warning(
                            self,
                            "Out of Stock",
                            f"Sorry, {product_name} is out of stock!"
                        )
                        return
                    
                    # Clear cart and add new item with quantity 1
                    self.cart_items.clear()
                    self.cart_items.append({
                        'id': product_id,
                        'name': product_name,
                        'price': price,
                        'quantity': 1
                    })
                    
                    self.update_cart_display()
                    self.update_summary()
                    
                    # Update product widget button status
                    if hasattr(self.parent(), 'update_product_cart_status'):
                        # Update old product (if exists) to "Add to Cart" state
                        if old_product_id:
                            self.parent().update_product_cart_status(old_product_id, False)
                        # Update new product to "In Cart" state
                        self.parent().update_product_cart_status(product_id, True)
                    
                    QMessageBox.information(
                        self,
                        "Cart Updated",
                        f"Cart updated with '{product_name}'"
                    )
                # If user chooses No, do nothing
            return
        
        # If cart is empty, add the item normally with quantity 1
        if stock_available <= 0:
            QMessageBox.warning(
                self,
                "Out of Stock",
                f"Sorry, {product_name} is out of stock!"
            )
            return
        
        self.cart_items.append({
            'id': product_id,
            'name': product_name,
            'price': price,
            'quantity': 1
        })
        
        self.update_cart_display()
        self.update_summary()
        
        if hasattr(self.parent(), 'update_product_cart_status'):
            self.parent().update_product_cart_status(product_id, True)
        
        QMessageBox.information(
            self,
            "Added to Cart",
            f"{product_name} has been added to your cart!\n\n"
            f"Price per unit: ₹{price:,.2f}\n"
            f"Quantity: 1\n"
            f"Total: ₹{price:,.2f}\n"
            f"Note: You can add multiple quantities of the same product."
        )
    
    def update_cart_display(self):
        """Update the cart table display"""
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            quantity = item.get('quantity', 1)
            unit_price = item['price'] / quantity if quantity > 0 else item['price']
            
            # Item name with quantity
            name_item = QTableWidgetItem(f"- {item['name']} (x{quantity})")
            name_item.setForeground(QColor("#2d3748"))
            name_item.setFont(QFont("Segoe UI", 12))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.cart_table.setItem(row, 0, name_item)
            
            # Total Price
            price_item = QTableWidgetItem(f"₹{item['price']:,.2f}")
            price_item.setForeground(QColor("#2d3748"))
            price_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(row, 1, price_item)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fed7d7;
                    color: #9b2c2c;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #feb2b2;
                }
            """)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 2, remove_btn)
    
    def on_cell_clicked(self, row, column):
        """Handle cell click - remove item if clicked on name or price"""
        if column in [0, 1]:  # Click on name or price column
            self.remove_from_cart(row)
    
    def remove_from_cart(self, row):
        """Remove item from cart at specified row"""
        if 0 <= row < len(self.cart_items):
            removed_item = self.cart_items.pop(row)
            self.update_cart_display()
            self.update_summary()
            
            # Update product widget button status
            if hasattr(self.parent(), 'update_product_cart_status'):
                self.parent().update_product_cart_status(removed_item['id'], False)
            
            QMessageBox.information(
                self,
                "Removed from Cart",
                f"{removed_item['name']} has been removed from your cart!"
            )
    
    def update_summary(self):
        """Update the summary totals"""
        total = sum(item['price'] for item in self.cart_items)
        total_quantity = sum(item.get('quantity', 1) for item in self.cart_items)
        
        self.total_label.setText(f"Total: ₹{total:,.2f}")
        self.items_count_label.setText(f"Items: {total_quantity} units")
    
    def clear_cart(self):
        """Clear all items from cart"""
        if not self.cart_items:
            return
        
        # Store product IDs before clearing
        product_ids = [item['id'] for item in self.cart_items]
        
        reply = QMessageBox.question(
            self, 'Clear Cart', 
            'Are you sure you want to clear all items from your cart?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cart_items.clear()
            self.cart_table.setRowCount(0)
            self.update_summary()
            
            # Update product widget button status for all removed items
            if hasattr(self.parent(), 'update_product_cart_status'):
                for product_id in product_ids:
                    self.parent().update_product_cart_status(product_id, False)
    
    def process_advance_payment(self):
        """Process advance payment"""
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Your cart is empty!")
            return
        
        # Check stock availability before checkout
        for item in self.cart_items:
            # Get current stock from database
            product = self.db.get_product(item['id'])
            if product:
                current_stock = product[6]  # stock_quantity at index 6
                try:
                    requested_quantity = item.get('quantity', 1)
                    if int(current_stock) < requested_quantity:
                        QMessageBox.warning(
                            self,
                            "Stock Issue",
                            f"Sorry, only {current_stock} units of {item['name']} are available.\n"
                            f"You have {requested_quantity} in your cart.\n"
                            f"Please adjust the quantity."
                        )
                        return
                except (ValueError, TypeError):
                    QMessageBox.warning(
                        self,
                        "Stock Issue",
                        f"Sorry, there was an issue checking stock for {item['name']}."
                    )
                    return
        
        total = sum(item['price'] for item in self.cart_items)
        
        # Show advance payment dialog
        advance_dialog = AdvancePaymentDialog(total, self)
        if advance_dialog.exec() != QDialog.Accepted:
            return
        
        # Get customer information
        customer_info = self.get_customer_info()
        if not customer_info:
            return
        
        customer_name, customer_address, customer_phone, customer_email = customer_info
        
        # Ask where to save the PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        payment_type = advance_dialog.payment_type
        if payment_type == "advance":
            default_filename = f"advance_invoice_{timestamp}.pdf"
        else:
            default_filename = f"invoice_{timestamp}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Invoice PDF",
            default_filename,
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            # User cancelled save dialog
            return
        
        try:
            # Generate PDF invoice with advance payment details
            pdf_file = PDFGenerator.generate_invoice(
                self.cart_items,
                total,
                payment_type=payment_type,
                advance_amount=advance_dialog.advance_amount,
                balance_amount=advance_dialog.balance_amount,
                due_date=advance_dialog.due_date if payment_type == "advance" else None,
                customer_name=customer_name,
                customer_address=customer_address,
                customer_phone=customer_phone,
                customer_email=customer_email,
                payment_method=advance_dialog.payment_method,
                file_path=file_path
            )
            
            # Store product IDs and quantities before clearing cart
            product_info = [(item['id'], item.get('quantity', 1)) for item in self.cart_items]
            
            # Update stock in database (deduct quantities purchased)
            for item in self.cart_items:
                product = self.db.get_product(item['id'])
                if product:
                    try:
                        current_stock = int(product[6])  # stock_quantity at index 6
                        quantity_purchased = item.get('quantity', 1)
                        new_stock = current_stock - quantity_purchased
                        self.db.update_product(item['id'], stock=new_stock)
                    except (ValueError, TypeError, IndexError):
                        print(f"Error updating stock for product {item['id']}")
            
            # Show success message based on payment type
            total_quantity = sum(item.get('quantity', 1) for item in self.cart_items)
            
            if payment_type == "advance" and advance_dialog.balance_amount > 0:
                msg = (f"Advance payment processed successfully!\n\n"
                       f"Invoice saved to:\n{pdf_file}\n\n"
                       f"Total: ₹{total:,.2f}\n"
                       f"Advance Paid: ₹{advance_dialog.advance_amount:,.2f}\n"
                       f"Balance Due: ₹{advance_dialog.balance_amount:,.2f}\n"
                       f"Due Date: {advance_dialog.due_date.toString('dd MMM yyyy')}\n"
                       f"Items: {total_quantity} units\n"
                       f"Customer: {customer_name}\n\n"
                       f"Please pay the balance amount by the due date.")
            else:
                msg = (f"Payment Successful!\n\n"
                       f"Invoice saved to:\n{pdf_file}\n\n"
                       f"Total: ₹{total:,.2f}\n"
                       f"Items: {total_quantity} units\n"
                       f"Customer: {customer_name}\n\n"
                       f"Thank you for your purchase!")
            
            reply = QMessageBox.question(
                self,
                "Payment Successful!",
                msg + "\n\nDo you want to open the PDF?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Open the PDF with default application
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(pdf_file)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', pdf_file])
                else:  # Linux
                    subprocess.run(['xdg-open', pdf_file])
            
            # Clear cart after successful checkout
            self.cart_items.clear()
            self.cart_table.setRowCount(0)
            self.update_summary()
            
            # Update product widget button status for all items
            if hasattr(self.parent(), 'update_product_cart_status'):
                for product_id, _ in product_info:
                    self.parent().update_product_cart_status(product_id, False)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate PDF: {str(e)}"
            )
    
    def get_customer_info(self):
        """Get customer information through a dialog"""
        # Create a dialog for customer information
        info_dialog = QDialog(self)
        info_dialog.setWindowTitle("Customer Information")
        info_dialog.setMinimumWidth(400)
        info_dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2d3748;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
                color: #1f2937;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        
        dialog_layout = QVBoxLayout(info_dialog)
        dialog_layout.setSpacing(15)
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📝 Enter Your Details")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2d3748; margin-bottom: 10px;")
        dialog_layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Customer Name
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter your full name")
        form_layout.addRow("Name:*", name_input)
        
        # Customer Address
        address_input = QTextEdit()
        address_input.setPlaceholderText("Enter your complete address\nStreet, City, State, PIN Code")
        address_input.setMaximumHeight(100)
        form_layout.addRow("Address:*", address_input)
        
        # Customer Phone
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Enter your phone number")
        form_layout.addRow("Phone:", phone_input)
        
        # Customer Email
        email_input = QLineEdit()
        email_input.setPlaceholderText("Enter your email")
        form_layout.addRow("Email:", email_input)
        
        dialog_layout.addLayout(form_layout)
        
        # Note for required fields
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #718096; font-size: 11px; font-style: italic;")
        dialog_layout.addWidget(note_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        proceed_btn = QPushButton("✅ Continue")
        proceed_btn.setCursor(Qt.PointingHandCursor)
        proceed_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #a0aec0;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #718096;
            }
        """)
        
        button_layout.addWidget(proceed_btn)
        button_layout.addWidget(cancel_btn)
        dialog_layout.addLayout(button_layout)
        
        # Store result
        result = []
        
        def on_proceed():
            if not name_input.text().strip():
                QMessageBox.warning(info_dialog, "Required", "Please enter your name!")
                return
            if not address_input.toPlainText().strip():
                QMessageBox.warning(info_dialog, "Required", "Please enter your address!")
                return
            
            result.extend([
                name_input.text().strip(),
                address_input.toPlainText().strip(),
                phone_input.text().strip(),
                email_input.text().strip()
            ])
            info_dialog.accept()
        
        proceed_btn.clicked.connect(on_proceed)
        cancel_btn.clicked.connect(info_dialog.reject)
        
        if info_dialog.exec() == QDialog.Accepted and result:
            return result
        return None
    
    def checkout(self):
        """Proceed to full payment checkout"""
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Your cart is empty!")
            return
        
        # Check stock availability before checkout
        for item in self.cart_items:
            # Get current stock from database
            product = self.db.get_product(item['id'])
            if product:
                try:
                    current_stock = int(product[6])  # stock_quantity at index 6
                    requested_quantity = item.get('quantity', 1)
                    if current_stock < requested_quantity:
                        QMessageBox.warning(
                            self,
                            "Stock Issue",
                            f"Sorry, only {current_stock} units of {item['name']} are available.\n"
                            f"You have {requested_quantity} in your cart.\n"
                            f"Please adjust the quantity."
                        )
                        return
                except (ValueError, TypeError, IndexError):
                    QMessageBox.warning(
                        self,
                        "Stock Issue",
                        f"Sorry, there was an issue checking stock for {item['name']}."
                    )
                    return
        
        # Get customer information
        customer_info = self.get_customer_info()
        if not customer_info:
            return
        
        customer_name, customer_address, customer_phone, customer_email = customer_info
        
        # Ask where to save the PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"invoice_{timestamp}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Invoice PDF",
            default_filename,
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            # User cancelled save dialog
            return
        
        total = sum(item['price'] for item in self.cart_items)
        
        # Store product IDs and quantities before clearing cart
        product_info = [(item['id'], item.get('quantity', 1)) for item in self.cart_items]
        
        try:
            # Generate PDF invoice with customer details
            pdf_file = PDFGenerator.generate_invoice(
                self.cart_items,
                total,
                payment_type="full",
                advance_amount=total,
                balance_amount=0,
                customer_name=customer_name,
                customer_address=customer_address,
                customer_phone=customer_phone,
                customer_email=customer_email,
                payment_method="Full Payment",
                file_path=file_path
            )
            
            # Update stock in database (deduct quantities purchased)
            for item in self.cart_items:
                product = self.db.get_product(item['id'])
                if product:
                    try:
                        current_stock = int(product[6])  # stock_quantity at index 6
                        quantity_purchased = item.get('quantity', 1)
                        new_stock = current_stock - quantity_purchased
                        self.db.update_product(item['id'], stock=new_stock)
                    except (ValueError, TypeError, IndexError):
                        print(f"Error updating stock for product {item['id']}")
            
            total_quantity = sum(item.get('quantity', 1) for item in self.cart_items)
            
            # Show success message with option to open PDF
            reply = QMessageBox.question(
                self,
                "Payment Successful!",
                f"Invoice has been saved to:\n{pdf_file}\n\n"
                f"Total: ₹{total:,.2f}\n"
                f"Items: {total_quantity} units\n"
                f"Customer: {customer_name}\n\n"
                f"Do you want to open the PDF?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Open the PDF with default application
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(pdf_file)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', pdf_file])
                else:  # Linux
                    subprocess.run(['xdg-open', pdf_file])
            
            # Clear cart after successful checkout
            self.cart_items.clear()
            self.cart_table.setRowCount(0)
            self.update_summary()
            
            # Update product widget button status for all items
            if hasattr(self.parent(), 'update_product_cart_status'):
                for product_id, _ in product_info:
                    self.parent().update_product_cart_status(product_id, False)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate PDF: {str(e)}"
            )


# ======================================================
# Customer Store Widget (with larger logo and no overlap)
# ======================================================
class CustomerStoreWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #f7fafc;
                color: #333333;
            }
        """)

        # Database connection
        self.db = Database()
        
        # Store all products data from database
        self.all_products = []
        
        # Store all product widgets
        self.product_widgets = []
        
        # Timer for search debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.last_search_text = ""
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #cbd5e0;
            }
        """)
        
        # Left side - Products
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: #f7fafc;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)
        
        # Calculate 10% of screen height for header (original size)
        screen_height = QApplication.primaryScreen().availableGeometry().height()
        header_height = int(screen_height * 0.10)  # Keep at original 10%
        
        # Header with logo and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Container widget for header to control height
        header_container = QWidget()
        # Increase container height to accommodate larger logo
        header_container.setFixedHeight(int(header_height * 1.2))  # Increased container height by 20%
        header_container.setStyleSheet("background-color: transparent;")

        header_inner_layout = QHBoxLayout(header_container)
        header_inner_layout.setContentsMargins(10, 5, 10, 5)
        header_inner_layout.setSpacing(15)

        # Logo Image - made significantly larger
        logo_label = QLabel()
        logo_path = os.path.join(BASE_DIR, "src", "logo.png")
        
        # Make logo larger - 150% of original header height
        logo_size = int(header_height * 1.5)  # 150% of header height

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale the logo to the larger size while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)

        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo_label.setFixedSize(logo_size, logo_size)

        # Title Image - keep original size (70% of header height)
        title_label = QLabel()
        title_path = os.path.join(BASE_DIR, "src", "title.png")
        title_width = int(header_height * 2.5)  # Keep at original 2.5x

        if os.path.exists(title_path):
            pixmap = QPixmap(title_path)
            scaled_pixmap = pixmap.scaledToWidth(title_width, Qt.SmoothTransformation)
            title_label.setPixmap(scaled_pixmap)
        else:
            # Fallback text if image not found
            title_label.setText("BASKARAN\nEVENTS")
            title_font_size = int(header_height * 0.25)  # Keep at original 0.25
            title_label.setFont(QFont("Segoe UI", title_font_size, QFont.Bold))
            title_label.setStyleSheet("color: #2d3748;")
            title_label.setAlignment(Qt.AlignCenter)

        title_label.setAlignment(Qt.AlignCenter)

        # Add logo and title to layout
        header_inner_layout.addWidget(logo_label)
        header_inner_layout.addWidget(title_label, 1)  # The '1' gives it stretch factor to center

        # Refresh button - keep original size
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        btn_height = int(header_height * 0.5)  # Keep at original 50%
        btn_font_size = int(header_height * 0.18)  # Keep at original font size

        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #667eea;
                color: white;
                padding: {int(btn_height*0.2)}px {int(btn_height*0.4)}px;
                border-radius: {int(btn_height*0.25)}px;
                font-weight: bold;
                font-size: {btn_font_size}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #5a67d8;
            }}
        """)
        refresh_btn.setFixedHeight(btn_height)
        refresh_btn.clicked.connect(self.refresh_products)
        header_inner_layout.addWidget(refresh_btn)

        # Add header container to main layout
        left_layout.addWidget(header_container)
        
        # Add spacer between header and search bar to prevent overlap
        left_layout.addSpacing(10)  # Add 10px spacing
        
        # Search bar - slightly reduced size to prevent overlap
        self.search_bar = SearchBar()
        search_bar_height = int(header_height * 0.5)  # Reduced from 60% to 50%
        self.search_bar.setFixedHeight(search_bar_height)
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        left_layout.addWidget(self.search_bar)
        
        # Results count label
        self.results_label = QLabel("")
        self.results_label.setFont(QFont("Segoe UI", 11))
        self.results_label.setStyleSheet("color: #4a5568; margin: 5px 0;")
        left_layout.addWidget(self.results_label)
        
        # Products scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #edf2f7;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0aec0;
            }
        """)
        
        # Products container
        self.products_container = QWidget()
        self.products_container.setStyleSheet("background-color: transparent;")
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setSpacing(15)
        self.products_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create cart widget
        self.cart_widget = CartWidget()
        
        # Load products from database
        self.load_products_from_db()
        
        scroll.setWidget(self.products_container)
        left_layout.addWidget(scroll)
        
        # Right side - Cart
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(0)
        
        # Add cart widget
        right_layout.addWidget(self.cart_widget)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes (65% products, 35% cart)
        splitter.setSizes([780, 420])
        
        main_layout.addWidget(splitter)
        
        # Show all products initially
        self.update_results_count(len([p for p in self.all_products if len(p) > 6 and p[6]]))
    
    def load_products_from_db(self):
        """Load products from database"""
        # Clear existing widgets
        for widget in self.product_widgets:
            widget.setParent(None)
        self.product_widgets.clear()
        
        # Load products from database
        self.all_products = self.db.get_all_products()
        
        # Create product widgets
        for product_data in self.all_products:
            # Only show available products
            if len(product_data) > 6 and product_data[6]:  # is_available at index 6
                product_widget = ProductWidget(
                    product_data,
                    cart_callback=self.cart_widget.add_to_cart
                )
                self.product_widgets.append(product_widget)
                self.products_layout.addWidget(product_widget)
        
        # Add stretch at the end
        self.products_layout.addStretch()
    
    def update_product_cart_status(self, product_id, is_in_cart):
        """Update product widget button status based on cart"""
        for widget in self.product_widgets:
            if widget.product_id == product_id:
                widget.update_cart_status(is_in_cart)
                break
    
    def refresh_products(self):
        """Refresh products from database"""
        self.load_products_from_db()
        self.update_results_count(len([p for p in self.all_products if len(p) > 6 and p[6]]))  # Count only available
        QMessageBox.information(self, "Refreshed", "Product list has been refreshed!")
    
    def on_search_text_changed(self, text):
        """Handle search text changes with debouncing"""
        # Start/restart the timer
        self.search_timer.start(300)  # 300ms delay
    
    def perform_search(self):
        """Perform the actual search with debouncing"""
        search_text = self.search_bar.text().strip().lower()
        
        # Skip if same search text
        if search_text == self.last_search_text:
            return
        
        self.last_search_text = search_text
        
        if not search_text:
            # Show all available products
            for widget in self.product_widgets:
                widget.setVisible(True)
            visible_count = len([p for p in self.all_products if len(p) > 6 and p[6]])  # Check is_available at index 6
        else:
            # Search in database
            search_results = self.db.search_products(search_text)
            visible_count = 0
            
            # Hide all widgets first
            for widget in self.product_widgets:
                widget.setVisible(False)
            
            # Show only matching products that are available
            for product_data in search_results:
                if len(product_data) > 6 and product_data[6]:  # is_available at index 6
                    # Find and show the corresponding widget
                    for widget in self.product_widgets:
                        if widget.product_id == product_data[0]:
                            widget.setVisible(True)
                            visible_count += 1
                            break
        
        self.update_results_count(visible_count)
    
    def update_results_count(self, count):
        """Update the results count label"""
        if count == 0:
            self.results_label.setText("No products found")
            self.results_label.setStyleSheet("color: #e53e3e;")
        else:
            self.results_label.setText(f"Showing {count} product(s)")
            self.results_label.setStyleSheet("color: #4a5568;")


# ======================================================
# Admin Panel Widget Adapter
# ======================================================
class AdminPanelWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create an instance of the AdminPanel
        self.admin_panel = AdminPanel()
        
        # Extract the central widget from AdminPanel (since it's a QMainWindow)
        if hasattr(self.admin_panel, 'centralWidget'):
            central = self.admin_panel.centralWidget()
            if central:
                # Set the central widget as this widget's layout
                layout = QVBoxLayout(self)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(central)
                self.admin_panel.setCentralWidget(None)  # Detach it
            else:
                # If no central widget, just use the admin panel itself
                layout = QVBoxLayout(self)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(self.admin_panel)
        else:
            # If it's not a QMainWindow, just add it directly
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.admin_panel)


# ======================================================
# Main Application with Tabs
# ======================================================
class MainApplication(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Baskaran Events - Management System")
        self.resize(1300, 750)
        
        # Set application-wide style
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background: white;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QTabBar::tab {
                background: #f7fafc;
                color: #4a5568;
                padding: 12px 30px;
                margin-right: 2px;
                font-weight: bold;
                font-size: 14px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #e2e8f0;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
            QTabBar::tab:hover:!selected {
                background: #e2e8f0;
            }
            QTabBar::tab:first {
                margin-left: 10px;
            }
        """)
        
        # Create tabs
        self.customer_tab = CustomerStoreWidget()
        self.admin_tab = AdminPanelWidget()
        
        # Add tabs
        self.addTab(self.customer_tab, "🛒 Customer Store")
        self.addTab(self.admin_tab, "👤 Admin Panel")
        
        # Connect tab change signal
        self.currentChanged.connect(self.on_tab_changed)
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        if index == 1:  # Admin tab
            # Refresh admin panel data if needed
            if hasattr(self.admin_tab.admin_panel, 'load_products'):
                self.admin_tab.admin_panel.load_products()


# ======================================================
# Run
# ======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: white;
            color: #333333;
        }
        QMessageBox {
            background-color: white;
            color: #333333;
        }
        QMessageBox QLabel {
            color: #333333;
        }
    """)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())