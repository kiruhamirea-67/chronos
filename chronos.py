import random
import json
import os
import tkinter as tk
from tkinter import messagebox

RECORDS_FILE = "records.json"

# ---------- БАЗА ВОПРОСОВ (15 событий) ----------
QUESTIONS = [
    {"event": "Крещение Руси князем Владимиром", "year": 988,
     "options": [862, 988, 1054, 1147],
     "clues": ["Событие связано с религией.", "Главный герой — князь, внук княгини Ольги.",
               "Жителей Киева крестили в Днепре."]},
    {"event": "Ледовое побоище на Чудском озере", "year": 1242,
     "options": [1223, 1240, 1242, 1380],
     "clues": ["Сражение произошло на льду.", "Противник — немецкие рыцари.",
               "Русским войском командовал Александр Невский."]},
    {"event": "Куликовская битва", "year": 1380,
     "options": [1242, 1380, 1480, 1552],
     "clues": ["Битва на поле у Дона.", "Поединок Пересвета и Челубея.",
               "Князь Дмитрий получил после неё прозвище «Донской»."]},
    {"event": "Стояние на реке Угре — конец ордынского ига", "year": 1480,
     "options": [1380, 1480, 1497, 1547],
     "clues": ["Битвы фактически не было.", "Два войска стояли на разных берегах реки.",
               "Правил Иван III."]},
    {"event": "Венчание Ивана IV на царство", "year": 1547,
     "options": [1533, 1547, 1565, 1584],
     "clues": ["Впервые в истории Руси правитель принял этот титул.",
               "Правителю было 16 лет.", "Позже его прозвали Грозным."]},
    {"event": "Освобождение Москвы ополчением Минина и Пожарского", "year": 1612,
     "options": [1598, 1605, 1612, 1613],
     "clues": ["Конец Смутного времени.", "Ополчение собиралось в Нижнем Новгороде.",
               "В честь события отмечается День народного единства."]},
    {"event": "Основание Санкт-Петербурга", "year": 1703,
     "options": [1700, 1703, 1709, 1721],
     "clues": ["Город на Неве.", "Начался с крепости на Заячьем острове.",
               "Основатель — Пётр I."]},
    {"event": "Полтавская битва", "year": 1709,
     "options": [1700, 1709, 1714, 1721],
     "clues": ["Сражение Северной войны.", "Противник — шведский король Карл XII.",
               "«И грянул бой, Полтавский бой!» — А. С. Пушкин."]},
    {"event": "Бородинское сражение", "year": 1812,
     "options": [1805, 1807, 1812, 1814],
     "clues": ["Крупнейшее сражение Отечественной войны.", "Противник — Наполеон.",
               "Русской армией командовал Кутузов."]},
    {"event": "Восстание декабристов на Сенатской площади", "year": 1825,
     "options": [1801, 1825, 1830, 1861],
     "clues": ["Произошло в декабре.", "Участники — офицеры-дворяне.",
               "Пятеро руководителей были казнены."]},
    {"event": "Отмена крепостного права", "year": 1861,
     "options": [1825, 1855, 1861, 1881],
     "clues": ["Реформа Александра II.", "Крестьяне получили личную свободу.",
               "Императора за неё прозвали Освободителем."]},
    {"event": "Октябрьская революция", "year": 1917,
     "options": [1905, 1914, 1917, 1922],
     "clues": ["Штурм Зимнего дворца.", "Залп крейсера «Аврора».",
               "К власти пришли большевики во главе с Лениным."]},
    {"event": "Начало Великой Отечественной войны", "year": 1941,
     "options": [1939, 1941, 1942, 1945],
     "clues": ["22 июня.", "Нападение без объявления войны.",
               "«Вставай, страна огромная!»"]},
    {"event": "Первый полёт человека в космос", "year": 1961,
     "options": [1957, 1961, 1963, 1965],
     "clues": ["12 апреля.", "Корабль «Восток-1».", "«Поехали!» — Юрий Гагарин."]},
    {"event": "Распад СССР", "year": 1991,
     "options": [1985, 1989, 1991, 1993],
     "clues": ["Беловежские соглашения.", "Над Кремлём спущен красный флаг.",
               "Первый и последний президент СССР — Горбачёв."]},
]


# ---------- ИГРОВАЯ ЛОГИКА (как в консольной версии) ----------
def date_hunt_points(guess, year):
    """Очки за «Охоту за датами» в зависимости от промаха."""
    diff = abs(guess - year)
    if diff == 0:
        return 20, diff
    if diff <= 5:
        return 10, diff
    if diff <= 25:
        return 5, diff
    if diff <= 100:
        return 1, diff
    return 0, diff


