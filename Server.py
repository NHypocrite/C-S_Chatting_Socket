import socket, threading, json


FILE_NAME = "user.txt"
NUM = 0

user = {}
sockets = {}

# 导入已注册的用户名，密码文件
try:
    f=open(FILE_NAME, 'r')
    users = eval(f.read())
    f.close()
except:
    f=open(FILE_NAME, 'w')
    f.write("{'root':'123456'}")
    f.close()
    users = {'root':'123456'}


# 聊天室程序
def chat(service_client_socket, addr):
    global NUM
    mode = False    # 正常登录记号
    while True:
        sign = service_client_socket.recv(1024) # 1. 接收的第一条消息是 注册/登录
        if sign.decode() == 'error1':
            print(addr, "关闭了登录窗口 ")
            exit(0) #  退出此进程
        if sign.decode() == 'log':
            print(addr, "请求登陆")
            while True:
                ret = service_client_socket.recv(1024)  # 2. 请求登录，第二条消息应是账号密码
                # 如果中途关闭窗口，这里传来的应该是utf-8格式的‘error1’
                if ret.decode() == 'error1':
                    print(addr, "关闭了登录窗口 ")
                    exit(0)
                #  正常状态传来的应当是json格式的账号-密码对
                Info = json.loads(ret)
                user_name = Info['name']
                user_passwd = Info['password']
                print(Info)
                if user_name not in users:
                    print("用户名不存在")
                    service_client_socket.send("username is not exist".encode('utf-8')) # 3.发送登录状态
                    break   # 用户名不存在，应重新输入密码再次尝试登录，但是再次点击尝试登录会直接再次发送log指令，所以退出以回到while循环开头，等待接受1.log/reg指令
                else:
                    if user_passwd != users[user_name]:
                        print("密码错误，请重新输入")
                        service_client_socket.send("password is wrong".encode('utf-8')) # 3.发送登录状态
                        break   
                    else:
                        print("登陆成功")
                        mode = True
                        service_client_socket.send("log in".encode('utf-8')) # 3.发送登录状态
                        break
            if mode == True:
                break   # 未能登录成功，回到接受1.之前的状态，即重新等待接受消息1. log/reg，即回到while循环开头
        if sign.decode() == 'reg':
            print(addr, "请求注册")
            while True:
                ret = service_client_socket.recv(1024)  # 2. 请求注册，传来的第二条消息应是账号密码
                if ret.decode() == 'error2':
                    print(addr, "关闭了注册窗口")
                    break

                try:
                    Info = json.loads(ret)
                    user_name = Info['name']
                    user_passwd = Info['password']
                    print(Info)
                    users[user_name] = user_passwd
                except:
                    service_client_socket.send("register failue".encode('utf-8'))   # 3. 发送注册状态
                    print("注册失败")
                    continue

                try:
                    f=open(FILE_NAME, 'w')
                    f.write(str(users))
                    f.close()
                    print("注册成功")
                    service_client_socket.send("register success".encode('utf-8'))  # 3. 发送注册状态
                    break
                except:
                    service_client_socket.send("register failue".encode('utf-8'))   # 3. 发送注册状态
                    continue

# 此时已经登陆成功
    userName = service_client_socket.recv(1024) # 4. 接收用户名
    if not addr in user:  
        print('Accept new connection from %s:%s...' % addr)
        NUM = NUM + 1
        print("当前聊天室人数：", NUM)
        # 向已登入的人员通告新成员
        for scs in sockets: 
            sockets[scs].send(userName + ' 进入聊天室 '.encode('utf-8'))  
            print("向其他成员发送了：",userName.decode('utf-8'),"进入")

        user[addr] = userName.decode('utf-8')
        sockets[addr] = service_client_socket

    while True:
        # 5. 接收新信息
        dataReceived = service_client_socket.recv(1024).decode('utf-8')
        print(addr, dataReceived)
        if ((dataReceived.lower() == 'EXIT'.lower())|(dataReceived == 'error1')):
            # 接收到退出信息
            name = user[addr]   
            user.pop(addr) 
            sockets.pop(addr)     
            for scs in sockets:     
                sockets[scs].send((name + ' 离开了聊天室 ').encode('utf-8'))     
            print('Connection from %s:%s closed.' % addr)
            NUM = NUM - 1
            break
        elif (dataReceived.lower().startswith('#upload'.lower())):    # 用户要上传文件到服务器
            pass
        elif (dataReceived.lower().startswith('#get'.lower())):       # 用户要从服务器下载文件
            pass
        else: 
            # 接收到正常文本信息
            print('"%s" from %s:%s' %(dataReceived, addr[0], addr[1]))  
            for scs in sockets:    
                if sockets[scs] != service_client_socket:  
                    sockets[scs].send(dataReceived.encode('utf-8'))     


# 程序主体部分

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象

addr = ('127.0.0.1', 9999)
s.bind(addr)  # 绑定地址和端口
s.listen(128)
print('TCP Server on', addr[0], ":",addr[1],"......")

while True:
    try:
        print("等待接收客户端的连接请求 ")
        service_client_socket, addr = s.accept()    # 没有新连接时会在此阻塞
        print("接收到客户端的连接请求 ")
    except ConnectionResetError:
        print('Someone left unexcept.')
    # 每个用户的连接建立一个新线程，调用chat函数
    r = threading.Thread(target=chat, args=(service_client_socket, addr), daemon=True) 
    r.start()