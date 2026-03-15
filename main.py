from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from fractions import Fraction

# Set a retro arcade dark background
Window.clearcolor = (0.1, 0.1, 0.1, 1)

class FractionSolverApp(App):
    def build(self):
        # Main layout
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Title Label (Neon Green)
        title = Label(
            text="[b]RETRO FRACTION SOLVER[/b]", 
            markup=True, 
            font_size='28sp', 
            color=(0.2, 1, 0.2, 1), 
            size_hint=(1, 0.2)
        )
        self.root.add_widget(title)

        # Inputs Layout (Grid for Fraction 1, Operation, Fraction 2)
        input_grid = GridLayout(cols=3, spacing=10, size_hint=(1, 0.3))
        
        # Fraction 1 Boxes
        box1 = BoxLayout(orientation='vertical', spacing=5)
        self.num1 = TextInput(input_filter='int', font_size='28sp', halign='center', hint_text='Num')
        self.den1 = TextInput(input_filter='int', font_size='28sp', halign='center', hint_text='Den')
        box1.add_widget(self.num1)
        box1.add_widget(self.den1)
        
        # Middle Divider Label
        op_label = Label(text="[b]VS[/b]", markup=True, font_size='30sp', color=(1, 0.8, 0, 1))
        
        # Fraction 2 Boxes
        box2 = BoxLayout(orientation='vertical', spacing=5)
        self.num2 = TextInput(input_filter='int', font_size='28sp', halign='center', hint_text='Num')
        self.den2 = TextInput(input_filter='int', font_size='28sp', halign='center', hint_text='Den')
        box2.add_widget(self.num2)
        box2.add_widget(self.den2)

        input_grid.add_widget(box1)
        input_grid.add_widget(op_label)
        input_grid.add_widget(box2)
        
        self.root.add_widget(input_grid)

        # Buttons Layout (Chunky red and blue)
        btn_grid = GridLayout(cols=4, spacing=10, size_hint=(1, 0.2))
        ops = ['+', '-', 'x', '/']
        for op in ops:
            btn = Button(
                text=f"[b]{op}[/b]", 
                markup=True, 
                font_size='35sp', 
                background_color=(0.8, 0.2, 0.2, 1) if op in ['+', '-'] else (0.2, 0.6, 1, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda instance, o=op: self.calculate(o))
            btn_grid.add_widget(btn)
            
        self.root.add_widget(btn_grid)

        # Result Label
        self.result_label = Label(text="PRESS A BUTTON!", font_size='24sp', color=(1, 1, 1, 1), size_hint=(1, 0.3))
        self.root.add_widget(self.result_label)

        return self.root

    def calculate(self, op):
        try:
            n1 = int(self.num1.text)
            d1 = int(self.den1.text)
            n2 = int(self.num2.text)
            d2 = int(self.den2.text)
            
            if d1 == 0 or d2 == 0:
                self.result_label.text = "ERROR: DIV BY 0"
                self.result_label.color = (1, 0, 0, 1)
                return

            f1 = Fraction(n1, d1)
            f2 = Fraction(n2, d2)

            if op == '+': res = f1 + f2
            elif op == '-': res = f1 - f2
            elif op == 'x': res = f1 * f2
            elif op == '/': res = f1 / f2

            self.result_label.text = f"RESULT: {res.numerator} / {res.denominator}"
            self.result_label.color = (0.2, 1, 0.2, 1) # Neon Green success

        except ValueError:
            self.result_label.text = "ENTER NUMBERS!"
            self.result_label.color = (1, 0.5, 0, 1) # Orange warning

if __name__ == '__main__':
    FractionSolverApp().run()
return f"[color=#D35400][b]  • {text}[/b][/color]\n"
        else: 
            return f"[color=#2C3E50][font=RobotoMono-Regular]  • {text}[/font][/color]\n"

    def solve_fraction(self, instance):
        text = self.entry.text.strip()
        if not text:
            self.output.text = "[color=#E74C3C][b]Warning: Please enter a fraction.[/b][/color]"
            return
            
        try:
            num, den = parse_fraction(text)
        except Exception as e:
            self.output.text = f"[color=#E74C3C][b]Error: {e}[/b][/color]"
            return

        simp_num, simp_den, simp_steps, direct = simplify_by_smallest_common_divisor(num, den)
        
        out = []
        out.append(self.format_line("FRACTION ANALYSIS", "title"))
        out.append(self.format_line(f"Input: {num}/{den}", "subtitle"))
        
        if direct or simp_den == 1:
            final_int = simp_num if direct else (simp_num // simp_den)
            out.append(self.format_line(f"Result: {final_int} (Exact Integer)", "highlight"))
        else:
            out.append(self.format_line(f"Simplified: {simp_num}/{simp_den}", "highlight"))
            dec_repr, _ = decimal_long_division_steps(simp_num, simp_den, 50)
            out.append(self.format_line(f"Decimal: ~ {dec_repr}", "subtitle"))
        
        out.append(self.format_line("-" * 40, "subtitle"))
        out.append(self.format_line("STEP 1: SIMPLIFICATION", "h1"))
        for s in simp_steps: out.append(self.format_line(s, "body"))

        if direct or simp_den == 1:
            out.append(self.format_line("ANALYSIS COMPLETE", "h1"))
            out.append(self.format_line("Fraction reduces perfectly to an integer.", "body"))
            self.output.text = "".join(out)
            return

        out.append(self.format_line("STEP 2: MIXED NUMBER", "h1"))
        for s in mixed_number_steps(simp_num, simp_den): out.append(self.format_line(s, "body_bold"))

        out.append(self.format_line("STEP 3: LONG DIVISION", "h1"))
        dec_repr, dec_logs = decimal_long_division_steps(simp_num, simp_den)
        out.append(self.format_line(f"Final Decimal: {dec_repr}", "body_bold"))
        for s in dec_logs: out.append(self.format_line(s, "body"))

        out.append(self.format_line("STEP 4: ADVANCED", "h1"))
        out.append(self.format_line("[ Reciprocal ]", "h2"))
        for s in reciprocal_steps(simp_num, simp_den): out.append(self.format_line(s, "body"))
        
        out.append(self.format_line("[ Continued Fraction ]", "h2"))
        cf, cf_logs = continued_fraction_steps(simp_num, simp_den)
        out.append(self.format_line(f"Notation: [{', '.join(map(str, cf))}]", "body_bold"))

        self.output.text = "".join(out)

if __name__ == '__main__':
    FractionSolverApp().run()
