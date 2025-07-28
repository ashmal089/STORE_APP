from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.core.window import Window
import sqlite3
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Set window size
Window.size = (450, 650)

# -------------------- FILE PATH SETUP --------------------
BASE_DIR = os.path.join(os.getcwd(), "store_app")
BILLS_DIR = os.path.join(BASE_DIR, "bills")
DB_PATH = os.path.join(BASE_DIR, "store.db")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)
if not os.path.exists(BILLS_DIR):
    os.makedirs(BILLS_DIR)

# ---------------- DATABASE ----------------
def setup_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        quantity INTEGER,
        price REAL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        items TEXT,
        total REAL,
        date TEXT
    )
    """)
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()

# ---------------- LOGIN SCREEN ----------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        layout.add_widget(Label(text="Login Page", font_size=32, color=(0, 0.5, 1, 1)))

        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.12))
        self.password = TextInput(hint_text="Password", multiline=False, password=True, size_hint=(1, 0.12))
        layout.add_widget(self.username)
        layout.add_widget(self.password)

        btn_login = Button(text="Login", on_press=self.login, size_hint=(1, 0.12), background_color=(0, 0.6, 0.9, 1))
        layout.add_widget(btn_login)

        self.add_widget(layout)

    def login(self, instance):
        username = self.username.text
        password = self.password.text
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            self.manager.current = "dashboard"
        else:
            Popup(title="Error", content=Label(text="Invalid credentials!"), size_hint=(0.6, 0.4)).open()

# ---------------- DASHBOARD ----------------
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        layout.add_widget(Label(text="Dashboard", font_size=32, color=(0.2, 0.6, 1, 1)))

        layout.add_widget(Button(text="Billing Page", on_press=lambda x: self.go_to("billing"),
                                 size_hint=(1, 0.15), background_color=(0.2, 0.7, 0.2, 1)))
        layout.add_widget(Button(text="Assets Page", on_press=lambda x: self.go_to("assets"),
                                 size_hint=(1, 0.15), background_color=(0.3, 0.5, 0.9, 1)))
        layout.add_widget(Button(text="Bill History", on_press=lambda x: self.go_to("history"),
                                 size_hint=(1, 0.15), background_color=(0.8, 0.5, 0.2, 1)))
        layout.add_widget(Button(text="Logout", on_press=lambda x: self.go_to("login"),
                                 size_hint=(1, 0.15), background_color=(0.9, 0.3, 0.3, 1)))
        self.add_widget(layout)

    def go_to(self, screen_name):
        if screen_name == "assets":
            self.manager.get_screen("assets").switch_view("list")
        elif screen_name == "history":
            self.manager.get_screen("history").load_bills()
        self.manager.current = screen_name

# ---------------- BILLING ----------------
class BillingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bill_items = []
        self.total_amount = 0

        layout = BoxLayout(orientation="vertical", padding=10, spacing=0)
        layout.add_widget(Label(text="Billing Page", font_size=32, color=(0, 0.5, 1, 1)))

        self.customer_name = TextInput(hint_text="Customer Name", size_hint=(1, 0.12))
        layout.add_widget(self.customer_name)

        self.asset_spinner = Spinner(text="Select Item", values=[], size_hint=(1, 0.12))
        self.asset_spinner.bind(text=self.load_price)

        self.item_qty = TextInput(hint_text="Quantity", size_hint=(1, 0.12))
        self.item_price = TextInput(hint_text="Price", size_hint=(1, 0.12))

        layout.add_widget(self.asset_spinner)
        layout.add_widget(self.item_qty)
        layout.add_widget(self.item_price)

        layout.add_widget(Button(text="Add Item", on_press=self.add_item, size_hint=(1, 0.12),
                                 background_color=(0, 0.8, 0.5, 1)))

        # Highlighted TOTAL label
        self.total_label = Label(text="Total: 0", font_size=28, color=(1, 0, 0, 1), bold=True)
        layout.add_widget(self.total_label)

        layout.add_widget(Button(text="Print Bill", on_press=self.print_bill,
                                 size_hint=(1, 0.12), background_color=(0.8, 0.8, 0, 1)))
        layout.add_widget(Button(text="Back", on_press=lambda x: self.go_back(),
                                 size_hint=(1, 0.12), background_color=(0.7, 0.3, 0.3, 1)))

        self.add_widget(layout)

    def on_pre_enter(self):
        self.load_assets()

    def load_assets(self, *args):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM assets")
        rows = c.fetchall()
        conn.close()
        self.asset_spinner.values = [row[0] for row in rows]

    def load_price(self, spinner, text):
        if text == "Select Item":
            self.item_price.text = ""
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT price FROM assets WHERE name=?", (text,))
        price = c.fetchone()
        conn.close()
        if price:
            self.item_price.text = str(price[0])

    def add_item(self, instance):
        try:
            name = self.asset_spinner.text.strip()
            if name == "Select Item":
                Popup(title="Error", content=Label(text="Please select an item!"), size_hint=(0.6, 0.4)).open()
                return

            qty = int(self.item_qty.text.strip())
            price = float(self.item_price.text.strip())

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT quantity FROM assets WHERE name=?", (name,))
            asset = c.fetchone()

            if not asset:
                Popup(title="Error", content=Label(text=f"Item '{name}' not found!"), size_hint=(0.6, 0.4)).open()
                conn.close()
                return

            available_qty = asset[0]
            if qty > available_qty:
                Popup(title="Error", content=Label(text=f"Not enough stock! Available: {available_qty}"),
                      size_hint=(0.6, 0.4)).open()
                conn.close()
                return

            new_qty = available_qty - qty
            c.execute("UPDATE assets SET quantity=? WHERE name=?", (new_qty, name))
            conn.commit()
            conn.close()

            total = qty * price
            self.bill_items.append((name, qty, price, total))
            self.total_amount += total
            self.total_label.text = f"Total: {self.total_amount}"

            self.item_qty.text = ""
            self.item_price.text = ""
            self.asset_spinner.text = "Select Item"

        except Exception as e:
            Popup(title="Error", content=Label(text=f"Error: {str(e)}"), size_hint=(0.6, 0.4)).open()

    def print_bill(self, instance):
        if not self.bill_items:
            Popup(title="Error", content=Label(text="No items in bill!"), size_hint=(0.6, 0.4)).open()
            return

        customer = self.customer_name.text.strip() or "Guest"
        bill_details = "\n".join([f"{i[0]} x {i[1]} = {i[3]}" for i in self.bill_items])

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO bills (customer_name, items, total, date) VALUES (?, ?, ?, ?)",
                  (customer, bill_details, self.total_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        bill_path = os.path.join(BILLS_DIR, f"bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        c_pdf = canvas.Canvas(bill_path, pagesize=A4)
        width, height = A4

        c_pdf.setFont("Helvetica-Bold", 18)
        c_pdf.drawString(200, height - 50, "=== BILL ===")

        c_pdf.setFont("Helvetica", 12)
        c_pdf.drawString(50, height - 80, f"Customer: {customer}")
        y = height - 120
        for item in self.bill_items:
            c_pdf.drawString(50, y, f"{item[0]} | Qty: {item[1]} | Price: {item[2]} | Total: {item[3]}")
            y -= 20

        c_pdf.setFont("Helvetica-Bold", 14)
        c_pdf.drawString(50, y - 20, f"TOTAL: {self.total_amount}")
        c_pdf.showPage()
        c_pdf.save()

        Popup(title="Bill Saved", content=Label(text=f"Bill saved at:\n{bill_path}"), size_hint=(0.7, 0.4)).open()

        self.bill_items.clear()
        self.total_amount = 0
        self.total_label.text = "Total: 0"
        self.customer_name.text = ""

    def go_back(self):
        self.manager.get_screen("assets").switch_view("list")
        self.manager.current = "dashboard"

# ---------------- BILL HISTORY ----------------
class BillHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.layout.add_widget(Label(text="Bill History", font_size=32, color=(0.2, 0.6, 1, 1)))

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.bill_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.bill_grid.bind(minimum_height=self.bill_grid.setter('height'))
        self.scroll.add_widget(self.bill_grid)
        self.layout.add_widget(self.scroll)

        self.layout.add_widget(Button(text="Back", on_press=lambda x: self.go_back(),
                                      size_hint=(1, 0.12), background_color=(0.7, 0.3, 0.3, 1)))

        self.add_widget(self.layout)

    def load_bills(self):
        self.bill_grid.clear_widgets()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, customer_name, total, date FROM bills ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()

        if rows:
            for row in rows:
                bill_id, cust, total, date = row
                btn = Button(text=f"Bill #{bill_id} | {cust} | Total: {total} | Date: {date}",
                             size_hint_y=None, height=50,
                             on_press=lambda x, id=bill_id: self.show_details(id))
                self.bill_grid.add_widget(btn)
        else:
            self.bill_grid.add_widget(Label(text="No bills found.", size_hint_y=None, height=40))

    def show_details(self, bill_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT items FROM bills WHERE id=?", (bill_id,))
        items = c.fetchone()[0]
        conn.close()
        Popup(title="Bill Details", content=Label(text=items), size_hint=(0.8, 0.8)).open()

    def go_back(self):
        self.manager.current = "dashboard"

# ---------------- ASSETS PAGE ----------------
class AssetsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_view = "list"

        self.main_layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.main_layout.add_widget(Label(text="Assets Page", font_size=32, color=(0.2, 0.6, 1, 1)))

        btn_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, 0.1))
        btn_layout.add_widget(Button(text="List", on_press=lambda x: self.switch_view("list"),
                                     background_color=(0.3, 0.5, 0.9, 1)))
        btn_layout.add_widget(Button(text="Add", on_press=lambda x: self.switch_view("add"),
                                     background_color=(0.2, 0.7, 0.2, 1)))
        self.main_layout.add_widget(btn_layout)

        self.content_layout = BoxLayout(orientation="vertical", spacing=10)
        self.main_layout.add_widget(self.content_layout)

        self.add_widget(self.main_layout)
        self.switch_view("list")

    def switch_view(self, view):
        self.current_view = view
        self.content_layout.clear_widgets()
        if view == "list":
            self.show_assets_list()
        else:
            self.show_add_asset()

    def show_assets_list(self):
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.asset_grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[10, 10])
        self.asset_grid.bind(minimum_height=self.asset_grid.setter('height'))
        self.scroll.add_widget(self.asset_grid)
        self.content_layout.add_widget(self.scroll)
        self.load_assets()

        self.content_layout.add_widget(Button(text="Back", on_press=lambda x: self.go_back(),
                                              size_hint=(1, 0.12), background_color=(0.7, 0.3, 0.3, 1)))

    def load_assets(self):
        self.asset_grid.clear_widgets()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM assets")
        rows = c.fetchall()
        conn.close()

        if rows:
            for row in rows:
                asset_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
                asset_box.add_widget(Label(text=f"{row[1]} | Qty: {row[2]} | Price: {row[3]}"))
                del_btn = Button(text="Delete", size_hint_x=None, width=80,
                                 background_color=(0.9, 0.2, 0.2, 1))
                del_btn.bind(on_press=lambda x, id=row[0]: self.delete_asset(id))
                asset_box.add_widget(del_btn)
                self.asset_grid.add_widget(asset_box)
        else:
            self.asset_grid.add_widget(Label(text="No assets found.", size_hint_y=None, height=40))

    def delete_asset(self, asset_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM assets WHERE id=?", (asset_id,))
        conn.commit()
        conn.close()
        self.load_assets()
        Popup(title="Deleted", content=Label(text="Asset deleted successfully!"), size_hint=(0.6, 0.4)).open()

    def show_add_asset(self):
        self.asset_name = TextInput(hint_text="Asset Name", size_hint=(1, 0.12))
        self.asset_qty = TextInput(hint_text="Quantity", size_hint=(1, 0.12))
        self.asset_price = TextInput(hint_text="Price", size_hint=(1, 0.12))

        self.content_layout.add_widget(self.asset_name)
        self.content_layout.add_widget(self.asset_qty)
        self.content_layout.add_widget(self.asset_price)
        self.content_layout.add_widget(Button(text="Save Asset", on_press=self.add_asset,
                                              size_hint=(1, 0.12), background_color=(0, 0.8, 0.5, 1)))
        self.content_layout.add_widget(Button(text="Back", on_press=lambda x: self.go_back(),
                                              size_hint=(1, 0.12), background_color=(0.7, 0.3, 0.3, 1)))

    def add_asset(self, instance):
        try:
            name = self.asset_name.text.strip()
            qty = int(self.asset_qty.text.strip())
            price = float(self.asset_price.text.strip())

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id FROM assets WHERE LOWER(name)=?", (name.lower(),))
            existing = c.fetchone()
            if existing:
                c.execute("UPDATE assets SET quantity=quantity+?, price=? WHERE id=?", (qty, price, existing[0]))
            else:
                c.execute("INSERT INTO assets (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
            conn.commit()
            conn.close()

            Popup(title="Success", content=Label(text="Asset Added!"), size_hint=(0.6, 0.4)).open()
            self.asset_name.text = ""
            self.asset_qty.text = ""
            self.asset_price.text = ""
        except Exception as e:
            Popup(title="Error", content=Label(text=f"Error: {str(e)}"), size_hint=(0.6, 0.4)).open()

    def go_back(self):
        self.manager.current = "dashboard"

# ---------------- MAIN APP ----------------
class StoreApp(App):
    def build(self):
        setup_database()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(BillingScreen(name="billing"))
        sm.add_widget(AssetsScreen(name="assets"))
        sm.add_widget(BillHistoryScreen(name="history"))
        return sm

if __name__ == "__main__":
    StoreApp().run()
