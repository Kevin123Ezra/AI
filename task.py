import sys
import os
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDateEdit, QListWidget, QListWidgetItem, QCheckBox, QWidget, QLabel
from PyQt5.QtCore import Qt, QDate

class HomeworkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Homework Tracker")
        self.setGeometry(100, 100, 600, 400)
        
        self.task_list = QListWidget()

        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter homework task...")

        self.desc_input = QLineEdit(self)
        self.desc_input.setPlaceholderText("Enter task description...")

        self.date_input = QDateEdit(self)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setDate(QDate.currentDate())

        self.add_button = QPushButton("Add Task", self)
        self.add_button.clicked.connect(self.add_task)

        # Layout setup
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.desc_input)
        input_layout.addWidget(self.date_input)
        input_layout.addWidget(self.add_button)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.task_list)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.load_tasks()

    def add_task(self):
        task_text = self.task_input.text().strip()
        task_desc = self.desc_input.text().strip()
        task_date = self.date_input.text().strip()

        if task_text == "" or task_desc == "":
            return

        task_data = (task_text, task_desc, False, task_date)  # Text, Description, Not Checked, Date
        self.save_task(task_data)
        self.add_task_to_list(task_text, task_desc, False, task_date)

        self.task_input.clear()
        self.desc_input.clear()

    def add_task_to_list(self, task_text, task_desc, is_checked, task_date):
        """Add a task with a checkbox and description to the list."""
        item = QListWidgetItem()

        checkbox = QCheckBox()
        checkbox.setChecked(is_checked)

        task_label = QLabel(f"{task_text} - {task_desc} ({task_date})")

        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(checkbox)
        layout.addWidget(task_label)
        layout.addStretch()
        widget.setLayout(layout)

        item.setSizeHint(widget.sizeHint())
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)

        checkbox.toggled.connect(lambda checked, label=task_label: self.toggle_task_state(checked, label))

        if is_checked:
            task_label.setText(f"<s>{task_label.text()}</s>")
        
    def toggle_task_state(self, checked, task_label):
        if checked:
            task_label.setText(f"<s>{task_label.text()}</s>")
        else:
            task_label.setText(task_label.text().replace("<s>", "").replace("</s>", ""))
        
        task_text = task_label.text().split(" - ")[0]
        self.update_task_state(task_text, checked)

    def update_task_state(self, task_text, is_checked):
        tasks = self.load_saved_tasks()
        for i, (text, desc, _, date) in enumerate(tasks):
            if text == task_text:
                tasks[i] = (text, desc, is_checked, date)
                break
        self.save_tasks(tasks)

    def save_task(self, task_data):
        tasks = self.load_saved_tasks()
        tasks.append(task_data)
        self.save_tasks(tasks)

    def save_tasks(self, tasks):
        with open('tasks.pkl', 'wb') as file:
            pickle.dump(tasks, file)

    def load_saved_tasks(self):
        if os.path.exists('tasks.pkl'):
            with open('tasks.pkl', 'rb') as file:
                tasks = pickle.load(file)

                for i, task in enumerate(tasks):
                    if len(task) == 3:
                        tasks[i] = (task[0], task[1], False, QDate.currentDate().toString("dd/MM/yyyy"))
                    elif len(task) == 2:
                        tasks[i] = (task[0], "", False, QDate.currentDate().toString("dd/MM/yyyy"))
                return tasks
        return []

    def load_tasks(self):
        tasks = self.load_saved_tasks()
        for task_text, task_desc, is_checked, task_date in tasks:
            self.add_task_to_list(task_text, task_desc, is_checked, task_date)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeworkApp()
    window.show()
    sys.exit(app.exec_())
