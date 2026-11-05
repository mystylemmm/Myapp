# CATCH THE STARS V3 - FIXED - Shop + Daily Bonus + Leaderboard!
import os, math, random, wave, struct, json
from datetime import date
from kivy.app import App
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock

Window.clearcolor = (0.1, 0.1, 0.3, 1)

def make_tone(filename, freq, duration=0.3, volume=0.5, type='sine'):
    if os.path.exists(filename): return
    rate = 22050; n = int(rate * duration)
    with wave.open(filename, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        for i in range(n):
            t = i / rate
            val = math.sin(2 * math.pi * freq * t) if type=='sine' else (1 if math.sin(2*math.pi*freq*t)>0 else -1)
            w.writeframes(struct.pack('<h', int(val * volume * 32767)))

def make_music():
    fn = "music.wav"
    if os.path.exists(fn): return fn
    rate = 22050
    notes = [(523,0.5),(523,0.5),(784,0.5),(784,0.5),(880,0.5),(880,0.5),(784,1.0),
             (698,0.5),(698,0.5),(659,0.5),(659,0.5),(587,0.5),(587,0.5),(523,1.0),
             (784,0.5),(784,0.5),(698,0.5),(698,0.5),(659,0.5),(659,0.5),(587,0.5),
             (784,0.5),(784,0.5),(698,0.5),(698,0.5),(659,0.5),(659,0.5),(587,0.5),
             (523,0.5),(523,0.5),(784,0.5),(784,0.5),(880,0.5),(880,0.5),(784,1.0),
             (698,0.5),(698,0.5),(659,0.5),(659,0.5),(587,0.5),(587,0.5),(523,1.0)]
    with wave.open(fn, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        for freq, dur in notes:
            n = int(rate * dur)
            for i in range(n):
                val = math.sin(2 * math.pi * freq * i/rate) * 0.3
                w.writeframes(struct.pack('<h', int(val * 32767)))
    return fn

class StarGame(App):
    def build(self):
        self.save_file = os.path.join(self.user_data_dir, "save.json")
        self.save = self.load_save()
        self.score = 0; self.lives = 3; self.level = 1; self.playing = False; self.items = []
        self.stars_this_game = 0; self.coins_this_game = 0; self.bombs_this_game = 0
        self.shop_mode = None

        # --- DAILY BONUS CHECK ---
        today = str(date.today())
        self.daily_msg = ""
        if self.save.get("last_day") != today:
            self.save["coins"] += 50
            self.save["last_day"] = today
            self.daily_msg = "📅 DAILY BONUS! +50 💰 for coming back today!"
            self.save_game()

        make_tone("ding.wav", 1200, 0.3, 0.6)
        make_tone("coin.wav", 1500, 0.2, 0.6)
        make_tone("heart.wav", 900, 0.4, 0.6)
        make_tone("boom.wav", 100, 0.5, 0.8, 'square')
        make_tone("gameover.wav", 200, 1.0, 0.6, 'square')
        make_tone("buy.wav", 2000, 0.4, 0.6)
        self.s_ding = SoundLoader.load("ding.wav"); self.s_coin = SoundLoader.load("coin.wav")
        self.s_heart = SoundLoader.load("heart.wav"); self.s_boom = SoundLoader.load("boom.wav")
        self.s_over = SoundLoader.load("gameover.wav"); self.s_buy = SoundLoader.load("buy.wav")
        self.music = SoundLoader.load(make_music())
        if self.music: self.music.loop = True; self.music.volume = 0.15

        self.layout = FloatLayout()
        # Backgrounds - can change in Shop!
        self.bg_colors = {
            "night": (0.1, 0.1, 0.35, 1),
            "sunset": (1.0, 0.5, 0.2, 1),
            "ocean": (0.0, 0.6, 0.8, 1),
            "candy": (1.0, 0.5, 0.8, 1),
        }
        bgc = self.bg_colors.get(self.save.get("bg", "night"), (0.1,0.1,0.35,1))
        with self.layout.canvas.before:
            self.bg_color = Color(*bgc)
            self.bg = Rectangle(size=Window.size, pos=(0,0))
            Color(1, 1, 0.7, 1)
            self.moon = Ellipse(pos=(Window.width-220, Window.height-220), size=(140,140))
        Window.bind(size=self.update_bg)

        # Top Bar
        self.score_label = Label(text="⭐ Score: 0", font_size='22sp', bold=True, color=(1,1,0,1), pos_hint={'x':0.01,'top':0.99}, size_hint=(None,None), size=(260,35))
        self.coins_label = Label(text=f"💰 Coins: {self.save['coins']}", font_size='22sp', bold=True, color=(1,0.8,0,1), pos_hint={'x':0.01,'top':0.93}, size_hint=(None,None), size=(260,35))
        self.high_label = Label(text=f"🏆 Best: {self.save['high']}", font_size='22sp', bold=True, color=(0,1,1,1), pos_hint={'x':0.01,'top':0.87}, size_hint=(None,None), size=(260,35))
        self.lives_label = Label(text="❤️❤️❤️", font_size='24sp', pos_hint={'center_x':0.5,'top':0.99}, size_hint=(None,None), size=(200,35))
        self.level_label = Label(text="Level 1", font_size='20sp', bold=True, color=(0,1,1,1), pos_hint={'right':0.99,'top':0.99}, size_hint=(None,None), size=(180,35))
        for w in [self.score_label, self.coins_label, self.high_label, self.lives_label, self.level_label]:
            self.layout.add_widget(w)

        # Buttons Row
        self.tasks_btn = Button(text="🎯 TASKS", font_size='18sp', bold=True, background_color=(1,0.5,0,1), size_hint=(None,None), size=(130,45), pos_hint={'right':0.99,'top':0.93})
        self.tasks_btn.bind(on_press=self.show_tasks)
        self.shop_btn = Button(text="🛒 SHOP", font_size='18sp', bold=True, background_color=(1,0,1,1), size_hint=(None,None), size=(130,45), pos_hint={'right':0.99,'top':0.87})
        self.shop_btn.bind(on_press=self.show_shop)
        self.leader_btn = Button(text="👫 LEADERBOARD", font_size='18sp', bold=True, background_color=(0,0.7,1,1), size_hint=(None,None), size=(180,45), pos_hint={'right':0.99,'top':0.81})
        self.leader_btn.bind(on_press=self.show_leaderboard)
        for b in [self.tasks_btn, self.shop_btn, self.leader_btn]: self.layout.add_widget(b)

        self.title = Label(text="⭐ CATCH THE STARS! ⭐", font_size='32sp', bold=True, color=(1,1,0,1), pos_hint={'center_x':0.5,'center_y':0.68}, size_hint=(None,None), size=(600,70))
        sub = f"🏆 Best: {self.save['high']}  |  💰 Coins: {self.save['coins']}\n{self.daily_msg}\nDrag basket to catch stars!"
        self.subtitle = Label(text=sub, font_size='19sp', color=(1,1,1,1), pos_hint={'center_x':0.5,'center_y':0.54}, size_hint=(None,None), size=(650,100))
        self.layout.add_widget(self.title); self.layout.add_widget(self.subtitle)

        self.basket = Button(text=self.save.get("basket","🧺"), font_size='60sp', background_color=(0,0,0,0), size_hint=(None,None), size=(140,110), pos_hint={'center_x':0.5,'y':0.02})
        self.layout.add_widget(self.basket)

        self.start_btn = Button(text="▶ START GAME!", font_size='28sp', bold=True, background_color=(0,1,0,1), size_hint=(None,None), size=(300,80), pos_hint={'center_x':0.5,'center_y':0.35})
        self.start_btn.bind(on_press=self.start_game)
        self.layout.add_widget(self.start_btn)

        self.msg = Label(text="", font_size='28sp', bold=True, color=(1,0.5,0,1), pos_hint={'center_x':0.5,'center_y':0.5}, size_hint=(None,None), size=(600,60))
        self.layout.add_widget(self.msg)

        # Popup
        self.popup = Label(text="", font_size='19sp', bold=True, color=(1,1,1,1), pos_hint={'center_x':0.5,'center_y':0.52}, size_hint=(None,None), size=(700,340))
        self.popup.opacity = 0; self.layout.add_widget(self.popup)
        self.popup_close = Button(text="CLOSE ✖", font_size='18sp', background_color=(1,0,0,1), size_hint=(None,None), size=(150,45), pos_hint={'center_x':0.5,'center_y':0.12})
        self.popup_close.bind(on_press=self.hide_popup); self.popup_close.opacity=0; self.popup_close.disabled=True; self.layout.add_widget(self.popup_close)

        # Shop buttons - FIXED positions, no overlap!
        self.shop_buttons = []
        shop_items = [
            ("👑 GOLD Basket - 100 💰", "basket", "👑", 100),
            ("🌈 RAINBOW Basket - 200 💰", "basket", "🌈", 200),
            ("🌇 SUNSET Sky - 100 💰", "bg", "sunset", 100),
            ("🌊 OCEAN Sky - 150 💰", "bg", "ocean", 150),
            ("🍬 CANDY Sky - 200 💰", "bg", "candy", 200),
        ]
        y = 0.44
        for txt, typ, val, price in shop_items:
            b = Button(text=txt, font_size='16sp', background_color=(1,1,1,1), size_hint=(None,None), size=(320,40), pos_hint={'center_x':0.5,'center_y':y})
            b.bind(on_press=lambda x, t=typ, v=val, p=price: self.buy_item(t, v, p))
            b.opacity=0; b.disabled=True; self.layout.add_widget(b); self.shop_buttons.append(b); y -= 0.06

        # Leaderboard - Add Friend
        self.friend_input = TextInput(hint_text="Friend name...", font_size='18sp', size_hint=(None,None), size=(250,45), pos_hint={'center_x':0.4,'center_y':0.30}, multiline=False)
        self.friend_input.opacity=0; self.friend_input.disabled=True; self.layout.add_widget(self.friend_input)
        self.add_friend_btn = Button(text="➕ ADD FRIEND", font_size='16sp', background_color=(0,1,0,1), size_hint=(None,None), size=(170,45), pos_hint={'center_x':0.72,'center_y':0.30})
        self.add_friend_btn.bind(on_press=self.add_friend); self.add_friend_btn.opacity=0; self.add_friend_btn.disabled=True; self.layout.add_widget(self.add_friend_btn)

        Window.bind(on_touch_move=self.move_basket); Window.bind(on_touch_down=self.move_basket)
        # Show daily bonus popup if got it
        if self.daily_msg:
            Clock.schedule_once(lambda dt: self.show_daily(), 0.5)
        return self.layout

    def load_save(self):
        default = {"high":0, "coins":0, "basket":"🧺", "bg":"night", "last_day":"", "friends":[{"name":"You","score":0},{"name":"Ahmed","score":120},{"name":"Sara","score":90},{"name":"Omar","score":60}]}
        try:
            with open(os.path.join(self.user_data_dir, "save.json")) as f:
                d = json.load(f)
                for k,v in default.items():
                    if k not in d: d[k]=v
                return d
        except: return default

    def save_game(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self.save_file, 'w') as f: json.dump(self.save, f)
        except: pass

    def update_bg(self, *args):
        self.bg.size = Window.size; self.moon.pos = (Window.width-220, Window.height-220)

    def move_basket(self, window, touch):
        if self.playing:
            self.basket.center_x = touch.x
            if self.basket.x < 0: self.basket.x = 0
            if self.basket.right > Window.width: self.basket.right = Window.width
        return False

    def show_daily(self, *args):
        self.popup.text = f"🎉 WELCOME BACK!\n\n{self.daily_msg}\n\nCome back tomorrow for +50 more!"
        self.popup.opacity=1; self.popup_close.opacity=1; self.popup_close.disabled=False

    def show_tasks(self, *args):
        self.hide_popup()
        self.popup.text = f"🎯 TASKS - Like Roblox Quests!\n\n⭐ Catch 10 Stars = +50 💰\n🪙 Catch 3 Coins = +30 💰\n💣 NO Bombs = +100 💰\n🏆 Every 100 Score = +10 💰\n📅 Daily Login = +50 💰\n\nYour Coins: {self.save['coins']} 💰"
        self.popup.opacity=1; self.popup_close.opacity=1; self.popup_close.disabled=False

    def show_shop(self, *args):
        self.hide_popup()
        self.popup.text = f"🛒 SUPER SHOP!\nYour Coins: {self.save['coins']} 💰\nPick below:"
        self.popup.opacity=1; self.popup_close.opacity=1; self.popup_close.disabled=False
        for b in self.shop_buttons: b.opacity=1; b.disabled=False

    def show_leaderboard(self, *args):
        self.hide_popup()
        # Update your score in friends list
        for f in self.save["friends"]:
            if f["name"] == "You": f["score"] = self.save["high"]
        sorted_f = sorted(self.save["friends"], key=lambda x: x["score"], reverse=True)
        txt = "👫 LEADERBOARD - Who is Best?\n\n"
        medals = ["🥇","🥈","🥉","4.","5.","6.","7.","8."]
        for i, f in enumerate(sorted_f[:8]):
            m = medals[i] if i < len(medals) else f"{i+1}."
            txt += f"{m} {f['name']} - {f['score']} ⭐\n"
        txt += f"\nYour Coins: {self.save['coins']} 💰"
        self.popup.text = txt
        self.popup.opacity=1; self.popup_close.opacity=1; self.popup_close.disabled=False
        self.friend_input.opacity=1; self.friend_input.disabled=False
        self.add_friend_btn.opacity=1; self.add_friend_btn.disabled=False

    def add_friend(self, *args):
        name = self.friend_input.text.strip()
        if name:
            self.save["friends"].append({"name": name, "score": random.randint(20, 150)})
            self.save_game(); self.friend_input.text = ""
            self.show_leaderboard()

    def hide_popup(self, *args):
        self.popup.opacity=0; self.popup_close.opacity=0; self.popup_close.disabled=True
        for b in self.shop_buttons: b.opacity=0; b.disabled=True
        self.friend_input.opacity=0; self.friend_input.disabled=True
        self.add_friend_btn.opacity=0; self.add_friend_btn.disabled=True

    def buy_item(self, typ, val, price):
        if self.save["coins"] >= price:
            self.save["coins"] -= price
            if typ == "basket":
                self.save["basket"] = val; self.basket.text = val
            else:
                self.save["bg"] = val; self.bg_color.rgba = self.bg_colors[val]
            self.coins_label.text = f"💰 Coins: {self.save['coins']}"
            self.save_game()
            if self.s_buy: self.s_buy.play()
            self.popup.text = f"🎉 YOU BOUGHT IT!\n{val}\nCoins Left: {self.save['coins']} 💰"
        else:
            self.popup.text = f"😢 Not enough coins!\nNeed {price} 💰, You have {self.save['coins']} 💰\nPlay more!"

    def start_game(self, *args):
        self.score=0; self.lives=3; self.level=1; self.playing=True
        self.stars_this_game=0; self.coins_this_game=0; self.bombs_this_game=0
        self.title.opacity=0; self.subtitle.opacity=0; self.start_btn.opacity=0; self.start_btn.disabled=True
        self.hide_popup(); self.msg.text=""; self.update_labels()
        if self.music: self.music.play()
        Clock.unschedule(self.spawn_item); Clock.unschedule(self.move_items)
        Clock.schedule_interval(self.spawn_item, 0.8)
        Clock.schedule_interval(self.move_items, 1/60)

    def update_labels(self):
        self.score_label.text = f"⭐ Score: {self.score}"
        self.coins_label.text = f"💰 Coins: {self.save['coins']}"
        self.high_label.text = f"🏆 Best: {self.save['high']}"
        self.lives_label.text = "❤️"*self.lives + "🖤"*(3-self.lives)
        self.level_label.text = f"Level {self.level}"

    def spawn_item(self, dt):
        if not self.playing: return
        kind = random.choice(['star','star','star','coin','coin','heart','bomb'])
        texts = {'star':'⭐','coin':'🪙','heart':'❤️','bomb':'💣'}
        item = Button(text=texts[kind], font_size='48sp', background_color=(0,0,0,0), size_hint=(None,None), size=(80,80), pos_hint={'x': random.random()*0.85, 'top':1.0})
        item.kind = kind; item.speed = 3 + self.level * 0.8
        self.layout.add_widget(item); self.items.append(item)

    def move_items(self, dt):
        if not self.playing: return
        for item in self.items[:]:
            item.y -= item.speed
            if item.collide_widget(self.basket): self.catch(item); continue
            if item.y < 0:
                self.layout.remove_widget(item); self.items.remove(item)
                if item.kind in ['star','coin']: self.lose_life("Missed!")

    def catch(self, item):
        self.layout.remove_widget(item); self.items.remove(item)
        if item.kind == 'star':
            self.score+=10; self.stars_this_game+=1
            if self.s_ding: self.s_ding.play()
            self.msg.text="+10 ⭐"; self.msg.color=(1,1,0,1)
        elif item.kind == 'coin':
            self.score+=20; self.coins_this_game+=1
            if self.s_coin: self.s_coin.play()
            self.msg.text="+20 🪙"; self.msg.color=(1,0.8,0,1)
        elif item.kind == 'heart':
            if self.lives<3: self.lives+=1
            if self.s_heart: self.s_heart.play()
            self.msg.text="+1 LIFE ❤️"; self.msg.color=(1,0.3,0.5,1)
        elif item.kind == 'bomb':
            self.bombs_this_game+=1
            if self.s_boom: self.s_boom.play()
            self.msg.text="BOOM! 💣"; self.msg.color=(1,0,0,1)
            self.lose_life("Boom!"); return
        new_level = self.score // 50 + 1
        if new_level > self.level:
            self.level = new_level; self.msg.text=f"LEVEL {self.level}! FASTER! 🔥"
            Clock.unschedule(self.spawn_item); Clock.schedule_interval(self.spawn_item, max(0.3, 0.8 - self.level*0.08))
        self.update_labels()
        Clock.schedule_once(lambda dt: setattr(self.msg,'text',''), 0.8)

    def lose_life(self, reason=""):
        self.lives-=1; self.update_labels()
        if self.lives<=0: self.game_over()
        else: self.msg.text=f"Ouch! {reason} Lives: {self.lives}"; self.msg.color=(1,0,0,1)

    def game_over(self):
        self.playing=False
        Clock.unschedule(self.spawn_item); Clock.unschedule(self.move_items)
        for item in self.items[:]: self.layout.remove_widget(item)
        self.items.clear()
        if self.music: self.music.stop()
        if self.s_over: self.s_over.play()
        earned = 0; reward_text = ""
        if self.stars_this_game >= 10: earned+=50; reward_text+="\n⭐ 10 Stars: +50 💰"
        if self.coins_this_game >= 3: earned+=30; reward_text+="\n🪙 3 Coins: +30 💰"
        if self.bombs_this_game == 0 and self.score>0: earned+=100; reward_text+="\n💣 No Bomb: +100 💰"
        earned += (self.score // 100) * 10
        if self.score>=100: reward_text+=f"\n🏆 Score Bonus: +{(self.score//100)*10} 💰"
        self.save["coins"] += earned
        is_new_best = self.score > self.save["high"]
        if is_new_best: self.save["high"] = self.score
        for f in self.save["friends"]:
            if f["name"]=="You": f["score"]=self.save["high"]
        self.save_game(); self.update_labels()
        self.msg.text = f"GAME OVER! Score: {self.score}"
        self.title.text = "⭐ GAME OVER ⭐" if not is_new_best else "🏆 NEW BEST SCORE! 🏆"
        self.title.opacity=1
        self.subtitle.text = f"Score: {self.score} | Earned: +{earned} 💰{reward_text}\nBest: {self.save['high']} | Coins: {self.save['coins']}"
        self.subtitle.opacity=1
        self.start_btn.text="🔄 PLAY AGAIN!"; self.start_btn.opacity=1; self.start_btn.disabled=False

if __name__ == '__main__':
    StarGame().run()
