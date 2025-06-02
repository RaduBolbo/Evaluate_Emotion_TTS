import os
import json
import random
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Button, Label, Frame
import pygame

AUDIO_EXT = ".wav"
DATA_DIR = "data"
RESULTS_DIR = "results"


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()

    def play(self, file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()


class ESTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EST Evaluation Tool")
        self.audio_player = AudioPlayer()
        self.results = {"responses": []}
        self.est_pairs = []
        self.current_index = 0
        self.setup_gui()

    def setup_gui(self):
        self.frame = Frame(self.root)
        self.frame.pack(padx=20, pady=20)
        Label(self.frame, text="Enter run name:").pack()
        self.entry = tk.Entry(self.frame)
        self.entry.pack()
        Button(self.frame, text="Start EST Evaluation", command=self.start_est_test).pack(pady=10)

    def start_est_test(self):
        self.run_name = self.entry.get().strip()
        if not self.run_name:
            messagebox.showerror("Error", "Please enter a run name.")
            return
        os.makedirs(RESULTS_DIR, exist_ok=True)
        self.frame.destroy()
        self.load_est_data()
        if not self.est_pairs:
            messagebox.showerror("Error", "No EST pairs found.")
            self.root.quit()
        else:
            self.show_next_pair()

    def load_est_data(self):
        est_dir = os.path.join(DATA_DIR, "EST")
        for model in os.listdir(est_dir):
            model_path = os.path.join(est_dir, model)
            if not os.path.isdir(model_path):
                continue

            files_by_id = {}
            for fname in os.listdir(model_path):
                if not fname.endswith(AUDIO_EXT) or "STRENGTH" not in fname:
                    continue
                parts = fname.replace(".wav", "").split("_")
                if "STRENGTH" not in parts:
                    continue
                idx = parts.index("STRENGTH")
                strength = parts[idx + 1]
                pair_id = "_".join(parts[:idx])  # everything before STRENGTH
                files_by_id.setdefault(pair_id, {})[strength] = fname

            for pair_id, pair_files in files_by_id.items():
                if "HIGH" in pair_files and "LOW" in pair_files:
                    emotion = self.extract_emotion_from_filename(pair_files["HIGH"])
                    self.est_pairs.append({
                        "model": model,
                        "pair_id": pair_id,
                        "emotion": emotion,
                        "file_high": os.path.join(model_path, pair_files["HIGH"]),
                        "file_low": os.path.join(model_path, pair_files["LOW"])
                    })

        random.shuffle(self.est_pairs)

    def extract_emotion_from_filename(self, fname):
        parts = fname.replace(".wav", "").split("_")
        try:
            idx = parts.index("emotion")
            return parts[idx + 1]
        except Exception:
            return "Unknown"

    def record_answer(self, selected_label):
        pair = self.est_pairs[self.current_index]
        correct = (selected_label == self.current_order["correct_choice"])

        self.results["responses"].append({
            "model": pair["model"],
            "pair_id": pair["pair_id"],
            "emotion": pair["emotion"],
            "selected": selected_label,
            "correct": correct,
            "file1": os.path.basename(self.current_order["file1"]),
            "file2": os.path.basename(self.current_order["file2"]),
            "correct_choice": self.current_order["correct_choice"]
        })

        self.audio_player.stop()
        self.window.destroy()
        self.current_index += 1
        self.show_next_pair()

    '''
    def show_next_pair(self):
        if self.current_index >= len(self.est_pairs):
            self.finish_experiment()
            return

        pair = self.est_pairs[self.current_index]

        order = random.choice(["HL", "LH"])
        if order == "HL":
            file1, file2 = pair["file_high"], pair["file_low"]
            correct_choice = "First"  # HIGH is first
        else:
            file1, file2 = pair["file_low"], pair["file_high"]
            correct_choice = "Second"  # HIGH is second

        self.current_order = {
            "file1": file1,
            "file2": file2,
            "correct_choice": correct_choice
        }

        self.window = tk.Toplevel(self.root)
        self.window.title(f"EST Evaluation - {self.current_index + 1}/{len(self.est_pairs)}")

        Label(self.window, text=f"Which clip expresses the emotion '{pair['emotion']}' stronger?").pack(pady=10)

        Button(self.window, text="Play First Audio", command=lambda: self.audio_player.play(file1)).pack(pady=5)
        Button(self.window, text="Play Second Audio", command=lambda: self.audio_player.play(file2)).pack(pady=5)

        Button(self.window, text="First Audio is stronger", command=lambda: self.record_answer("First")).pack(pady=5)
        Button(self.window, text="Second Audio is stronger", command=lambda: self.record_answer("Second")).pack(pady=5)
    '''

    def show_next_pair(self):
        if self.current_index >= len(self.est_pairs):
            self.finish_experiment()
            return

        pair = self.est_pairs[self.current_index]

        order = random.choice(["HL", "LH"])
        if order == "HL":
            file1, file2 = pair["file_high"], pair["file_low"]
            correct_choice = "First"
        else:
            file1, file2 = pair["file_low"], pair["file_high"]
            correct_choice = "Second"

        self.current_order = {
            "file1": file1,
            "file2": file2,
            "correct_choice": correct_choice
        }

        self.window = tk.Toplevel(self.root)
        self.window.title(f"EST Evaluation - {self.current_index + 1}/{len(self.est_pairs)}")

        main_frame = Frame(self.window)
        main_frame.pack(padx=20, pady=20)

        # Step 1
        Label(main_frame, text=f"Step 1: Listen to both {pair['emotion'].upper()} audio samples", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        Button(main_frame, text="Play First Audio", width=30, command=lambda: self.audio_player.play(file1)).pack(pady=5)
        Button(main_frame, text="Play Second Audio", width=30, command=lambda: self.audio_player.play(file2)).pack(pady=5)

        # Step 2
        Label(main_frame, text="Step 2: Choose which audio expresses the emotion", font=("Arial", 10)).pack(pady=(20, 0))
        Label(main_frame, text=pair['emotion'].upper(), font=("Arial", 10, "bold")).pack()
        Label(main_frame, text="more strongly.", font=("Arial", 10)).pack(pady=(0, 10))

        Button(main_frame, text="First Audio is stronger", width=30, command=lambda: self.record_answer("First")).pack(pady=5)
        Button(main_frame, text="Second Audio is stronger", width=30, command=lambda: self.record_answer("Second")).pack(pady=5)
        
    def finish_experiment(self):
        result_path = os.path.join(RESULTS_DIR, f"{self.run_name}_EST.json")
        with open(result_path, "w") as f:
            json.dump(self.results, f, indent=4)
        messagebox.showinfo("Finished", f"✅ EST test completed.\nSaved to: {result_path}\n"
                                        f"📧 Now proceed to the 2nd experiemnt by running `python app_part5_EDiT.py`")
        self.root.quit()

if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    app = ESTApp(root)
    root.mainloop()
