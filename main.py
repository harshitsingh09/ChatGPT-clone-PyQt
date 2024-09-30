import sys
import random
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QWidget, QTextEdit, QListWidget, QSplitter, 
    QToolButton, QListWidgetItem, QLabel, QComboBox
)
from PyQt5.QtCore import Qt, QTimer


# Emulate a streamed response generator
def response_generator():
    responses = [
        "Hello! How can I assist you today?",
        "Hi! Is there something you'd like to discuss?",
        "I'm here to help you with any questions you have.",
        "Can I assist you with something?"
    ]
    response = random.choice(responses)
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


class ChatGPTReplica(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up main window
        self.setWindowTitle("ChatGPT Replica")
        self.setGeometry(100, 100, 900, 600)

        # Keep track of conversations
        self.conversations = {}  # Stores all conversations by session name
        self.current_session = None

        # Set style sheet for aesthetics
        self.setStyleSheet("""
    QMainWindow {
            background-color: #F5F5F5;
        }
        QTextEdit {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 15px;
            font-size: 14px;
            color: #333333;
            border: none;
        }
        QLineEdit {
            border: 2px solid #CCCCCC;
            border-radius: 15px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 15px;
            padding: 10px 15px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QListWidget {
            background-color: #FAFAFA;
            border: none;
            font-size: 14px;
            padding: 5px;
        }
        QListWidget::item {
            padding: 15px;
            margin: 5px;
            background-color: #E0F7FA;
            border-radius: 10px;
        }
        QListWidget::item:selected {
            background-color: #B2DFDB;
            border-radius: 10px;
            font-weight: bold;
        }
        QToolButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 20px;
            padding: 5px;  /* Reduced padding for compactness */
            font-size: 16px;  /* Adjusted font size */
        }
        QToolButton:hover {
            background-color: #45a049;
        }
        QLabel {
            font-size: 16px;  /* Adjusted font size for logo */
        }
    """)


        # Central widget and layout setup
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)  # Set the layout for central widget
        self.setCentralWidget(self.central_widget)

        # Create a navigation bar
        self.create_nav_bar()

        # Sidebar layout
        self.sidebar_widget = QWidget(self)
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(10)

        # Create a conversation list in the sidebar
        self.conversation_list = QListWidget(self)
        self.conversation_list.clicked.connect(self.load_conversation)
        self.sidebar_layout.addWidget(self.conversation_list)

        # Add a button to start a new conversation
        self.new_conversation_button = QPushButton("New Conversation", self)
        self.new_conversation_button.clicked.connect(self.start_new_conversation)
        self.sidebar_layout.addWidget(self.new_conversation_button)

        # Chat display and input field setup
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Start a conversation...")

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        # Layout for input field and send button
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.send_button)

        # Chat layout (chat display and input box)
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addWidget(self.chat_display)
        self.chat_layout.addLayout(self.input_layout)

        # Split the layout into sidebar (left) and chat window (right)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.sidebar_widget)
        self.splitter.addWidget(QWidget(self))  # Placeholder for chat layout
        self.splitter.widget(1).setLayout(self.chat_layout)
        self.layout.addWidget(self.splitter)

        # Initialize the sidebar as visible
        self.sidebar_visible = True

        # Start with a new conversation
        self.start_new_conversation()

    def create_nav_bar(self):
        """Create the navigation bar with a logo, hamburger icon, and model selection dropdown."""
        nav_bar = QHBoxLayout()
        nav_bar.setSpacing(10)  # Adjusted spacing for compactness
        nav_bar.setContentsMargins(0, 0, 0, 0)  # Remove margins for compactness

        # Hamburger icon
        self.toggle_button = QToolButton(self)
        self.toggle_button.setText("☰")  # Changed to a right arrow
        self.toggle_button.setStyleSheet("font-size: 20px;")  # Increase size of the arrow
        self.toggle_button.setFixedSize(50, 50)  # Set fixed size for consistency
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        nav_bar.addWidget(self.toggle_button)

        # Title label
        title_label = QLabel("ChatGPT clone on PyQt", self)  # Title label
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")  # Optional style
        title_label.setAlignment(Qt.AlignCenter)  # Center the title label
        nav_bar.addWidget(title_label)

        # Logo placeholder
        logo_label = QLabel("Logo", self)  # Replace with your logo image if needed
        logo_label.setAlignment(Qt.AlignCenter)  # Center the logo label
        nav_bar.addWidget(logo_label)

        # Model selection dropdown (reduced width and made softer)
        self.model_selection = QComboBox(self)
        self.model_selection.setFixedWidth(120)  # Increased fixed width for a larger appearance
        self.model_selection.setStyleSheet("""
            QComboBox {
                padding: 8px;  /* Adjusted padding for softness */
                font-size: 14px;  /* Set font size for better visibility */
                border: 1px solid #CCCCCC;  /* Light border for soft appearance */
                border-radius: 10px;  /* Rounded corners */
            }
        """)
        self.model_selection.addItems(["Model 1", "Model 2", "Model 3"])  # Add your model options here
        nav_bar.addWidget(self.model_selection)

        # Add the navigation bar to the main layout
        self.layout.addLayout(nav_bar)  # Use self.layout to add the nav bar layout

    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        if self.sidebar_visible:
            self.sidebar_widget.hide()
            self.toggle_button.setText("→")  # Change to right arrow
            self.splitter.setSizes([0, self.width()])  # Adjust splitter sizes
        else:
            self.sidebar_widget.show()
            self.toggle_button.setText("←")  # Change to left arrow
            self.splitter.setSizes([200, self.width() - 200])
        self.sidebar_visible = not self.sidebar_visible

    def start_new_conversation(self):
        """Start a new conversation session"""
        session_id = len(self.conversations) + 1
        session_name = f"Session {session_id}"
        self.conversations[session_name] = []  # Initialize an empty conversation
        self.current_session = session_name
        self.add_conversation_to_sidebar(session_name)
        self.chat_display.clear()
        self.chat_display.append(f"Started {session_name}.")

    def add_conversation_to_sidebar(self, session_name):
        """Add a styled conversation item to the sidebar"""
        item = QListWidgetItem(session_name)
        self.conversation_list.addItem(item)

    def load_conversation(self):
        """Load the selected conversation from the sidebar"""
        selected_item = self.conversation_list.currentItem()
        if selected_item:
            selected_session = selected_item.text()
            if selected_session in self.conversations:
                self.current_session = selected_session
                self.chat_display.clear()
                for message in self.conversations[selected_session]:
                    role = message["role"].capitalize()
                    content = message["content"]
                    self.chat_display.append(f"<b>{role}:</b> {content}")

    def send_message(self):
        """Send a user message and generate an assistant response"""
        user_message = self.input_field.text().strip()
        if user_message and self.current_session:
            self.chat_display.append(f"<b>User:</b> {user_message}")
            self.save_message("user", user_message)
            self.input_field.clear()

            # Simulate assistant response
            QTimer.singleShot(500, self.stream_assistant_response)

    def stream_assistant_response(self):
        """Simulate typing animation for assistant response"""
        response_text = ""
        self.chat_display.append(f"<b>Assistant:</b> ")
        for word in response_generator():
            response_text += word
            self.chat_display.insertPlainText(word)
            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )
            QApplication.processEvents()  # Ensure UI updates for each word

        self.save_message("assistant", response_text)
        self.chat_display.append("")  # Add a newline after response

    def save_message(self, role, content):
        """Save the current message to the conversation"""
        if self.current_session:
            self.conversations[self.current_session].append({"role": role, "content": content})


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTReplica()
    window.show()
    sys.exit(app.exec_())
