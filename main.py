import math
import re
from fractions import Fraction
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle

# ------------------ Utility math functions ------------------

def parse_fraction(s: str):
    s = s.strip()
    if '/' in s:
        p, q = s.split('/', 1)
        num = int(p.strip() or 0)
        den = int(q.strip())
    else:
        num = int(s or 0)
        den = 1
    if den == 0:
        raise ZeroDivisionError("Denominator cannot be zero.")
    if den < 0:
        num = -num
        den = -den
    return num, den

def prime_factors_list(n: int):
    factors = []
    if n <= 1: return factors
    a = n
    while a % 2 == 0:
        factors.append(2)
        a //= 2
    f = 3
    limit = int(math.isqrt(a)) + 1
    while f <= limit and a > 1:
        while a % f == 0:
            factors.append(f)
            a //= f
            limit = int(math.isqrt(a)) + 1
        f += 2
    if a > 1:
        factors.append(a)
    return factors

def decimal_long_division_steps(num: int, den: int, max_steps: int = 500):
    logs = []
    sign = '-' if num * den < 0 else ''
    a, b = abs(num), abs(den)
    integer_part = a // b
    remainder = a % b
    
    if remainder == 0:
        logs.append("No fractional part (exact integer).")
        return f"{sign}{integer_part}", logs
        
    digits = []
    remainder_pos = {}
    pos = 0
    while remainder != 0 and remainder not in remainder_pos and pos < max_steps:
        remainder_pos[remainder] = pos
        multiply = remainder * 10
        digit = multiply // b
        new_remainder = multiply % b
        logs.append(f" Step {pos+1}: {remainder} × 10 = {multiply}  ➔  digit = {digit}, rem = {new_remainder}")
        digits.append(str(digit))
        remainder = new_remainder
        pos += 1
        
    if remainder == 0:
        dec_part = ''.join(digits)
        logs.append("Terminating decimal (remainder reached 0).")
        return f"{sign}{integer_part}.{dec_part}", logs
    else:
        start = remainder_pos[remainder]
        non_rep = ''.join(digits[:start])
        rep = ''.join(digits[start:])
        logs.append(f"Remainder {remainder} repeated; cycle starts at position {start+1}.")
        return f"{sign}{integer_part}.{non_rep}({rep})", logs

def mixed_number_steps(num: int, den: int):
    steps = []
    sign = '-' if num * den < 0 else ''
    a, b = abs(num), abs(den)
    integer_part = a // b
    remainder = a % b
    if remainder == 0:
        steps.append(f"No fractional remainder. Value = {sign}{integer_part}")
    else:
        steps.append(f"Mixed number = {sign}{integer_part} and {remainder}/{b}")
    return steps

def reciprocal_steps(num: int, den: int):
    steps = []
    if num == 0:
        steps.append("Reciprocal undefined (numerator = 0).")
        return steps
    rnum, rden = den, num
    if rden < 0:
        rnum, rden = -rnum, -rden
    g = math.gcd(abs(rnum), abs(rden))
    steps.append(f"Initial reciprocal: {rnum}/{rden}")
    if g > 1:
        steps.append(f"Simplifying reciprocal by GCD({abs(rnum)}, {abs(rden)}) = {g}")
        steps.append(f"Simplified reciprocal: {rnum//g}/{rden//g}")
    else:
        steps.append("Reciprocal is already in lowest terms.")
    return steps

def continued_fraction_steps(num: int, den: int):
    logs = []
    a, b = num, den
    cf = []
    while b != 0:
        q = a // b
        r = a % b
        cf.append(q)
        logs.append(f"{a} = {q} × {b} + {r}")
        a, b = b, r
    return cf, logs

