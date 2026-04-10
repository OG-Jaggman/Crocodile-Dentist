import random
import tkinter as tk


BG_COLOR = "#9ED9A3"
CROC_GREEN = "#3A9B57"
CROC_GREEN_DARK = "#27723E"
CROC_GREEN_LIGHT = "#63BE76"
MOUTH_RED = "#CF4C4C"
MOUTH_DARK = "#9E2E2E"
TOOTH_COLOR = "#FFF8EA"
TOOTH_SHADOW = "#D7D0C4"
TOOTH_PRESSED = "#CFC8BD"
DANGER_COLOR = "#D94B4B"
TEXT_COLOR = "#16301B"
SKY_ACCENT = "#CDEED1"


class CrocodileDentistGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Crocodile Dentist")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.canvas_width = 860
        self.canvas_height = 500
        self.total_teeth = 10
        self.top_tooth_ids: list[int] = []
        self.bottom_tooth_ids: list[int] = []
        self.tooth_hit_areas: dict[int, int] = {}
        self.pressed_teeth: set[int] = set()

        self.safe_presses = 0
        self.game_over = False
        self.losing_tooth = 0

        self.status_var = tk.StringVar()
        self.score_var = tk.StringVar()

        self._build_ui()
        self.reset_game()

    def _build_ui(self) -> None:
        title = tk.Label(
            self.root,
            text="Crocodile Dentist",
            font=("Comic Sans MS", 24, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            pady=10,
        )
        title.pack()

        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 12, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        self.status_label.pack()

        self.score_label = tk.Label(
            self.root,
            textvariable=self.score_var,
            font=("Segoe UI", 11),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            pady=4,
        )
        self.score_label.pack()

        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=SKY_ACCENT,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(padx=14, pady=(4, 10))

        self._draw_scene()

        controls = tk.Frame(self.root, bg=BG_COLOR)
        controls.pack(pady=(0, 16))

        self.reset_button = tk.Button(
            controls,
            text="New Game",
            font=("Segoe UI", 11, "bold"),
            bg=CROC_GREEN_DARK,
            fg="white",
            activebackground=CROC_GREEN,
            activeforeground="white",
            padx=18,
            pady=8,
            command=self.reset_game,
        )
        self.reset_button.pack()

    def _draw_scene(self) -> None:
        self.canvas.delete("all")

        self.canvas.create_rectangle(
            0, 350, self.canvas_width, self.canvas_height, fill="#8ACF8B", outline=""
        )
        self.canvas.create_oval(20, 355, 280, 510, fill="#78C77E", outline="")
        self.canvas.create_oval(540, 360, 840, 530, fill="#78C77E", outline="")

        self.canvas.create_polygon(
            120,
            185,
            640,
            130,
            760,
            170,
            720,
            205,
            635,
            222,
            220,
            248,
            fill=CROC_GREEN,
            outline=CROC_GREEN_DARK,
            width=4,
        )
        self.canvas.create_polygon(
            155,
            255,
            635,
            278,
            730,
            320,
            690,
            358,
            610,
            360,
            200,
            320,
            fill=CROC_GREEN_LIGHT,
            outline=CROC_GREEN_DARK,
            width=4,
        )

        self.canvas.create_polygon(
            200,
            240,
            635,
            220,
            710,
            245,
            625,
            282,
            220,
            295,
            160,
            270,
            fill=MOUTH_RED,
            outline=MOUTH_DARK,
            width=3,
        )
        self.canvas.create_polygon(
            228,
            250,
            622,
            235,
            672,
            248,
            615,
            270,
            240,
            279,
            196,
            264,
            fill="#F27B7B",
            outline="",
        )

        self.canvas.create_oval(
            170, 162, 262, 230, fill="white", outline=CROC_GREEN_DARK, width=3
        )
        self.canvas.create_oval(206, 186, 228, 208, fill="black", outline="black")
        self.canvas.create_oval(212, 191, 218, 197, fill="white", outline="")

        self.canvas.create_oval(
            660, 200, 676, 216, fill=CROC_GREEN_DARK, outline=CROC_GREEN_DARK
        )
        self.canvas.create_oval(
            690, 212, 706, 228, fill=CROC_GREEN_DARK, outline=CROC_GREEN_DARK
        )

        self.canvas.create_text(
            430,
            94,
            text="Click the crocodile's teeth",
            fill=TEXT_COLOR,
            font=("Segoe UI", 16, "bold"),
        )

        self._draw_teeth()

    def _draw_teeth(self) -> None:
        self.top_tooth_ids.clear()
        self.bottom_tooth_ids.clear()
        self.tooth_hit_areas.clear()

        left = 250
        top_y = 224
        bottom_y = 286
        tooth_width = 33
        tooth_gap = 5

        for index in range(self.total_teeth):
            x1 = left + index * (tooth_width + tooth_gap)
            x2 = x1 + tooth_width

            top_tooth = self.canvas.create_polygon(
                x1,
                top_y,
                x2,
                top_y,
                x2 - 5,
                top_y + 32,
                x1 + 5,
                top_y + 32,
                fill=TOOTH_COLOR,
                outline=TOOTH_SHADOW,
                width=2,
                tags=(f"tooth_{index}", "clickable_tooth"),
            )
            bottom_tooth = self.canvas.create_polygon(
                x1,
                bottom_y,
                x2,
                bottom_y,
                x2 - 5,
                bottom_y - 30,
                x1 + 5,
                bottom_y - 30,
                fill=TOOTH_COLOR,
                outline=TOOTH_SHADOW,
                width=2,
                tags=(f"tooth_{index}", "clickable_tooth"),
            )

            hit_area = self.canvas.create_rectangle(
                x1 - 2,
                top_y - 2,
                x2 + 2,
                bottom_y + 2,
                outline="",
                fill="",
                tags=(f"tooth_{index}", "clickable_tooth"),
            )

            self.top_tooth_ids.append(top_tooth)
            self.bottom_tooth_ids.append(bottom_tooth)
            self.tooth_hit_areas[index] = hit_area

            for tag in (f"tooth_{index}",):
                self.canvas.tag_bind(tag, "<Button-1>", lambda _event, idx=index: self.press_tooth(idx))
                self.canvas.tag_bind(tag, "<Enter>", lambda _event, idx=index: self._hover_tooth(idx, True))
                self.canvas.tag_bind(tag, "<Leave>", lambda _event, idx=index: self._hover_tooth(idx, False))

    def reset_game(self) -> None:
        self.safe_presses = 0
        self.game_over = False
        self.pressed_teeth.clear()
        self.losing_tooth = random.randrange(self.total_teeth)
        self.status_var.set("Press a tooth. One random tooth will snap the jaws shut.")
        self.score_var.set("Safe presses: 0")
        self.status_label.configure(fg=TEXT_COLOR)

        self._draw_scene()

    def _hover_tooth(self, index: int, entering: bool) -> None:
        if self.game_over or index in self.pressed_teeth:
            return

        fill = "#FFF0D2" if entering else TOOTH_COLOR
        self.canvas.itemconfigure(self.top_tooth_ids[index], fill=fill)
        self.canvas.itemconfigure(self.bottom_tooth_ids[index], fill=fill)

    def press_tooth(self, index: int) -> None:
        if self.game_over or index in self.pressed_teeth:
            return

        self.pressed_teeth.add(index)
        self.canvas.itemconfigure(self.top_tooth_ids[index], fill=TOOTH_PRESSED)
        self.canvas.itemconfigure(self.bottom_tooth_ids[index], fill=TOOTH_PRESSED)
        self.canvas.move(self.bottom_tooth_ids[index], 0, 10)

        if index == self.losing_tooth:
            self.end_game(index)
            return

        self.safe_presses += 1
        self.score_var.set(f"Safe presses: {self.safe_presses}")

        if len(self.pressed_teeth) == self.total_teeth - 1:
            self.status_var.set("Only one tooth left. This is the dangerous one.")
        else:
            self.status_var.set("Still safe. Try another tooth.")

    def end_game(self, losing_index: int) -> None:
        self.game_over = True
        self.status_var.set(f"Snap! Tooth {losing_index + 1} triggered the bite.")
        self.status_label.configure(fg=DANGER_COLOR)
        self.score_var.set(f"Final safe presses: {self.safe_presses}")

        self.canvas.itemconfigure(self.top_tooth_ids[losing_index], fill=DANGER_COLOR, outline=MOUTH_DARK)
        self.canvas.itemconfigure(self.bottom_tooth_ids[losing_index], fill=DANGER_COLOR, outline=MOUTH_DARK)

        self._close_jaw_animation(step=0)

    def _close_jaw_animation(self, step: int) -> None:
        top_offsets = [0, 8, 16, 24, 32, 38]
        bottom_offsets = [0, -6, -12, -18, -24, -28]

        if step == 0:
            self.closed_top = []
            self.closed_bottom = []
            for tooth_id in self.top_tooth_ids:
                self.closed_top.append(self.canvas.coords(tooth_id))
            for tooth_id in self.bottom_tooth_ids:
                self.closed_bottom.append(self.canvas.coords(tooth_id))

        for index, tooth_id in enumerate(self.top_tooth_ids):
            coords = self.closed_top[index]
            self.canvas.coords(
                tooth_id,
                coords[0],
                coords[1] + top_offsets[step],
                coords[2],
                coords[3] + top_offsets[step],
                coords[4],
                coords[5] + top_offsets[step],
                coords[6],
                coords[7] + top_offsets[step],
            )

        for index, tooth_id in enumerate(self.bottom_tooth_ids):
            coords = self.closed_bottom[index]
            self.canvas.coords(
                tooth_id,
                coords[0],
                coords[1] + bottom_offsets[step],
                coords[2],
                coords[3] + bottom_offsets[step],
                coords[4],
                coords[5] + bottom_offsets[step],
                coords[6],
                coords[7] + bottom_offsets[step],
            )

        self.canvas.move("current", 0, 0)

        if step < len(top_offsets) - 1:
            self.root.after(55, lambda: self._close_jaw_animation(step + 1))


def main() -> None:
    root = tk.Tk()
    CrocodileDentistGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
