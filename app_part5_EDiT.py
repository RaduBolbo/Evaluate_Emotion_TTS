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


class EDiTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EDiT Evaluation Tool")
        self.audio_player = AudioPlayer()
        self.results = {"responses": []}
        self.edit_files = []
        self.current_index = 0
        self.setup_gui()

    def setup_gui(self):
        self.frame = Frame(self.root)
        self.frame.pack(padx=20, pady=20)
        Label(self.frame, text="Enter run name:").pack()
        self.entry = tk.Entry(self.frame)
        self.entry.pack()
        Button(self.frame, text="Start EDiT Evaluation", command=self.start_edit_test).pack(pady=10)

    def start_edit_test(self):
        self.run_name = self.entry.get().strip()
        if not self.run_name:
            messagebox.showerror("Error", "Please enter a run name.")
            return
        os.makedirs(RESULTS_DIR, exist_ok=True)
        self.frame.destroy()
        self.load_edit_data()
        if not self.edit_files:
            messagebox.showerror("Error", "No EDiT files found.")
            self.root.quit()
        else:
            self.show_next_file()

    def load_edit_data(self):
        edit_dir = os.path.join(DATA_DIR, "EDiT")
        for model in os.listdir(edit_dir):
            model_path = os.path.join(edit_dir, model)
            if not os.path.isdir(model_path):
                continue

            for fname in os.listdir(model_path):
                if not fname.endswith(AUDIO_EXT):
                    continue
                parts = fname.replace(".wav", "").split("_")
                try:
                    source_idx = parts.index("source")
                    target_idx = parts.index("target")
                    source_emotion = parts[source_idx + 1]
                    target_emotion = parts[target_idx + 1]
                    self.edit_files.append({
                        "model": model,
                        "file": os.path.join(model_path, fname),
                        "file_name": fname,
                        "source": source_emotion,
                        "target": target_emotion
                    })
                except ValueError:
                    continue

        random.shuffle(self.edit_files)

    def show_next_file(self):
        if self.current_index >= len(self.edit_files):
            self.finish_experiment()
            return

        example = self.edit_files[self.current_index]

        self.window = tk.Toplevel(self.root)
        self.window.title(f"EDiT Evaluation - {self.current_index + 1}/{len(self.edit_files)}")

        Label(self.window, text=f"Which emotion do you hear most clearly in this clip?").pack(pady=10)
        Button(self.window, text="Play Audio", command=lambda: self.audio_player.play(example["file"])).pack(pady=5)

        Button(self.window, text=f"{example['source']}",
               command=lambda: self.record_answer("source")).pack(pady=5)
        Button(self.window, text=f"{example['target']}",
               command=lambda: self.record_answer("target")).pack(pady=5)

    def record_answer(self, selected):
        example = self.edit_files[self.current_index]
        correct = (selected == "target")  # We assume target is the goal
        self.results["responses"].append({
            "model": example["model"],
            "file": example["file_name"],
            "source": example["source"],
            "target": example["target"],
            "selected": selected,
            "correct": correct
        })

        self.audio_player.stop()
        self.window.destroy()
        self.current_index += 1
        self.show_next_file()

    def finish_experiment(self):
        result_path = os.path.join(RESULTS_DIR, f"{self.run_name}_EDiT.json")
        with open(result_path, "w") as f:
            json.dump(self.results, f, indent=4)
        messagebox.showinfo("Finished", f"✅ EDiT test completed.\nSaved to: {result_path}\n"
                                        f"📧 Send it to radu.bolborici@gmail.com")
        self.root.quit()


if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    app = EDiTApp(root)
    root.mainloop()
