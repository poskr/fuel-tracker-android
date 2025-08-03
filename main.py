# main.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
# если у вас есть свой модуль fueltracker.py с классом FuelTrackerApp, вы можете импортировать его:
# from fueltracker import FuelTrackerApp

class FuelTrackerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Fuel Tracker App", font_size='20sp'))
        # сюда добавляйте ваши виджеты: таблицы, графики, кнопки и т.д.
        return layout

if __name__ == "__main__":
    FuelTrackerApp().run()
