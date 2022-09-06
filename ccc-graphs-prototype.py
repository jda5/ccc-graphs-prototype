import tkinter as tk
import tkinter.ttk as ttk
import csv
import time


data = {
    'Question number': [],
    '# correct responses': [],
    '# incorrect responses': [],
    '# peeks': [],
    'time looking at model': [],
    'time doing question': []
}

GUIDANCE = ['1. Calculate the slope of the line (change in y)/(change in x).',
            '2. Substitute the slope into the general equation of a line y=mx+c',
            '3. Substitute either point into the general equation.',
            '4. Solve for c.',
            '5. Write the equation of the line.']

question_model = [
    ('Find the equation of a line that goes through the coordinates (3,4) and (5,20)',
     ('(20 - 4) ÷ (5 - 3) = 8', 'y = 8x + c', '4 = 8 × 3 + c', 'c = -20', 'y = 8x - 20')),
    ('Find the equation of a line that goes through the coordinates (6,-2) and (3,10)',
     ('(-2 - 10) ÷ (6 - 3) = -4', 'y = -4x + c', '10 = -4 × 3 + c', 'c = 22', 'y = -4x + 22')),
]

possible_answers = {'00': ['20-4÷5-3=8', '(20-4)÷(5-3)=8', '16÷2=8', '4-20÷3-5=8', '(4-20)÷(3-5)=8', '-16÷-2=8', '8'],
                    '01': ['y=8x+c', 'y=c+8x'],
                    '02': ['4=8×3+c', '4=3×8+c', '3×8+c=4', '8×3+c=4', '4=c+3×8', '20=8×5+c', '20=5x8+c', '5x8+c=20',
                           '8x5+c=20', '4=24+c', '20=40+c', '24+c=4', '40+c=20'],
                    '03': ['c=-20', '-20=c'],
                    '04': ['y=8x-20'],
                    '10': ['-2-10÷6-3=-4', '(-2-10)÷(6-3)=-4', '-12÷3=-4', '10--2÷3-6=-4', '(10--2)÷(3-6)=-4',
                           '12÷-3=-4', '-4'],
                    '11': ['y=-4x+c', 'y=c-4x'],
                    '12': ['10=-4×3+c', '10=c-4×3', '10=3×-4+c', '3×-4+c=10', '-4×3+c=10', '-2=c-4×6', '-2=-4×6+c',
                           '-2=6×-4+c', 'c+-4×6=-2', '4×6+c=-2', '6×-4+c=-2', '10=-12+c', '10=c-12', 'c-12=10',
                           '-12+c=10', '-2=-24+c', 'c-24=-2', '-2=c-24'],
                    '13': ['c=22', '22=c'],
                    '14': ['y=-4x+22']}

number_of_correct = 0
number_of_incorrect = 0
number_of_peeks = 0
start_time = None
time_after_ready = None
time_after_compare = None
current_question = 0

WIDTH = 820
HEIGHT = 650


def dump_data():
    global data
    with open('ccc_data.csv', mode='w') as data_file:
        data_writer = csv.writer(data_file)
        for key, value in data.items():
            row_data = [key]
            for elem in value:
                row_data.append(elem)
            data_writer.writerow(row_data)

def calculate_time():
    global data
    global start_time
    global time_after_compare
    global time_after_ready
    data['time looking at model'].append(time_after_ready - start_time)
    data['time doing question'].append(time_after_compare - time_after_ready)


