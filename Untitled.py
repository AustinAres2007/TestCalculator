# -*- coding: utf-8 -*-

command_line = False

import sys
import random

print(f'Booting calculator.\nOS: {sys.platform}\n')

if sys.platform != 'darwin' and not command_line:

    import ui
    import clipboard
    from console import alert, hud_alert

from typing import Generator
from math import modf

global saved_items, debug

π = '3.14159'
debug = True
operators = ['^', '*', '/', '+', '-', '**', '//', '√', '§']
saved_items, stored_calculations, sums = {'pi': π, 'π': π}, {}, []
allowed_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_'
operators_algb = ['**']
operators_illegal = ['√', '§', '|']
power_val = {'√': 2, '§': 3}
allowed_numbers = '0123456789.'
other = ')('

full_list_allowed = list(allowed_numbers)+list(other)+list(operators)+list(allowed_chars)+list(power_val)

class IllegalObject(BaseException):
    pass

# used for getting values ahead of an iterations loop, this can be useful.
def get_forward(string: str) -> list:
    pos_values = []
    
    for char in string:
        if char in full_list_allowed:
            pos_values.append(str(char))
        else:
            break
  

    return pos_values if pos_values else None

def get_forward_v(string: str) -> list:
    pos_values = []
    index = 0
    f = False

    for ind, char in enumerate(string):
        index = ind
        if char in full_list_allowed:
            pos_values.append(str(char)); f = True
        elif f:
            break

    return pos_values, index

def check_illegal(string: str) -> bool:
    for let in string:
        if let in operators:
            return False
    return True


def to_bin(dec: list) -> Generator:
    for diget in dec:
        e = diget

        while e:
            f, e = modf(e / 2)
            f = 1 if f <= 0.5 else 0

            yield str(f)


def process(sender) -> None:
    command = sender.title
    labels: ui.Label = sender.superview['result']

    if command in operators and labels.text[-1] not in operators:
        labels.text += command

    elif command == "=":
        try:

            calc = str(eval(labels.text))

            if labels.text != str(calc):
                stored_calculations[len(stored_calculations)] = str(labels.text)
                labels.text = calc

        except (SyntaxError, ZeroDivisionError):
            labels.text = '0'

    elif command == "AC":
        labels.text = '0'

    elif command == 'C' and len(labels.text) > 1:
        labels.text = labels.text[0:-1]

    elif command == 'B':
        try:
            o = False
            for let in labels.text:
                if let in operators or not int(labels.text):
                    return

            for letter in labels.text:
                if str(letter) in '01':
                    pass
                else:
                    o = True

            if o:
                binary = [_ for _ in to_bin([int(labels.text)])]
                labels.text = str(f"{binary[0]}")

        except ValueError:
            return
    else:
        if command in '0123456789' and labels.text != '0' and len(labels.text) >= 1 and labels.text[0] != 'B':
            labels.text += command

        elif command in '0123456789':
            labels.text = command


def save_result(sender) -> None:
    command: str = sender.title
    variable: ui.TextField = sender.superview['var-input']
    data: ui.Label = sender.superview['result']

    if command[0] == "S":
        for letter in variable.text:
            if letter and letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_1234567890':
                pass
            else:
                return alert('Illegal Character, or no name provided')

        saved_items[str(variable.text)] = str(data.text)
        hud_alert('Saved result to variable: {}'.format(variable.text))

    else:
        try:
            data.text = str(saved_items[variable.text])
        except KeyError:
            alert('No saved calculation with that name.')


def save_sum(sender):
    sum: ui.TextField = sender.superview['var-input']
    if str(sum): sums.append(sum.text)


def clear_memory(*args) -> None:
    if saved_items:
        hud_alert('Cleared saved calculations.')
        saved_items.clear()


def copy_to(sender):
    global debug

    command = sender.superview['var-input'].text

    if command == "Variables":

        saved = 'Algebra Variables:\n'
        data = ''
        for item in saved_items.keys():
            data += f'{item}: {saved_items[item]}\n'

        alert(saved + data[0:len(saved) - 1] if data else saved + 'No Variables')

    elif command == 'Saved':

        saved = 'Saved Calculations:\n'
        calculations = ''

        for calculation in stored_calculations.keys():
            calculations += f'{calculation} - {stored_calculations[calculation]}\n'

        alert(saved + calculations[:-1] if calculations else saved + 'None Saved')

    elif command == 'Sums':
        saved = 'Saved Sums:\n'
        l_sums = ''

        for sum in sums:
            l_sums += f'{sum}\n'

        alert(saved + l_sums[:-1] if l_sums else saved + 'No Sums Saved')
    elif command == 'debug':
        if not debug:
            hud_alert('Active');
            debug = True
        else:
            hud_alert('Disabled');
            debug = False
    else:

        clipboard.set(sender.superview['result'].text)
        hud_alert('Copied to clipboard.')


