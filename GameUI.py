import tkinter as tk
from tkinter import ttk
import random
import pyxel
import threading

# Function to safely start a Pyxel game in a separate thread
def start_game(game_class, exit_callback):
    def game_thread():
        game = game_class(exit_callback)
        pyxel.run(game.update, game.draw)
    thread = threading.Thread(target=game_thread)
    thread.start()

# Define the primary and secondary colors game
class ColorTheoryGame:
    def __init__(self, exit_callback):
        self.exit_callback = exit_callback
        pyxel.init(160, 120, title="Color Theory Game")
        pyxel.cls(0)  # Clear screen with black

        # Define primary and secondary colors using custom 24-bit RGB values
        self.primary_colors_rgb = [0xffff00, 0xff0000, 0x0000ff]  # Yellow, Red, Blue
        self.secondary_colors_rgb = [0x00ff00, 0xffa500, 0x8a2be2]  # Green, Orange, Violet

        # Assign the colors to Pyxel's palette
        pyxel.colors.from_list([0x000000] + self.primary_colors_rgb + self.secondary_colors_rgb)  # Start with black, then primary and secondary colors

        self.screen = 0  # Track which screen to display
        self.current_color = None
        self.correct_answer = None
        self.answer_selected = None
        self.success = 0
        self.failed = 0
        self.start_time = pyxel.frame_count

    def stop(self):
        pyxel.quit()
        self.exit_callback()

    def update(self):
        # Check for exit button press
        if pyxel.btnp(pyxel.KEY_E):
            self.stop()
            return

        # Key press handling to transition between screens
        if self.screen == 0 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.screen = 1
        elif self.screen == 1 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.screen = 2
        elif self.screen == 2 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.screen = 3
            self.start_time = pyxel.frame_count

        # Update logic for quiz
        if self.screen == 3:
            if (pyxel.frame_count - self.start_time) > 300:
                self.screen = 4
                self.start_time = pyxel.frame_count

        if self.screen == 4:
            if pyxel.btnp(pyxel.KEY_P):
                self.answer_selected = True
                self.check_answer()
                self.screen = 5  # Change to screen 5 for answer feedback
            elif pyxel.btnp(pyxel.KEY_S):
                self.answer_selected = False
                self.check_answer()
                self.screen = 5  # Change to screen 5 for answer feedback
        elif self.screen == 5 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.current_color = self.get_random_color()
            self.correct_answer = self.is_primary_color(self.current_color)
            self.answer_selected = None
            self.screen = 4
            self.start_time = pyxel.frame_count

        # Transition to quiz section if conditions are met (e.g., score threshold)
        if self.success >= 5 and self.screen == 4:
            self.screen = 6

    def draw(self):
        pyxel.cls(0)  # Clear screen with black

        if self.screen in [0, 1, 2]:
            self.draw_theory()
        elif self.screen in [3, 4, 5]:
            self.draw_quiz()

        # Draw the success and failed counts on the top right corner
        success_text = f"Success: {self.success}"
        failed_text = f"Failed: {self.failed}"
        success_x = 160 - len(success_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        failed_x = 160 - len(failed_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        pyxel.text(success_x, 5, success_text, pyxel.COLOR_WHITE)
        pyxel.text(failed_x, 15, failed_text, pyxel.COLOR_WHITE)

    def draw_theory(self):
        if self.screen == 0:
            self.draw_primary_colors()
        elif self.screen == 1:
            self.draw_secondary_colors()
        elif self.screen == 2:
            self.draw_complete_message()

    def draw_primary_colors(self):
        pyxel.cls(0)  # Clear screen with black
        
        # Display primary colors category
        pyxel.text(10, 5, "Primary Colors:", pyxel.COLOR_WHITE)
        for idx, color in enumerate(self.primary_colors_rgb):
            y = 20 + idx * 15  # Vertical position for each color box
            self.draw_color_box_theory(10, y, color)
            pyxel.text(35, y + 2, self.color_name(color), pyxel.COLOR_WHITE)

        pyxel.text(40, 110, "Press 'C' or 'SPACE' to continue", pyxel.COLOR_WHITE)

    def draw_secondary_colors(self):
        pyxel.cls(0)  # Clear screen with black
        
        # Display secondary colors category
        pyxel.text(10, 5, "Secondary Colors:", pyxel.COLOR_WHITE)
        for idx, color in enumerate(self.secondary_colors_rgb):
            y = 20 + idx * 15  # Vertical position for each color box
            self.draw_color_box_theory(10, y, color)
            pyxel.text(35, y + 2, self.color_name(color), pyxel.COLOR_WHITE)

        pyxel.text(40, 110, "Press 'C' or 'SPACE' to finish", pyxel.COLOR_WHITE)

    def draw_complete_message(self):
        pyxel.cls(0)  # Clear screen with black
        
        pyxel.text(50, 60, "End of practice!", pyxel.COLOR_WHITE)
        pyxel.text(40, 110, "Press 'C' or 'SPACE' to continue to quiz", pyxel.COLOR_WHITE)

    def draw_color_box_theory(self, x, y, color):
        # Specify the size of the box for the theory part
        box_width = 20  # Width of the box
        box_height = 10  # Height of the box

        # Draw a filled rectangle (box) at the specified position
        pyxel.rect(x, y, box_width, box_height, self.get_color_index(color))

    def draw_quiz(self):
        pyxel.cls(0)  # Clear screen with black

        if self.screen == 3:
            self.current_color = self.get_random_color()
            self.correct_answer = self.is_primary_color(self.current_color)
            self.answer_selected = None
            self.screen = 4
            self.start_time = pyxel.frame_count

        if self.screen == 4:
            # Display color challenge prompt
            challenge_text_1 = "Is this color"
            challenge_text_2 = "primary or secondary?"
            pyxel.text(20, 10, challenge_text_1, pyxel.COLOR_WHITE)
            pyxel.text(20, 20, challenge_text_2, pyxel.COLOR_WHITE)

            # Display key prompt for primary and secondary selection
            key_prompt_text_1 = "Press 'P' for Primary"
            key_prompt_text_2 = "Press 'S' for Secondary"
            pyxel.text(20, 30, key_prompt_text_1, pyxel.COLOR_WHITE)
            pyxel.text(20, 40, key_prompt_text_2, pyxel.COLOR_WHITE)

            # Display current color box
            self.draw_color_box_quiz()

        elif self.screen == 5:
            # Display answer feedback
            feedback_text = "Correct!" if self.answer_selected == self.correct_answer else "Incorrect!"
            pyxel.text(20, 30, feedback_text, pyxel.COLOR_GREEN if self.answer_selected == self.correct_answer else pyxel.COLOR_RED)

            continue_text = "Press 'C' or 'SPACE' to continue"
            pyxel.text(20, 50, continue_text, pyxel.COLOR_WHITE)

    def draw_color_box_quiz(self, x=44, y=None, color=None):
        if color is None:
            color = self.current_color
        if y is None:
            y = pyxel.height // 3 + 14  # Y-coordinate of the top-left corner of the box, adjusted down

        # Specify the size of the box for the quiz part
        box_width = 60  # Width of the box, made bigger
        box_height = 60  # Height of the box, made bigger

        # Draw a filled rectangle (box) at the specified position
        pyxel.rect(x, y, box_width, box_height, self.get_color_index(color))

    def check_answer(self):
        if self.answer_selected == self.correct_answer:
            self.success += 1
        else:
            self.failed += 1

    def get_random_color(self):
        return random.choice(self.primary_colors_rgb + self.secondary_colors_rgb)

    def is_primary_color(self, color):
        return color in self.primary_colors_rgb

    def get_color_index(self, color):
        # Return the index of the color in Pyxel's palette
        if color in self.primary_colors_rgb:
            return self.primary_colors_rgb.index(color) + 1  # Add 1 to skip black at index 0
        elif color in self.secondary_colors_rgb:
            return len(self.primary_colors_rgb) + self.secondary_colors_rgb.index(color) + 1  # Skip primary colors and black
        else:
            return 0  # Default to black if color not found

    def color_name(self, color):
        # Map the RGB values to their color names
        color_names = {
            0xffff00: "Yellow",
            0xff0000: "Red",
            0x0000ff: "Blue",
            0x00ff00: "Green",
            0xffa500: "Orange",
            0x8a2be2: "Violet"
        }
        return color_names.get(color, "Unknown")

# Define the mixing colors game
class ColorMixingGame:
    def __init__(self, exit_callback):
        self.exit_callback = exit_callback
        pyxel.init(160, 120, title="Primary Colors Mixing")
        pyxel.cls(0)  # Clear screen with black

        # Define primary and secondary colors using custom 24-bit RGB values
        self.colors_rgb = {
            "Yellow": 0xffff00,
            "Red": 0xff0000,
            "Blue": 0x0000ff,
            "Green": 0x00ff00,
            "Orange": 0xffa500,
            "Violet": 0x8a2be2
        }

        # Define mix examples for primary and secondary colors
        self.mix_examples = [
            ("Yellow", "Red", "Orange"),
            ("Yellow", "Blue", "Green"),
            ("Red", "Blue", "Violet"),
        ]

        # Assign the colors to Pyxel's palette
        pyxel.colors.from_list([0x000000] + list(self.colors_rgb.values()))  # Start with black, then all defined colors

        self.current_question = self.get_random_mixing_question()
        self.correct_answer = self.check_mixing(self.current_question)
        self.answer_selected = None
        self.success = 0
        self.failed = 0
        self.start_time = pyxel.frame_count

        self.screen = 0  # Track which screen to display

    def stop(self):
        pyxel.quit()
        self.exit_callback()

    def update(self):
        # Check for exit button press
        if pyxel.btnp(pyxel.KEY_E):
            self.stop()
            return

        # Key press handling to transition between screens
        if self.screen == 0 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.screen = 1

        # Quiz logic
        if self.screen == 1:
            if pyxel.btnp(pyxel.KEY_T):
                self.answer_selected = True
                self.check_answer()
                self.screen = 2  # Change to screen 2 for answer feedback
            elif pyxel.btnp(pyxel.KEY_F):
                self.answer_selected = False
                self.check_answer()
                self.screen = 2  # Change to screen 2 for answer feedback

        elif self.screen == 2 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.current_question = self.get_random_mixing_question()
            self.correct_answer = self.check_mixing(self.current_question)
            self.answer_selected = None
            self.screen = 1
            self.start_time = pyxel.frame_count

    def draw(self):
        pyxel.cls(0)  # Clear screen with black
        
        if self.screen == 0:
            self.draw_primary_color_mixing()
        elif self.screen == 1:
            self.draw_quiz()
        elif self.screen == 2:
            self.draw_feedback()

        # Draw the success and failed counts on the top right corner
        success_text = f"Success: {self.success}"
        failed_text = f"Failed: {self.failed}"
        success_x = 160 - len(success_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        failed_x = 160 - len(failed_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        pyxel.text(success_x, 5, success_text, pyxel.COLOR_WHITE)
        pyxel.text(failed_x, 15, failed_text, pyxel.COLOR_WHITE)

    def draw_primary_color_mixing(self):
        pyxel.text(10, 5, "Primary Colors Mixing", pyxel.COLOR_WHITE)
        y_offset = 20
        for color1, color2, result_color in self.mix_examples:
            self.draw_example(10, y_offset, color1, color2, result_color)
            y_offset += 20

        pyxel.text(10, 100, "Press 'C' or 'SPACE' to continue", pyxel.COLOR_WHITE)

    def draw_example(self, x, y, color1, color2, result_color):
        self.draw_color_box(x, y, self.colors_rgb[color1])
        pyxel.text(x + 25, y + 2, "+", pyxel.COLOR_WHITE)
        self.draw_color_box(x + 35, y, self.colors_rgb[color2])
        pyxel.text(x + 60, y + 2, "=", pyxel.COLOR_WHITE)
        self.draw_color_box(x + 70, y, self.colors_rgb[result_color])
        pyxel.text(x + 95, y + 2, result_color, pyxel.COLOR_WHITE)

    def draw_color_box(self, x, y, color):
        box_width = 20
        box_height = 10
        pyxel.rect(x, y, box_width, box_height, self.get_color_index(color))  # Use the color for the box

    def draw_quiz(self):
        # Centering the quiz text and color boxes
        prompt_lines = [
            f"Does {self.current_question[0].lower()} and {self.current_question[1].lower()} mix make violet?",
            "Press 'T' for True, 'F' for False"
        ]
        y_start = (pyxel.height - len(prompt_lines) * pyxel.FONT_HEIGHT) // 2 - 10
        for index, line in enumerate(prompt_lines):
            text_width = len(line) * pyxel.FONT_WIDTH
            x = (pyxel.width - text_width) // 2
            pyxel.text(x, y_start + index * pyxel.FONT_HEIGHT, line, pyxel.COLOR_WHITE)

        # Draw the color boxes for the current question
        y_boxes = y_start + len(prompt_lines) * pyxel.FONT_HEIGHT + 10
        self.draw_color_box(40, y_boxes, self.colors_rgb[self.current_question[0]])
        pyxel.text(65, y_boxes + 2, "+", pyxel.COLOR_WHITE)
        self.draw_color_box(75, y_boxes, self.colors_rgb[self.current_question[1]])
        pyxel.text(100, y_boxes + 2, "=", pyxel.COLOR_WHITE)
        pyxel.text(110, y_boxes + 2, "?", pyxel.COLOR_WHITE)

    def draw_feedback(self):
        # Centering the feedback text
        if self.answer_selected is not None:
            feedback_text = "Correct!" if self.answer_selected == self.correct_answer else "Incorrect!"
            pyxel.text(20, 40, feedback_text, pyxel.COLOR_GREEN if self.answer_selected == self.correct_answer else pyxel.COLOR_RED)
            pyxel.text(20, 60, "Press 'C' or 'SPACE' to continue", pyxel.COLOR_WHITE)

    def check_answer(self):
        if self.answer_selected == self.correct_answer:
            self.success += 1
        else:
            self.failed += 1

    def get_random_mixing_question(self):
        # Get random primary colors for mixing question
        color1, color2 = random.sample(list(self.colors_rgb.keys()), 2)
        return (color1, color2)

    def check_mixing(self, question):
        color1, color2 = question
        return (color1 == "Red" and color2 == "Blue") or (color1 == "Blue" and color2 == "Red")

    def get_color_index(self, color):
        # Return the index of the color in Pyxel's palette
        color_list = list(self.colors_rgb.values())
        if color in color_list:
            return color_list.index(color) + 1  # Add 1 to skip black at index 0
        else:
            return 0  # Default to black if color not found

# Define the warm and cool colors game
class WarmCoolColorTheoryGame:
    def __init__(self, exit_callback):
        self.exit_callback = exit_callback
        pyxel.init(160, 120, title="Warm and Cool Colors")
        pyxel.cls(0)  # Clear screen with black

        # Define warm and cool colors using custom 24-bit RGB values
        self.warm_colors_rgb = [0xc71585, 0xff0000, 0xff4500, 0xffa500, 0xffd700, 0xffff00]  # red-violet, red, red-orange, orange, yellow-orange, yellow
        self.cool_colors_rgb = [0x8a2be2, 0x4b0082, 0x0000ff, 0x00ced1, 0x008000, 0x9acd32]  # violet, blue-violet, blue, blue-green, green, yellow-green

        # Assign the colors to Pyxel's palette
        pyxel.colors.from_list([0x000000] + self.warm_colors_rgb + self.cool_colors_rgb)  # Start with black, then warm and cool colors

        self.screen = 0  # Track which screen to display
        self.quiz_game = None  # Placeholder for the quiz game instance

    def stop(self):
        pyxel.quit()
        self.exit_callback()

    def update(self):
        # Check for exit button press
        if pyxel.btnp(pyxel.KEY_E):
            self.stop()
            return

        # Key press handling to transition between screens
        if self.screen == 0 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.screen = 1
        elif self.screen == 1 and (pyxel.btnp(pyxel.KEY_C) or pyxel.btnp(pyxel.KEY_SPACE)):
            self.screen = 2
            self.quiz_game = QuizGame(self.stop)  # Pass the stop method as exit_callback

        # If quiz_game is initialized, update it
        if self.screen == 2 and self.quiz_game is not None:
            self.quiz_game.update()

    def draw(self):
        pyxel.cls(0)  # Clear screen with black

        if self.screen == 0:
            self.draw_warm_colors()
        elif self.screen == 1:
            self.draw_quiz_instructions()
        elif self.screen == 2 and self.quiz_game is not None:
            self.quiz_game.draw()

    def draw_warm_colors(self):
        pyxel.cls(0)  # Clear screen with black
        
        # Display warm colors category
        pyxel.text(10, 5, "Warm Colors:", pyxel.COLOR_WHITE)
        for idx, color in enumerate(self.warm_colors_rgb):
            y = 20 + idx * 15  # Vertical position for each color box
            self.draw_color_box(10, y, color)
            pyxel.text(35, y + 2, self.color_name(color), pyxel.COLOR_WHITE)

        pyxel.text(40, 110, "Press 'C' or 'SPACE' to continue", pyxel.COLOR_WHITE)

    def draw_quiz_instructions(self):
        pyxel.cls(0)  # Clear screen with black
        # Display quiz instructions
        pyxel.text(10, 5, "Quiz Instructions:", pyxel.COLOR_WHITE)
        pyxel.text(10, 20, "Press 'L' for Warm", pyxel.COLOR_WHITE)
        pyxel.text(10, 35, "Press 'W' for Cool", pyxel.COLOR_WHITE)
        pyxel.text(10, 110, "Press 'C' or 'SPACE' to start quiz", pyxel.COLOR_WHITE)

    def draw_color_box(self, x, y, color):
        box_width = 20
        box_height = 10
        pyxel.rect(x, y, box_width, box_height, self.get_color_index(color))  # Use the color for the box

    def get_color_index(self, color):
        # Return the index of the color in Pyxel's palette
        if color in self.warm_colors_rgb:
            return self.warm_colors_rgb.index(color) + 1  # Add 1 to skip black at index 0
        elif color in self.cool_colors_rgb:
            return len(self.warm_colors_rgb) + self.cool_colors_rgb.index(color) + 1  # Skip warm colors and black
        else:
            return 0  # Default to black if color not found

    def color_name(self, color):
        # Map the RGB values to their color names
        color_names = {
            0xff0000: "Red",
            0xff4500: "Red-Orange",
            0xffa500: "Orange",
            0xffd700: "Yellow-Orange",
            0xffff00: "Yellow",
            0xc71585: "Red-Violet",
            0x8a2be2: "Violet",
            0x4b0082: "Blue-Violet",
            0x0000ff: "Blue",
            0x00ced1: "Blue-Green",
            0x008000: "Green",
            0x9acd32: "Yellow-Green"
        }
        return color_names.get(color, "Unknown")

class QuizGame:
    def __init__(self, exit_callback):
        self.exit_callback = exit_callback
        pyxel.cls(0)  # Clear screen with black

        # Initialize the quiz game instance
        self.warm_colors_rgb = [0xff0000, 0xff4500, 0xffa500, 0xffd700, 0xffff00]  # red, red-orange, orange, yellow-orange, yellow
        self.cool_colors_rgb = [0x8a2be2, 0x4b0082, 0x0000ff, 0x00ced1, 0x008000]  # violet, blue-violet, blue, blue-green, green

        self.current_color = self.get_random_color()
        self.correct_answer = self.is_warm_color(self.current_color)
        self.answer_selected = None
        self.success = 0
        self.failed = 0  # Initialize failed count
        self.start_time = pyxel.frame_count

        self.screen = 0  # Track which screen to display

    def stop(self):
        pyxel.quit()
        self.exit_callback()

    def update(self):
        # Check for exit button press
        if pyxel.btnp(pyxel.KEY_E):
            self.stop()
            return

        # Key press handling to register user's input
        if self.screen == 0:
            if pyxel.btnp(pyxel.KEY_L):
                self.answer_selected = True
                self.check_answer()
                self.screen = 1  # Change to screen 1 for answer feedback
            elif pyxel.btnp(pyxel.KEY_W):
                self.answer_selected = False
                self.check_answer()
                self.screen = 1  # Change to screen 1 for answer feedback
        elif self.screen == 1 and pyxel.btnp(pyxel.KEY_SPACE):
            self.current_color = self.get_random_color()
            self.correct_answer = self.is_warm_color(self.current_color)
            self.answer_selected = None
            self.screen = 0
            self.start_time = pyxel.frame_count

    def draw(self):
        pyxel.cls(0)  # Clear screen with black
        
        if self.screen == 0:
            # Display color challenge prompt
            pyxel.text(20, 20, "Is this color warm or cool?", pyxel.COLOR_WHITE)
            pyxel.text(20, 40, "(Press 'L' for Warm, 'W' for Cool)", pyxel.COLOR_WHITE)

            # Display current color box
            self.draw_color_box()

        elif self.screen == 1:
            # Display answer feedback
            pyxel.cls(0)  # Clear screen with black
            if self.answer_selected is not None:
                if self.answer_selected == self.correct_answer:
                    pyxel.text(20, 40, "Correct!", pyxel.COLOR_GREEN)
                else:
                    pyxel.text(20, 40, "Incorrect!", pyxel.COLOR_RED)
                pyxel.text(20, 60, "Press SPACE to continue", pyxel.COLOR_WHITE)

        # Draw the score on the top right corner
        score_text = f"Score: {self.success}"
        score_x = 160 - len(score_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        pyxel.text(score_x, 5, score_text, pyxel.COLOR_WHITE)

    def draw_color_box(self):
        # Specify the position and size of the box
        x = 44  # X-coordinate of the top-left corner of the box
        y = pyxel.height // 3 + 14  # Y-coordinate of the top-left corner of the box, adjusted down
        box_width = 20  # Width of the box, made smaller
        box_height = 6  # Height of the box, made shorter

        # Draw a filled rectangle (box) at the specified position
        pyxel.rect(x, y, x + box_width, y + box_height, self.get_color_index(self.current_color))

    def check_answer(self):
        if self.answer_selected == self.correct_answer:
            self.success += 1
        else:
            self.failed += 1

    def get_random_color(self):
        return random.choice(self.warm_colors_rgb + self.cool_colors_rgb)

    def is_warm_color(self, color):
        return color in self.warm_colors_rgb

    def get_color_index(self, color):
        # Return the index of the color in Pyxel's palette
        if color in self.warm_colors_rgb:
            return self.warm_colors_rgb.index(color) + 1  # Add 1 to skip black at index 0
        elif color in self.cool_colors_rgb:
            return len(self.warm_colors_rgb) + self.cool_colors_rgb.index(color) + 1  # Skip warm colors and black
        else:
            return 0  # Default to black if color not found

    def color_name(self, color):
        # Map the RGB values to their color names
        color_names = {
            0xff0000: "Red",
            0xff4500: "Red-Orange",
            0xffa500: "Orange",
            0xffd700: "Yellow-Orange",
            0xffff00: "Yellow",
            0x8a2be2: "Violet",
            0x4b0082: "Blue-Violet",
            0x0000ff: "Blue",
            0x00ced1: "Blue-Green",
            0x008000: "Green",
            0x9acd32: "Yellow-Green"
        }
        return color_names.get(color, "Unknown")


class ColorTheoryGameB:
    def __init__(self):
        pyxel.init(160, 120, title="Color Theory Game")

        # Define warm and cool colors using custom 24-bit RGB values
        self.warm_colors_rgb = [0xc71585, 0xff0000, 0xff4500, 0xffa500, 0xffd700, 0xffff00]  # red-violet, red, red-orange, orange, yellow-orange, yellow
        self.cool_colors_rgb = [0x8a2be2, 0x4b0082, 0x0000ff, 0x00ced1, 0x008000, 0x9acd32]  # violet, blue-violet, blue, blue-green, green, yellow-green

        # Assign the colors to Pyxel's palette
        pyxel.colors.from_list([0x000000] + self.warm_colors_rgb + self.cool_colors_rgb)  # Start with black, then warm and cool colors

        self.screen = 0  # Track which screen to display
        self.quiz_game = None  # Placeholder for the quiz game instance

        pyxel.run(self.update, self.draw)

    def update(self):
        # Key press handling to transition between screens
        if self.screen == 0 and pyxel.btnp(pyxel.KEY_C):
            self.screen = 1
        elif self.screen == 1 and pyxel.btnp(pyxel.KEY_C):
            self.screen = 2
            self.quiz_game = QuizGame()

    def draw(self):
        if self.screen == 0:
            self.draw_warm_colors()
        elif self.screen == 1:
            self.draw_cool_colors()

    def draw_warm_colors(self):
        pyxel.cls(0)  # Clear screen with black
        
        # Display warm colors category
        pyxel.text(10, 5, "Warm Colors:", pyxel.COLOR_WHITE)
        for idx, color in enumerate(self.warm_colors_rgb):
            y = 20 + idx * 15  # Vertical position for each color box
            self.draw_color_box(10, y, color)
            pyxel.text(35, y + 2, self.color_name(color), pyxel.COLOR_WHITE)

        pyxel.text(40, 110, "Press 'C' to continue", pyxel.COLOR_WHITE)

    def draw_cool_colors(self):
        pyxel.cls(0)  # Clear screen with black
        
        # Display cool colors category
        pyxel.text(10, 5, "Cool Colors:", pyxel.COLOR_WHITE)
        for idx, color in enumerate(self.cool_colors_rgb):
            y = 20 + idx * 15  # Vertical position for each color box
            self.draw_color_box(10, y, color)
            pyxel.text(35, y + 2, self.color_name(color), pyxel.COLOR_WHITE)

        pyxel.text(40, 110, "Press 'C' to continue", pyxel.COLOR_WHITE)

    def draw_color_box(self, x, y, color):
        box_width = 20
        box_height = 10
        pyxel.rect(x, y, box_width, box_height, self.get_color_index(color))  # Use the color for the box

    def get_color_index(self, color):
        # Return the index of the color in Pyxel's palette
        if color in self.warm_colors_rgb:
            return self.warm_colors_rgb.index(color) + 1  # Add 1 to skip black at index 0
        elif color in self.cool_colors_rgb:
            return len(self.warm_colors_rgb) + self.cool_colors_rgb.index(color) + 1  # Skip warm colors and black
        else:
            return 0  # Default to black if color not found

    def color_name(self, color):
        # Map the RGB values to their color names
        color_names = {
            0xff0000: "Red",
            0xff4500: "Red-Orange",
            0xffa500: "Orange",
            0xffd700: "Yellow-Orange",
            0xffff00: "Yellow",
            0xc71585: "Red-Violet",
            0x8a2be2: "Violet",
            0x4b0082: "Blue-Violet",
            0x0000ff: "Blue",
            0x00ced1: "Blue-Green",
            0x008000: "Green",
            0x9acd32: "Yellow-Green"
        }
        return color_names.get(color, "Unknown")

class QuizGame:
    def __init__(self):
        # Initialize the quiz game instance
        self.warm_colors_rgb = [0xff0000, 0xff4500, 0xffa500, 0xffd700, 0xffff00]  # red, red-orange, orange, yellow-orange, yellow
        self.cool_colors_rgb = [0x8a2be2, 0x4b0082, 0x0000ff, 0x00ced1, 0x008000]  # violet, blue-violet, blue, blue-green, green

        self.current_color = self.get_random_color()
        self.correct_answer = self.is_warm_color(self.current_color)
        self.answer_selected = None
        self.score = 0  # Initialize score
        self.start_time = pyxel.frame_count

        self.screen = 0  # Track which screen to display

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.screen == 0 and (pyxel.frame_count - self.start_time) > 300:
            self.screen = 1
            self.start_time = pyxel.frame_count
        
        # Key press handling to register user's input
        if self.screen == 0:
            if pyxel.btnp(pyxel.KEY_L):
                self.answer_selected = True
                self.check_answer()
                self.screen = 1  # Change to screen 1 for answer feedback
            elif pyxel.btnp(pyxel.KEY_W):
                self.answer_selected = False
                self.check_answer()
                self.screen = 1  # Change to screen 1 for answer feedback
        elif self.screen == 1 and pyxel.btnp(pyxel.KEY_SPACE):
            self.current_color = self.get_random_color()
            self.correct_answer = self.is_warm_color(self.current_color)
            self.answer_selected = None
            self.screen = 0
            self.start_time = pyxel.frame_count

    def draw(self):
        pyxel.cls(0)  # Clear screen with black
        
        if self.screen == 0:
            # Display color challenge prompt
            pyxel.text(20, 20, "Is this color warm or cool?", pyxel.COLOR_WHITE)
            pyxel.text(20, 40, "(Press 'L' for Warm, 'W' for Cool)", pyxel.COLOR_WHITE)

            # Display current color box
            self.draw_color_box()

        elif self.screen == 1:
            # Display answer feedback
            pyxel.cls(0)  # Clear screen with black
            if self.answer_selected is not None:
                if self.answer_selected == self.correct_answer:
                    pyxel.text(20, 40, "Correct!", pyxel.COLOR_GREEN)
                else:
                    pyxel.text(20, 40, "Incorrect!", pyxel.COLOR_RED)
                pyxel.text(20, 60, "Press SPACE to continue", pyxel.COLOR_WHITE)

        # Draw the score on the top right corner
        score_text = f"Score: {self.score}"
        score_x = 160 - len(score_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        pyxel.text(score_x, 5, score_text, pyxel.COLOR_WHITE)

    def draw_color_box(self):
        # Specify the position and size of the box
        x = 44  # X-coordinate of the top-left corner of the box
        y = pyxel.height // 3 + 14  # Y-coordinate of the top-left corner of the box, adjusted down
        box_width = 20  # Width of the box, made smaller
        box_height = 6  # Height of the box, made shorter

        # Draw a filled rectangle (box) at the specified position
        pyxel.rect(x, y, x + box_width, y + box_height, self.get_color_index(self.current_color))

    def check_answer(self):
        if self.answer_selected == self.correct_answer:
            self.score += 1

    def get_random_color(self):
        return random.choice(self.warm_colors_rgb + self.cool_colors_rgb)

    def is_warm_color(self, color):
        return color in self.warm_colors_rgb

    def get_color_index(self, color):
        # Return the index of the color in Pyxel's palette
        if color in self.warm_colors_rgb:
            return self.warm_colors_rgb.index(color) + 1  # Add 1 to skip black at index 0
        elif color in self.cool_colors_rgb:
            return len(self.warm_colors_rgb) + self.cool_colors_rgb.index(color) + 1  # Skip warm colors and black
        else:
            return 0  # Default to black if color not found
    def __init__(self, exit_callback):
        self.exit_callback = exit_callback
        pyxel.cls(0)  # Clear screen with black

        # Initialize the quiz game instance
        self.warm_colors_rgb = [0xff0000, 0xff4500, 0xffa500, 0xffd700, 0xffff00]  # red, red-orange, orange, yellow-orange, yellow
        self.cool_colors_rgb = [0x8a2be2, 0x4b0082, 0x0000ff, 0x00ced1, 0x008000]  # violet, blue-violet, blue, blue-green, green

        self.current_color = self.get_random_color()
        self.correct_answer = self.is_warm_color(self.current_color)
        self.answer_selected = None
        self.success = 0
        self.failed = 0  # Initialize failed count
        self.start_time = pyxel.frame_count

        self.screen = 0  # Track which screen to display

    def stop(self):
        pyxel.quit()
        self.exit_callback()

    def update(self):
        # Check for exit button press
        if pyxel.btnp(pyxel.KEY_E):
            self.stop()
            return

        # Key press handling to register user's input
        if self.screen == 0 and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_C)):
            self.screen = 1  # Move to the warm colors explanation screen
        elif self.screen == 1 and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_C)):
            self.screen = 2  # Move to the cool colors explanation screen
        elif self.screen == 2 and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_C)):
            self.screen = 3  # Move to the quiz screen

        # Quiz logic
        if self.screen == 3:
            if pyxel.btnp(pyxel.KEY_L):
                self.answer_selected = True
                self.check_answer()
                self.screen = 4  # Change to screen 4 for answer feedback
            elif pyxel.btnp(pyxel.KEY_W):
                self.answer_selected = False
                self.check_answer()
                self.screen = 4  # Change to screen 4 for answer feedback

        elif self.screen == 4 and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_C)):
            self.current_color = self.get_random_color()
            self.correct_answer = self.is_warm_color(self.current_color)
            self.answer_selected = None
            self.screen = 3  # Return to the quiz screen

    def draw(self):
        pyxel.cls(0)  # Clear screen with black

        if self.screen == 0:
            self.draw_warm_colors()
        elif self.screen == 1:
            self.draw_cool_colors()
        elif self.screen == 2:
            self.draw_quiz_instructions()
        elif self.screen == 3:
            self.draw_quiz()
        elif self.screen == 4:
            self.draw_feedback()

        # Draw the success and failed counts on the top right corner
        success_text = f"Success: {self.success}"
        failed_text = f"Failed: {self.failed}"
        success_x = 160 - len(success_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        failed_x = 160 - len(failed_text) * pyxel.FONT_WIDTH - 5  # Adjusted to ensure it fits within the screen
        pyxel.text(success_x, 5, success_text, pyxel.COLOR_WHITE)
        pyxel.text(failed_x, 15, failed_text, pyxel.COLOR_WHITE)

    def draw_warm_colors(self):
        pyxel.cls(0)  # Clear screen with black
        # Display warm colors category
        pyxel.text(10, 5, "Warm Colors:", pyxel.COLOR_WHITE)
        for idx, color in enumerate(self.warm_colors_rgb):
            y = 20 + idx * 15  # Vertical position for each color box
            self.draw_color_box(10, y, color)
            pyxel.text(35, y + 2, self.color_name(color), pyxel.COLOR_WHITE)
        pyxel.text(10, 110, "Press 'C' or 'SPACE' to continue", pyxel.COLOR_WHITE)

    def draw_cool_colors(self):
        pyxel.cls(0)  # Clear screen with black
        # Display cool colors category
        pyxel.text(10, 5, "Cool Colors:", pyxel.COLOR_WHITE)
        for idx, color in enumerate(self.cool_colors_rgb):
            y = 20 + idx * 15  # Vertical position for each color box
            self.draw_color_box(10, y, color)
            pyxel.text(35, y + 2, self.color_name(color), pyxel.COLOR_WHITE)
        pyxel.text(10, 110, "Press 'C' or 'SPACE' to continue", pyxel.COLOR_WHITE)

    def draw_quiz_instructions(self):
        pyxel.cls(0)  # Clear screen with black
        # Display quiz instructions
        pyxel.text(10, 5, "Quiz Instructions:", pyxel.COLOR_WHITE)
        pyxel.text(10, 20, "Press 'L' for Warm", pyxel.COLOR_WHITE)
        pyxel.text(10, 35, "Press 'W' for Cool", pyxel.COLOR_WHITE)
        pyxel.text(10, 110, "Press 'C' or 'SPACE' to start quiz", pyxel.COLOR_WHITE)

    def draw_quiz(self):
        # Centering the quiz text and color boxes
        prompt_lines = [
            "Is this color warm or cool?",
            "(Press 'L' for Warm, 'W' for Cool)"
        ]
        y_start = (pyxel.height - len(prompt_lines) * pyxel.FONT_HEIGHT) // 2 - 10
        for index, line in enumerate(prompt_lines):
            text_width = len(line) * pyxel.FONT_WIDTH
            x = (pyxel.width - text_width) // 2
            pyxel.text(x, y_start + index * pyxel.FONT_HEIGHT, line, pyxel.COLOR_WHITE)

        # Draw the color box for the current question
        y_boxes = y_start + len(prompt_lines) * pyxel.FONT_HEIGHT + 10
        self.draw_color_box(44, y_boxes, self.current_color)

    def draw_feedback(self):
        # Centering the feedback text
        if self.answer_selected is not None:
            feedback_text = "Correct!" if self.answer_selected == self.correct_answer else "Incorrect!"
            pyxel.text(20, 40, feedback_text, pyxel.COLOR_GREEN if self.answer_selected == self.correct_answer else pyxel.COLOR_RED)
            pyxel.text(20, 60, "Press 'C' or 'SPACE' to continue", pyxel.COLOR_WHITE)

    def draw_color_box(self, x, y, color):
        box_width = 20
        box_height = 10
        pyxel.rect(x, y, box_width, box_height, self.get_color_index(color))  # Use the color for the box

    def check_answer(self):
        if self.answer_selected == self.correct_answer:
            self.success += 1
        else:
            self.failed += 1

    def get_random_color(self):
        return random.choice(self.warm_colors_rgb + self.cool_colors_rgb)

    def is_warm_color(self, color):
        return color in self.warm_colors_rgb

    def get_color_index(self, color):
        # Return the index of the color in Pyxel's palette
        if color in self.warm_colors_rgb:
            return self.warm_colors_rgb.index(color) + 1  # Add 1 to skip black at index 0
        elif color in self.cool_colors_rgb:
            return len(self.warm_colors_rgb) + self.cool_colors_rgb.index(color) + 1  # Skip warm colors and black
        else:
            return 0  # Default to black if color not found

    def color_name(self, color):
        # Map the RGB values to their color names
        color_names = {
            0xff0000: "Red",
            0xff4500: "Red-Orange",
            0xffa500: "Orange",
            0xffd700: "Yellow-Orange",
            0xffff00: "Yellow",
            0x8a2be2: "Violet",
            0x4b0082: "Blue-Violet",
            0x0000ff: "Blue",
            0x00ced1: "Blue-Green",
            0x008000: "Green",
            0x9acd32: "Yellow-Green"
        }
        return color_names.get(color, "Unknown")

# Main application window
def main():
    root = tk.Tk()
    root.title("Color Games Dashboard")
    
    def start_color_theory_game():
        root.withdraw()
        start_game(ColorTheoryGame, root.deiconify)
    
    def start_color_mixing_game():
        root.withdraw()
        start_game(ColorMixingGame, root.deiconify)
    
    def start_warm_cool_game():
        root.withdraw()
        start_game(WarmCoolColorTheoryGame, root.deiconify)
    
    label = tk.Label(root, text="Select a game stage:", font=("Arial", 16))
    label.pack(pady=20)
    
    stage1_button = ttk.Button(root, text="1 - Primary and Secondary Colors", command=start_color_theory_game)
    stage1_button.pack(pady=10)
    
    stage2_button = ttk.Button(root, text="2 - Mixing Colors", command=start_color_mixing_game)
    stage2_button.pack(pady=10)
    
    stage3_button = ttk.Button(root, text="3 - Warm and Cool Colors", command=start_warm_cool_game)
    stage3_button.pack(pady=10)
    
    exit_button = ttk.Button(root, text="4 - Exit", command=root.quit)
    exit_button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()