def black_box_match(answer, q):
    """Проверка ответа в «Чёрном ящике» по ключевым словам события или году."""
    answer = answer.strip().lower()
    if not answer:
        return False
    keywords = [w.lower().strip(".,—«»") for w in q["event"].split() if len(w) > 4]
    keywords.append(str(q["year"]))
    return any(k[:5] in answer or answer in k for k in keywords)


def load_records():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_record(name, mode, score):
    records = load_records()
    records.append({"name": name, "mode": mode, "score": score})
    records.sort(key=lambda r: r["score"], reverse=True)
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records[:10], f, ensure_ascii=False, indent=2)


def rank(pct):
    if pct >= 80:
        return "Академик истории"
    if pct >= 50:
        return "Знаток"
    return "Начинающий летописец"


# ---------- ОФОРМЛЕНИЕ ----------
BG = "#1e1b2e"        # фон окна
PANEL = "#2a2640"     # панели
ACCENT = "#f2c14e"    # золотой акцент
TEXT = "#f5f1e8"      # основной текст
MUTED = "#a9a3c2"     # второстепенный текст
OK = "#58c27d"
BAD = "#e5604f"
FONT = "Georgia"


class ChronosApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ХРОНОС — историческая игра")
        self.geometry("760x600")
        self.minsize(680, 540)
        self.configure(bg=BG)
        self.player = "Игрок"
        self.frame = None
        self.show(StartScreen)

    def show(self, screen_cls, **kwargs):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = screen_cls(self, **kwargs)
        self.frame.pack(fill="both", expand=True)


def title_label(parent, text, size=26):
    return tk.Label(parent, text=text, font=(FONT, size, "bold"), fg=ACCENT, bg=BG)


class FlatButton(tk.Label):
    """Кнопка на основе Label — красится одинаково на Windows, macOS и Linux
    (родной tk.Button на macOS игнорирует bg)."""

    def __init__(self, parent, text, cmd, color=ACCENT, fg=BG, width=24):
        super().__init__(parent, text=text, font=(FONT, 13, "bold"), bg=color, fg=fg,
                         padx=12, pady=8, width=width, cursor="hand2")
        self.cmd = cmd
        self.color = color
        self.fg_color = fg
        self.enabled = True
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", lambda e: self.enabled and self.config(bg=TEXT, fg=BG))
        self.bind("<Leave>", lambda e: self.enabled and self.config(bg=self.color, fg=self.fg_color))

    def _click(self, _event=None):
        if self.enabled and self.cmd:
            self.cmd()

    def set_color(self, color):
        self.color = color
        self.config(bg=color)

    def disable(self):
        self.enabled = False
        self.config(cursor="arrow")

    def set_text(self, text, cmd=None):
        self.config(text=text)
        if cmd is not None:
            self.cmd = cmd

    def invoke(self):
        self._click()


def make_button(parent, text, cmd, color=ACCENT, fg=BG, width=24):
    return FlatButton(parent, text, cmd, color=color, fg=fg, width=width)


# ---------- ЭКРАН: СТАРТ ----------
class StartScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app = app
        title_label(self, "⏳ ХРОНОС").pack(pady=(50, 4))
        tk.Label(self, text="историческая игра", font=(FONT, 14, "italic"),
                 fg=MUTED, bg=BG).pack()

        tk.Label(self, text="Как тебя зовут?", font=(FONT, 13), fg=TEXT, bg=BG).pack(pady=(40, 6))
        self.name_var = tk.StringVar(value=app.player)
        entry = tk.Entry(self, textvariable=self.name_var, font=(FONT, 14), justify="center",
                         bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat", width=24,
                         highlightthickness=0)
        entry.pack(ipady=6)
        entry.focus_set()
        entry.bind("<Return>", lambda e: self.go())

        make_button(self, "Начать", self.go).pack(pady=(30, 8))
        make_button(self, "Таблица рекордов", lambda: app.show(RecordsScreen),
                    color=PANEL, fg=TEXT).pack()

    def go(self):
        self.app.player = self.name_var.get().strip() or "Игрок"
        self.app.show(MenuScreen)