def algb_calculation_from_memory(sender, cmd_line=False):
    local_variables = {}

    if cmd_line is False:
        variable: ui.TextField = sender.superview['var-input']
        data: ui.Label = sender.superview['result']
        string: str = variable.text
    else:
        string: str = cmd_line

    global debug

    if string:
        # Handles defined variables in the calculation  (Example: you can do: x = 50; x(2) = 50)

        if ';' in string:
            string = list(string)
            char, x_count, str_len_count = None, 0, len(string)

            while x_count < str_len_count:
                x_count += 1
                char = string[x_count-1]

                if char in allowed_chars:
                    variable = ''.join(get_forward(string[x_count-1:len(string)]))
                    x_count += len(variable)
                    value = get_forward_v(string[x_count-1:len(string)])
                    int_value: str = ''.join(value[0])
                    x_count += value[1] - 1

                    for key in saved_items:
                        int_value = int_value.replace(key, saved_items[key])
                    for key in local_variables:
                        int_value = int_value.replace(key, local_variables[key])

                    int_value = str(eval(int_value))
                    local_variables[variable] = int_value

                elif char == ';':
                    string = string[x_count-1:len(string)]; break

        # Switiches existing variables with their respective values (the for statement below is an experiment, will explain later)

        string = [letter for letter in string if letter in list(allowed_chars)+operators+list(allowed_numbers)+list(power_val)+list(other)]
        string = ''.join(string)

        if debug:
            start_point = 0
            for ind in range(len(string)+1):
                variable_space, pv = None, string[start_point:ind]

                if pv in local_variables:
                    variable_space = local_variables
                elif pv in saved_items:
                    variable_space = saved_items

                if variable_space:

                    if ind < len(string) and string[ind] in allowed_chars:
                        string = string[:ind]+'*'+string[ind:]
                    start_point = ind
                else:
                    if pv in operators+list(other):
                        start_point += len(pv)

        for key in saved_items:
            string = string.replace(key, saved_items[key])
        for key in local_variables:
            string = string.replace(key, local_variables[key])

        if debug: print(f'Debug (local and global variables): {saved_items} :local: {local_variables}')

        # Switiches English Mathematical operators with Pythonistic ones
        for i, var in enumerate('^'):
            string = list(''.join(string).replace(var, operators_algb[i]))

        # Inserts asterixs at certain points (Example: 4(2) = 8, but python would need it done like this: 4*(2) this for loop inserts the asterix (*))
        for i in range(len(string)):

            t = i if len(string) - 1 == i else i + 1
            if (str(string[i]) in '0123456789)' and str(string[t]) == '(') or (
                    str(string[i]) == ')' and str(string[t]) in '0123456789'):
                string.insert(t, '*')

        # This following code handles roots (√ for square roots, § for cubed roots)
        a = len(string)
        z_c = z = 0

        if '§' in string or '√' in string:
            while z_c < a:
                z_c += 1
                z = z_c - 1 if z_c - 1 != len(string) else len(string) - 1
                a = len(string)

                local_num = []
                flag_close = flag_open = 0

                if string[z] in '√§':
                    operator = string[z]
                    if string[z - 1] == "(":
                        flag_open += 1

                    for x in range(z, len(string)):
                        try:
                            char = string[z + 1]

                            if char in '0123456789.+*/-':
                                local_num.append(str(char));
                                string.pop(z + 1)

                            elif char == ')':
                                flag_close += 1;
                                string.pop(z + 1)
                                if flag_close >= flag_open: break

                            elif char == '(':
                                flag_open += 1;
                                string.pop(z + 1)


                        except IndexError:
                            break

                    if not local_num: continue
                    if string[z - 1] == '(': string.pop(z - 1)

                    try:
                        root, number = power_val[operator], float(eval(''.join(local_num)))
                        power_root = number ** (1. / root) if number > 0 else (abs(number) ** (1. / root)) * (-1)

                        string.insert(z, str(power_root))

                    except SyntaxError:
                        alert('Invalid Syntax (square root engine)')


        # Tries to compile and compute the given parsed command, if an error is found, read except statements

        try:
            if ''.join(string) == '()':  return

            string = [ce for ce in string if ce not in operators_illegal]

            for local in globals():
                if local in ''.join(string) and local not in ['debug']:
                    raise IllegalObject('A part of your script is in the global variable space.')

            if string and sys.platform != 'darwin' and not command_line:
                final_number = str(eval(''.join(string)))

                data.text = str(final_number)
                sums.append(variable.text)

                if len(final_number) > 18:
                    alert(final_number)

            elif sys.platform == 'darwin' or command_line:
                return str(eval(''.join(string)))

        # Error handlers
        except (SyntaxError, TypeError) as fatal_err:
            alert('Invalid Syntax (complier)')
        except NameError as e:
            alert(str(e))
        except ZeroDivisionError:
            data.text = '0'


if sys.platform != 'darwin' and not command_line:
    v = ui.load_view()
    v.name = "Calculator"
    v.present('sheet')

elif debug or command_line:
    while True:
        cmd = input('Debug Command line: ')
        print(algb_calculation_from_memory(sender=None, cmd_line=cmd))
else:
    print(f'You cannot run the calculator on a MacOS Device, if you want to, enable debug mode within the code. You are running {sys.platform}')

# Bug notes for this program are stated in my notes on my iPad, only peak if your the developer.
