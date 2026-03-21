import math
import re
from fractions import Fraction
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# ==========================================
# ------------------ Utility math functions ------------------
# ==========================================

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


# ==========================================
# ------------------ UI Components ------------------
# ==========================================

class LightBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.95, 0.96, 0.98, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class ModernButton(Button):
    def __init__(self, bg_color=(0.95, 0.95, 0.95, 1), txt_color=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  
        self.background_color = (0, 0, 0, 0) 
        self.color = txt_color 
        self.font_size = '28sp'
        self.bold = True
        self.custom_bg = bg_color
        
        self.bind(pos=self.redraw, size=self.redraw, state=self.redraw)

    def redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == 'normal':
                Color(*self.custom_bg)
            else:
                Color(self.custom_bg[0]*0.8, self.custom_bg[1]*0.8, self.custom_bg[2]*0.8, 1)
            
            radius = min(self.width, self.height) / 4.0
            RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])

class NavTab(ToggleButton):
    def __init__(self, target_screen, sm, **kwargs):
        self.target_screen = target_screen
        self.sm = sm
        super().__init__(**kwargs)
        self.group = 'nav_tabs' 
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]
        self.markup = True
        self.bind(state=self.on_state_change, pos=self.update_canvas, size=self.update_canvas)

    def on_state_change(self, instance, value):
        if value == 'down':
            self.sm.current = self.target_screen 
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # 🔨 THE FIX: Force the highlight box to be 1.6x wider than it is tall!
            # This creates a perfect wide pill/rectangle shape like your screenshots.
            box_h = self.height * 0.65
            box_w = box_h * 1.6
            
            x = self.center_x - box_w / 2
            y = self.center_y - box_h / 2
            
            if self.state == 'down':
                Color(*get_color_from_hex("#D35400")) # Deep Orange
                self.color = (1, 1, 1, 1) 
            else:
                Color(0, 0, 0, 0)
                self.color = get_color_from_hex("#7F8C8D") 
                
            RoundedRectangle(pos=(x, y), size=(box_w, box_h), radius=[box_h / 4])

