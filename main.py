from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import random
import os
import wave
import math
import struct

class GameApp(App):
    def build(self):
        self.layout = FloatLayout()
        self.player_name = "Player"
        self.score = 0
        self.time_left = 120
        self.level = 1
        self.music_on = True
        self.high_name = "Nobody"
        self.high_score = self.load_high_score()
        self.create_sounds()

        # --- SKY BACKGROUND ---
        with self.layout.canvas.before:
            Color(0.53, 0.81, 0.98, 1)
            Rectangle(size=(1000, 1000), pos=(0, 0))
            Color(1, 0.9, 0.2, 1)
            Ellipse(pos=(700, 500), size=(120, 120))
            Color(1, 1, 1, 1)
            Ellipse(pos=(100, 550), size=(150, 60))
            Ellipse(pos=(150, 580), size=(150, 60))
            Ellipse(pos=(500, 600), size=(180, 60))
            Ellipse(pos=(550, 630), size=(180, 60))
            Color(0.3, 0.8, 0.3, 1)
            Rectangle(pos=(0, 0), size=(1000, 120))

        self.show_start_screen()
        return self.layout

    # --- SOUNDS - FIXED FAST VERSION ---
    def make_tone(self, filename, notes):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
        except:
            pass
        path = os.path.join(self.user_data_dir, filename)
        if os.path.exists(path):
            return path
        try:
            samplerate = 44100
            all_data = bytearray()
            for freq, dur in notes:
                if freq == 0:
                    frames = int(samplerate * dur)
                    all_data += b'\x00\x00' * frames
                    continue
                frames = int(samplerate * dur)
                for i in range(frames):
                    volume = 1.0 - (i / frames)
                    value = int(32767 * 0.5 * volume * math.sin(2 * math.pi * freq * i / samplerate))
                    all_data += struct.pack('<h', value)
                gap = int(samplerate * 0.05)
                all_data += b'\x00\x00' * gap
            with wave.open(path, 'w') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(samplerate)
                wav.writeframes(bytes(all_data))
        except Exception as e:
            print("Sound error:", e)
        return path

    def create_sounds(self):
        self.ting_sound = None
        self.tadaa_sound = None
        self.over_sound = None
        self.music_sound = None
        try:
            ting_path = self.make_tone('ting.wav', [(1320, 0.15)])
            win_path = self.make_tone('tadaa.wav', [(523, 0.15), (659, 0.15), (784, 0.15), (1046, 0.35)])
            over_path = self.make_tone('over.wav', [(300, 0.2), (200, 0.4)])
            music_notes = [
                (523, 0.25), (659, 0.25), (784, 0.25), (659, 0.25),
                (880, 0.25), (784, 0.25), (659, 0.25), (523, 0.25),
                (587, 0.25), (659, 0.25), (698, 0.25), (784, 0.25),
                (784, 0.4), (659, 0.4), (523, 0.4), (0, 0.3),
            ]
            music_path = self.make_tone('music.wav', music_notes)
            self.ting_sound = SoundLoader.load(ting_path)
            self.tadaa_sound = SoundLoader.load(win_path)
            self.over_sound = SoundLoader.load(over_path)
            self.music_sound = SoundLoader.load(music_path)
            if self.music_sound:
                self.music_sound.loop = True
                self.music_sound.volume = 0.3
                self.music_sound.play()
        except Exception as e:
            print("Create sounds error:", e)

    def play_ting(self):
        try:
            if self.ting_sound:
                self.ting_sound.play()
        except:
            pass

    def play_tadaa(self):
        try:
            if self.tadaa_sound:
                self.tadaa_sound.play()
        except:
            pass

    def play_over(self):
        try:
            if self.over_sound:
                self.over_sound.play()
        except:
            pass

    def toggle_music(self, instance):
        try:
            if self.music_on:
                if self.music_sound:
                    self.music_sound.stop()
                self.music_on = False
                instance.text = 'MUSIC: OFF'
            else:
                if self.music_sound:
                    self.music_sound.play()
                self.music_on = True
                instance.text = 'MUSIC: ON'
        except:
            pass

    # --- EASY INFINITE LEVELS ---
    def get_level_settings(self):
        return self.get_level_settings_for(self.level)

    def get_level_settings_for(self, lvl):
        time = max(20, 120 - (lvl - 1) * 8)
        size = max(80, 220 - (lvl - 1) * 8)
        target = 5 + (lvl - 1) * 3
        return time, size, target

    # --- HIGH SCORE SAVE / LOAD ---
    def get_file(self):
        return os.path.join(self.user_data_dir, 'highscore.txt')

    def load_high_score(self):
        try:
            with open(self.get_file(), 'r') as f:
                parts = f.read().strip().split(',')
                if len(parts) == 2:
                    self.high_name = parts[0]
                    return int(parts[1])
        except:
            pass
        self.high_name = "Nobody"
        return 0

    def load_high_name(self):
        return getattr(self, 'high_name', 'Nobody')

    def save_high_score(self):
        try:
            with open(self.get_file(), 'w') as f:
                f.write(f"{self.player_name},{self.high_score}")
        except:
            pass

    # --- SCREEN 1: ENTER NAME ---
    def show_start_screen(self):
        self.layout.clear_widgets()
        self.level = 1
        title = Label(text='TAP! GAME', font_size=60, bold=True, color=(1, 0.3, 0.5, 1), size_hint=(1, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.88})
        self.layout.add_widget(title)
        best = Label(text=f'HIGHEST SCORE: {self.high_score} by {self.high_name}', font_size=22, bold=True, color=(0, 0, 0, 1), size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.76})
        self.layout.add_widget(best)
        levels_info = Label(text='INFINITE LEVELS!\nLevel 1: 2 MINS, only 5 taps - SUPER EASY!', font_size=22, color=(0, 0, 0, 1), size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.68})
        self.layout.add_widget(levels_info)
        ask = Label(text='Enter Your Name:', font_size=30, color=(0, 0, 0, 1), size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.58})
        self.layout.add_widget(ask)
        self.name_input = TextInput(hint_text='Type your name here...', font_size=30, multiline=False, size_hint=(0.8, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.48})
        self.layout.add_widget(self.name_input)
        start_btn = Button(text='START GAME', font_size=30, bold=True, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1), size_hint=(0.6, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.30})
        start_btn.bind(on_press=self.start_game)
        self.layout.add_widget(start_btn)
        music_text = 'MUSIC: ON' if self.music_on else 'MUSIC: OFF'
        music_btn = Button(text=music_text, font_size=20, background_color=(1, 0.7, 0, 1), color=(1, 1, 1, 1), size_hint=(0.4, 0.07), pos_hint={'center_x': 0.5, 'center_y': 0.18})
        music_btn.bind(on_press=self.toggle_music)
        self.layout.add_widget(music_btn)

    # --- SCREEN 2: GAME ---
    def start_game(self, instance):
        if self.level == 1:
            try:
                name = self.name_input.text.strip()
                if name == "":
                    name = "Player"
                self.player_name = name
            except:
                pass
        time_for_level, btn_size, target = self.get_level_settings()
        self.time_left = time_for_level
        self.target = target
        self.btn_size = btn_size
        self.score = 0
        self.layout.clear_widgets()
        self.score_label = Label(text=f'LEVEL {self.level} | {self.player_name} | Score: 0 / {self.target} | Time: {self.time_left}\nBest: {self.high_score} by {self.high_name}', font_size=20, color=(0, 0, 0, 1), size_hint=(1, 0.15), pos_hint={'top': 1})
        self.layout.add_widget(self.score_label)
        self.tap_btn = Button(text='TAP!', font_size=30, bold=True, background_color=(1, 0.3, 0.5, 1), color=(1, 1, 1, 1), size_hint=(None, None), size=(btn_size, btn_size), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.tap_btn.bind(on_press=self.tap_it)
        self.layout.add_widget(self.tap_btn)
        Clock.schedule_interval(self.update_timer, 1)

    def tap_it(self, instance):
        self.play_ting()
        self.score += 1
        self.score_label.text = f'LEVEL {self.level} | {self.player_name} | Score: {self.score} / {self.target} | Time: {self.time_left}\nBest: {self.high_score} by {self.high_name}'
        instance.pos_hint = {'center_x': random.uniform(0.2, 0.8), 'center_y': random.uniform(0.3, 0.8)}
        instance.background_color = (random.random(), random.random(), random.random(), 1)

    def update_timer(self, dt):
        self.time_left -= 1
        self.score_label.text = f'LEVEL {self.level} | {self.player_name} | Score: {self.score} / {self.target} | Time: {self.time_left}\nBest: {self.high_score} by {self.high_name}'
        if self.time_left <= 0:
            Clock.unschedule(self.update_timer)
            if self.score >= self.target:
                self.show_level_complete()
            else:
                self.show_game_over()

    # --- SCREEN 3: LEVEL COMPLETE ---
    def show_level_complete(self):
        self.play_tadaa()
        self.layout.clear_widgets()
        win = Label(text=f'LEVEL {self.level} COMPLETE!', font_size=45, bold=True, color=(0, 0.7, 0, 1), size_hint=(1, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.75})
        self.layout.add_widget(win)
        next_time, next_size, next_target = self.get_level_settings_for(self.level + 1)
        result = Label(text=f'You got {self.score} taps!\nNext: Level {self.level + 1}\n{next_target} taps in {next_time} sec - a little harder!', font_size=26, color=(0, 0, 0, 1), size_hint=(1, 0.25), pos_hint={'center_x': 0.5, 'center_y': 0.55})
        self.layout.add_widget(result)
        next_btn = Button(text=f'NEXT LEVEL {self.level + 1}', font_size=30, bold=True, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1), size_hint=(0.6, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.32})
        next_btn.bind(on_press=self.next_level)
        self.layout.add_widget(next_btn)

    def next_level(self, instance):
        self.level += 1
        self.start_game(instance)

    # --- SCREEN 4: GAME OVER ---
    def show_game_over(self):
        self.play_over()
        total = (self.level - 1) * 100 + self.score
        is_new_record = False
        if total > self.high_score:
            self.high_score = total
            self.high_name = self.player_name
            self.save_high_score()
            is_new_record = True
        self.layout.clear_widgets()
        over = Label(text='GAME OVER!', font_size=60, bold=True, color=(1, 0, 0, 1), size_hint=(1, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.78})
        self.layout.add_widget(over)
        if is_new_record:
            record = Label(text='NEW RECORD!!!', font_size=35, bold=True, color=(1, 0.7, 0, 1), size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.66})
            self.layout.add_widget(record)
        result = Label(text=f'You reached Level {self.level}\n{self.player_name}, Score: {self.score} / {self.target}\nHighest: {self.high_score} by {self.high_name}', font_size=28, color=(0, 0, 0, 1), size_hint=(1, 0.25), pos_hint={'center_x': 0.5, 'center_y': 0.45})
        self.layout.add_widget(result)
        again_btn = Button(text='PLAY AGAIN', font_size=30, bold=True, background_color=(0.2, 0.8, 0.2, 1), color=(1, 1, 1, 1), size_hint=(0.6, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.25})
        again_btn.bind(on_press=self.play_again)
        self.layout.add_widget(again_btn)

    def play_again(self, instance):
        self.show_start_screen()

if __name__ == '__main__':
    GameApp().run()
