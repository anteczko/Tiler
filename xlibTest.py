import Xlib
import os
import Xlib.display

def x11_move_window(window_id_dec, x, y, width, height):
    """ Use x11 library to move window From:
        https://gist.github.com/chipolux/13963019c6ca4a2fed348a36c17e1277
    """


    d = Xlib.display.Display()
    window = d.create_resource_object('window', window_id_dec)
    window.configure(x=x, y=y, width=width, height=height, border_width=0,
                     stack_mode=Xlib.X.Above)

    d.sync()

def getWindow(name):
    #window_id_hex = os.popen("wmctrl -l | "+str(name)).read().strip().split()[0]
    window_id_hex = os.popen("wmctrl -lG | grep "+str(name)).read().strip()
    print(window_id_hex)
    window_id_hex=window_id_hex.split()[0]
    window_id_dec = int(window_id_hex, 16)
    return window_id_dec

id=getWindow("Terminal")
for i in range(800,1000):
    x11_move_window(id,0,0,i,i)
    data = os.popen("wmctrl -lG | grep Terminal").read().strip().split()
    x=int(data[4])
    y=int(data[5])
    if(x!=i): print(i,"|",x," ",i-x)

print("Hello")