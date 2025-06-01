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


class EITApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EIT Evaluation Tool")
        self.audio_player = AudioPlayer()
        self.results = {"responses": []}
        self.eit_items = []
        self.current_index = 0

        self.setup_gui()

    def setup_gui(self):
        self.frame = Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        self.label = Label(self.frame, text="Enter run name:")
        self.label.pack()

        self.entry = tk.Entry(self.frame)
        self.entry.pack()

        self.start_button = Button(self.frame, text="Start EIT Evaluation", command=self.start_eit_test)
        self.start_button.pack(pady=10)

    def start_eit_test(self):
        self.run_name = self.entry.get().strip()
        if not self.run_name:
            messagebox.showerror("Error", "Please enter a run name.")
            return

        os.makedirs(RESULTS_DIR, exist_ok=True)
        self.frame.destroy()

        self.load_eit_data()
        if not self.eit_items:
            messagebox.showerror("Error", "No EIT items found in data folder.")
            self.root.quit()
        else:
            self.show_next_audio()

    def load_eit_data(self):
        eit_dir = os.path.join(DATA_DIR, "EIT")
        for model in os.listdir(eit_dir):
            model_path = os.path.join(eit_dir, model)
            if not os.path.isdir(model_path):
                continue
            for emotion in os.listdir(model_path):
                emotion_path = os.path.join(model_path, emotion)
                if not os.path.isdir(emotion_path):
                    continue
                for fname in os.listdir(emotion_path):
                    if not fname.endswith(AUDIO_EXT):
                        continue
                    self.eit_items.append({
                        "model": model,
                        "expected_emotion": emotion,
                        "file": os.path.join(emotion_path, fname)
                    })
        random.shuffle(self.eit_items)

    def show_next_audio(self):
        if self.current_index >= len(self.eit_items):
            self.finish_experiment()
            return

        item = self.eit_items[self.current_index]

        self.window = tk.Toplevel(self.root)
        self.window.title(f"EIT Evaluation - {self.current_index + 1}/{len(self.eit_items)}")

        Label(self.window, text="Listen to the audio and select the emotion you hear:").pack(pady=10)

        Button(self.window, text="Play Audio", command=lambda: self.audio_player.play(item["file"])).pack(pady=5)

        for emotion in EMOTIONS:
            Button(self.window, text=emotion, command=lambda e=emotion: self.record_answer(e)).pack(pady=3)

    def record_answer(self, selected_emotion):
        item = self.eit_items[self.current_index]
        correct = (selected_emotion == item["expected_emotion"])

        self.results["responses"].append({
            "model": item["model"],
            "file": os.path.basename(item["file"]),
            "expected_emotion": item["expected_emotion"],
            "selected_emotion": selected_emotion,
            "correct": correct
        })

        self.audio_player.stop()
        self.window.destroy()
        self.current_index += 1
        self.show_next_audio()

    def finish_experiment(self):
        result_path = os.path.join(RESULTS_DIR, f"{self.run_name}_EIT.json")
        with open(result_path, "w") as f:
            json.dump(self.results, f, indent=4)

        messagebox.showinfo("Finished", f"✅ EIT test completed.\nResults saved to: {result_path}\n"
                                        f"📧 Please send the file to radu.bolborici@gmail.com")
        self.root.quit()


if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    app = EITApp(root)
    root.mainloop()
