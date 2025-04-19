import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

DATA_FILE = "transactions.json"
BUDGET_FILE = "budgets.json"
CURRENCY = "₹"

class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("400x600")
        self.root.resizable(False, False)

        self.colors = self.configure_styles()

        self.bg_image = None
        try:
            img = Image.open("finance_bg.jpg")
            self.bg_image = ImageTk.PhotoImage(img)
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.image = self.bg_image
            self.root.configure(bg=self.colors['bg'])
        except (FileNotFoundError, AttributeError):
            self.root.configure(bg=self.colors['bg'])
            
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        ttk.Label(self.main_frame, text="Finance Tracker", style='Header.TLabel').pack(pady=(0, 20))
        self.create_buttons()
        ttk.Label(self.main_frame, text="© 2023 Personal Finance Tracker", font=('Segoe UI', 8), foreground="#666").pack(side=tk.BOTTOM, pady=10)
        self.init_files()

    def create_buttons(self):
        button_frame = ttk.Frame(self.main_frame, style='TFrame')
        button_frame.pack(fill=tk.BOTH, expand=True)

        buttons = [
            ("➕ Add Income", lambda: self.add_transaction("Income"), 'Income.TButton'),
            ("➖ Add Expense", lambda: self.add_transaction("Expense"), 'Expense.TButton'),
            ("💰 Set Budget", self.set_budget, 'Action.TButton'),
            ("📊 View Budgets", self.show_budgets, 'TButton'),
            ("📈 Financial Summary", self.show_summary, 'TButton'),
            ("📋 Transaction History", self.show_transactions, 'TButton'),
            ("📊 Spending Analysis", self.show_spending_chart, 'TButton'),
            ("🚪 Exit", self.root.quit, 'TButton')
        ]

        for text, command, style in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, style=style)
            btn.pack(fill=tk.X, pady=5, ipady=8)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        bg_color = "#f0f2f5"
        primary_color = "#FFA500"
        secondary_color = "#03dac6"
        danger_color = "#ff4444"
        text_color = "#000000"

        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color, font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=primary_color)
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), borderwidth=1, relief="flat", padding=6)
        style.map('TButton', background=[('active', primary_color), ('!disabled', primary_color)], foreground=[('active', 'white'), ('!disabled', 'white')])
        style.configure('Income.TButton', background="#4CAF50")
        style.configure('Expense.TButton', background=danger_color)
        style.configure('Action.TButton', background=secondary_color)

        return {'bg': bg_color, 'primary': primary_color, 'secondary': secondary_color, 'danger': danger_color, 'text': text_color}

    def init_files(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump([], f)
        if not os.path.exists(BUDGET_FILE):
            with open(BUDGET_FILE, "w") as f:
                json.dump({}, f)

    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_data(self, data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_budgets(self):
        try:
            with open(BUDGET_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_budgets(self, budgets):
        with open(BUDGET_FILE, "w") as f:
            json.dump(budgets, f, indent=4)

    def add_transaction(self, type_):
        try:
            amount = simpledialog.askfloat(f"Add {type_}", f"Amount ({CURRENCY}):", minvalue=0.01)
            if amount is None: return
            category = simpledialog.askstring(f"Add {type_}", "Category:")
            if not category:
                messagebox.showerror("Error", "Category cannot be empty")
                return
            date = simpledialog.askstring(f"Add {type_}", "Date (YYYY-MM-DD):")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            else:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format")
                    return

            budgets = self.load_budgets()
            if type_ == "Expense" and category in budgets:
                if amount > float(budgets[category]):
                    if not messagebox.askyesno("Budget Alert", f"This exceeds {category} budget ({CURRENCY}{budgets[category]})\nProceed anyway?"):
                        return

            transaction = {"type": type_, "amount": amount, "category": category, "date": date}
            data = self.load_data()
            data.append(transaction)
            self.save_data(data)
            messagebox.showinfo("Success", f"{type_} of {CURRENCY}{amount:.2f} added!")
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {str(e)}")

    def set_budget(self):
        category = simpledialog.askstring("Set Budget", "Category name:")
        if not category: return
        amount = simpledialog.askfloat("Set Budget", f"Amount ({CURRENCY}):", minvalue=0.01)
        if amount is None: return
        budgets = self.load_budgets()
        budgets[category] = amount
        self.save_budgets(budgets)
        messagebox.showinfo("Success", f"Budget set for {category}")

    def show_budgets(self):
        budgets = self.load_budgets()
        if not budgets:
            messagebox.showinfo("Budgets", "No budgets set yet")
            return
        budget_window = tk.Toplevel(self.root)
        budget_window.title("Current Budgets")
        budget_window.geometry("300x400")
        budget_window.configure(bg=self.colors['bg'])
        ttk.Label(budget_window, text="Your Budgets", style='Header.TLabel').pack(pady=10)
        frame = ttk.Frame(budget_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        canvas = tk.Canvas(frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        for i, (category, amount) in enumerate(budgets.items()):
            ttk.Label(scrollable_frame, text=f"{category}: {CURRENCY}{float(amount):.2f}", font=('Segoe UI', 11)).grid(row=i, column=0, sticky="w", pady=5)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        ttk.Button(budget_window, text="Close", command=budget_window.destroy).pack(pady=10)

    def show_spending_chart(self):
        data = self.load_data()
        expenses = [t for t in data if t["type"] == "Expense"]
        if not expenses:
            messagebox.showinfo("Info", "No expenses to visualize")
            return
        categories = {}
        for t in expenses:
            categories[t["category"]] = categories.get(t["category"], 0) + t["amount"]
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Spending Analysis")
        chart_window.geometry("600x500")
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        wedges, texts, autotexts = ax.pie(categories.values(), labels=categories.keys(), autopct=lambda p: f"{p:.1f}%\n({CURRENCY}{p * sum(categories.values()) / 100:.2f})", startangle=90, colors=plt.cm.Pastel1.colors)
        ax.set_title("Spending by Category", pad=20)
        plt.setp(autotexts, size=8, weight="bold")
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        ttk.Button(chart_window, text="Close", command=chart_window.destroy).pack(pady=10)

    def show_transactions(self):
        data = sorted(self.load_data(), key=lambda x: x["date"], reverse=True)
        history_window = tk.Toplevel(self.root)
        history_window.title("Transaction History")
        history_window.geometry("700x500")
        history_window.configure(bg=self.colors['bg'])
        header_frame = ttk.Frame(history_window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(header_frame, text="Transaction History", style='Header.TLabel').pack()
        tree_frame = ttk.Frame(history_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ("type", "amount", "category", "date")
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, anchor="center")
        for t in data:
            tree.insert("", "end", values=(t["type"], f"{CURRENCY}{t['amount']:.2f}", t["category"], t["date"]))
        tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(history_window, text="Close", command=history_window.destroy).pack(pady=10)

    def show_summary(self):
        data = self.load_data()
        income = sum(t["amount"] for t in data if t["type"] == "Income")
        expense = sum(t["amount"] for t in data if t["type"] == "Expense")
        balance = income - expense
        messagebox.showinfo("Summary", f"Total Income: {CURRENCY}{income:.2f}\nTotal Expense: {CURRENCY}{expense:.2f}\nBalance: {CURRENCY}{balance:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()
