import tkinter as tk
from tkinter import messagebox
import socket, threading, time, json

string=''
def my_string(s_input):
    string = s_input.get()
 
def Send(sock, name):

    if string != '':
        message = name + ' : ' + string
        data = message.encode('utf-8')
        sock.send(data)
        if string.lower() == 'EXIT'.lower():
            exit()
 
 
def recv(sock, name, ChatWindow):
    sock.send(name.encode('utf-8'))
    while True:
        data = sock.recv(1024)

        time_tuple = time.localtime(time.time())
        str = ("{}点{}分".format(time_tuple[3], time_tuple[4]))
        rrecv = tk.Label(ChatWindow, text = data.decode('utf-8'), width = 40, anchor = 'w', bg = 'pink')
        rrecv.pack()

def left(name, rE1, ChatWindow):
    global string
    string = rE1.get()
    Send(s, name)
    if string != '':
        rleft = tk.Label(ChatWindow, text = string, width = 40, anchor = 'e')#发送的消息靠右边
        rleft.pack()
        rE1.delete(0, tk.END)
 
def Creat(name):

    root.destroy()
    ChatWindow = tk.Tk()
    ChatWindow.title("聊天室")
    ChatWindow.geometry("1000x800")
    rL0 = tk.Label(ChatWindow, text = '%s的聊天室'%name, width = 40)
    rL0.pack()
    rL1 = tk.Label(ChatWindow, text = '请输入消息：', width = 20, height = 1)
    rL1.place(x=0, y=450)
    rE1 = tk.Entry(ChatWindow)
    rE1.place(x=250, y=450) 
    rB1 = tk.Button(ChatWindow, text = "发送", command = lambda : left(name, rE1, ChatWindow))  
    rB1.place(x=700, y=450)

    #接收进程
    trecv = threading.Thread(target = recv, args=(s, name, ChatWindow), daemon = True)
    # daemon=True 表示创建的子线程守护主线程，主线程退出子线程直接销毁
    trecv.start()

    ChatWindow.protocol("WM_DELETE_WINDOW", End)
    ChatWindow.mainloop()
    #发送进程

def log():
    s.send("log".encode('utf-8'))
    global usernameEntry, passwordEntry
    username = usernameEntry.get()
    password = passwordEntry.get()
    if username == '':
        messagebox.showinfo("提示", "用户名不能为空")
        return
    if password == '':
        messagebox.showinfo("提示", "密码不能为空")
        return
    
    Info = json.dumps({'name':username, 'password':password}).encode('utf-8')
    s.send(Info)

    while True:
        data = s.recv(1024)
        if data.decode() == 'log in':
            Creat(username)
            break
        elif data.decode() == 'password is wrong':
            messagebox.showinfo("错误", "密码错误，请重新输入")
            passwordEntry.delete(0, tk.END)
            break
        elif data.decode() == 'username is not exist':
            messagebox.showinfo("提示", "用户名不存在")
            usernameEntry.delete(0, tk.END)
            passwordEntry.delete(0, tk.END)
            break

def reg():
    s.send("reg".encode('utf-8'))
    RegWindow = tk.Tk()
    RegWindow.title("注册")
    RegWindow.geometry('800x500')
    RegWindow.resizable(width = False, height = False)

    usernameLabel = tk.Label(RegWindow, text = "用户名:", width = 10, anchor = 'w', font = ("Sylfaen", 12))
    usernameLabel.grid(row = 1, column = 0, padx = (150,0), pady = (30, 0))
    passwordLabel = tk.Label(RegWindow, text = "密码:", width = 10, anchor = 'w', font = ("Sylfaen", 12))
    passwordLabel.grid(row = 2, column = 0, padx = (150,0))
    password2Label = tk.Label(RegWindow, text = "确认密码:", width = 10, anchor = 'w', font = ("Sylfaen", 12))
    password2Label.grid(row = 3, column = 0, padx = (150,0))

    usernameEntry = tk.Entry(RegWindow, width = 20)
    passwordEntry = tk.Entry(RegWindow, width = 20, show = '*')
    password2Entry = tk.Entry(RegWindow, width = 20, show = '*')

    usernameEntry.grid(row = 1, column = 1, padx = (0, 0), pady = (30, 20))
    passwordEntry.grid(row = 2, column = 1, padx = (0, 0), pady = 20)
    password2Entry.grid(row = 3, column = 1, padx = (0, 0), pady = 20 )

    Loginbutton = tk.Button(RegWindow, text = "注册", width = 10, command = lambda : confirm(usernameEntry, passwordEntry, password2Entry, RegWindow))
    Loginbutton.grid(row = 4, column = 1, padx = (100, 0), pady = 30)

    CancelButton = tk.Button(RegWindow, text = "取消", width = 10, command = lambda : cancel(RegWindow))
    CancelButton.grid(row = 4, column = 0, padx = (100, 100))

    RegWindow.protocol("WM_DELETE_WINDOW", lambda : cancel(RegWindow))

    RegWindow.mainloop()

