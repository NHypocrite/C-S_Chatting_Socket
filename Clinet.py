import tkinter as tk
from tkinter import messagebox
import socket
import threading
import time
import json

string = ''


# def my_string(s_input):
#     string = s_input.get()

# # 发送消息函数
# def sendMessage(sock, name):
#     if string != '':
#         message = name + ' : ' + string
#         data = message.encode('utf-8')
#         sock.send(data)
#         # 写在上一层更好吧
#         if string.lower() == 'EXIT'.lower():
#             exit()

# 向聊天室消息窗口中写入时间；消息的函数
def writeChatText(text, chatTextField):
    # 使文本区域可编辑
    chatTextField['state'] = 'normal'
    # 写入消息时间
    time_tuple = time.localtime(time.time())
    timeStr = ("{}:{}:{}\n".format(
        time_tuple[3], time_tuple[4], time_tuple[5]))
    chatTextField.insert('end', timeStr)
    # 写入消息
    chatTextField.insert('end', text+'\n')

    chatTextField['state'] = 'disabled'


# 接收消息进程
def recvProcess(sock, name, ChatWindow, chatTextField):
    # 4. 此时将用户名发送给接收端
    sock.send(name.encode('utf-8'))
    while True:
        data = sock.recv(1024).decode('utf-8')
        # if
        writeChatText(data, chatTextField)
        # writeChatText(data.decode('utf-8'), chatTextField)


# 发送消息并显示到聊天室窗口中
# 改名为sendButton更好吧
def sendButton(name, messageEntry, ChatWindow, chatTextField):
    global string
    string = messageEntry.get()
    if (string == ""):
        return
    # 5. 发送消息
    elif (string.lower() == 'EXIT'.lower()):                # 退出
        s.send(string.encode('utf-8'))
        exit()
    elif (string.lower().startswith('#upload'.lower())):    # 上传
        pass
    elif (string.lower().startswith('#get'.lower())):       # 下载
        pass
    else:
        s.send((name + "：" + string).encode('utf-8'))
        writeChatText("我："+string, chatTextField)
    # 清空输入文本框
    messageEntry.delete(0, tk.END)


# 建立聊天室
def Create(name):

    root.destroy()  # 关闭登录界面
    ChatWindow = tk.Tk()
    ChatWindow.title("公共聊天室")
    # ChatWindow.geometry("800x600")

    # 标题
    chatTitle = tk.Label(ChatWindow, text='%s的聊天界面' % name,
                         bg='grey', fg='white', font=('Arial', 20),  height=2)
    # chatTitle.pack(fill=tk.X, side=tk.TOP)
    chatTitle.grid(row=0, column=0, sticky='we')

    messageLabel = tk.Label(ChatWindow, text='请在此输入消息：',
                            font=('楷体', 16), width=20, height=1)
    messageLabel.grid(row=1, column=0, sticky='ws')
    # 消息输入界面
    messageEntry = tk.Entry(ChatWindow, font=('Arial', 16))
    messageEntry.grid(row=2, column=0, sticky='we')

    # 按下按钮时发送消息
    sendMessageButton = tk.Button(ChatWindow, text="发送", font=(
        'Arial', 16), bg='grey', fg='white', command=lambda: sendButton(name, messageEntry, ChatWindow, chatTextField))
    sendMessageButton.grid(row=3, column=0)

    # 聊天文字区域
    chatTextField = tk.Text(ChatWindow, width=30,
                            height=20, font=('Consolas', 16))
    chatTextField.grid(row=0, column=1, rowspan=4, sticky='nswe')
    chatTextField.insert('1.0', '---------您已加入聊天室--------\n')
    chatTextField['state'] = 'disabled'  # 锁定文本不可编辑

    # 聊天文字区域滚动条
    chatTextScrollbar = tk.Scrollbar(
        ChatWindow, orient='vertical', command=chatTextField.yview)
    chatTextField['yscrollcommand'] = chatTextScrollbar.set
    chatTextScrollbar.grid(row=0, column=2, rowspan=4, sticky='ns')

    # 元素权重，在窗口放大时使用
    ChatWindow.rowconfigure(0, weight=0)
    ChatWindow.columnconfigure(0, weight=1)

    ChatWindow.rowconfigure(1, weight=0)
    ChatWindow.columnconfigure(0, weight=1)

    ChatWindow.rowconfigure(2, weight=0)
    ChatWindow.columnconfigure(0, weight=1)

    ChatWindow.rowconfigure(3, weight=0)
    ChatWindow.columnconfigure(0, weight=1)

    ChatWindow.rowconfigure(1, weight=1)
    ChatWindow.columnconfigure(1, weight=2)

    # 接收进程
    trecv = threading.Thread(target=recvProcess, args=(
        s, name, ChatWindow, chatTextField), daemon=True)
    # daemon=True 表示创建的子线程守护主线程，主线程退出子线程直接销毁
    trecv.start()

    ChatWindow.protocol("WM_DELETE_WINDOW", End)
    ChatWindow.mainloop()