def simplify_by_smallest_common_divisor(num: int, den: int):
    steps = []
    sign = '-' if num * den < 0 else ''
    num_abs, den_abs = abs(num), abs(den)

    if den_abs != 0 and num_abs % den_abs == 0:
        q = (num_abs // den_abs)
        if sign: q = -q
        steps.append(f"Denominator {den} divides numerator {num} exactly.")
        return q, 1, steps, True

    g = math.gcd(num_abs, den_abs)
    if g == 1:
        steps.append("Fraction is coprime (already in lowest terms).")
        return num, den, steps, False

    steps.append(f"GCD is {g}. Dividing by prime factors:")
    pf = prime_factors_list(g)
    temp_num, temp_den = num_abs, den_abs
    for p in pf:
        temp_num //= p
        temp_den //= p
        steps.append(f" ÷ {p}  ➔  {temp_num}/{temp_den}")
        
    if sign: temp_num = -temp_num
    return temp_num, temp_den, steps, False

# ------------------ The UI Application Class ------------------

class FractionSolverApp(App):
    
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Forces Android to use the beautiful light-gray background
        with main_layout.canvas.before:
            Color(0.95, 0.96, 0.98, 1) # #F4F6F9
            self.rect = Rectangle(size=Window.size, pos=main_layout.pos)
            
        def update_rect(instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
        main_layout.bind(pos=update_rect, size=update_rect)
        
        # --- FIXED TOP BAR ---
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=10)
        
        lbl = Label(
            text="[b][color=#34495E]Fraction:[/color][/b]", 
            markup=True, font_size='22sp', size_hint_x=0.35, halign='right', valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size')) 
        
        self.entry = TextInput(
            font_size='38sp', multiline=False, readonly=True, halign='center',
            background_normal='', background_active='', background_color=(1, 1, 1, 1), 
            foreground_color=get_color_from_hex("#2980B9"), size_hint_x=0.65
        )
        
        def center_text(instance, *args):
            pad_y = max(0, (instance.height - instance.line_height) / 2)
            instance.padding = [10, pad_y, 10, pad_y]
        self.entry.bind(height=center_text, text=center_text)
        
        top_bar.add_widget(lbl)
        top_bar.add_widget(self.entry)
        main_layout.add_widget(top_bar)
        
        # --- Output Text Area (Scrollable) ---
        scroll = ScrollView(size_hint_y=0.5)
        self.output = Label(
            text="[color=#7F8C8D][i]Math results will appear here...[/i][/color]", 
            markup=True, size_hint_y=None, valign='top', padding=(10, 10)
        )
        self.output.bind(
            width=lambda *x: self.output.setter('text_size')(self.output, (self.output.width, None)),
            texture_size=lambda *x: self.output.setter('height')(self.output, self.output.texture_size[1])
        )
        scroll.add_widget(self.output)
        main_layout.add_widget(scroll)
        
        # --- Custom Keyboard (Perfect Calculator Layout) ---
        kb_layout = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=8)
        
        # Operators are now neatly stacked on the right column!
        rows = [
            [('7', 1), ('8', 1), ('9', 1), ('DEL', 1)],
            [('4', 1), ('5', 1), ('6', 1), ('÷', 1)],
            [('1', 1), ('2', 1), ('3', 1), ('x', 1)],
            [('Clear', 1), ('0', 1), ('/', 1), ('-', 1)]
        ]
        
        for row in rows:
            row_layout = BoxLayout(orientation='horizontal', spacing=8)
            for text, weight in row:
                bg_color = (1, 1, 1, 1) 
                text_color = (0.2, 0.2, 0.2, 1)
                
                if text == 'DEL': 
                    bg_color = get_color_from_hex("#BDC3C7")
                elif text == 'Clear': 
                    bg_color = get_color_from_hex("#FFCDD2")
                    text_color = get_color_from_hex("#C0392B")
                elif text in ['÷', 'x', '-', '/']:
                    bg_color = get_color_from_hex("#ECF0F1")
                    text_color = get_color_from_hex("#2980B9")
                
                btn = Button(
                    text=f"[b]{text}[/b]", markup=True, font_size='28sp' if len(text) <= 1 else '22sp', 
                    size_hint_x=weight, background_normal='', background_down='', 
                    background_color=bg_color, color=text_color
                )
                
                if text == 'DEL': btn.bind(on_press=self.backspace)
                elif text == 'Clear': btn.bind(on_press=self.clear_all)
                else: btn.bind(on_press=lambda instance, t=text: self.type_char(t))
                row_layout.add_widget(btn)
            kb_layout.add_widget(row_layout)
            
        # The Bottom Row: Solve + Addition
        bottom_row = BoxLayout(orientation='horizontal', spacing=8)
        
        btn_solve = Button(
            text="[b]Solve[/b]", markup=True, font_size='28sp', size_hint_x=3,
            background_normal='', background_down='', background_color=get_color_from_hex("#2ECC71"), color=(1,1,1,1)
        )
        btn_solve.bind(on_press=self.solve_fraction)
        
        btn_plus = Button(
            text="[b]+[/b]", markup=True, font_size='28sp', size_hint_x=1,
            background_normal='', background_down='', background_color=get_color_from_hex("#ECF0F1"), color=get_color_from_hex("#2980B9")
        )
        btn_plus.bind(on_press=lambda instance, t='+': self.type_char(t))
        
        bottom_row.add_widget(btn_solve)
        bottom_row.add_widget(btn_plus)
        kb_layout.add_widget(bottom_row)
        
        main_layout.add_widget(kb_layout)
        return main_layout

    # --- Keyboard Actions ---
    def type_char(self, char):
        # Add spaces around math symbols so the equation looks clean!
        if char in ['+', '-', 'x', '÷']:
            self.entry.text += f" {char} "
        else:
            self.entry.text += char

    def backspace(self, instance):
        if len(self.entry.text) > 0:
            # If we are deleting a math symbol with spaces around it, delete the whole block
            if self.entry.text[-1] == ' ':
                self.entry.text = self.entry.text[:-3]
            else:
                self.entry.text = self.entry.text[:-1]

    def clear_all(self, instance):
        self.entry.text = ""
        self.output.text = "[color=#7F8C8D][i]Cleared.[/i][/color]"

    def format_line(self, text, style="body"):
        if style == "title": return f"[size=45sp][b][color=#2C3E50]{text}[/color][/b][/size]\n"
        elif style == "subtitle": return f"[size=30sp][color=#7F8C8D]{text}[/color][/size]\n"
        elif style == "highlight": return f"[size=35sp][b][color=#27AE60]{text}[/color][/b][/size]\n"
        elif style == "h1": return f"\n[size=28sp][b][color=#34495E]{text}[/color][/b][/size]\n"
        elif style == "h2": return f"[size=24sp][b][color=#8E44AD]{text}[/color][/b][/size]\n"
        elif style == "body_bold": return f"[color=#D35400][b]  • {text}[/b][/color]\n"
        else: return f"[color=#2C3E50][font=RobotoMono-Regular]  • {text}[/font][/color]\n"

    def solve_fraction(self, instance):
        text = self.entry.text.strip()
        if not text:
            self.output.text = "[color=#E74C3C][b]Warning: Please enter a fraction.[/b][/color]"
            return
            
        # CHECK IF IT IS AN EQUATION (e.g., 1/2 + 3/4)
        if any(op in text for op in ['+', '-', 'x', '÷']):
            match = re.search(r'([\d/]+)\s*([\+\-x÷])\s*([\d/]+)', text)
            if not match:
                self.output.text = "[color=#E74C3C][b]Error: Invalid equation format.[/b][/color]"
                return
            
            f1_str, op, f2_str = match.groups()
            try:
                n1, d1 = parse_fraction(f1_str)
                n2, d2 = parse_fraction(f2_str)
                frac1 = Fraction(n1, d1)
                frac2 = Fraction(n2, d2)

                if op == '+': res = frac1 + frac2
                elif op == '-': res = frac1 - frac2
                elif op == 'x': res = frac1 * frac2
                elif op == '÷': res = frac1 / frac2

                out = []
                out.append(self.format_line("EQUATION ANALYSIS", "title"))
                out.append(self.format_line(f"Input: {text}", "subtitle"))
                
                if res.denominator == 1:
                    out.append(self.format_line(f"Result: {res.numerator}", "highlight"))
                else:
                    out.append(self.format_line(f"Result: {res.numerator}/{res.denominator}", "highlight"))
                
                out.append(self.format_line("-" * 40, "subtitle"))
                out.append(self.format_line("STEP 1: CALCULATION", "h1"))
                out.append(self.format_line(f"Evaluated {f1_str} {op} {f2_str}", "body"))
                out.append(self.format_line(f"Reduced to lowest terms.", "body"))
                
                self.output.text = "".join(out)
            except Exception as e:
                self.output.text = f"[color=#E74C3C][b]Error: {e}[/b][/color]"
            return

        # OTHERWISE, DO THE STANDARD SINGLE FRACTION ANALYSIS
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