# ---------- ЭКРАН: МЕНЮ ----------
class MenuScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app = app
        title_label(self, f"Привет, {app.player}!", 22).pack(pady=(30, 4))
        tk.Label(self, text="Выбери режим игры", font=(FONT, 13), fg=MUTED, bg=BG).pack(pady=(0, 18))

        modes = [
            ("📜  Викторина", "4 варианта года, 10 очков за ответ", "quiz"),
            ("🎯  Охота за датами", "введи точный год: 20 очков — в яблочко", "hunt"),
            ("📦  Чёрный ящик", "угадай событие по подсказкам: до 30 очков", "box"),
        ]
        for name, desc, key in modes:
            card = tk.Frame(self, bg=PANEL, padx=16, pady=10, cursor="hand2")
            card.pack(fill="x", padx=120, pady=6)
            tk.Label(card, text=name, font=(FONT, 15, "bold"), fg=ACCENT, bg=PANEL,
                     anchor="w").pack(fill="x")
            tk.Label(card, text=desc, font=(FONT, 11), fg=MUTED, bg=PANEL, anchor="w").pack(fill="x")
            for w in (card, *card.winfo_children()):
                w.bind("<Button-1>", lambda e, k=key: self.pick(k))

        tk.Label(self, text="Количество вопросов:", font=(FONT, 12), fg=TEXT, bg=BG).pack(pady=(14, 2))
        self.count = tk.Scale(self, from_=10, to=len(QUESTIONS), orient="horizontal", length=240,
                              bg=BG, fg=TEXT, troughcolor=PANEL, highlightthickness=0,
                              activebackground=ACCENT, font=(FONT, 11), bd=0)
        self.count.set(10)
        self.count.pack()

        make_button(self, "← Назад", lambda: app.show(StartScreen), color=PANEL, fg=TEXT,
                    width=12).pack(pady=12)

    def pick(self, key):
        n = int(self.count.get())
        qs = random.sample(QUESTIONS, n)
        screen = {"quiz": QuizScreen, "hunt": HuntScreen, "box": BoxScreen}[key]
        self.app.show(screen, questions=qs)


# ---------- БАЗОВЫЙ ИГРОВОЙ ЭКРАН ----------
class GameScreen(tk.Frame):
    MODE = ""
    MAX_PER_Q = 10

    def __init__(self, app, questions):
        super().__init__(app, bg=BG)
        self.app = app
        self.questions = questions
        self.idx = 0
        self.score = 0

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=30, pady=(18, 6))
        tk.Label(top, text=self.MODE, font=(FONT, 16, "bold"), fg=ACCENT, bg=BG).pack(side="left")
        self.score_lbl = tk.Label(top, text="Очки: 0", font=(FONT, 13), fg=TEXT, bg=BG)
        self.score_lbl.pack(side="right")

        self.progress = tk.Canvas(self, height=8, bg=PANEL, highlightthickness=0)
        self.progress.pack(fill="x", padx=30)

        self.counter = tk.Label(self, text="", font=(FONT, 11), fg=MUTED, bg=BG)
        self.counter.pack(pady=(6, 0))

        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True, padx=30, pady=10)

        self.feedback = tk.Label(self, text="", font=(FONT, 13, "bold"), fg=TEXT, bg=BG,
                                 wraplength=640)
        self.feedback.pack(pady=(0, 6))
        self.next_btn = make_button(self, "Дальше →", self.next_question, width=14)
        self.render()

    def clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def update_header(self):
        self.score_lbl.config(text=f"Очки: {self.score}")
        self.counter.config(text=f"Вопрос {self.idx + 1} из {len(self.questions)}")
        self.progress.delete("all")
        self.progress.update_idletasks()
        w = self.progress.winfo_width() or 700
        self.progress.create_rectangle(0, 0, w * self.idx / len(self.questions), 8,
                                       fill=ACCENT, outline="")

    def show_feedback(self, text, good):
        self.feedback.config(text=text, fg=OK if good else BAD)
        self.next_btn.pack(pady=(0, 16))
        self.bind_all("<Return>", lambda e: self.next_question())

    def next_question(self):
        self.unbind_all("<Return>")
        self.next_btn.pack_forget()
        self.feedback.config(text="")
        self.idx += 1
        if self.idx >= len(self.questions):
            self.finish()
        else:
            self.render()

    def finish(self):
        save_record(self.app.player, self.MODE, self.score)
        self.app.show(ResultScreen, mode=self.MODE, score=self.score,
                      max_score=self.MAX_PER_Q * len(self.questions))

    @property
    def q(self):
        return self.questions[self.idx]

    def render(self):
        raise NotImplementedError


