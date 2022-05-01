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
    mode = False
    while True:
        sign = service_client_socket.recv(1024)
        if sign.decode() == 'error1':
            print(addr, "关闭了登录窗口 ")
            exit(0)
        if sign.decode() == 'log':
            print(addr, "请求登陆")
            while True:
                ret = service_client_socket.recv(1024)
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
                    service_client_socket.send("username is not exist".encode('utf-8'))
                    break
                else:
                    if user_passwd != users[user_name]:
                        print("密码错误，请重新输入")
                        service_client_socket.send("password is wrong".encode('utf-8'))
                        break
                    else:
                        print("登陆成功")
                        mode = True
                        service_client_socket.send("log in".encode('utf-8'))
                        break
            if mode == True:
                break
        if sign.decode() == 'reg':
            print(addr, "请求注册")
            while True:
                ret = service_client_socket.recv(1024)
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
                    print("注册失败")
                    break
                try:
                    f=open(FILE_NAME, 'w')
                    f.write(str(users))
                    f.close()
                    print("注册成功")
                    service_client_socket.send("register success".encode('utf-8'))
                    break
                except:
                    service_client_socket.send("register failue".encode('utf-8'))
                    continue

    data = service_client_socket.recv(1024)
    if not addr in user:  
        print('Accept new connection from %s:%s...' % addr)
        NUM = NUM + 1
        print("聊天室人数：", NUM)
        # 向已登入的人员通告新成员
        for scs in sockets: 
            sockets[scs].send(data + ' 进入聊天室 '.encode('utf-8'))  

        user[addr] = data.decode('utf-8')
        sockets[addr] = service_client_socket

    while True:
        # 接收到新信息
        d = service_client_socket.recv(1024)
        print(addr, d)
        if (('EXIT'.lower() in d.decode('utf-8'))|(d.decode('utf-8') == 'error1')):
            # 退出信息
            name = user[addr]   

            user.pop(addr) 
            sockets.pop(addr)     

            for scs in sockets:     
                sockets[scs].send((name + ' 离开了聊天室 ').encode('utf-8'))     
            print('Connection from %s:%s closed.' % addr)
            
            NUM = NUM - 1
            break
        else: 
            # 正常消息
            print('"%s" from %s:%s' %(d.decode('utf-8'), addr[0], addr[1]))  
            for scs in sockets:    
                if sockets[scs] != service_client_socket:  
                    sockets[scs].send(d)     


# 程序主体部分

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象

addr = ('127.0.0.1', 9999)
s.bind(addr)  # 绑定地址和端口

s.listen(128)

print('TCP Server on', addr[0], ":",addr[1],"......")

while True:
    try:
        print("等待接收客户端的连接请求 ")
        service_client_socket, addr = s.accept()
        print("接收到客户端的连接请求 ")
    except ConnectionResetError:
        print('Someone left unexcept.')

    r = threading.Thread(target=chat, args=(service_client_socket, addr), daemon=True) 
    r.start()