def confirm(usernameEntry, passwordEntry, password2Entry, Window):
    user_name = usernameEntry.get()
    user_passwd = [None, None]

    if ' ' in user_name:
        messagebox.showinfo("错误", "密码中不能含有空格")
        usernameEntry.delete(0, tk.END)
    elif user_name == '':
        messagebox.showinfo("错误", "密码中不能为空")
        usernameEntry.delete(0, tk.END)
    else:
        #设置密码
        while True:
            user_passwd[0]=str(passwordEntry.get())
            if ' ' in str(user_passwd[0]):
                messagebox.showinfo("错误", "密码中不能含有空格")
                passwordEntry.delete(0, tk.END)
                password2Entry.delete(0, tk.END)
            elif user_passwd[0] == '':
                messagebox.showinfo("错误", "密码中不能为空")
                passwordEntry.delete(0, tk.END)
                password2Entry.delete(0, tk.END)
            elif len(user_passwd[0]) < 6:
                messagebox.showinfo("错误", "密码长度太短,至少6位")
            else:
                #再次输入密码
                user_passwd[1] = str(password2Entry.get())
                if user_passwd[0] != user_passwd[1]:
                    messagebox.showinfo("错误", "两次输入的密码不一致")
                    password2Entry.delete(0, tk.END)
                else:
                    password = user_passwd[0]
                    Info = json.dumps({'name':user_name, 'password':password}).encode('utf-8')
                    s.send(Info)
                    while True:
                        data = s.recv(1024)
                        if data.decode() == 'register success':
                            messagebox.showinfo("成功", "注册成功，请重新登陆")
                            Window.destroy()
                            break
                        elif data.decode() == 'register failue':
                            messagebox.showinfo("失败", "注册失败,请重新注册")
                            break
                    break

def cancel(Window):
    s.send("error2".encode('utf-8'))
    Window.destroy()

def End():
    s.send("error1".encode('utf-8'))
    exit(0)   
    
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
server = ('127.0.0.1', 9999)
s.connect(server)#建立连接
#s.send("log".encode('utf-8'))

root = tk.Tk()
root.title("登陆")
root.geometry('800x400')
root.resizable(width = False, height = False)

usernameLabel = tk.Label(root, text = "用户名:", width = 10, anchor = 'w', font = ("Sylfaen", 12))
usernameLabel.grid(row = 1, column = 0, padx = (100,0), pady = (30, 0))
passwordLabel = tk.Label(root, text = "密码:", width = 10, anchor = 'w', font = ("Sylfaen", 12))
passwordLabel.grid(row = 2, column = 0, padx = (100,0))

usernameEntry = tk.Entry(root, width = 20)
passwordEntry = tk.Entry(root, width = 20, show = '*')

usernameEntry.grid(row = 1, column = 1, padx = (0, 0), pady = (30, 20))
passwordEntry.grid(row = 2, column = 1, padx = (0, 0), pady = 20)

Loginbutton = tk.Button(root, text = "登陆", width = 10, command = lambda : log())
Loginbutton.grid(row = 3, column = 1, pady = 30, padx = (200, 0))

RegButton = tk.Button(root, text = "注册", width = 10, command = lambda : reg())
RegButton.grid(row = 3, column = 0, padx = (100, 0))

root.protocol("WM_DELETE_WINDOW", End)

root.mainloop()

s.close()