# ---------- РЕЖИМ 1: ВИКТОРИНА ----------
class QuizScreen(GameScreen):
    MODE = "Викторина"
    MAX_PER_Q = 10

    def render(self):
        self.clear_body()
        self.update_header()
        tk.Label(self.body, text=self.q["event"], font=(FONT, 18, "bold"), fg=TEXT, bg=BG,
                 wraplength=640, justify="center").pack(pady=(20, 24))
        opts = self.q["options"][:]
        random.shuffle(opts)
        grid = tk.Frame(self.body, bg=BG)
        grid.pack()
        self.buttons = []
        for i, year in enumerate(opts):
            b = make_button(grid, str(year), lambda y=year: self.answer(y), color=PANEL,
                            fg=TEXT, width=14)
            b.grid(row=i // 2, column=i % 2, padx=10, pady=8)
            self.buttons.append((b, year))

    def answer(self, year):
        for b, y in self.buttons:
            b.disable()
            if y == self.q["year"]:
                b.set_color(OK)
            elif y == year:
                b.set_color(BAD)
        if year == self.q["year"]:
            self.score += 10
            self.show_feedback("Верно! +10", True)
        else:
            self.show_feedback(f"Неверно. Правильный ответ: {self.q['year']}", False)
        self.score_lbl.config(text=f"Очки: {self.score}")


# ---------- РЕЖИМ 2: ОХОТА ЗА ДАТАМИ ----------
class HuntScreen(GameScreen):
    MODE = "Охота за датами"
    MAX_PER_Q = 20

    def render(self):
        self.clear_body()
        self.update_header()
        tk.Label(self.body, text=self.q["event"], font=(FONT, 18, "bold"), fg=TEXT, bg=BG,
                 wraplength=640, justify="center").pack(pady=(20, 10))
        tk.Label(self.body, text="В каком году это произошло?", font=(FONT, 12), fg=MUTED,
                 bg=BG).pack()
        self.var = tk.StringVar()
        self.entry = tk.Entry(self.body, textvariable=self.var, font=(FONT, 20), width=8,
                              justify="center", bg=PANEL, fg=TEXT, insertbackground=TEXT,
                              relief="flat", highlightthickness=0,
                              disabledbackground=PANEL, disabledforeground=MUTED)
        self.entry.pack(pady=14, ipady=6)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.answer())
        self.ok_btn = make_button(self.body, "Ответить", self.answer, width=14)
        self.ok_btn.pack()
        tk.Label(self.body, text="Точно — 20 • до 5 лет — 10 • до 25 лет — 5 • до 100 лет — 1",
                 font=(FONT, 10), fg=MUTED, bg=BG).pack(pady=(14, 0))

    def answer(self):
        s = self.var.get().strip()
        if not s.isdigit() or not (0 <= int(s) <= 2100):
            messagebox.showwarning("Хронос", "Введи год числом от 0 до 2100.")
            return
        pts, diff = date_hunt_points(int(s), self.q["year"])
        self.score += pts
        self.entry.config(state="disabled")
        self.ok_btn.disable()
        if diff == 0:
            self.show_feedback("В яблочко! +20", True)
        else:
            self.show_feedback(f"Правильно: {self.q['year']} (промах на {diff} лет). +{pts}",
                               pts > 0)
        self.score_lbl.config(text=f"Очки: {self.score}")


