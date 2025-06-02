import os
import json
import random
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Button, Label, Frame
import pygame

# Constants
AUDIO_EXT = ".wav"
EMOTIONS = ["Neutral", "Suprise", "Angry", "Sad", "Happy"]
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


class EDTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EDT Evaluation Tool")
        self.audio_player = AudioPlayer()
        self.results = {"responses": []}
        self.edt_pairs = []
        self.current_index = 0

        self.setup_gui()

    def setup_gui(self):
        self.frame = Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        self.label = Label(self.frame, text="Enter run name:")
        self.label.pack()

        self.entry = tk.Entry(self.frame)
        self.entry.pack()

        self.start_button = Button(self.frame, text="Start EDT Evaluation", command=self.start_edt_test)
        self.start_button.pack(pady=10)

    def start_edt_test(self):
        self.run_name = self.entry.get().strip()
        if not self.run_name:
            messagebox.showerror("Error", "Please enter a run name.")
            return

        os.makedirs(RESULTS_DIR, exist_ok=True)
        self.frame.destroy()

        self.load_edt_data()
        if not self.edt_pairs:
            messagebox.showerror("Error", "No valid EDT pairs found in the data folder.")
            self.root.quit()
        else:
            self.show_next_pair()

    def load_edt_data(self):
        edt_dir = os.path.join(DATA_DIR, "EDT")
        for model in os.listdir(edt_dir):
            model_path = os.path.join(edt_dir, model)
            if not os.path.isdir(model_path):
                continue

            phrase_groups = {}
            for fname in os.listdir(model_path):
                if not fname.endswith(AUDIO_EXT):
                    continue
                if not fname.startswith("phrase_"):
                    continue
                phrase_id = "_".join(fname.split("_")[:2])  # e.g., phrase_1
                phrase_groups.setdefault(phrase_id, []).append(fname)

            for phrase_id, files in phrase_groups.items():
                if len(files) != 2:
                    continue
                file1, file2 = sorted(files)
                info1 = self.parse_edt_filename(file1)
                info2 = self.parse_edt_filename(file2)
                if not info1 or not info2:
                    continue
                if info1["emotion"] == info2["emotion"]:
                    continue
                self.edt_pairs.append({
                    "model": model,
                    "phrase": phrase_id,
                    "file1": os.path.join(model_path, file1),
                    "file2": os.path.join(model_path, file2),
                    "emotion1": info1["emotion"],
                    "emotion2": info2["emotion"]
                })

        random.shuffle(self.edt_pairs)

    def parse_edt_filename(self, filename):
        try:
            parts = filename.replace(".wav", "").split("_")
            emotion_index = parts.index("emotion")
            return {"emotion": parts[emotion_index + 1]}
        except Exception:
            return None
        


    def show_next_pair(self):
        if self.current_index >= len(self.edt_pairs):
            self.finish_experiment()
            return

        pair = self.edt_pairs[self.current_index]
        emotion_text = pair['emotion1'].upper()

        self.window = tk.Toplevel(self.root)
        self.window.title(f"EDT Evaluation - Pair {self.current_index + 1}/{len(self.edt_pairs)}")

        main_frame = Frame(self.window)
        main_frame.pack(padx=20, pady=20)

        # === Step 1 ===
        Label(main_frame, text="Step 1: Listen to both of the audio samples", font=("Arial", 10, "bold")).pack(pady=(0, 10))

        Button(main_frame, text="Play First Audio", width=30, command=lambda: self.audio_player.play(pair["file1"])).pack(pady=5)
        Button(main_frame, text="Play Second Audio", width=30, command=lambda: self.audio_player.play(pair["file2"])).pack(pady=5)

        # === Step 2 ===
        Label(main_frame, text="Step 2: Choose which audio better expresses the emotion", font=("Arial", 10)).pack(pady=(20, 0))
        Label(main_frame, text=emotion_text, font=("Arial", 10, "bold")).pack()
        Label(main_frame, text="Do not account for naturalness.", font=("Arial", 10)).pack(pady=(0, 10))

        Button(main_frame, text="First Audio is better", width=30, command=lambda: self.record_choice("file1")).pack(pady=5)
        Button(main_frame, text="Second Audio is better", width=30, command=lambda: self.record_choice("file2")).pack(pady=5)



    '''
    def show_next_pair(self):
        if self.current_index >= len(self.edt_pairs):
            self.finish_experiment()
            return

        pair = self.edt_pairs[self.current_index]

        self.window = tk.Toplevel(self.root)
        self.window.title(f"EDT Evaluation - Pair {self.current_index + 1}/{len(self.edt_pairs)}")

        prompt = f"Which audio expresses the emotion '{pair['emotion1']}' more clearly?"
        Label(self.window, text=prompt, wraplength=400).pack(pady=10)

        Button(self.window, text="Play First Audio", command=lambda: self.audio_player.play(pair["file1"])).pack(pady=5)
        Button(self.window, text="Play Second Audio", command=lambda: self.audio_player.play(pair["file2"])).pack(pady=5)

        Button(self.window, text="First Audio is better", command=lambda: self.record_choice("file1")).pack(pady=5)
        Button(self.window, text="Second Audio is better", command=lambda: self.record_choice("file2")).pack(pady=5)
    '''

    # def record_choice(self, choice):
    #     pair = self.edt_pairs[self.current_index]
    #     correct = (choice == "file1")  # file1 is always the one with emotion1

    #     self.results["responses"].append({
    #         "model": pair["model"],
    #         "phrase": pair["phrase"],
    #         "file1": os.path.basename(pair["file1"]),
    #         "file2": os.path.basename(pair["file2"]),
    #         "emotion1": pair["emotion1"],
    #         "emotion2": pair["emotion2"],
    #         "selected": "file1" if choice == "file1" else "file2",
    #         "correct": correct
    #     })

    #     self.audio_player.stop()
    #     self.window.destroy()
    #     self.current_index += 1
    #     self.show_next_pair()

    def record_choice(self, choice):
        pair = self.edt_pairs[self.current_index]

        emo1 = self.parse_edt_filename(os.path.basename(pair["file1"]))["emotion"]
        emo2 = self.parse_edt_filename(os.path.basename(pair["file2"]))["emotion"]

        expected_emotion = pair["emotion1"]
        correct_file = "file1" if emo1 == expected_emotion else "file2"

        correct = (choice == correct_file)

        self.results["responses"].append({
            "model": pair["model"],
            "phrase": pair["phrase"],
            "file1": os.path.basename(pair["file1"]),
            "file2": os.path.basename(pair["file2"]),
            "emotion1": pair["emotion1"],
            "emotion2": pair["emotion2"],
            "selected": "file1" if choice == "file1" else "file2",
            "correct": correct
        })

        self.audio_player.stop()
        self.window.destroy()
        self.current_index += 1
        self.show_next_pair()

    def finish_experiment(self):
        result_path = os.path.join(RESULTS_DIR, f"{self.run_name}_EDT.json")
        with open(result_path, "w") as f:
            json.dump(self.results, f, indent=4)

        messagebox.showinfo("Finished", f"✅ EDT test completed.\nResults saved to: {result_path}\n"
                                        f"📧 Now proceed to the 2nd experiemnt by running `python app_part3_EIT.py`")
        self.root.quit()


if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    app = EDTApp(root)
    root.mainloop()