class MasterCalculatorApp(App):
    
    def build(self):
        Window.clearcolor = (0.95, 0.96, 0.98, 1)

        master_layout = BoxLayout(orientation='vertical')
        
        nav_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=200, padding=10, spacing=40)
        with nav_bar.canvas.before:
            Color(0.95, 0.96, 0.98, 1) 
            Rectangle(pos=nav_bar.pos, size=nav_bar.size)

        self.sm = ScreenManager(transition=NoTransition())

        # 🔨 THE FIX: Swapped the broken emoji for a bold "H" that Pydroid 3 can render safely
        tab1 = NavTab(text="[size=35sp][b]½[/b][/size]", target_screen='frac', sm=self.sm, state='down')
        tab2 = NavTab(text="[size=35sp][b]=[/b][/size]", target_screen='calc', sm=self.sm)
        tab3 = NavTab(text="[size=35sp][b]H[/b][/size]", target_screen='hist', sm=self.sm)
        
        nav_bar.add_widget(Widget(size_hint_x=0.5))
        nav_bar.add_widget(tab1)
        nav_bar.add_widget(tab2)
        nav_bar.add_widget(tab3)
        nav_bar.add_widget(Widget(size_hint_x=0.5))

        # ==========================================
        # SCREEN 1: FRACTIONS
        # ==========================================
        frac_screen = Screen(name='frac')
        frac_layout = LightBoxLayout(orientation='vertical', padding=15, spacing=15)
        
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=10)
        lbl = Label(text="[b][color=#34495E]Fraction:[/color][/b]", markup=True, font_size='22sp', size_hint_x=0.35, halign='right', valign='middle')
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
        frac_layout.add_widget(top_bar)
        
        scroll = ScrollView(size_hint_y=0.5)
        self.output = Label(
            text="[color=#7F8C8D][i]Math results will appear here...[/i][/color]", 
            markup=True, size_hint_y=None, valign='top', padding=(10, 10), color=(0.2, 0.2, 0.2, 1)
        )
        self.output.bind(
            width=lambda *x: self.output.setter('text_size')(self.output, (self.output.width, None)),
            texture_size=lambda *x: self.output.setter('height')(self.output, self.output.texture_size[1])
        )
        scroll.add_widget(self.output)
        frac_layout.add_widget(scroll)
        
        kb_layout = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=10)
        rows = [
            [('7', 1), ('8', 1), ('9', 1), ('DEL', 1)],
            [('4', 1), ('5', 1), ('6', 1), ('÷', 1)],
            [('1', 1), ('2', 1), ('3', 1), ('x', 1)],
            [('Clear', 1), ('0', 1), ('/', 1), ('-', 1)]
        ]
        
        light_blue = get_color_from_hex("#ECF0F1") 
        primary_blue = get_color_from_hex("#2980B9") 
        pure_white = (1, 1, 1, 1) 
        light_gray = get_color_from_hex("#BDC3C7") 
        black_text = (0.2, 0.2, 0.2, 1)
        
        for row in rows:
            row_layout = BoxLayout(orientation='horizontal', spacing=10)
            for text, weight in row:
                bg_color, text_color = pure_white, black_text
                if text == 'DEL': bg_color = light_gray
                elif text == 'Clear': 
                    bg_color, text_color = get_color_from_hex("#FFCDD2"), get_color_from_hex("#C0392B")
                elif text in ['÷', 'x', '-', '/']:
                    bg_color, text_color = light_blue, primary_blue
                
                btn = ModernButton(text=f"{text}", size_hint_x=weight, bg_color=bg_color, txt_color=text_color)
                if len(text) > 1: btn.font_size = '22sp'
                
                if text == 'DEL': btn.bind(on_press=self.backspace)
                elif text == 'Clear': btn.bind(on_press=self.clear_all)
                else: btn.bind(on_press=lambda instance, t=text: self.type_char(t))
                row_layout.add_widget(btn)
            kb_layout.add_widget(row_layout)
            
        bottom_row = BoxLayout(orientation='horizontal', spacing=10)
        btn_solve = ModernButton(text="Solve", font_size='28sp', size_hint_x=3, bg_color=get_color_from_hex("#2ECC71"), txt_color=(1,1,1,1))
        btn_solve.bind(on_press=self.solve_fraction_action)
        btn_plus = ModernButton(text="+", size_hint_x=1, bg_color=light_blue, txt_color=primary_blue)
        btn_plus.bind(on_press=lambda instance, t='+': self.type_char(t))
        
        bottom_row.add_widget(btn_solve)
        bottom_row.add_widget(btn_plus)
        kb_layout.add_widget(bottom_row)
        frac_layout.add_widget(kb_layout)
        
        frac_screen.add_widget(frac_layout)
        self.sm.add_widget(frac_screen)

        # ==========================================
        # SCREEN 2: CALCULATOR 
        # ==========================================
        calc_screen = Screen(name='calc')
        calc_layout = LightBoxLayout(orientation='vertical', padding=15, spacing=10)
        
        self.calc_display = TextInput(
            font_size='50sp', readonly=True, halign='right', multiline=False, size_hint_y=0.25,
            background_normal='', background_active='', background_color=(1, 1, 1, 1),
            foreground_color=get_color_from_hex("#2C3E50")
        )
        calc_layout.add_widget(self.calc_display)
        
        calc_grid = GridLayout(cols=4, spacing=10, size_hint_y=0.65)
        calc_buttons = [
            'AC', 'DEL', '%', '÷',
            '7', '8', '9', 'x',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '00', '0', '.', '='
        ]
        
        for text in calc_buttons:
            bg_color, text_color = pure_white, black_text
            if text in ['AC', 'DEL', '%']: bg_color = light_gray
            elif text in ['÷', 'x', '-', '+', '=']:
                bg_color, text_color = primary_blue, (1, 1, 1, 1)
                
            btn = ModernButton(text=text, bg_color=bg_color, txt_color=text_color)
            btn.bind(on_press=self.on_normal_calc_press)
            calc_grid.add_widget(btn)
            
        calc_layout.add_widget(calc_grid)
        calc_layout.add_widget(Widget(size_hint_y=0.10))
        
        calc_screen.add_widget(calc_layout)
        self.sm.add_widget(calc_screen)

        # ==========================================
        # SCREEN 3: HISTORY
        # ==========================================
        hist_screen = Screen(name='hist')
        hist_layout = LightBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        hist_header = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        title_lbl = Label(text="[b][color=#34495E]History[/color][/b]", markup=True, font_size='24sp', halign='left', valign='middle', size_hint_x=0.6)
        title_lbl.bind(size=title_lbl.setter('text_size'))
        hist_header.add_widget(title_lbl)
        
        btn_del_hist = ModernButton(
            text="Delete All", font_size='18sp', size_hint_x=0.4,
            bg_color=get_color_from_hex("#E74C3C"), txt_color=(1, 1, 1, 1)
        )
        btn_del_hist.bind(on_press=self.clear_history)
        hist_header.add_widget(btn_del_hist)
        
        hist_layout.add_widget(hist_header)
        
        self.history_scroll = ScrollView(size_hint_y=0.9)
        self.history_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        self.history_scroll.add_widget(self.history_layout)
        hist_layout.add_widget(self.history_scroll)
        
        self.history = [] 
        hist_screen.add_widget(hist_layout)
        self.sm.add_widget(hist_screen)

        # Assemble Master Layout
        master_layout.add_widget(nav_bar)
        master_layout.add_widget(self.sm)

        return master_layout

    # ==========================================
    # LOGIC ENGINES
    # ==========================================

    def type_char(self, char):
        if char in ['+', '-', 'x', '÷']:
            self.entry.text += f" {char} "
        else:
            self.entry.text += char

    def backspace(self, instance):
        if len(self.entry.text) > 0:
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

    def solve_fraction_action(self, instance):
        text = self.entry.text.strip()
        if not text:
            self.output.text = "[color=#E74C3C][b]Warning: Please enter a fraction.[/b][/color]"
            return
            
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

    def on_normal_calc_press(self, instance):
        text = instance.text
        current = self.calc_display.text
        
        if current == 'Error':
            current = ''
            self.calc_display.text = ''

        if text == 'AC':
            self.calc_display.text = ''
        elif text == 'DEL':
            self.calc_display.text = current[:-1]
        elif text == '=':
            try:
                math_string = current.replace('÷', '/').replace('x', '*')
                math_string = math_string.replace('%', '/100')
                
                val = eval(math_string)
                if isinstance(val, float):
                    val = round(val, 8)
                    
                answer = str(val)
                if answer.endswith('.0'):
                    answer = answer[:-2]
                
                self.calc_display.text = answer
                self.add_to_history(f"{current} = {answer}")
                
            except Exception:
                self.calc_display.text = 'Error'
        else:
            self.calc_display.text += text

    def add_to_history(self, calculation_str):
        self.history.append(calculation_str)
        
        entry = Label(
            text=f"[color=#2C3E50]{calculation_str}[/color]", 
            markup=True, font_size='22sp', size_hint_y=None, halign='left'
        )
        
        entry.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', value[1] + 20)
        )
        
        self.history_layout.add_widget(entry)
        self.history_scroll.scroll_y = 0

    def clear_history(self, instance):
        self.history_layout.clear_widgets()

if __name__ == '__main__':
    MasterCalculatorApp().run()