import socket
import threading
server=('127.0.0.1', 7734)
serverSock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSock.bind(server)
serverSock.listen(5)

clientList={}
rfcList={}
rfcTitle={}

def addResponse(rfcNum,rfcTitle,clientName,clientPort):
    addMessage="P2P-CI/1.0 200 OK\n"\
                "RFC "+rfcNum+" "+rfcTitle+" "+clientName+" "+clientPort
    return addMessage

def lookupResponse(rfcNum):
    if rfcNum in rfcList:
        lookupMessage="P2P-CI/1.0 200 OK\n"
        for clientName in rfcList[rfcNum]:
            lookupMessage+="RFC "+rfcNum+" "+rfcTitle[rfcNum]+" "+clientName+" "+clientList[clientName]+"\n"
    else:
        lookupMessage="P2P-CI/1.0 404 Not Found\n"
    return lookupMessage

def listResponse(rfcTitle,rfcList,clientList):
    listMessage="P2P-CI/1.0 200 OK\n"
    for rfcNum,rfcTitle in rfcTitle.items():
        for clientName in rfcList[rfcNum]:
            listMessage+="RFC "+rfcNum+" "+rfcTitle+" "+clientName+" "+clientList[clientName]+"\n"
    return listMessage

def deleteClient(clentName):
    pass

def p2sRequest(conn):
    request=conn.recv(1024)
    print(request)

while 1:
	conn, addr = serverSock.accept()
	threading.Thread(target=p2sRequest, args=(conn))
serverSock.close()