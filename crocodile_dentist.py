import random
from pathlib import Path
import tkinter as tk


BG_COLOR = "#9ED9A3"
TEXT_COLOR = "#16301B"
SKY_ACCENT = "#CDEED1"
TOOTH_GLOW = "#FFF0D2"
TOOTH_PRESSED = "#B9B1A6"
DANGER_COLOR = "#D94B4B"


class CrocodileDentistGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Crocodile Dentist")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.image_path = Path(__file__).with_name("Crocodile-Dentist-Teeth.png")
        self.croc_image = self._load_game_image()
        self.canvas_width = self.croc_image.width() + 80
        self.canvas_height = self.croc_image.height() + 110

        self.total_teeth = 10
        self.tooth_shapes: dict[int, tuple[int, int]] = {}
        self.pressed_teeth: set[int] = set()
        self.safe_presses = 0
        self.game_over = False
        self.losing_tooth = 0

        self.status_var = tk.StringVar()
        self.score_var = tk.StringVar()

        self._build_ui()
        self.reset_game()

    # Tooth positions are normalized against the source PNG so they still line up
    # after the displayed image is cropped and optionally subsampled.
    TOOTH_SPECS = [
        {"center": (0.30, 0.65), "size": (0.048, 0.090)},
        {"center": (0.36, 0.68), "size": (0.048, 0.090)},
        {"center": (0.42, 0.70), "size": (0.044, 0.090)},
        {"center": (0.48, 0.71), "size": (0.046, 0.094)},
        {"center": (0.54, 0.70), "size": (0.050, 0.098)},
        {"center": (0.60, 0.68), "size": (0.052, 0.102)},
        {"center": (0.66, 0.65), "size": (0.050, 0.098)},
        {"center": (0.40, 0.60), "size": (0.046, 0.094)},
        {"center": (0.50, 0.58), "size": (0.044, 0.090)},
        {"center": (0.60, 0.60), "size": (0.038, 0.082)},
    ]
    TOOTH_HITBOX_SCALE = 0.75

    def _load_game_image(self) -> tk.PhotoImage:
        source_image = tk.PhotoImage(file=str(self.image_path))

        max_width = 900
        max_height = 520
        scale = max(
            1,
            (source_image.width() + max_width - 1) // max_width,
            (source_image.height() + max_height - 1) // max_height,
        )

        if scale > 1:
            image = source_image.subsample(scale, scale)
        else:
            image = source_image

        return image

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

        # Removed New Game button

    def _draw_scene(self) -> None:
        self.canvas.delete("all")
        self.tooth_shapes.clear()

        center_x = self.canvas_width // 2
        image_y = 18

        self.canvas.create_text(
            center_x,
            18,
            text="Click the teeth on the crocodile",
            fill=TEXT_COLOR,
            font=("Segoe UI", 16, "bold"),
        )

        self.canvas.create_image(center_x, image_y + 18, image=self.croc_image, anchor="n")
        self._init_tooth_positions(center_x, image_y + 18)

    def _init_tooth_positions(self, center_x: int, image_y: int) -> None:
        image_left = center_x - (self.croc_image.width() // 2)
        image_top = image_y

        for index, spec in enumerate(self.TOOTH_SPECS):
            center_x_pos = image_left + (self.croc_image.width() * spec["center"][0])
            center_y_pos = image_top + (self.croc_image.height() * spec["center"][1])
            tooth_width = max(10, int(self.croc_image.width() * spec["size"][0] * self.TOOTH_HITBOX_SCALE))
            tooth_height = max(14, int(self.croc_image.height() * spec["size"][1] * self.TOOTH_HITBOX_SCALE))

            top_tooth = self.canvas.create_oval(
                center_x_pos - tooth_width / 2,
                center_y_pos - tooth_height / 2,
                center_x_pos + tooth_width / 2,
                center_y_pos + tooth_height / 2,
                outline="",
                width=0,
                fill="",
                tags=(f"tooth_{index}", "clickable_tooth"),
            )
            bottom_tooth = self.canvas.create_oval(
                center_x_pos - tooth_width / 2,
                center_y_pos - tooth_height / 2,
                center_x_pos + tooth_width / 2,
                center_y_pos + tooth_height / 2,
                outline="",
                fill="",
                tags=(f"tooth_{index}", "clickable_tooth"),
            )

            self.tooth_shapes[index] = (top_tooth, bottom_tooth)

            self.canvas.tag_bind(
                f"tooth_{index}",
                "<Button-1>",
                lambda _event, idx=index: self.press_tooth(idx),
            )
            self.canvas.tag_bind(
                f"tooth_{index}",
                "<Enter>",
                lambda _event, idx=index: self._hover_tooth(idx, True),
            )
            self.canvas.tag_bind(
                f"tooth_{index}",
                "<Leave>",
                lambda _event, idx=index: self._hover_tooth(idx, False),
            )

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

        fill = TOOTH_GLOW if entering else ""
        for shape_id in self.tooth_shapes[index]:
            self.canvas.itemconfigure(
                shape_id,
                fill=fill,
                stipple="gray25" if entering else "",
                outline="#F6EFE3" if entering else "",
            )

    def press_tooth(self, index: int) -> None:
        if self.game_over or index in self.pressed_teeth:
            return

        self.pressed_teeth.add(index)
        top_tooth, bottom_tooth = self.tooth_shapes[index]
        self.canvas.itemconfigure(top_tooth, fill=TOOTH_PRESSED, stipple="gray50", outline="")
        self.canvas.itemconfigure(bottom_tooth, fill=TOOTH_PRESSED, stipple="gray50", outline="")
        self.canvas.move(top_tooth, 0, 2)
        self.canvas.move(bottom_tooth, 0, 2)

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

        top_tooth, bottom_tooth = self.tooth_shapes[losing_index]
        self.canvas.itemconfigure(top_tooth, fill=DANGER_COLOR, stipple="gray50", outline="")
        self.canvas.itemconfigure(bottom_tooth, fill=DANGER_COLOR, stipple="gray50", outline="")

        self._close_jaw_animation(step=0)

    def _close_jaw_animation(self, step: int) -> None:
        offsets = [0, 3, 6, 9, 12, 14]

        if step == 0:
            self.base_coords: dict[int, tuple[list[float], list[float]]] = {}
            for index, (top_tooth, bottom_tooth) in self.tooth_shapes.items():
                self.base_coords[index] = (
                    self.canvas.coords(top_tooth),
                    self.canvas.coords(bottom_tooth),
                )

        offset = offsets[step]

        for index, (top_tooth, bottom_tooth) in self.tooth_shapes.items():
            top_coords, bottom_coords = self.base_coords[index]
            self.canvas.coords(
                top_tooth,
                top_coords[0],
                top_coords[1] + offset,
                top_coords[2],
                top_coords[3] + offset,
                top_coords[4],
                top_coords[5] + offset,
                top_coords[6],
                top_coords[7] + offset,
            )
            self.canvas.coords(
                bottom_tooth,
                bottom_coords[0],
                bottom_coords[1] - offset,
                bottom_coords[2],
                bottom_coords[3] - offset,
                bottom_coords[4],
                bottom_coords[5] - offset,
                bottom_coords[6],
                bottom_coords[7] - offset,
            )

        if step < len(offsets) - 1:
            self.root.after(55, lambda: self._close_jaw_animation(step + 1))
        else:
            # Reset game after animation
            self.root.after(1000, self.reset_game)


def main() -> None:
    root = tk.Tk()
    CrocodileDentistGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
