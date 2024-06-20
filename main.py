import tkinter as tk
from tkinter import messagebox

from Application import Application
from database import create_db, add_user, authenticate_user, add_request_to_db, get_requests, get_managers
import random


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система управления заявками на ремонт компьютеров")
        self.geometry("800x600")
        self.current_user = None
        self.show_login()

    def show_login(self):
        self.clear_frame()

        login_frame = tk.Frame(self)
        login_frame.pack(pady=20)

        tk.Label(login_frame, text="Email").grid(row=0, column=0, padx=10, pady=5)
        self.email_entry = tk.Entry(login_frame)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(login_frame, text="Пароль").grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(login_frame, show='*')
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        login_button = tk.Button(login_frame, text="Войти", command=self.login)
        login_button.grid(row=2, columnspan=2, pady=10)

        register_button = tk.Button(login_frame, text="Регистрация", command=self.show_register)
        register_button.grid(row=3, columnspan=2, pady=5)

    def show_home(self):
        self.clear_frame()

        home_frame = tk.Frame(self)
        home_frame.pack(pady=20)

        tk.Label(home_frame, text=f"Добро пожаловать, {self.current_user[1]}").pack()

        if self.current_user[4] == 'admin':
            tk.Button(home_frame, text="Управление заявками", command=self.show_manage_requests).pack()

        tk.Button(home_frame, text="Добавить заявку", command=self.show_add_request).pack()
        tk.Button(home_frame, text="Мои заявки", command=self.show_my_requests).pack()
        tk.Button(home_frame, text="Выход", command=self.logout).pack()

    def show_add_request(self):
        self.clear_frame()

        add_request_frame = tk.Frame(self)
        add_request_frame.pack(pady=20)

        tk.Label(add_request_frame, text="Номер заявки").pack()
        self.request_number_entry = tk.Entry(add_request_frame)
        self.request_number_entry.pack()

        tk.Label(add_request_frame, text="Дата подачи (ГГГГ-ММ-ДД)").pack()
        self.submission_date_entry = tk.Entry(add_request_frame)
        self.submission_date_entry.pack()

        tk.Label(add_request_frame, text="Оборудование для ремонта").pack()
        self.equipment_entry = tk.Entry(add_request_frame)
        self.equipment_entry.pack()

        tk.Label(add_request_frame, text="Тип неисправности").pack()
        self.issue_type_entry = tk.Entry(add_request_frame)
        self.issue_type_entry.pack()

        tk.Label(add_request_frame, text="Описание проблемы").pack()
        self.description_entry = tk.Text(add_request_frame, height=5)
        self.description_entry.pack()

        tk.Label(add_request_frame, text="Имя клиента").pack()
        self.client_name_entry = tk.Entry(add_request_frame)
        self.client_name_entry.pack()

        submit_button = tk.Button(add_request_frame, text="Подтвердить", command=self.add_request)
        submit_button.pack()

        back_button = tk.Button(add_request_frame, text="Назад", command=self.show_home)
        back_button.pack()

    def add_request(self):
        try:
            request_number = self.request_number_entry.get()
            submission_date = self.submission_date_entry.get()
            content = self.description_entry.get("1.0", tk.END)
            user_id = self.current_user[0]
            managers = get_managers()

            if not managers:
                messagebox.showerror("Ошибка", "Нет доступных менеджеров для назначения заявки")
                return

            if len(managers) > 0:
                manager_id = random.choice(managers)[0]  # Выбор случайного менеджера по его id
            else:
                messagebox.showerror("Ошибка", "Нет доступных менеджеров для назначения заявки")
                return

            equipment_to_repair = self.equipment_entry.get()
            issue_type = self.issue_type_entry.get()
            problem_description = self.description_entry.get("1.0", tk.END)
            client_name = self.client_name_entry.get()

            add_request_to_db(request_number, submission_date, content, user_id, manager_id, equipment_to_repair,
                              issue_type, problem_description, client_name)
            messagebox.showinfo("Успешно", "Заявка успешно добавлена")

            self.show_my_requests()  # Обновляем список заявок после добавления
            self.clear_frame()  # Очищаем текущий интерфейс, если это необходимо

        except IndexError as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            print(f"Ошибка IndexError: {str(e)}")

        except Exception as ex:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(ex)}")
            print(f"Необработанная ошибка: {str(ex)}")

    def show_my_requests(self):
        self.clear_frame()

        my_requests_frame = tk.Frame(self)
        my_requests_frame.pack(pady=20)

        tk.Label(my_requests_frame, text="Мои заявки").pack()

        requests = get_requests(user_id=self.current_user[0])
        for req in requests:
            if len(req) >= 10:  # Проверим, что данных достаточно для отображения заявки
                tk.Label(my_requests_frame,
                         text=f"ID заявки: {req[0]}, Номер заявки: {req[1]}, Дата подачи: {req[2]}, Оборудование: {req[5]}, Тип: {req[6]}, Описание: {req[7]}, Статус: {req[9]}"
                         ).pack()
            else:
                tk.Label(my_requests_frame,
                         text=f"Некорректные данные заявки: {req}"
                         ).pack()

        refresh_button = tk.Button(my_requests_frame, text="Обновить", command=self.show_my_requests)
        refresh_button.pack(side=tk.LEFT, padx=10)

        back_button = tk.Button(my_requests_frame, text="Назад", command=self.show_home)
        back_button.pack(side=tk.RIGHT, padx=10)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        user = authenticate_user(email, password)
        if user:
            self.current_user = user
            self.show_home()
        else:
            messagebox.showerror("Ошибка", "Неправильный email или пароль")

    def logout(self):
        self.current_user = None
        self.show_login()

    def show_register(self):
        self.clear_frame()

        register_frame = tk.Frame(self)
        register_frame.pack(pady=20)

        tk.Label(register_frame, text="Имя").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = tk.Entry(register_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(register_frame, text="Email").grid(row=1, column=0, padx=10, pady=5)
        self.email_entry = tk.Entry(register_frame)
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(register_frame, text="Пароль").grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(register_frame, show='*')
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(register_frame, text="Роль").grid(row=3, column=0, padx=10, pady=5)
        self.role_var = tk.StringVar(register_frame)
        self.role_var.set("user")
        role_optionmenu = tk.OptionMenu(register_frame, self.role_var, "user", "admin")
        role_optionmenu.grid(row=3, column=1, padx=10, pady=5)

        register_button = tk.Button(register_frame, text="Зарегистрироваться", command=self.register_user)
        register_button.grid(row=4, columnspan=2, pady=10)

        back_button = tk.Button(register_frame, text="Назад", command=self.show_login)
        back_button.grid(row=5, columnspan=2, pady=5)

    def register_user(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        add_user(name, email, password, role)
        messagebox.showinfo("Успешно", "Регистрация прошла успешно. Теперь вы можете войти.")
        self.show_login()

    if __name__ == "__main__":
        create_db()  # Создаем базу данных при первом запуске
        app = Application()
        app.mainloop()
