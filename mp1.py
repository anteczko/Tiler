from multiprocessing import Process,Pipe

def f(child_conn,msg):
    child_conn.send(msg)
    child_conn.close()