# 登录按钮调用的函数
def log():
    s.send("log".encode('utf-8'))   # 1. 发送登录命令
    # usernameEntry 属于这个函数外部的变量，故需要使用global
    global usernameEntry, passwordEntry
    username = usernameEntry.get()
    password = passwordEntry.get()
    if username == '':
        messagebox.showinfo("提示", "用户名不能为空")
        return
    if password == '':
        messagebox.showinfo("提示", "密码不能为空")
        return

    Info = json.dumps({'name': username, 'password': password}).encode('utf-8')
    s.send(Info)                    # 2. 发送账号密码

    while True:  # 这里while循环是用来定位到指定位置的，起到jmp的作用
        logStatus = s.recv(1024)    # 3. 接受服务器返回的登录状态
        if logStatus.decode() == 'log in':
            Create(username)        # 成功登录，打开聊天室界面
            break
        elif logStatus.decode() == 'password is wrong':
            messagebox.showinfo("错误", "密码错误，请重新输入")
            passwordEntry.delete(0, tk.END)
            break
        elif logStatus.decode() == 'username is not exist':
            messagebox.showinfo("提示", "用户名不存在")
            usernameEntry.delete(0, tk.END)
            passwordEntry.delete(0, tk.END)
            break


# 注册按钮调用的函数：弹出用户注册窗口
def reg():
    s.send("reg".encode('utf-8'))       # 1. 发送注册命令
    RegWindow = tk.Tk()
    RegWindow.title("注册")
    RegWindow.geometry('800x500')
    RegWindow.resizable(width=False, height=False)

    usernameLabel = tk.Label(RegWindow, text="用户名:",
                             width=10, anchor='w', font=("Sylfaen", 12))
    usernameLabel.grid(row=1, column=0, padx=(150, 0), pady=(30, 0))
    passwordLabel = tk.Label(RegWindow, text="密码:",
                             width=10, anchor='w', font=("Sylfaen", 12))
    passwordLabel.grid(row=2, column=0, padx=(150, 0))
    password2Label = tk.Label(RegWindow, text="确认密码:",
                              width=10, anchor='w', font=("Sylfaen", 12))
    password2Label.grid(row=3, column=0, padx=(150, 0))

    usernameEntry = tk.Entry(RegWindow, width=20)
    passwordEntry = tk.Entry(RegWindow, width=20, show='*')
    password2Entry = tk.Entry(RegWindow, width=20, show='*')

    usernameEntry.grid(row=1, column=1, padx=(0, 0), pady=(30, 20))
    passwordEntry.grid(row=2, column=1, padx=(0, 0), pady=20)
    password2Entry.grid(row=3, column=1, padx=(0, 0), pady=20)

    Loginbutton = tk.Button(RegWindow, text="注册", width=10, command=lambda: confirm(
        usernameEntry, passwordEntry, password2Entry, RegWindow))
    Loginbutton.grid(row=4, column=1, padx=(100, 0), pady=30)

    CancelButton = tk.Button(RegWindow, text="取消",
                             width=10, command=lambda: cancel(RegWindow))
    CancelButton.grid(row=4, column=0, padx=(100, 100))

    RegWindow.protocol("WM_DELETE_WINDOW", lambda: cancel(RegWindow))

    RegWindow.mainloop()


