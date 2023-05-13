import os
import sqlite3
import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Web Crawler")
        self.db_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'database')) + "\\KNF_sentiment.db"
        self.create_widgets()

    def create_widgets(self):
        self.left_frame = tk.Frame(self.master)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.tables_button = tk.Button(self.left_frame, text="Pokaż tabele", command=self.show_tables)
        self.tables_button.pack(side=tk.TOP, padx=10, pady=10)

        self.query_button = tk.Button(self.left_frame, text="Wykonaj polecenie", command=self.execute_query)
        self.query_button.pack(side=tk.TOP, padx=10, pady=10)

        self.right_frame = tk.Frame(self.master)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_box = tk.Text(self.right_frame, height=10, width=50)
        self.text_box.pack()

        self.result_box = tk.Text(self.right_frame, height=10, width=50, state="disabled")
        self.result_box.pack()

    def execute_query(self):
        query = self.text_box.get("1.0", "end-1c")
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(query)
            result = c.fetchall()
            self.result_box.delete('1.0', tk.END)
            self.result_box.insert(tk.END, str(result))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            self.result_box.delete('1.0', tk.END)
            self.result_box.insert(tk.END, str(e))

    def show_tables(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()
            self.result_box.delete('1.0', tk.END)
            self.result_box.config(state='normal')
            self.result_box.insert(tk.END, "Tabele:\n")
            for table in tables:
                self.result_box.insert(tk.END, table[0] + "\n")
            self.result_box.config(state='disabled')
            conn.close()
        except sqlite3.Error as e:
            self.result_box.delete('1.0', tk.END)
            self.result_box.insert(tk.END, str(e))

root = tk.Tk()
app = Application(master=root)
app.mainloop()
