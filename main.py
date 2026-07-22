import json
import random
import tkinter as tk
from tkinter import messagebox, ttk

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎉 Interactive Colorful Quiz Application")
        self.geometry("700x500")
        self.resizable(False, False)
        self.config(bg="#282c34")  # dark background

        # Load questions
        with open("questions_large.json", "r") as file:
            self.all_questions = json.load(file)["questions"]

        self.score = 0
        self.question_index = 0
        self.time_per_question = 20  # seconds
        self.timer_id = None

        self.selected_difficulty = tk.StringVar(value="easy")

        self.font_heading = ("Comic Sans MS", 20, "bold")
        self.font_text = ("Arial", 14)
        self.font_option = ("Arial", 13)

        self.create_widgets()

    def create_widgets(self):
        # Difficulty selection frame
        self.diff_frame = tk.Frame(self, bg="#282c34")
        self.diff_frame.pack(pady=30)

        tk.Label(self.diff_frame, text="Select Difficulty Level:", font=self.font_heading, fg="white", bg="#282c34").pack(pady=10)
        difficulties = ["easy", "medium", "hard"]
        for diff in difficulties:
            tk.Radiobutton(
                self.diff_frame,
                text=diff.title(),
                variable=self.selected_difficulty,
                value=diff,
                font=self.font_text,
                fg="white",
                bg="#282c34",
                selectcolor="#61afef"
            ).pack(side="left", padx=20)

        # Start button
        self.start_button = tk.Button(self.diff_frame, text="Start Quiz", font=("Comic Sans MS", 16, "bold"), bg="#61afef", fg="black", relief="ridge", command=self.start_quiz)
        self.start_button.pack(pady=25)

        # Quiz frame (hidden initially)
        self.quiz_frame = tk.Frame(self, bg="#21252b")
        self.quiz_frame.pack(fill="both", expand=True)
        self.quiz_frame.pack_forget()

        # Question label
        self.question_label = tk.Label(self.quiz_frame, text="", font=self.font_heading, fg="#98c379", bg="#21252b", wraplength=650, justify="center")
        self.question_label.pack(pady=(40,20))

        # Options (radio buttons)
        self.user_answer = tk.StringVar()
        self.option_buttons = []
        for _ in range(4):
            rb = tk.Radiobutton(
                self.quiz_frame,
                text="",
                variable=self.user_answer,
                value="",
                font=self.font_option,
                fg="#bbc2cf",
                bg="#21252b",
                selectcolor="#56b6c2",
                activebackground="#21252b",
                activeforeground="white",
                anchor="w",
                padx=20
            )
            rb.pack(fill="x", pady=7, padx=100)
            self.option_buttons.append(rb)

        # Timer label (blinking effect)
        self.timer_label = tk.Label(self.quiz_frame, text="", font=("Helvetica", 14, "bold"), fg="#e06c75", bg="#21252b")
        self.timer_label.pack(pady=10)

        # Progress bar for quiz progress
        self.progress = ttk.Progressbar(self.quiz_frame, length=600, maximum=100, mode='determinate')
        self.progress.pack(pady=5)

        # Submit button
        self.submit_button = tk.Button(self.quiz_frame, text="Submit Answer", font=("Comic Sans MS", 14, "bold"), bg="#61afef", fg="black", relief="ridge", command=self.submit_answer)
        self.submit_button.pack(pady=15)

        # Score label (shows at end)
        self.score_label = tk.Label(self, text="", font=self.font_heading, fg="#98c379", bg="#282c34")

    def start_quiz(self):
        difficulty = self.selected_difficulty.get()
        self.questions = [q for q in self.all_questions if q["difficulty"] == difficulty]
        random.shuffle(self.questions)

        self.score = 0
        self.question_index = 0
        self.progress["value"] = 0

        # Hide difficulty frame
        self.diff_frame.pack_forget()
        self.score_label.pack_forget()
        self.quiz_frame.pack(fill="both", expand=True)

        self.show_question()

    def show_question(self):
        if self.question_index >= len(self.questions):
            self.end_quiz()
            return

        question = self.questions[self.question_index]
        self.question_label.config(text=f"Q{self.question_index + 1}: {question['question']}")
        self.user_answer.set(None)

        for idx, option in enumerate(question["options"]):
            self.option_buttons[idx].config(text=option, value=option)

        self.remaining_time = self.time_per_question
        self.update_timer()
        self.blink = True
        self.blink_timer()

        # Update progress bar
        progress_percent = ((self.question_index) / len(self.questions)) * 100
        self.progress["value"] = progress_percent

    def update_timer(self):
        self.timer_label.config(text=f"⏳ Time Left: {self.remaining_time}s")
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_id = self.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's up!", "You ran out of time for this question!")
            self.submit_answer(timeout=True)

    def blink_timer(self):
        if self.blink:
            current_color = self.timer_label.cget("fg")
            new_color = "#e06c75" if current_color == "#282c34" else "#282c34"
            self.timer_label.config(fg=new_color)
            self.after(600, self.blink_timer)
        else:
            self.timer_label.config(fg="#e06c75")  # reset color

    def submit_answer(self, timeout=False):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.blink = False

        if not timeout:
            selected = self.user_answer.get()
            if not selected:
                messagebox.showwarning("No option selected", "Please select an answer before submitting.")
                self.update_timer()  # restart timer for this question
                self.blink = True
                self.blink_timer()
                return
            correct = self.questions[self.question_index]["answer"]
            if selected == correct:
                self.score += 1
                messagebox.showinfo("Correct!", "Your answer is correct.")
            else:
                messagebox.showinfo("Wrong!", f"Incorrect answer.\nCorrect answer: {correct}")
        else:
            # Timeout counts as incorrect answer
            messagebox.showinfo("Timeout", "You did not answer in time.")

        self.question_index += 1
        self.show_question()

    def end_quiz(self):
        self.quiz_frame.pack_forget()
        self.score_label.config(text=f"🎉 Quiz Completed! Your score: {self.score} / {len(self.questions)}")
        self.score_label.pack(pady=30)
        self.progress["value"] = 100

        # Show Restart button in difficulty frame
        self.start_button.config(text="Restart Quiz")
        self.diff_frame.pack(pady=30)

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
