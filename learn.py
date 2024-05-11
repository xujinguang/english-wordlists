#!/bin/python
#-*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
import json
import re
from datetime import datetime
import os
import random

class VocabularyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Vocabulary Learning App")
        self.master.geometry("500x200")  # Set window size

        # Initialize vocabulary list and index
        self.vocabulary = []
        self.current_index = 0
        self.auto_running = False
        self.file_path = ""

        # Create the GUI components
        self.word_label = tk.Label(master, text="", font=("微软雅黑", 16))
        self.word_label.pack()

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, pady = 10)

        self.prev_button = tk.Button(self.button_frame, text="上一个", command=self.prev_word)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.button_frame, text="下一个", command=self.next_word)
        self.next_button.pack(side=tk.LEFT)

        self.auto_button = tk.Button(self.button_frame, text="自动", command=self.toggle_auto_display)
        self.auto_button.pack(side=tk.LEFT)

        self.new_word_button = tk.Button(self.button_frame, text="生词", command=self.add_to_new_word_file)
        self.new_word_button.pack(side=tk.LEFT, padx=5)

        # Menu to load the vocabulary file
        self.menu = tk.Menu(master)
        self.master.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="打开单词本", command=self.load_file)
        self.file_menu.add_command(label="备份生词本", command=self.backup_new_word_file)

        self.order_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="播放顺序", menu=self.order_menu)

        self.order_menu.add_command(label="顺序", command=lambda: self.set_play_order("sequential"))
        self.order_menu.add_command(label="乱序", command=lambda: self.set_play_order("random"))


        self.load_previous_session()
        self.update_word_label()

        # Ensure the current index is saved when the window is closed
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_previous_session(self):
        try:
            with open('session.json', 'r', encoding='utf-8') as file:
                session = json.load(file)
                self.current_index = session['index']
                self.file_path = session['file_path']
                with open(session['file_path'], 'r', encoding='utf-8') as f:
                    self.vocabulary = [line.strip() for line in f.readlines()]
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            # Either the session file does not exist, or it's invalid
            pass

    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.vocabulary = [line.strip() for line in file.readlines()]
            self.current_index = 0
            self.update_word_label()

    def prev_word(self):
        if self.vocabulary:
            self.current_index = (self.current_index - 1) % len(self.vocabulary)
            self.update_word_label()

    def set_play_order(self, order):
        self.play_order = order
        print(f"播放顺序设置为: {'顺序' if order == 'sequential' else '乱序'}")

    def next_word(self):
        if self.vocabulary:
            if self.play_order == "sequential":
                self.current_index = (self.current_index + 1) % len(self.vocabulary)
            else:  # 如果是乱序播放
                self.current_index = random.randint(0, len(self.vocabulary) - 1)
            self.update_word_label()

    def toggle_auto_display(self):
        if self.auto_running:
            self.stop_auto_display()
        else:
            self.start_auto_display()

    def start_auto_display(self):
        self.auto_running = True
        self.auto_button.config(text="停止")
        self.auto_next_word()

    def stop_auto_display(self):
        self.auto_running = False
        self.auto_button.config(text="自动")

    def auto_next_word(self):
        if self.auto_running:
            self.next_word()
            self.master.after(2000, self.auto_next_word)

    #def auto_display(self):
    #    if not self.auto_running:
    #        self.auto_running = True
    #        #self.auto_button.config(relief=tk.SUNKEN)
    #        self.auto_next_word()

    #def auto_next_word(self):
    #    if self.auto_running:
    #        self.next_word()
    #        self.master.after(2000, self.auto_next_word)
    #    else:
    #        self.auto_button.config(relief=tk.RAISED)

    def add_to_new_word_file(self):
        if self.vocabulary:
            current_word = self.vocabulary[self.current_index]
            with open('new_word.txt', 'a', encoding='utf-8') as file:
                file.write(f"{current_word}\n")
            print(f"单词 '{current_word}' 已添加到生词本。")

    def backup_new_word_file(self):
        current_date = datetime.now().strftime("%Y%m%d")
        backup_filename = f"new_word_{current_date}.txt"
        if os.path.exists('new_word.txt'):
            os.rename('new_word.txt', backup_filename)
            with open('new_word.txt', 'w', encoding='utf-8') as file:  # 创建一个新的空文件
                pass
            print(f"生词本已备份为 '{backup_filename}'。")
        else:
            print("生词本文件不存在，无需备份。")

    def update_word_label(self):
        if self.vocabulary:
            word_info = self.vocabulary[self.current_index]
            pattern = re.compile(r'(\w+)\s+(\[[^\]]+\])\s+(.*)')
            match = pattern.match(word_info)

            if match:
                word = match.group(1)
                phonetic = match.group(2)
                definition = match.group(3)
                word_info = "\n" + word + "\n" + phonetic + "\n\n" + definition

            self.word_label.config(text=word_info)

    def on_closing(self):
        # Save the current index and file path to a file
        if self.vocabulary:
            session = {
                'index': self.current_index,
                'file_path': self.file_path,
            }
            with open('session.json', 'w', encoding='utf-8') as file:
                json.dump(session, file, ensure_ascii=False)
        self.auto_running = False
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VocabularyApp(root)
    root.mainloop()

