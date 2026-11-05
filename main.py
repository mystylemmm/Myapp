from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import random

class StarGame(App):
    def build(self):
            self.score = 0
                    self.time_left = 30
                            self.layout = FloatLayout()
                                    self.score_label = Label(text='Score: 0  |  Time: 30', font_size=28, pos_hint={'center_x': 0.5, 'top': 1}, size_hint=(1, 0.15))
                                            self.layout.add_widget(self.score_label)
                                                    self.star = Button(text='⭐', font_size=60, size_hint=(None, None), size=(120, 120), pos_hint={'center_x': 0.5, 'center_y': 0.5})
                                                            self.star.bind(on_press=self.tap_star)
                                                                    self.layout.add_widget(self.star)
                                                                            Clock.schedule_interval(self.tick, 1)
                                                                                    return self.layout
                                                                                        def tap_star(self, instance):
                                                                                                if self.time_left <= 0:
                                                                                                            return
                                                                                                                    self.score += 1
                                                                                                                            self.star.pos_hint = {'center_x': random.uniform(0.15, 0.85), 'center_y': random.uniform(0.2, 0.75)}
                                                                                                                                    self.update_label()
                                                                                                                                        def tick(self, dt):
                                                                                                                                                if self.time_left <= 0:
                                                                                                                                                            return
                                                                                                                                                                    self.time_left -= 1
                                                                                                                                                                            if self.time_left <= 0:
                                                                                                                                                                                        self.score_label.text = f'GAME OVER! Score: {self.score}'
                                                                                                                                                                                                    self.score = 0
                                                                                                                                                                                                                self.time_left = 30
                                                                                                                                                                                                                            Clock.schedule_once(self.reset_game, 3)
                                                                                                                                                                                                                                    else:
                                                                                                                                                                                                                                                self.update_label()
                                                                                                                                                                                                                                                    def reset_game(self, dt):
                                                                                                                                                                                                                                                            self.update_label()
                                                                                                                                                                                                                                                                def update_label(self):
                                                                                                                                                                                                                                                                        self.score_label.text = f'Score: {self.score}  |  Time: {self.time_left}'
                                                                                                                                                                                                                                                                        StarGame().run()
