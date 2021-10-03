from pynput import keyboard
import functools

def function_1():
    print('Function 1 activated')

def function_2():
    print('Function 2 activated')

def test(str):
    print("bye "+str)
    exit(0)

partial=functools.partial(test,"test")

with keyboard.GlobalHotKeys({
        '<alt>+<ctrl>+r': function_1,
        '<alt>+<ctrl>+t': function_1,
        '<alt>+<ctrl>+y': function_2,
        '<alt>+<esc>': partial
        }) as h:
            h.join()
