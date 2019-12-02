import os
import platform
import socket
import time
import threading

hostName=platform.node()
hostPort=1111
server=('server', 7734)

p2sSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2sSocket.connect(server)

rfcList={}
rfcPath=os.getcwd()+'/RFC/'
for rfc in os.listdir(rfcPath):
    rfcNum,rfcTitle=rfc.split("-")
    rfcTitle,_=rfcTitle.split(".")
    rfcList[int(rfcNum)]=str(rfcTitle)

message=""
for rfcNum,rfcTitle in rfcList.items():
    message+="ADD RFC "+str(rfcNum)+" P2P-CI/1.0\n"\
             "Host: "+hostName+"\n"\
             "Port: "+str(hostPort)+"\n"\
             "Title: "+rfcTitle+"\n\n"
p2sSocket.sendall(message.encode('utf-8'))
registerResponse=p2sSocket.recv(1024)
print(registerResponse.decode('utf-8'))

def p2sAddMessage(rfcNum,rfcTitle):
    addMessage="ADD RFC "+str(rfcNum)+" P2P-CI/1.0\n"\
             "Host: "+hostName+"\n"\
             "Port: "+str(hostPort)+"\n"\
             "Title: "+rfcTitle
    return addMessage

def p2sLookupMessage(rfcNum,rfcTitle):
    lookupMessage="LOOKUP RFC "+str(rfcNum)+" P2P-CI/1.0\n"\
                  "Host: "+hostName+"\n"\
                  "Port: "+str(hostPort)+"\n"\
                  "Title: "+rfcTitle
    return lookupMessage

def p2sListMessage():
    listMessage="LIST ALL P2P-CI/1.0\n"\
                "Host: "+hostName+"\n"\
                "Port: "+str(hostPort)
    return listMessage

def p2pGetMessage(rfcNum,rfcHost,title):
    getRequest="GET RFC "+str(rfcNum)+" P2P-CI/1.0\n"\
            "Host: "+rfcHost+"\n"\
            "OS "+platform.platform()+"\n"\
            "Title: "+title
    return getRequest

def p2sGet():
    response=p2sLookup()
    response=response.decode('utf-8')
    res=list(response.split("\n"))
    if "200 OK" in res[0]:
        _,rfc,title,peername,peerport=res[1].split(" ")
        p2pRequest(peername,peerport,rfc,title)
    else:
        print(res)
        return

def p2sLookup():
    rfcNum=input("Enter RFC Number: ")
    rfcTitle=input("Enter RFC Title: ")
    lookupMessage=p2sLookupMessage(rfcNum,rfcTitle)
    p2sSocket.sendall(lookupMessage.encode('utf-8'))
    p2sResponse=p2sSocket.recv(1024)
    return p2sResponse

def p2sList():
    listMessage=p2sListMessage()
    p2sSocket.sendall(listMessage.encode('utf-8'))
    listResponse=p2sSocket.recv(1024)
    print(listResponse)

def p2sAdd():
    rfcNum=input("Enter RFC Number: ")
    rfcTitle=input("Enter RFC Title: ")
    if str(rfcNum)+"-"+rfcTitle+".txt" not in os.listdir(rfcPath):
        print("File not found in the RFC Directory")
    else:
        addMessage=p2sAddMessage(rfcNum,rfcTitle)
        p2sSocket.sendall(addMessage.encode('utf-8'))
        p2sResponse=p2sSocket.recv(1024)
        print(p2sResponse.decode('utf-8'))

def p2pRequest(rfcHost,peerPort,rfcNum,rfcTitle):
    p2pSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2pSocket.connect(('10.160.0.4',int(peerPort)))
    rfcRequest=p2pGetMessage(rfcNum,hostName,rfcTitle)
    p2pSocket.sendall(rfcRequest.encode('utf-8'))
    rfcResponse = ''
    addMessage=''
    while True:
        data = p2pSocket.recv(1024)
        if data:
            rfcResponse += data.decode('utf-8')
        else:
            break
    _,rfcResponse=rfcResponse.split("----")
    file_=open(rfcPath+str(rfcNum)+"-"+rfcTitle+".txt", "w")
    file_.write(rfcResponse[0])
    file_.close()
    p2pSocket.close()
    addMessage=p2sAddMessage(rfcNum,rfcTitle)
    p2sSocket.sendall(addMessage.encode('utf-8'))
    p2sResponse=p2sSocket.recv(1024)
    print(p2sResponse.decode('utf-8'))
    return

def p2pResponse(rfcNum,rfcTitle):
    rfcFile=rfcPath+str(rfcNum)+"-"+rfcTitle+".txt"
    if os.path.isfile(rfcFile):
        response="P2P-CI/1.0 200 OK\n"\
                 "Date: "+time.strftime("%a %d %b %Y %X %Z", time.localtime())+"\n"\
                 "OS: "+platform.platform()+"\n"\
                 "Last-Modified: "+time.ctime(os.path.getmtime(rfcFile))+"\n"\
                 "Content-Length: "+str(os.path.getsize(rfcFile))+"\n"\
                 "Content-Type: text/text\n"
        with open(rfcFile, "r") as data:
            rfc=data.read()
        response=response+"----"+rfc
    else:
        response="P2P-CI/1.0 404 Not Found\n"\
                 "Date: "+time.strftime("%a %d %b %Y %X %Z", time.localtime())+"\n"\
                 "OS: "+platform.platform()+"\n"
    return response

def peerClient():
    data=""
    clientSock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.bind(('10.160.0.3',hostPort))
    clientSock.listen(5)
    while 1:
        dsocket,_ = clientSock.accept()
        message_received = dsocket.recv(307200)
        print(message_received)
        message_received=message_received.decode('utf-8')
        res_split=message_received.split("\n")
        if "P2P-CI/1.0" not in res_split[0]:
            data="P2P-CI/1.0 505 Version Not Supported"
        else:
            _,_,rfcnum,_=res_split[0].split(" ")
            _,title=res_split[3].split(" ")
            data=p2pResponse(rfcnum,title)
        dsocket.sendall(data.encode('utf-8'))
        dsocket.close()

clientThread=threading.Thread(target=peerClient)
clientThread.start()

while True:
    method=input("GET, LIST, LOOKUP, EXIT: ")
    if method=="GET":
        p2sGet()

    elif method=="LIST":
        p2sList()

    elif method=="LOOKUP":
        p2sLookup()

    elif method=="ADD":
        p2sAdd()

    elif method=="EXIT":
        print("Exiting and Closing the connection")
        data="EXIT\nHost: "+hostName
        p2sSocket.sendall(data.encode('utf-8'))
        p2sSocket.close()
        break
    else:
        print("Wrong input.Try again")
clientThread.join()