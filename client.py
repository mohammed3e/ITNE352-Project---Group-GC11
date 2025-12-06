import socket
import json
import tkinter as tk
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 5000

class SimpleNewsClient:
    def __init__(self, root):
        self.root = root
        self.root.title("News Client")

        self.sock = None
        self.connected = False
        self.items = []

        # --- Connection section ---
        tk.Label(root, text="Username:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.connect_btn = tk.Button(root, text="Connect", command=self.connect)
        self.connect_btn.pack()

        self.status_label = tk.Label(root, text="Not connected", fg="red")
        self.status_label.pack()

        # --- Search section ---
        tk.Label(root, text="Keyword:").pack()
        self.keyword_entry = tk.Entry(root)
        self.keyword_entry.pack()

        self.search_btn = tk.Button(root, text="Search Headlines", command=self.search_headlines)
        self.search_btn.pack()
