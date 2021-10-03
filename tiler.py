import subprocess
import re
import os
import sys
from operator import attrgetter
import time
import math
from copy import deepcopy
from tendo import singleton
from pynput import keyboard
import functools
from random import random

class Window:
    def __init__(self,data):
        self.id=data[0]
        self.workspace=data[1]
        self.pid=data[2]
        self.x=int(data[3])-2*BORDER
        self.y=int(data[4])-2*BORDER-2*BORDER_UP
        self.width=int(data[5])+2*BORDER
        self.height=int(data[6])+2*BORDER+BORDER_UP+BORDER_DOWN
        self.name=""

        self.x=int(data[3])-X0
        self.y=int(data[4])-Y0
        self.width=int(data[5])+BORDER_LEFT+BORDER_RIGHT
        self.height=int(data[6])+BORDER_UP+BORDER_DOWN
        self.tiled=(math.remainder(self.x,GRID)+math.remainder(self.y,GRID)+math.remainder(self.width,GRID)+math.remainder(self.height,GRID))==0

        if(self.x<1920):
            self.screen=0
        else:
            self.screen=1

        for i in range(8,len(data)):
            self.name+=data[i]+' '

        if "Terminal" in self.name:
            print(self.name)
            remx=math.remainder(self.width,GRID)
            remy=math.remainder(self.height,GRID)
            self.width-=remx
            self.height-=remy
            self.tiled=(math.remainder(self.x,GRID)+math.remainder(self.y,GRID)+math.remainder(self.width,GRID)+math.remainder(self.height,GRID))==0


    def __str__(self):
        return str(self.workspace)+' '+str(self.screen)+' '+str(self.tiled)+' '+' '+str(self.x)+' '+str(self.y)+' '+str(self.width)+' '+str(self.height)+' '+str(self.name)

def bash(command):
    process = subprocess.Popen(command.split(),stdout=subprocess.PIPE)
    output, error=process.communicate()
    return str(output,"utf-8").replace("\xe2\x80\x94","\n")

def notification(data):
    entire="notify-send -t 500 \""
    try:
        for v in data:
            entire+=str(v)+'\n'
    except TypeError:
        entire+=str(data)
    entire+="\""
    os.system(entire)
    return entire

def printAll(data):
    if isinstance(data,dict):
        for k, v in data.items():
            print(k+"|"+str(v))
    elif isinstance(data,Window):
        print(data.id+"|"+str(data))

def printWindows():
    global window
    printAll(window)

def getActiveWindowID():
    temp=bash("xdotool getactivewindow")
    temp=bash("printf 0x%08x "+temp)
    return str(temp)

def ID():
    return getActiveWindowID

def getActiveWorkspace():
    workspaces=bash("wmctrl -d").split('\n')
    secondName=-10
    activeWorkspace=[]
    for i in range( 0, len(workspaces)-1 ):
        temp=workspaces[i].split(' ')
        if(temp[2]=='*'):
            return i
            #TODO Yeet that line out and add ability to use two workspaces at once
            activeWorkspace.append(i)
            #secondName=int(temp[-1])+int(10)
    for i in range( 0, len(workspaces)-1 ):
        temp=workspaces[i].split(' ')
        if(temp[-1]==secondName):
            activeWorkspace.append(temp[0])
    return activeWorkspace

def loadWindows():
    global window
    window={}
    temp=bash("wmctrl -lGp").split('\n')
    del temp[-1]
    for w in temp:
        w=(re.sub(' +', ' ',(w.replace('\n',' ')))).strip()
        w=w.split(' ')
        #if(w[1]!="-1"):
        if(w[1]==str(ACTIVE_WORKSPACE)):
            window[w[0]]=Window(w)
        #TODO add some better blasting of windows
        #print(window[w[0]])

