import os
import json
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter.ttk import Button, Label, Frame
import pygame

# Global configuration
AUDIO_EXT = ".wav"
EMOTIONS = ["Neutral", "Suprise", "Angry", "Sad", "Happy"]
STRENGTHS = ["HIGH", "LOW"]
TEST_TYPES = ["naturallness", "EDT", "EIT", "EST", "EDiT"]
RESULTS_DIR = "results"
DATA_DIR = "data"


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()

    def play(self, file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()


class EvaluationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subjective Evaluation Tool")
        self.audio_player = AudioPlayer()
        self.run_name = ""
        self.results = {}
        self.current_audio = None
        self.current_test_index = 0

        self.setup_gui()

    def setup_gui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.pack(padx=20, pady=20)

        self.intro_label = Label(self.main_frame, text="Enter a run name:")
        self.intro_label.pack()

        self.run_name_entry = tk.Entry(self.main_frame)
        self.run_name_entry.pack()

        self.start_button = Button(self.main_frame, text="Start", command=self.start_experiment)
        self.start_button.pack(pady=10)

    def start_experiment(self):
        self.run_name = self.run_name_entry.get().strip()
        if not self.run_name:
            messagebox.showerror("Error", "Please enter a run name.")
            return

        os.makedirs(RESULTS_DIR, exist_ok=True)
        self.main_frame.destroy()
        self.results = {"run_name": self.run_name, "responses": {}}
        self.load_test_sequence()

    def load_test_sequence(self):
        self.test_functions = [
            self.run_naturalness_test,
            self.run_edt_test,
            self.run_eit_test,
            self.run_est_test,
            self.run_edit_test,
            self.finish_experiment
        ]
        self.run_next_test()

    def run_next_test(self):
        if self.current_test_index < len(self.test_functions):
            test_func = self.test_functions[self.current_test_index]
            self.current_test_index += 1
            test_func()
        else:
            self.finish_experiment()

    def run_naturalness_test(self):
        messagebox.showinfo(
            "MOS Naturalness Test",
            "This is a MOS naturalness test. You will be listening to audio samples and rate how human-like they sound.\n\n"
            "0 = extremely robotic, 5 = indistinguishable from a human."
        )
        test_dir = os.path.join(DATA_DIR, "naturallness")
        audios = []
        for model in os.listdir(test_dir):
            model_path = os.path.join(test_dir, model)
            if os.path.isdir(model_path):
                for file in os.listdir(model_path):
                    if file.endswith(AUDIO_EXT):
                        audios.append((os.path.join(model_path, file), model))
        random.shuffle(audios)
        self.current_test_audios = audios
        self.current_audio_index = 0
        self.results["responses"]["naturalness"] = []
        self.show_naturalness_audio()

    def show_naturalness_audio(self):
        if self.current_audio_index >= len(self.current_test_audios):
            self.run_next_test()
            return

        audio_path, model = self.current_test_audios[self.current_audio_index]

        def rate_audio(score):
            self.results["responses"]["naturalness"].append({
                "file": os.path.basename(audio_path),
                "model": model,
                "score": score
            })
            self.current_audio_index += 1
            self.audio_player.stop()
            score_window.destroy()
            self.show_naturalness_audio()

        score_window = tk.Toplevel(self.root)
        score_window.title("Rate Naturalness")

        Label(score_window, text="Step 1: Press 'Play' to listen to the audio 1–2 times").pack(pady=(10, 5))
        Button(score_window, text="Play", command=lambda: self.audio_player.play(audio_path)).pack(pady=(0, 10))

        separator = tk.Frame(score_window, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        Label(score_window, text="Step 2: Rate the audio's naturalness by clicking one of the buttons below").pack(pady=(5, 10))

        rating_frame = Frame(score_window)
        rating_frame.pack(pady=5)

        descriptions = [
            "0 = Noise or Extremely robotic",
            "1 = Very robotic",
            "2 = Robotic",
            "3 = Natural, but noisy or distorted",
            "4 = Natural, but you think it is still not a real voice",
            "5 = Very natural, human voice"
        ]

        for i in range(6):
            row = Frame(rating_frame)
            row.pack(anchor="w", pady=2)
            Button(row, text=str(i), width=5, command=lambda s=i: rate_audio(s)).pack(side="left", padx=(0, 10))
            Label(row, text=descriptions[i], anchor="w", justify="left").pack(side="left")

    def run_edt_test(self):
        self.results["responses"]["EDT"] = []
        self.run_next_test()

    def run_eit_test(self):
        self.results["responses"]["EIT"] = []
        self.run_next_test()

    def run_est_test(self):
        self.results["responses"]["EST"] = []
        self.run_next_test()

    def run_edit_test(self):
        self.results["responses"]["EDiT"] = []
        self.run_next_test()

    def finish_experiment(self):
        result_path = os.path.join(RESULTS_DIR, f"{self.run_name}_naturalness.json")
        with open(result_path, "w") as f:
            json.dump(self.results, f, indent=4)
        messagebox.showinfo("Finished", f"Experiment finished! Results saved to {result_path}.\n"
                                        f"Now proceed to the 2nd experiemnt by running `python app_part2_EDT.py`")
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = EvaluationApp(root)
    root.mainloop()