# ---------- РЕЖИМ 3: ЧЁРНЫЙ ЯЩИК ----------
class BoxScreen(GameScreen):
    MODE = "Чёрный ящик"
    MAX_PER_Q = 30

    def render(self):
        self.clear_body()
        self.update_header()
        self.clue_n = 0
        tk.Label(self.body, text="📦", font=(FONT, 36), fg=ACCENT, bg=BG).pack(pady=(2, 0))
        tk.Label(self.body, text="В ящике — историческое событие. Что это?",
                 font=(FONT, 13), fg=MUTED, bg=BG).pack()
        self.clues_box = tk.Frame(self.body, bg=PANEL, padx=14, pady=10)
        self.clues_box.pack(fill="x", pady=10)

        row = tk.Frame(self.body, bg=BG)
        row.pack()
        self.var = tk.StringVar()
        self.entry = tk.Entry(row, textvariable=self.var, font=(FONT, 14), width=26,
                              bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat",
                              highlightthickness=0, disabledbackground=PANEL,
                              disabledforeground=MUTED)
        self.entry.pack(side="left", ipady=5, padx=(0, 8))
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.answer())
        self.ok_btn = make_button(row, "Ответить", self.answer, width=10)
        self.ok_btn.pack(side="left")
        self.hint_btn = make_button(self.body, "Ещё подсказка", self.show_clue, color=PANEL,
                                    fg=TEXT, width=16)
        self.hint_btn.pack(pady=8)
        tk.Label(self.body,
                 text="Ответ — ключевое слово события или год.  С 1-й подсказки — 30 • со 2-й — 20 • с 3-й — 10",
                 font=(FONT, 10), fg=MUTED, bg=BG, wraplength=640).pack()
        self.show_clue()

    def show_clue(self):
        if self.clue_n >= len(self.q["clues"]):
            return
        self.clue_n += 1
        tk.Label(self.clues_box, text=f"{self.clue_n}. {self.q['clues'][self.clue_n - 1]}",
                 font=(FONT, 13), fg=TEXT, bg=PANEL, anchor="w", wraplength=600,
                 justify="left").pack(fill="x", pady=2)
        if self.clue_n == len(self.q["clues"]):
            self.hint_btn.set_text("Открыть ящик", self.reveal)

    def lock(self):
        self.entry.config(state="disabled")
        self.ok_btn.disable()
        self.hint_btn.disable()

    def answer(self):
        if black_box_match(self.var.get(), self.q):
            pts = {1: 30, 2: 20, 3: 10}[self.clue_n]
            self.score += pts
            self.lock()
            self.show_feedback(f"Верно! «{self.q['event']}» ({self.q['year']}). +{pts}", True)
            self.score_lbl.config(text=f"Очки: {self.score}")
        else:
            self.var.set("")
            if self.clue_n < len(self.q["clues"]):
                self.show_clue()
                self.feedback.config(text="Мимо — вот следующая подсказка", fg=BAD)
            else:
                self.reveal()

    def reveal(self):
        self.lock()
        self.show_feedback(f"Открываем ящик: «{self.q['event']}», {self.q['year']} год.", False)


# ---------- ЭКРАН: РЕЗУЛЬТАТ ----------
class ResultScreen(tk.Frame):
    def __init__(self, app, mode, score, max_score):
        super().__init__(app, bg=BG)
        pct = score / max_score * 100 if max_score else 0
        title_label(self, "Игра окончена", 24).pack(pady=(60, 6))
        tk.Label(self, text=f"Режим «{mode}»", font=(FONT, 13), fg=MUTED, bg=BG).pack()
        tk.Label(self, text=f"{score}", font=(FONT, 56, "bold"), fg=TEXT, bg=BG).pack(pady=(20, 0))
        tk.Label(self, text=f"очков из {max_score}  ({pct:.0f}%)", font=(FONT, 13),
                 fg=MUTED, bg=BG).pack()
        tk.Label(self, text=rank(pct), font=(FONT, 18, "bold"), fg=ACCENT, bg=BG).pack(pady=18)
        make_button(self, "Играть ещё", lambda: app.show(MenuScreen)).pack(pady=(10, 8))
        make_button(self, "Таблица рекордов", lambda: app.show(RecordsScreen),
                    color=PANEL, fg=TEXT).pack()


# ---------- ЭКРАН: РЕКОРДЫ ----------
class RecordsScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        title_label(self, "🏆 Таблица рекордов", 22).pack(pady=(40, 16))
        records = load_records()
        table = tk.Frame(self, bg=PANEL, padx=20, pady=12)
        table.pack(padx=80, fill="x")
        if not records:
            tk.Label(table, text="Пока пусто — стань первым!", font=(FONT, 13), fg=MUTED,
                     bg=PANEL).pack()
        else:
            for col, head in enumerate(("#", "Игрок", "Режим", "Очки")):
                tk.Label(table, text=head, font=(FONT, 12, "bold"), fg=ACCENT, bg=PANEL,
                         anchor="w").grid(row=0, column=col, sticky="w", padx=8, pady=(0, 6))
            for i, r in enumerate(records, 1):
                vals = (str(i), r["name"], r["mode"], str(r["score"]))
                for col, v in enumerate(vals):
                    tk.Label(table, text=v, font=(FONT, 12), fg=TEXT, bg=PANEL,
                             anchor="w").grid(row=i, column=col, sticky="w", padx=8, pady=2)
            table.grid_columnconfigure(1, weight=1)
            table.grid_columnconfigure(2, weight=1)
        make_button(self, "← В меню", lambda: app.show(MenuScreen), color=PANEL, fg=TEXT,
                    width=14).pack(pady=24)


if __name__ == "__main__":
    ChronosApp().mainloop()