def loadWindow(id):
    text=""
    if isinstance(id,str):
        text=bash("xdotool getwindowgeometry --shell "+id)
    elif isinstance(id,Window):
        text=bash("xdotool getwindowgeometry --shell "+id.id)
    text=text.split('\n')
    data=[]
    for x in text:
        x=x.split('=')
        data.append(x[-1])

    tempWindow=window[id]
    tempWindow.x=int(data[1])-BORDER
    tempWindow.y=int(data[2])-BORDER-BORDER_UP
    tempWindow.width=int(data[3])+2*BORDER
    tempWindow.height=int(data[4])+2*BORDER+BORDER_UP
    tempWindow.tiled=math.remainder(tempWindow.x,GRID)+math.remainder(tempWindow.y,GRID)+math.remainder(tempWindow.width,GRID)+math.remainder(tempWindow.height,GRID)==0


    tempWindow.x=int(data[1])-BORDER_LEFT
    tempWindow.y=int(data[2])-BORDER_UP
    tempWindow.width=int(data[3])+BORDER_LEFT+BORDER_RIGHT
    tempWindow.height=int(data[4])+BORDER_DOWN+BORDER_UP
    window[id]=tempWindow
    #print(window[id])
    return window[id]
    
def mouse(x,y):
    bash("xdotool mousemove "+str(x)+" "+str(y))

def moveWindow(id,x,y):
    if isinstance(id,Window):
        id=id.id

    bash("timeout 0.1 xdotool windowmove --sync "+id+" "+str(x)+" "+str(y))
    return loadWindow(id)


def resizeWindow(id,x,y):
    if isinstance(id,Window):
        id=id.id
    
    bash("timeout 0.1 xdotool windowsize --sync "+id+" "+str(int(x)-BORDER_LEFT-BORDER_RIGHT)+" "+str(int(y)-BORDER_DOWN-BORDER_UP))
    return loadWindow(id)

def AW():
    global window
    return window[getActiveWindowID()]

def roundWindow(w):
    if(isinstance(w,int) or isinstance(w,str)):
        w=window[str(w)]
    remx=math.remainder(w.x,GRID)
    remy=math.remainder(w.y,GRID)
    w=moveWindow(w,w.x-remx,w.y-remy)
    #TODO add rounding of widnow size too
    #w=loadWindow(w.id)
    #print("x:",remx," y",remy)
    i=0
    #while int(i)<2:
    for i in range(0,2):
        remx=math.remainder(w.x+w.width,GRID)
        remy=math.remainder(w.y+w.height,GRID)
        #printAll(w)
        #print("x:",remx," y",remy)
        w=resizeWindow(w,w.width-remx,w.height-remy)
        i+=1
        if(remx==0 and remy==0): break
    #window[w.id].tiled=True
    return loadWindow(w.id)

def unroundWindow(w):
    if(isinstance(w,int) or isinstance(w,str)):
        w=window[str(w)]

    mar=10
    w=moveWindow(w,w.x+mar,w.y+mar)
    w=resizeWindow(w,w.width-2*mar,w.height-2*mar)
    return loadWindow(w.id)


def moveWindowDirSafe(w,dir):
    if(isinstance(w,int) or isinstance(w,str)):
        w=window[str(w)]

    #w=roundWindow(w)
    modx=0
    mody=0
    if dir=="left": modx=-GRID
    elif dir=="right": modx=GRID
    elif dir =="up": mody=-GRID
    elif dir =="down": mody=GRID

    if(0<=w.x+modx and w.x+w.width+modx<=MARGIN_RIGHT):
        moveWindow(w,w.x+modx,w.y+mody)
        #TODO add some if that won't move window out of the screen like -10000 gozylions or 666 milion pixels right/down
        return loadWindow(w.id)


def moveWindowDir(w,dir):
    if(isinstance(w,int) or isinstance(w,str)):
        w=window[str(w)]

    #w=roundWindow(w)
    modx=0
    mody=0
    if dir=="left": modx=-GRID
    elif dir=="right": modx=GRID
    elif dir =="up": mody=-GRID
    elif dir =="down": mody=GRID

    moveWindow(w,w.x+modx,w.y+mody)
    #TODO add some if that won't move window out of the screen like -10000 gozylions or 666 milion pixels right/down
    return loadWindow(w.id)

