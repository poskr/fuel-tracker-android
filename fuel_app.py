#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEL Fuel Tracker – AUTO AMOUNT + DELETE SELECTED
✔️ Автоподсчёт amount из gallons × price_per_gal
✔️ Price/Gal добавлено в UI
✔️ Amount readonly (автозаполняется)
✔️ Delete Selected работает как раньше
"""

import requests, json
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window

# === CONFIG ===
SUPABASE_URL = "https://rvfgaincutbfybaarsdj.supabase.co/rest/v1"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ2ZmdhaW5jdXRiZnliYWFyc2RqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM5ODAzODEsImV4cCI6MjA2OTU1NjM4MX0.Xx9BJbaRRKrX1_n9C-P8ie0c7VZz6sUI8MfVw1vYkok"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

TABLE_FUEL = "fuel"
TABLE_STATES = "states"
PAYMENT_TYPES = ["UFC", "Mudflap", "Cash", "Other"]
LOCAL_STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA",
                "MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD",
                "TN","TX","UT","VT","VA","WA","WV","WI","WY"]

Window.clearcolor = (0.05, 0.05, 0.05, 1)

# === API ===
def api_request(method, path, params=None, body=None):
    url = f"{SUPABASE_URL}/{path}"
    try:
        r = requests.request(method, url, headers=HEADERS, params=params, json=body, timeout=10)
        print(f"[DEBUG] {method} {url} → {r.status_code} {r.text[:200]}")
        return r.json() if r.status_code in (200, 201) else []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def load_records():
    r = api_request("GET", TABLE_FUEL, {"select": "*", "order": "id.desc"})
    return r[:7] if isinstance(r, list) else []

def load_states():
    s = api_request("GET", TABLE_STATES, {"select": "code"})
    return [i["code"] for i in s] if isinstance(s, list) and s else LOCAL_STATES

def add_record(date, state, gallons, price_per_gal, mileage, payment, notes):
    g = float(gallons) if gallons else 0
    ppg = float(price_per_gal) if price_per_gal else 0
    m = float(mileage) if mileage else 0
    amount = g * ppg
    gpm = (m / g) if g > 0 else 0

    return api_request("POST", TABLE_FUEL, body={
        "date": date, "state": state, "gallons": g, "price_per_gal": ppg,
        "mileage": m, "amount": amount, "gpm": gpm,
        "payment": payment, "notes": notes
    })

def delete_record(record_id):
    return api_request("DELETE", TABLE_FUEL, params={"id": f"eq.{record_id}"})


# === UI ===
class FuelUI(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor_y = "top"
        self.states = load_states()
        self.selected_state = None
        self.selected_payment = "UFC"
        self.selected_id = None

        root = BoxLayout(orientation="horizontal", spacing=5)

        # ==== LEFT PANEL ====
        left_scroll = ScrollView(size_hint=(0.35, 1))
        left_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8, padding=8)
        left_box.bind(minimum_height=left_box.setter("height"))

        self.api_log = Label(text="[API] Connecting...", color=(1,1,0,1), size_hint_y=None, height=25)
        left_box.add_widget(self.api_log)

        self.date = self._field(left_box, "Date (MM/DD/YYYY)")

        # STATE
        self.state_btn = Button(text="Select State", background_color=(0.2,0.5,1,1), size_hint_y=None, height=40)
        self.state_btn.bind(on_release=lambda x:self.open_state_popup())
        left_box.add_widget(self.state_btn)

        # GALLONS
        self.gallons = self._field(left_box, "Gallons")

        # PRICE PER GAL
        self.price_gal = self._field(left_box, "Price/Gal")

        # AMOUNT (readonly)
        self.amount = self._field(left_box, "Amount")
        self.amount.readonly = True

        # MILEAGE
        self.mileage = self._field(left_box, "Mileage")

        # PAYMENT
        self.pay_btn = Button(text=f"Payment: {self.selected_payment}", background_color=(0.3,0.3,0.3,1), size_hint_y=None, height=40)
        self.pay_btn.bind(on_release=lambda x:self.open_payment_popup())
        left_box.add_widget(self.pay_btn)

        # NOTES
        self.notes = self._field(left_box, "Notes")

        # AUTO CALC AMOUNT при вводе Gallons/Price
        self.gallons.bind(text=lambda i,v:self.calc_amount())
        self.price_gal.bind(text=lambda i,v:self.calc_amount())

        # SAVE
        save_btn = Button(text="💾 SAVE", background_color=(0,0.7,0,1), size_hint_y=None, height=50)
        save_btn.bind(on_release=lambda x:self.save_record())
        left_box.add_widget(save_btn)

        # DELETE SELECTED
        del_btn = Button(text="🗑 Delete Selected", background_color=(0.7,0,0,1), size_hint_y=None, height=50)
        del_btn.bind(on_release=lambda x:self.delete_selected())
        left_box.add_widget(del_btn)

        left_scroll.add_widget(left_box)
        root.add_widget(left_scroll)

        # ==== RIGHT TABLE ====
        self.table = GridLayout(cols=7, size_hint_y=None, row_default_height=35, spacing=5, padding=5)
        self.table.bind(minimum_height=self.table.setter('height'))
        scroll = ScrollView(size_hint=(0.65, 1)); scroll.add_widget(self.table)
        root.add_widget(scroll)

        self.add_widget(root)
        self.refresh_table()
        self.check_api()

    def _field(self, parent, label):
        parent.add_widget(Label(text=label, color=(1,1,1,1), size_hint_y=None, height=20))
        f = TextInput(multiline=False, size_hint_y=None, height=40, background_color=(0.2,0.2,0.2,1), foreground_color=(1,1,1,1))
        parent.add_widget(f); return f

    def calc_amount(self):
        try:
            g = float(self.gallons.text) if self.gallons.text else 0
            p = float(self.price_gal.text) if self.price_gal.text else 0
            self.amount.text = f"{g*p:.2f}" if g > 0 and p > 0 else ""
        except:
            self.amount.text = ""

    # === POPUPS ===
    def open_state_popup(self):
        box = BoxLayout(orientation="vertical", spacing=3, padding=5)
        grid = GridLayout(cols=1, size_hint_y=None, spacing=3)
        grid.bind(minimum_height=grid.setter("height"))
        for s in self.states:
            btn = Button(text=s, size_hint_y=None, height=40)
            btn.bind(on_release=lambda b,v=s:(self.set_state(v), popup.dismiss()))
            grid.add_widget(btn)
        scroll = ScrollView(); scroll.add_widget(grid)
        box.add_widget(scroll)
        popup = Popup(title="Select State", content=box, size_hint=(0.5,0.7))
        popup.open()

    def set_state(self, code):
        self.selected_state = code
        self.state_btn.text = f"State: {code}"

    def open_payment_popup(self):
        box = BoxLayout(orientation="vertical", spacing=3, padding=5)
        for p in PAYMENT_TYPES:
            btn = Button(text=p, size_hint_y=None, height=40)
            btn.bind(on_release=lambda b,v=p:(self.set_payment(v), popup.dismiss()))
            box.add_widget(btn)
        popup = Popup(title="Select Payment", content=box, size_hint=(0.4,0.4))
        popup.open()

    def set_payment(self, val):
        self.selected_payment = val
        self.pay_btn.text = f"Payment: {val}"

    # === TABLE ===
    def refresh_table(self):
        self.table.clear_widgets()
        for h in ["Date","State","Gallons","Mileage","GPM","Price/Gal","Amount"]:
            self.table.add_widget(Label(text=f"[b]{h}[/b]", markup=True, color=(1,1,1,1)))

        for r in load_records():
            rec_id = r.get("id")
            g = r.get("gallons") or 0
            m = r.get("mileage") or 0
            a = r.get("amount") or 0
            gpm = r.get("gpm") or (m/g if g>0 else 0)
            ppg = r.get("price_per_gal") or (a/g if g>0 else 0)

            row = [r.get("date","-"), r.get("state","-"), f"{g:.3f}", f"{m:.1f}", f"{gpm:.2f}", f"{ppg:.2f}", f"${a:.2f}"]
            for v in row:
                cell = Button(text=v, background_color=(0.1,0.1,0.1,1), size_hint_y=None, height=30)
                cell.bind(on_release=lambda b, rid=rec_id: self.select_record(rid))
                self.table.add_widget(cell)

    def select_record(self, rec_id):
        self.selected_id = rec_id
        self.api_log.text = f"[DEBUG] Selected ID: {rec_id}"
        self.api_log.color = (0,1,1,1)

    # === SAVE ===
    def save_record(self):
        if not self.selected_state:
            self.api_log.text = "[ERROR] Select state!"
            self.api_log.color = (1,0,0,1)
            return
        res = add_record(self.date.text, self.selected_state, self.gallons.text,
                         self.price_gal.text, self.mileage.text, self.selected_payment, self.notes.text)
        self.api_log.text = "[DEBUG] Saved OK" if res else "[DEBUG] Save Failed"
        self.api_log.color = (0,1,0,1) if res else (1,0,0,1)
        self.refresh_table()

    # === DELETE ===
    def delete_selected(self):
        if not self.selected_id:
            self.api_log.text = "[ERROR] No record selected!"
            self.api_log.color = (1,0,0,1)
            return
        delete_record(self.selected_id)
        self.api_log.text = "[DEBUG] Deleted"
        self.api_log.color = (1,1,0,1)
        self.selected_id = None
        self.refresh_table()

    def check_api(self):
        test = api_request("GET", TABLE_FUEL, {"select": "id", "limit": 1})
        if isinstance(test, list):
            self.api_log.text = "[API] Connected"
            self.api_log.color = (0,1,0,1)
        else:
            self.api_log.text = "[API] ERROR"
            self.api_log.color = (1,0,0,1)


class FuelApp(App):
    def build(self): return FuelUI()

if __name__ == "__main__":
    FuelApp().run()