class Points(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.points = tk.IntVar()
        self.points.set(0)
        text_label = ttk.Label(self, text='Score: ')
        points_label = ttk.Label(self, textvariable=self.points)
        text_label.pack(side=tk.LEFT, padx=(27, 0), pady=15)
        points_label.pack(side=tk.LEFT)

    def peek(self, subtract=False):
        global number_of_peeks
        if subtract:
            self.points.set(self.points.get() - 150)
            number_of_peeks += 1

    def correct(self):
        self.points.set(self.points.get() + 100)


class Questions(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        question = ttk.Label(self, text=f"{question_model[current_question][0]}", justify=tk.CENTER)
        question.pack(fill=tk.BOTH, pady=30, padx=92)


class Guidance(ttk.Frame):
    def __init__(self, master, text):
        super().__init__(master)
        guidance = ttk.Label(self, text=text, justify=tk.LEFT)
        guidance.pack(side=tk.LEFT, fill=tk.BOTH, padx=40, pady=27)


class Solutions(ttk.Frame):
    def __init__(self, master, question_list):
        super().__init__(master)
        if isinstance(question_list, str):
            label = ttk.Label(self, text=question_list, style='maths.TLabel')
            label.pack(padx=(0, 40), pady=27, fill=tk.BOTH)
        else:
            for solution in question_list:
                label = ttk.Label(self, text=solution, style='maths.TLabel')
                label.pack(padx=(0, 40), fill=tk.BOTH)


class Entry(ttk.Frame):
    def __init__(self, master, question_list):
        super().__init__(master)
        entry_style = ttk.Style()
        entry_style.map('TEntry',
                        highlightcolor=[("active", "#add8e6")])
        ttk.Style().configure('green.TEntry', background='#8bc34a')
        ttk.Style().configure('red.TEntry', background='#db5c5c')
        if type(question_list) == str:
            self.multiple = False
            self.entry = ttk.Entry(self, font=('STIXGeneral', 14))
            self.entry.pack(padx=(0, 40), pady=27, fill=tk.BOTH)
        else:
            self.multiple = True
            self.multi_entry = [ttk.Entry(self, font=('STIXGeneral', 14)) for _ in question_list]
            for entry in self.multi_entry:
                entry.pack(padx=(0, 40), fill=tk.BOTH)

    # TODO: Dynamically change the colour of the background of the entry field as they enter the correct value..... I
    #  tried doing the above by binding the event to the existing colour changing function, but was unsuccessful. Could
    #  try again, but will ask if this is important.

    # TODO: Dynamically include highlighting as mouse moves over entry field

    def check_correct(self, index):
        global number_of_correct
        global number_of_incorrect
        if self.multiple:
            entry_set = []
            for entry in self.multi_entry:
                attempt = entry.get().replace(" ", "")
                entry_list = list(attempt)
                entry_list.sort()
                sorted_entry = ''.join(entry_list)
                if sorted_entry not in entry_set:
                    entry_set.append(sorted_entry)
                    duplicate = False
                else:
                    duplicate = True
                if attempt in possible_answers[f"{current_question}{index}"] and not duplicate:
                    entry.configure(style='green.TEntry')
                    number_of_correct += 1
                    window.points.correct()
                else:
                    entry.configure(style='red.TEntry')
                    number_of_incorrect += 1
        else:
            attempt = self.entry.get().replace(" ", "")
            if attempt in possible_answers[f"{current_question}{index}"]:
                self.entry.configure(style='green.TEntry')
                number_of_correct += 1
                window.points.correct()
            else:
                self.entry.configure(style='red.TEntry')
                number_of_incorrect += 1


class Navigation(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        button_style = ttk.Style(self)
        button_style.configure("TButton", padding=30, foreground="#48505B")
        button_style.map("TButton",
                         foreground=[("pressed", "grey"), ("active", "#2177f0"), ('disabled', '#343639')],
                         background=[("pressed", "#2177f0"), ("active", "#04ff00"), ('disabled', '#9da0ab')],
                         relief=[('pressed', 'groove'), ('!pressed', 'ridge')]
                         )

        self.ready_button = ttk.Button(self, text="Ready",
                                       command=self.begin_question, style="TButton")
        self.next_button = ttk.Button(self, text="Next",
                                      command=self.next_question, style="TButton")
        self.peek_button = ttk.Button(self, text="Peek",
                                      command=self.peek, style="TButton")
        self.solution_button = ttk.Button(self, text="Compare",
                                          command=self.compare, style="TButton")

        self.draw_buttons(master)

        # TODO: Look into ways to change the background of a button

    def draw_buttons(self, master):
        global start_time
        if not master.question_active:
            self.next_button.pack_forget()
            self.ready_button.pack()
            start_time = time.time()

        if master.question_active and not master.display_answer:
            self.ready_button.pack_forget()
            self.peek_button.pack(side=tk.LEFT, padx=(35, 25))
            self.solution_button.pack(side=tk.LEFT, padx=25)
            if master.show_solutions:
                self.solution_button.state(["disabled"])
            else:
                self.solution_button.state(["!disabled"])

        if master.display_answer:
            self.peek_button.pack_forget()
            self.solution_button.pack_forget()
            self.next_button.pack()

    @staticmethod
    def peek():
        window.show_solutions = not window.show_solutions
        window.points.peek(window.show_solutions)
        window.draw_navigation()
        window.draw_entry_fields()

    @staticmethod
    def compare():
        global time_after_compare
        window.display_answer = True
        time_after_compare = time.time()
        window.draw_navigation()
        window.compare_working()

    @staticmethod
    def begin_question():
        global time_after_ready
        window.question_active = not window.question_active
        window.show_solutions = not window.show_solutions
        time_after_ready = time.time()
        return window.draw_window()

    @staticmethod
    def next_question():
        global current_question
        global number_of_incorrect
        global number_of_correct
        global number_of_peeks
        global data
        data['Question number'].append(current_question)
        data['# correct responses'].append(number_of_correct)
        data['# incorrect responses'].append(number_of_incorrect)
        data['# peeks'].append(number_of_peeks)
        calculate_time()
        dump_data()
        current_question += 1
        number_of_incorrect = 0
        number_of_correct = 0
        number_of_peeks = 0
        return window.reset_window()


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        for row in range(2, 7):
            self.grid_rowconfigure(row, weight=1)
        for column in range(2):
            self.grid_columnconfigure(column, weight=1)
        self.title("Cover, Copy and Compare - Equation of a Straight Line Given Two Points")
        self.geometry(f"{WIDTH}x{HEIGHT}+10+10")
        self.resizable(0, 0)

        self.show_solutions = True
        self.question_active = False
        self.display_answer = False

        mathematical_font = ttk.Style()
        mathematical_font.configure('maths.TLabel', font=('STIXGeneral', 15))
        text_font = ttk.Style()
        text_font.configure('TLabel', font=('Verdana', 13))

        self.points = Points(self)
        self.questions = Questions(self)
        self.guidance = [Guidance(self, t) for t in GUIDANCE]
        self.solutions = [Solutions(self, t) for t in question_model[current_question][1]]
        self.entries = [Entry(self, t) for t in question_model[current_question][1]]
        self.navigation = Navigation(self)

        self.bind_all('/', self.replace_character)
        self.bind_all('*', self.replace_character)

        self.draw_window()

    def draw_window(self):
        self.points.grid(row=0, column=0, sticky='w')
        self.questions.grid(row=1, column=0, columnspan=2)
        self.draw_entry_fields()
        self.draw_navigation()

    def draw_entry_fields(self):
        if self.show_solutions:
            for index, (entry, answer, guidance) in enumerate(zip(self.entries, self.solutions, self.guidance)):
                entry.grid_forget()
                guidance.grid(row=index + 2, column=0, sticky='w')
                answer.grid(row=index + 2, column=1)
        else:
            for index, (entry, answer, guidance) in enumerate(zip(self.entries, self.solutions, self.guidance)):
                answer.grid_forget()
                guidance.grid(row=index + 2, column=0, sticky='w')
                entry.grid(row=index + 2, column=1)

    def draw_navigation(self):
        self.navigation.draw_buttons(self)
        self.navigation.grid(row=7, columnspan=2)

    def compare_working(self):
        for index, (guidance, answer, entry) in enumerate(zip(self.guidance, self.solutions, self.entries)):
            guidance.grid_forget()
            answer.grid(row=index + 2, column=0, padx=(50, 0))
            entry.check_correct(index)

    def reset_window(self):
        self.questions.destroy()
        for answers, entry in zip(self.solutions, self.entries):
            answers.destroy()
            entry.destroy()
        self.show_solutions = True
        self.question_active = False
        self.display_answer = False
        self.questions = Questions(self)
        self.guidance = [Guidance(self, t) for t in GUIDANCE]
        self.solutions = [Solutions(self, t) for t in question_model[current_question][1]]
        self.entries = [Entry(self, t) for t in question_model[current_question][1]]
        self.navigation = Navigation(self)
        self.draw_window()

    @staticmethod
    def replace_character(event):
        character_exchange = {'/': '÷', '*': '×'}
        index = 0
        symbol = ''
        for i, char in enumerate(event.widget.get()):
            if char in character_exchange:
                index = i
                symbol = character_exchange[char]
                break
        event.widget.delete(index)
        event.widget.insert(index, symbol)


if __name__ == '__main__':
    window = MainWindow()
    window.mainloop()