def resizeWindowDirSafe(w,dir):
    if(isinstance(w,int) or isinstance(w,str)):
        w=window[str(w)]

    w=roundWindow(w)
    backup=deepcopy(w)
    modx=0
    mody=0
    if dir=="left": modx=-GRID
    elif dir=="right": modx=GRID
    elif dir =="up": mody=-GRID
    elif dir =="down": mody=GRID

    w=resizeWindow(w,w.width+modx,w.height+mody)

    #w=roundWindow(w)
    #return roundWindow(w)
    mar=20

    if(0<=w.x+w.width<=MARGIN_RIGHT and 0<=w.y+w.height<=MARGIN_DOWN
    and -mar<(backup.width+modx-w.width)<mar and -mar<(backup.height+mody-w.height)<mar):
        w=roundWindow(w)
        return w
    else:
        resizeWindow(w.id,backup.width,backup.height)
        #w=roundWindow(w)
        print(backup.width+modx," ",w.width," | ",backup.height+mody," ",w.height)
        print(backup.width+modx-w.width," | ",backup.height+mody-w.height)
        print("Unproper resize!!!! Reverting back!!!")
        roundWindow(w)
        return False



def resizeWindowDir(w,dir):
    if(isinstance(w,int) or isinstance(w,str)):
        w=window[str(w)]

    #w=roundWindow(w)
    modx=0
    mody=0
    if dir=="left": modx=-GRID
    elif dir=="right": modx=GRID
    elif dir =="up": mody=-GRID
    elif dir =="down": mody=GRID

    resizeWindow(w,w.width+modx,w.height+mody)
    #return roundWindow(w)
    return loadWindow(w)

#used to define how 'near' is a window
def score(focused,candidate,dir):
    if isinstance(focused,str):
        focused=window[focused]
    if isinstance(candidate,str):
        candidate=window[candidate]

    mod=1

    #TODO add better secondary if checks
    if(dir=="left" and candidate.x<focused.x):
        return abs(focused.x-candidate.x-candidate.width)+mod*abs(focused.y-candidate.y)
    elif(dir=="right" and candidate.x>focused.x):
        return abs(focused.x+focused.width-candidate.x)+mod*abs(focused.y-candidate.y)
    elif(dir=="down" and candidate.y>focused.y):
        return abs(focused.y-candidate.y-candidate.height)+mod*abs(focused.x-candidate.x)
    elif(dir=="up" and candidate.y<focused.y):
        return abs(focused.y-focused.height-candidate.y)+mod*abs(focused.x-candidate.x)
    return 666666

def isTiled(w):
    if(isinstance(w,int) or isinstance(w,str)):
        w=window[str(w)]
    return math.remainder(w.x,GRID)+math.remainder(w.y,GRID)+math.remainder(w.width,GRID)+math.remainder(w.height,GRID)==0

def getFocusOn(focused,dir):
    if isinstance(focused,str):
        focused=window[focused]
    
    bestScore=666666
    id="NULL"
    #print("Focusing in ",dir," direction")
    for k,v in window.items():
        scr=score(focused,v,dir)
        if( (scr<bestScore) and (k!=focused.id) ):
            bestScore=scr
            id=k
        #print(scr,"|",v.name)
        #printAll(v)
    #print("Best is!!!!")
    #printAll(window[id])
    if(id!="NULL"): return id

def focusOn(focused,dir):
    if isinstance(focused,str):
        focused=window[focused]

    bash("xdotool windowactivate "+getFocusOn(focused,dir))

def focus(focused):
    if isinstance(focused,Window):
        focused=focused.id
    bash("xdotool windowactivate "+str(focused))

