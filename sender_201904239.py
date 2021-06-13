# -*- coding: utf-8 -*-
"""
Created on Tue May 11 23:02:24 2021

@author: bonyb
its new version 1.0.4
"""

import sys
import os
import socket

def carry_around_add(a, b):
    c = a + b
    #print("before sum : " + hex(c))
    return (c & 0xffff) + ((c & 0xF0000) >> 16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        result = 0
        #print(i)
        if i < len(msg) - 1:
            hex1 = msg[i]
            #print("hex1 : " + hex1)
            hex2 = msg[i + 1]
            #print("hex2 : " + hex2)
            result = hex1 + hex2
        else:
            result = msg[i]
        #print(result)
        w = int(result, 16)
        #print("data for addition : 0x" + format(w, '04x'))
        s = carry_around_add(s, w)
    #print("before checksum : " + hex(s))
    return ~s & 0xffff

def assemble_header(data):
    udp_length = format(len(data) + 8, '04x')
    data_list = []
    for i in data:
        data_list.append(format(i, '02x'))
    
    #print(data_list)
    
    pseudo_header = ['c0','a8','00','04','c0','a0','00','02','00','11', udp_length[:2], udp_length[2:4]]
    udp_header = ['1f', '40', 'cf', '75', udp_length[:2], udp_length[2:4], '00', '00']
    
    total_header = pseudo_header + udp_header + data_list
    
    cs = checksum(total_header)
    cs = format(cs, '04x')
    #print("### final checksum ###")
    #print(cs)
    
    
    udp_header[6] = cs[:2]
    udp_header[7] = cs[2:4]
    
    return ''.join(pseudo_header) + ''.join(udp_header)

def sender_send(target_file):
    print("sending acknowledgment of command.")
    server_socket.sendto("valid list command.".encode(), addr)
    if os.path.isfile(target_file):
        print("message about file existence sent.")
        server_socket.sendto("file exists!".encode(), addr)
        file_size = os.stat(target_file).st_size
        print("file size in bytes: " + str(file_size))
        #checksum1
        div_number = int(file_size/983)
        merged_header = assemble_header(str(div_number).encode())
        server_socket.sendto((merged_header + str(div_number)).encode(), addr)
        read_file = open(target_file, 'rb')
        ack_number = 0
        one_time_error = False
        is_active = False
        i = 0
        
        while(i < div_number + 1):
            chunk_file = read_file.read(983)
            merged_header = assemble_header(chunk_file)
            chunk_data = str(ack_number) + merged_header + chunk_file.decode()
            
            if one_time_error == True or is_active == False:
                server_socket.sendto(chunk_data.encode(), addr)
            elif one_time_error == False and is_active == True:
                server_socket.sendto(chunk_data.encode(), (addr[0], int(addr[1] + 1)))
                one_time_error = True
            print("sending index : " + str(ack_number))
            try:   
                data, address = server_socket.recvfrom(2000)
                if data.decode() == "NAK":
                    read_file.seek(-983, 1)
                else:
                    ack_number = int(data.decode())
                    print("received ack index : " + str(ack_number))
                    print("packet number " + str(i+1))
                    i += 1
            except socket.timeout:
                print("=======================================================")
                print("timeout! not received packet! resend about prev packet!")
                print("=======================================================")
                read_file.seek(-983, 1)
                print("packet number " + str(i+1))
        print("sent all the files normally!")
        

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('',8000))
#server_socket.setblocking(0)
#server_socket.settimeout(15)
print("server socket created")
print("successful binding. wating for client now...")
data , addr = server_socket.recvfrom(2000)
print(data.decode())


while True:
    data, addr = server_socket.recvfrom(2000)
    data = data.decode()
    #data = data.split(' ')
    print(data)
    
    if data == "201904239":
        #print("received receive command.")
        sender_send("speech_script.txt")
    else:
        print("received wrong number")
        print("system received exit command... closing my socket..")
        server_socket.close()
        sys.exit()
