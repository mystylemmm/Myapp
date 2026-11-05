from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
import random

class GameApp(App):
    def build(self):
        self.score = 0
        self.time_left = 30
        self.layout = FloatLayout()

        # --- SKY BACKGROUND ---
        with self.layout.canvas.before:
            Color(0.53, 0.81, 0.98, 1) # sky blue
            Rectangle(size=(1000, 1000), pos=(0, 0))
            # Sun
            Color(1, 0.9, 0.2, 1)
            Ellipse(pos=(700, 500), size=(120, 120))
            # Clouds
            Color(1, 1, 1, 1)
            Ellipse(pos=(100, 550), size=(150, 60))
            Ellipse(pos=(150, 580), size=(150, 60))
            Ellipse(pos=(500, 600), size=(180, 60))
            Ellipse(pos=(550, 630), size=(180, 60))
            # Grass
            Color(0.3, 0.8, 0.3, 1)
            Rectangle(pos=(0, 0), size=(1000, 120))

        # Score label
        self.score_label = Label(text='Score: 0 | Time: 30', font_size=30, color=(0,0,0,1), size_hint=(1, 0.1), pos_hint={'top': 1})
        self.layout.add_widget(self.score_label)

        # TAP BUTTON - NO STAR ANYMORE!
        self.tap_btn = Button(text='TAP!', font_size=60, bold=True, background_color=(1, 0.3, 0.5, 1), color=(1,1,1,1), size_hint=(None, None), size=(200, 200), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.tap_btn.bind(on_press=self.tap_it)
        self.layout.add_widget(self.tap_btn)

        Clock.schedule_interval(self.update_timer, 1)
        return self.layout

    def tap_it(self, instance):
        self.score += 1
        self.score_label.text = f'Score: {self.score} | Time: {self.time_left}'
        # move TAP button to random place + change color each tap!
        instance.pos_hint = {'center_x': random.uniform(0.2, 0.8), 'center_y': random.uniform(0.3, 0.8)}
        instance.background_color = (random.random(), random.random(), random.random(), 1)

    def update_timer(self, dt):
        self.time_left -= 1
        self.score_label.text = f'Score: {self.score} | Time: {self.time_left}'
        if self.time_left <= 0:
            self.score_label.text = f'GAME OVER! Score: {self.score}'
            self.tap_btn.text = 'DONE!'
            Clock.unschedule(self.update_timer)

if __name__ == '__main__':
    GameApp().run()