#return id of widnow that is tiled and also happends to be nearest at <dir> of focused window
def getTiledWindowOn(focused,dir):
    if(isinstance(focused,int) or isinstance(focused,str)):
        focused=window[str(focused)]

    bestScore=666666
    id="NULL"
    for k,v in window.items():
        if(dir=="right"): test=(focused.x+focused.width==v.x)
        elif(dir=="left"): test=(focused.x==v.x+v.width)
        elif(dir=="down"): test=(focused.y+focused.height==v.y)
        elif(dir=="up"): test=(focused.y==v.y+v.height)

        if(test):
            scr=score(focused,v,dir)
            if( (scr<bestScore) and (k!=focused.id) ):
                bestScore=scr
                id=k
            #print(scr,"|",v.name)
    #print("Best is!!!!")
    #printAll(window[id])
    if(id!="NULL"): return id

def focusTiledWindowOn(focused,dir):
    if(isinstance(focused,int) or isinstance(focused,str)):
        focused=window[str(focused)]

    bash("xdotool windowactivate "+(getTiledWindowOn(focused,dir)))

def swapWindows(focused,candidate):
    if(isinstance(focused,int) or isinstance(focused,str)):
        focused=window[str(focused)]
    if(isinstance(candidate,int) or isinstance(candidate,str)):
        candidate=window[str(candidate)]

    backup=deepcopy(focused)

    moveWindow(focused,candidate.x,candidate.y)
    resizeWindow(focused,candidate.width,candidate.height)
    moveWindow(candidate,backup.x,backup.y)
    resizeWindow(candidate,backup.width,backup.height)

    roundWindow(backup.id)
    roundWindow(candidate.id)

def resizeM(focused,dir):
    print("Tiled resize")
    #1.get list of windows at center (only to resize)
    #2.get list of windows that are sticking to, and will be needed to be moved and resized
    if(isinstance(focused,int) or isinstance(focused,str)):
        focused=window[str(focused)]



    toResize=[]
    toMove=[] #and resize in opposite direction

    backup=[]

    focused=deepcopy(focused)

    for k,v in window.items():
        if( (dir=="left") or (dir=="right")):
            if(v.x==focused.x and v.width==focused.width):
                toResize.append(v.id)
                backup.append(deepcopy(v))
#                resizeWindowDir(k,dir)

            if(v.x==focused.x+focused.width):
                toMove.append(v.id)
                backup.append(deepcopy(v))
#                moveWindowDir(k,dir)
#                resizeWindowDir(k,("left" if dir=="right" else "right"))
        elif( (dir=="up") or (dir=="down")):
            if(v.y==focused.y and v.height==focused.height):
                toResize.append(v.id)
                backup.append(deepcopy(v))
#                resizeWindowDir(k,dir)

            if(v.y==focused.y+focused.height):
                toMove.append(v.id)
                backup.append(deepcopy(v))
                #moveWindowDir(k,dir)
                #resizeWindowDir(k,("up" if dir=="down" else "down"))
    
    test=True

    for id in toResize:
        if(resizeWindowDirSafe(id,dir)==False):
            test=False

    for id in toMove:
        if(dir=="right"):
            if(resizeWindowDirSafe(id,("left" if dir=="right" else "right"))==False):
                test=False
            moveWindowDir(id,dir)
        elif(dir=="left"):
            moveWindowDir(id,dir)
            if(resizeWindowDirSafe(id,("left" if dir=="right" else "right"))==False):
                test=False
        elif(dir=="up"):
            moveWindowDir(id,dir)
            if(resizeWindowDirSafe(id,("up" if dir=="down" else "down"))==False):
                test=False
        elif(dir=="down"):
            if(resizeWindowDirSafe(id,("up" if dir=="down" else "down"))==False):
                test=False
            moveWindowDir(id,dir)

    if(test==False):
        print("something went wrong!!!!!")
        for w in backup:
            resizeWindow(w.id,w.width,w.height)
            roundWindow(w)

