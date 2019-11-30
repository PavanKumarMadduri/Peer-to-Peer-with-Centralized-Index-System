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
for rfc in rfcPath:
    rfcNum,rfcTitle=rfc.split("-")
    rfcList[int(rfcNum)]=str(rfcTitle)

message=""
for rfcNum,rfcTitle in rfcList.items():
    message+="ADD RFC "+rfcNum+" P2P-CI/1.0\n"\
             "Host: "+hostName+"\n"\
             "Port: "+hostPort+"\n"\
             "Title: "+rfcTitle+"\n"
p2sSocket.sendall(message)

def p2sAddMessage(rfcNum,rfcTitle):
    addMessage="ADD RFC "+rfcNum+" P2P-CI/1.0\n"\
             "Host: "+hostName+"\n"\
             "Port: "+hostPort+"\n"\
             "Title: "+rfcTitle
    return addMessage

def p2sLookupMessage(rfcNum,rfcTitle):
    lookupMessage="LOOKUP RFC "+rfcNum+" P2P-CI/1.0\n"\
                  "Host: "+hostName+"\n"\
                  "Port: "+hostPort+"\n"\
                  "Title: "+rfcTitle
    return lookupMessage

def p2sListMessage():
    listMessage="LIST ALL P2P-CI/1.0\n"\
                "Host: "+hostName+"\n"\
                "Port: "+hostPort
    return listMessage

def p2pGetMessage(rfcNum,rfcHost):
    getRequest="GET RFC "+rfcNum+" P2P-CI/1.0\n"\
            "Host: "+rfcHost+"\n"\
            "OS "+platform.platform()
    return getRequest

def p2sGet():
    rfcNum=input("Enter RFC Number: ")
    rfcTitle=input("Enter RFC Title")
    getRequest="GET-"+rfcNum+"-"+rfcTitle
    p2sSocket.send(getRequest)
    getResponse=p2sSocket.recv(1024)
    print(getResponse)
    # p2pRequest()

def p2sLookup():
    rfcNum=input("Enter RFC Number: ")
    rfcTitle=input("Enter RFC Title: ")
    lookupMessage=p2sLookupMessage(rfcNum,rfcTitle)
    p2sSocket.send(lookupMessage)
    p2sResponse=p2sSocket.recv(1024)
    print(p2sResponse)

def p2sList():
    listMessage=p2sListMessage()
    p2sSocket.send(listMessage)
    listResponse=p2sSocket.recv(1024)
    print(listResponse)

def p2sAdd():
    rfcNum=input("Enter RFC Number: ")
    rfcTitle=input("Enter RFC Title: ")
    addMessage=p2sAddMessage(rfcNum,rfcTitle)
    p2sSocket.send(addMessage)
    p2sResponse=p2sSocket.recv(1024)
    print(p2sResponse)

def p2pRequest(rfcHost,peerPort,rfcNum,rfcTitle):
    p2pSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2pSocket.connect(rfcHost,peerPort)
    rfcRequest=p2pGetMessage(rfcNum,rfcHost)
    p2pSocket.sendall(rfcRequest)
    rfcResponse=p2pSocket.recv(1024)
    print(rfcResponse)
    p2pSocket.close()

def p2pResponse(rfcNum,rfcTitle):
    rfcFile=rfcPath+"/RFC/"+rfcNum+"-"+rfcTitle+".txt"
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
    clientSock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.bind((hostName,hostPort))
    clientSock.listen(5)
    while 1:
        dsocket,_ = clientSock.accept()
        message_received = dsocket.recv(307200)
        print(message_received)
        # response_list = p2pResponse()
        # dsocket.send(response_pickle)
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
        p2sSocket.send("EXIT")
        p2sSocket.close()
        break
    else:
        print("Wrong input.Try again")