# 确认注册按钮 调用的函数
def confirm(usernameEntry, passwordEntry, password2Entry, Window):
    user_name = usernameEntry.get()
    user_passwd = [None, None]
    # 检查用户名是否符合要求
    if ' ' in user_name:
        messagebox.showinfo("错误", "用户名中不能含有空格")
        usernameEntry.delete(0, tk.END)
        return
    elif user_name == '':
        messagebox.showinfo("错误", "用户名不能为空")
        usernameEntry.delete(0, tk.END)
        return
    else:
        # 用户名符合要求，检查密码是否符合要求
        # while True:
            # if ((passwordEntry.get() == "") | (password2Entry.get() == "")):
            #     time.sleep(1)
            # else:
        user_passwd[0] = str(passwordEntry.get())
        if ' ' in str(user_passwd[0]):
            messagebox.showinfo("错误", "密码中不能含有空格")
            passwordEntry.delete(0, tk.END)
            password2Entry.delete(0, tk.END)
            return
        elif user_passwd[0] == '':
            messagebox.showinfo("错误", "密码不能为空")
            passwordEntry.delete(0, tk.END)
            password2Entry.delete(0, tk.END)
            return
        elif len(user_passwd[0]) < 6:
            messagebox.showinfo("错误", "密码长度太短,至少6位")
            return
        else:
            # 检查再次输入密码是否符合要求
            user_passwd[1] = str(password2Entry.get())
            if user_passwd[0] != user_passwd[1]:
                messagebox.showinfo("错误", "两次输入的密码不一致")
                password2Entry.delete(0, tk.END)
                return
            else:
                # 用户名、密码均符合要求，设置密码
                password = user_passwd[0]
                # json.dumps：将 Python 对象编码成 JSON 字符串
                Info = json.dumps(
                    {'name': user_name, 'password': password}).encode('utf-8')
                s.send(Info)    # 2. 发送合法的注册用户名-密码对
                while True:
                    regStatus = s.recv(1024)  # 3. 接收注册状态
                    if regStatus.decode() == 'register success':
                        messagebox.showinfo("成功", "注册成功，请重新登陆")
                        Window.destroy()
                        break
                    elif regStatus.decode() == 'register failue':
                        messagebox.showinfo("失败", "注册失败,请重新注册")
                        break
                # break   # 回到等待发送消息2.的状态


# 关闭窗口（注册后自动关闭或手动退出注册窗口时使用）
def cancel(Window):
    s.send("error2".encode('utf-8'))
    Window.destroy()


# 结束程序（关闭聊天室、登录窗口时使用）
def End():
    s.send("error1".encode('utf-8'))
    exit(0)


# 程序主体部分

# 创建socket对象：
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = ('127.0.0.1', 9999)
s.connect(server)  # 建立连接
# s.send("log".encode('utf-8'))

# 客户端登录界面
root = tk.Tk()
root.title("登陆")
root.geometry('800x400')
root.resizable(width=False, height=False)

usernameLabel = tk.Label(root, text="用户名:", width=10,
                         anchor='w', font=("Sylfaen", 12))
usernameLabel.grid(row=1, column=0, padx=(100, 0), pady=(30, 0))
passwordLabel = tk.Label(root, text="密码:", width=10,
                         anchor='w', font=("Sylfaen", 12))
passwordLabel.grid(row=2, column=0, padx=(100, 0))

usernameEntry = tk.Entry(root, width=20)
passwordEntry = tk.Entry(root, width=20, show='*')

usernameEntry.grid(row=1, column=1, padx=(0, 0), pady=(30, 20))
passwordEntry.grid(row=2, column=1, padx=(0, 0), pady=20)

Loginbutton = tk.Button(root, text="登陆", width=10, command=lambda: log())
Loginbutton.grid(row=3, column=1, pady=30, padx=(200, 0))

RegButton = tk.Button(root, text="注册", width=10, command=lambda: reg())
RegButton.grid(row=3, column=0, padx=(100, 0))

# 定义当用户使用窗口管理器显式关闭窗口时发生的情况
root.protocol("WM_DELETE_WINDOW", End)

root.mainloop()

s.close()