#        if( (dir=="up") or (dir=="down")):
#            resizeWindowDir(id,("up" if dir=="down" else "down"))
#            moveWindowDir(id,dir)

    #print("To resize:")
    #print(toResize)
    #print("To Move:")
    #print(toMove)

def closeProgram():
    print("Closing program")
    exit(0)


def execute(command):
    command="timeout 0.1 "+command
    return subprocess.Popen(command,shell=True).wait()

def testImpossibleResize():
    #fucntion that will check 
    temp2 = subprocess.Popen("sleep 2; echo kokoszka",shell=True).wait().stdout
    print(str(temp2))
    #temp = subprocess.call("timeout 0.2 sleep 4",shell=True)
    temp = subprocess.Popen("xdotool windowsize --sync 0x03600005 100 100",shell=True).wait()
    print(str(temp))
    #print(temp)
    '''
    print(execute("xdotool windowsize --sync 0x03600005 100 100"))
    '''

def borders():
    global X0
    global Y0

    global BORDER
    global BORDER_LEFT
    global BORDER_RIGHT
    global BORDER_DOWN
    global BORDER_UP

    X0=0
    Y0=0

    BORDER=0
    BORDER_LEFT=0
    BORDER_RIGHT=0
    BORDER_DOWN=0
    BORDER_UP=0

    aw=str(getActiveWindowID())
    backup=deepcopy( AW() )
    moveWindow(aw,0,0)

    text=bash("xwininfo -id "+aw+" -wm")
    t=re.search('\d+, \d+, \d+, \d+',str(text))
    numbers=t.group(0).split(',')

    loadWindows()

    zero=window[aw]
    #print("ACTIVE")
    printAll(zero)
    X0=int(zero.x)
    Y0=int(zero.y)
    BORDER_LEFT=int(numbers[0].strip())
    BORDER_RIGHT=int(numbers[1].strip())
    BORDER=int(numbers[0].strip())
    BORDER_UP=int(numbers[2].strip())
    BORDER_DOWN=int(numbers[3].strip())

    loadWindows()
    moveWindow(aw,backup.x-X0,backup.y-Y0)
    loadWindow(aw)

    print("X0:",X0," Y0:",Y0," B_L:",BORDER_LEFT,"B_R",BORDER_RIGHT," B_UP:",BORDER_UP," B_DOWN",BORDER_DOWN)
    text=str(X0)+"\n"+str(Y0)+"\n"+str(BORDER_LEFT)+"\n"+str(BORDER_RIGHT)+"\n"+str(BORDER_UP)+"\n"+str(BORDER_DOWN)
    #print(text)
    file1 = open("myfile.txt","w")
    file1.writelines(text)
    file1.close()

def loadBorders():
    global X0
    global Y0
    global BORDER
    global BORDER_LEFT
    global BORDER_RIGHT
    global BORDER_DOWN
    global BORDER_UP

    file1 = open("myfile.txt","r")
    text=file1.readlines()
    X0=int(text[0].strip())
    Y0=int(text[1].strip())
    BORDER_LEFT=int(text[2].strip())
    BORDER_RIGHT=int(text[3].strip())
    BORDER=int(text[3].strip())
    BORDER_UP=int(text[4].strip())
    BORDER_DOWN=int(text[5].strip())
    file1.close()
    #print("X0:",X0," Y0:",Y0," B_L:",BORDER_LEFT,"B_R",BORDER_RIGHT," B_UP:",BORDER_UP," B_DOWN",BORDER_DOWN)
    loadWindows()

def changeWorkspace(dir):
    if dir=="left": delta=-1
    elif dir=="right": delta=1
    elif dir =="up": delta=-1
    elif dir =="down": delta=1
    else: delta=0

    bash("xdotool set_desktop "+str(ACTIVE_WORKSPACE+delta))



#########################################
#                   MAIN                #
#########################################
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running
# VARIABLES
###################
MARGIN_DOWN=1080
MARGIN_RIGHT=3840

GAPS_OUTER=0
GAPS_HORIZONTAL=0
GAPS_VERTICAL=0

