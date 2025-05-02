import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import json
import os
from datetime import datetime

def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Failed to load data from {filename}. File may be corrupted.")
    return {} if filename.endswith(".json") else []

def save_data(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Tracker - Login")
        self.root.geometry("500x400")
        
        bg_image = Image.open("background.jpg")
        bg_photo = ImageTk.PhotoImage(bg_image.resize((500, 400)))
        bg_label = tk.Label(self.root, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.frame = tk.Frame(self.root, bg="#ffffff", bd=0)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.username_label = tk.Label(self.frame, text="Username:", font=("Arial", 12), bg="#ffffff")
        self.username_label.grid(row=0, column=0, pady=10, padx=5)

        self.username_entry = tk.Entry(self.frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, pady=10)

        self.password_label = tk.Label(self.frame, text="Password:", font=("Arial", 12), bg="#ffffff")
        self.password_label.grid(row=1, column=0, pady=10, padx=5)

        self.password_entry = tk.Entry(self.frame, show="*", font=("Arial", 12))
        self.password_entry.grid(row=1, column=1, pady=10)

        self.login_button = tk.Button(self.frame, text="Login", command=self.login, font=("Arial", 12), bg="#4CAF50", fg="white")
        self.login_button.grid(row=2, columnspan=2, pady=10)

        self.register_button = tk.Button(self.frame, text="Register", command=self.open_register, font=("Arial", 12), bg="#2196F3", fg="white")
        self.register_button.grid(row=3, columnspan=2, pady=5)

        self.users = load_data("users.json")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username in self.users and self.users[username]["password"] == password:
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.root.destroy()
            dashboard = tk.Tk()
            app = FinanceTracker(dashboard, username)
            dashboard.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def open_register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register New User")
        register_window.geometry("400x300")

        tk.Label(register_window, text="New Username:", font=("Arial", 12)).pack(pady=5)
        new_username_entry = tk.Entry(register_window, font=("Arial", 12))
        new_username_entry.pack(pady=5)

        tk.Label(register_window, text="New Password:", font=("Arial", 12)).pack(pady=5)
        new_password_entry = tk.Entry(register_window, show="*", font=("Arial", 12))
        new_password_entry.pack(pady=5)

        tk.Button(register_window, text="Register", font=("Arial", 12), bg="#4CAF50", fg="white",
                  command=lambda: self.register_user(new_username_entry.get(), new_password_entry.get(), register_window)).pack(pady=20)

    def register_user(self, username, password, window):
        username = username.strip()
        password = password.strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty!")
            return

        if username in self.users:
            messagebox.showerror("Error", "Username already exists!")
            return

        self.users[username] = {"password": password}
        save_data(self.users, "users.json")
        save_data([], f"{username}_transactions.json")
        save_data({}, f"{username}_budgets.json")

        messagebox.showinfo("Success", "Registration successful!")
        window.destroy()

class FinanceTracker:
    def __init__(self, root, username):
        self.root = root
        self.root.title(f"Finance Tracker - {username}")
        self.root.geometry("900x600")
        self.username = username

        self.transactions = load_data(f"{username}_transactions.json")
        self.budgets = load_data(f"{username}_budgets.json")

        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="Finance Tracker Dashboard", font=("Arial", 20, "bold"), bg="#4CAF50", fg="white")
        title.pack(fill=tk.X)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Add Transaction", command=self.add_transaction_window, width=20, bg="#2196F3", fg="white").grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="View Transactions", command=self.view_transactions, width=20, bg="#9C27B0", fg="white").grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Set Budget", command=self.set_budget_window, width=20, bg="#FF5722", fg="white").grid(row=0, column=2, padx=10)
        tk.Button(button_frame, text="View Budgets", command=self.view_budgets, width=20, bg="#3F51B5", fg="white").grid(row=0, column=3, padx=10)

        tk.Button(self.root, text="Logout", command=self.logout, width=10, bg="red", fg="white").pack(pady=10)

        self.pie_frame = tk.Frame(self.root)
        self.pie_frame.pack(pady=10)
        self.update_pie_chart()

    def add_transaction_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Transaction")
        win.geometry("400x300")

        tk.Label(win, text="Amount:", font=("Arial", 12)).pack(pady=5)
        amount_entry = tk.Entry(win, font=("Arial", 12))
        amount_entry.pack(pady=5)

        tk.Label(win, text="Category:", font=("Arial", 12)).pack(pady=5)
        category_entry = tk.Entry(win, font=("Arial", 12))
        category_entry.pack(pady=5)

        tk.Button(win, text="Save", command=lambda: self.save_transaction(amount_entry.get(), category_entry.get(), win), bg="#4CAF50", fg="white").pack(pady=20)

    def save_transaction(self, amount, category, window):
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return

        self.transactions.append({
            "amount": amount,
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        save_data(self.transactions, f"{self.username}_transactions.json")
        window.destroy()
        self.update_pie_chart()

    def view_transactions(self):
        win = tk.Toplevel(self.root)
        win.title("Transactions")
        win.geometry("400x400")

        tree = ttk.Treeview(win, columns=("Amount", "Category", "Date"), show="headings")
        tree.heading("Amount", text="Amount")
        tree.heading("Category", text="Category")
        tree.heading("Date", text="Date")
        tree.pack(fill=tk.BOTH, expand=True)

        for tx in self.transactions:
            tree.insert("", tk.END, values=(tx["amount"], tx["category"], tx.get("date", "N/A")))

    def set_budget_window(self):
        win = tk.Toplevel(self.root)
        win.title("Set Budget")
        win.geometry("400x300")

        tk.Label(win, text="Category:", font=("Arial", 12)).pack(pady=5)
        category_entry = tk.Entry(win, font=("Arial", 12))
        category_entry.pack(pady=5)

        tk.Label(win, text="Budget Amount:", font=("Arial", 12)).pack(pady=5)
        budget_entry = tk.Entry(win, font=("Arial", 12))
        budget_entry.pack(pady=5)

        tk.Button(win, text="Save", command=lambda: self.save_budget(category_entry.get(), budget_entry.get(), win), bg="#4CAF50", fg="white").pack(pady=20)

    def save_budget(self, category, budget, window):
        try:
            budget = float(budget)
        except ValueError:
            messagebox.showerror("Error", "Budget must be a number!")
            return

        self.budgets[category] = budget
        save_data(self.budgets, f"{self.username}_budgets.json")
        window.destroy()

    def view_budgets(self):
        win = tk.Toplevel(self.root)
        win.title("Budgets")
        win.geometry("400x400")

        tree = ttk.Treeview(win, columns=("Category", "Budget"), show="headings")
        tree.heading("Category", text="Category")
        tree.heading("Budget", text="Budget Amount")
        tree.pack(fill=tk.BOTH, expand=True)

        for category, amount in self.budgets.items():
            tree.insert("", tk.END, values=(category, amount))

    def update_pie_chart(self):
        for widget in self.pie_frame.winfo_children():
            widget.destroy()

        categories = {}
        for tx in self.transactions:
            cat = tx["category"]
            amt = tx["amount"]
            categories[cat] = categories.get(cat, 0) + amt

        if categories:
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.pie(categories.values(), labels=categories.keys(), autopct="%1.1f%%")
            ax.set_title("Expenses by Category")

            pie_canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
            pie_canvas.draw()
            pie_canvas.get_tk_widget().pack()
        else:
            tk.Label(self.pie_frame, text="No transactions to display.", font=("Arial", 12)).pack()

    def logout(self):
        self.root.destroy()
        main()

def main():
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()

