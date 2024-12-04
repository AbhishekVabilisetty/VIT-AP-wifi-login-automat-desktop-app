from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox,QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
import json
import os
import sys

CONFIG_FILE1 = "config.json"

def superscript_to_int(sup_char):
    superscript_map = {
        '⁰': 0, '¹': 1, '²': 2, '³': 3, '⁴': 4, '⁵': 5, '⁶': 6, '⁷': 7, '⁸': 8, '⁹': 9, 
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9 
    }
    return superscript_map.get(sup_char, None) 

def gen_list(reg_no : str):
    reg_no = reg_no
    super_script = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']
    sup_list = []
    sup_list.append(reg_no)
    for i in sup_list:
        for j in range(len(i)):
            if(i[j].isdigit()):
                temp = i[0:j] + super_script[superscript_to_int(i[j])] + i[j+1:]
                if temp not in sup_list:
                    sup_list.append(temp)
    return sup_list

def save_credentials(username, password):
    """Save the username and password to a configuration file."""
    with open(CONFIG_FILE1, "w") as file:
        json.dump({"username": username, "password": password}, file)

def load_credentials():
    """Load the username and password from the configuration file."""
    if os.path.exists(CONFIG_FILE1):
        with open(CONFIG_FILE1, "r") as file:
            return json.load(file)
    return None

def delete_credentials():
    if os.path.exists(CONFIG_FILE1):
        os.remove(CONFIG_FILE1)
        
count=1
class LoginApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VIT-AP WiFi Login Automation")
        self.setGeometry(100, 100, 800, 600)
        # Set the application icon
        self.setWindowIcon(QIcon("app_icon.ico"))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Browser View
        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)

        # Reset Button
        self.reset_button = QPushButton("Reset Saved Credentials")
        self.reset_button.clicked.connect(self.reset_credentials)
        self.layout.addWidget(self.reset_button)
        
        # Style the button
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                font-size: 16px;
                padding: 8px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
        """)

        # Load the stored credentials or ask for them
        credentials = load_credentials()
        if credentials:
            self.username = credentials["username"]
            self.password = credentials["password"]
            reg_list = gen_list(self.username)
        else:
            self.username, self.password = self.ask_for_credentials()
            save_credentials(self.username, self.password)

        # Generate variations of the username
        self.username_variations = gen_list(self.username)

        # Load the URL and trigger login
        self.url = QUrl("http://172.18.10.10:1000/logout?")
        self.browser.setUrl(self.url)
        self.browser.page().loadFinished.connect(self.on_page_loaded)
        self.browser.show()

    def ask_for_credentials(self):
        """Ask the user for their username and password."""
        username, ok1 = QInputDialog.getText(self, "Input Required", "Enter your Reg_number:")
        if not ok1 or not username:
            sys.exit("Username input canceled or empty.")
        
        password, ok2 = QInputDialog.getText(self, "Input Required", "Enter your password:")
        if not ok2 or not password:
            sys.exit("Password input canceled or empty.")
        
        return username, password
    
    def on_page_loaded(self):
        """Inject username and password into the page."""
        username_xpath = '//*[@id="ft_un"]'
        password_xpath = '//*[@id="ft_pd"]'
        button_xpath = '/html/body/div/div/form/div[3]/button'

        # Use the first variation of the username
        username = self.username_variations
        print(len(username))
        global count
        if count<len(username):
            self.fill_username_password(username_xpath, password_xpath, username[count], self.password, button_xpath)
            count+=1
    def reset_credentials(self):
        """Prompt user to confirm reset and delete saved credentials."""
        reply = QMessageBox.question(self, "Reset Credentials", 
                                      "Are you sure you want to reset your credentials? This cannot be undone.", 
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_credentials()
            QMessageBox.information(self, "Reset Successful", "Credentials have been reset. Please restart the application.")
            sys.exit()

    def fill_username_password(self, username_xpath, password_xpath, username, password, button_xpath):
        """Fill in the username and password and click the login button."""
        js_code = f"""
        (function() {{
            try {{
                let usernameField = document.evaluate('{username_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                let passwordField = document.evaluate('{password_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                let loginButton = document.evaluate('{button_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

                if (usernameField && passwordField && loginButton) {{
                    usernameField.value = '{username}';
                    passwordField.value = '{password}';
                    loginButton.click();
                }} else {{
                    console.error("One or more elements not found.");
                }}
            }} catch (error) {{
                console.error("Error executing JS:", error.message);
            }}
        }})();
        """
        self.browser.page().runJavaScript(js_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    app.exec_()