X0=0
Y0=0
BORDER=0
BORDER_LEFT=0
BORDER_RIGHT=0
BORDER_DOWN=0
BORDER_UP=0
#TODO add some option that would calcualte these variables automatically
GRID=120



ACTIVE_WORKSPACE=getActiveWorkspace()
# INIT
###################
window={}
loadWindows()
#borders()
loadWindows()
loadBorders()


print(ACTIVE_WORKSPACE)

printWindows()


'''
with keyboard.GlobalHotKeys({
        '<alt>+<esc>': closeProgram
        }) as h:
            h.join()
'''

if(len(sys.argv)==1):
    print("No arguments")
elif(len(sys.argv)==2):
    arg=sys.argv[1]
    if(arg=="testTerminal"):
        id=getActiveWindowID()
        for i in range(600,700):
            resizeWindow(id,i,i)
            loadWindow(id)
            if(window[id].width<i or window[id].height<i):
                print(window[id].width," ",window[id].height)
    elif(arg=="yeet"):
        aw=AW()
        if(aw.tiled==False):
            print("Rounding window!!!")
            roundWindow(aw)
        else:
            print("Unrounding!!!")
            unroundWindow(AW())

        #testImpossibleResize()
        #aw=AW()
        #moveWindow(aw,aw.x,aw.y)
        #resizeWindow(aw,aw.width,aw.height)
    elif(arg=="borders"):
        borders()
    elif(arg=="tiles"):
        print("Tiling windows!!!")
        aw=AW()
        n=0
        screen=0
        for k,v in window.items():
            if(aw.x<1920 and v.x<1920):
                n+=1
                screen=0
                x0=0
            elif(aw.x>=1920 and v.x>=1920):
                n+=1
                screen=1
                x0=1920
        print("There are "+str(n)+" windows on this screen")
        #n=int(random()*10)
        row=math.floor(math.sqrt(n))
        col=math.floor(n/row)
        rest=n-(col*row)
        mod=0
        if rest>0: mod=1
        print("N:",n," col:",col," row:",row," rest",rest," mod:",mod)

        #col+=rest

        width=1920*(1/(col+mod))
        height=1080*(1/row)
        print("Window width:",width," height:",height)
        m=0
        #for m in range(0,col*row):
        for k,v in window.items():
            if v.screen==screen:
                j=int(m/row)
                i=m%(row)
                x=1920*((j)/col)
                y=1080*((i)/row)
                x=width*j
                y=height*i
                if(m==n-1): 
                    if(y+height!=1080):
                        height=1080-y
                        print("Make it fatt!!!",height)
                print(x," ",y)
                print(i," ",j)
                resizeWindow(k,width,height)
                moveWindow(k,x0+x,y)
                m+=1




    print("One argument")
elif(len(sys.argv)==3):
    if(sys.argv[1]=="move"):
        moveWindowDir(AW(),sys.argv[2])
    elif(sys.argv[1]=="resize"):
        aw=AW()
        if(aw.tiled):
            resizeM(aw,sys.argv[2])
        else:
            resizeWindowDir(aw,sys.argv[2])
    elif(sys.argv[1]=="focus"):
        if(len(window)>0):
            aw=AW()
            cand=getTiledWindowOn(aw,sys.argv[2])
            if(cand):
                focusTiledWindowOn(aw,sys.argv[2])
            else:
                w=getFocusOn(aw,sys.argv[2])
                if(w):
                    focus(w)
                else:
                    print("changing workspace")
                    changeWorkspace(sys.argv[2])
        else:
            print("changing workspace")
            changeWorkspace(sys.argv[2])

            
    elif(sys.argv[1]=="focusTiled"):
        #focusTiledWindowOn(AW(),sys.argv[2])
        aw=AW()
        cand=getTiledWindowOn(AW(),sys.argv[2])
        if(cand):
            swapWindows(aw,cand)
        else:
            focusOn(aw,sys.argv[2])
    print("Two arguments")

