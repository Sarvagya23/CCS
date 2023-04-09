import socket
import time
import random

# define the IP address and port number of the server
SERVER_IP = '0.0.0.0'
SERVER_PORT = 8000

# create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
client_socket.connect((SERVER_IP, SERVER_PORT))

# send an initial string to the server
client_socket.send(b'network')
response = client_socket.recv(4096)
print(response)

dropped_sequences_csv = open("dropped_sequences.csv", "w")
dropped_sequences_csv.write("Sequence_number,timestamp\n")

sender_window_size_csv = open("sender_window_size.csv", "w")
sender_window_size_csv.write("window_size,timestamp\n")

retransmission_sequences_csv = open("retransmission_sequences.csv", "w")
retransmission_sequences_csv.write("retransmission_sequences,retransmission_count,timestamp\n")

window_size = 8
packet_size = 1
total_packets = 10000000
max_seq_number = 65536
curr_packet_number = 0
dropped_packets = []
total_sent = 0
swt = 0
prev_ack = 0
no_drop = True
retransmission_dict = {}


def toBeOrNotToBe():
    x = random.randint(1, 100)
    return (x == 1)

def retransmission(flag):
    global total_sent
    global dropped_packets
    global retransmission_dict
    global packet

    # print(retransmission_dict)
    index = 0
    while(index < len(dropped_packets)):
        packet = dropped_packets[index]
        retransmission_dict[packet] += 1
        if flag and toBeOrNotToBe():
            index += 1
            dropped_sequences_csv.write("{},{}\n".format(packet, time.time()))
        else:
            client_socket.send(str.encode(str(packet)))
            ack = int(str.encode(str(int((client_socket.recv(4096))))))
            if packet == ack:
                del dropped_packets[index]
                retransmission_sequences_csv.write("{},{},{}\n".format(packet, retransmission_dict[packet], time.time()))
                
# def sendIndividualPacket(packet):
    # global client_socket
    # global prev_ack
    # global max_seq_number
    # global dropped_packets
    # client_socket.send(str.encode(packet))
    # ack = int(str.encode(str(int((client_socket.recv(4096))))))
    # prev_ack = prev_ack % max_seq_number
    # if not(prev_ack + 1 == ack):
    #     dropped_packets.append(prev_ack + 1)
    #     no_drop = False
    # prev_ack = ack  

def sendWindow(to_send):
    global client_socket,dropped_packets,no_drop,window_size
    data  = ""
    for packet in to_send:
        if not toBeOrNotToBe():
            data += str(packet) + " "
        else:
            if window_size > 1:
                window_size = int(window_size / 2)
            # print(window_size)
            print("DROPPED", str(packet))
            dropped_packets.append(int(packet))
            dropped_sequences_csv.write("{},{}\n".format(packet, time.time()))

    data = data[:-1]
    
    client_socket.send(str.encode(data))
    acks = client_socket.recv(1024).decode()
    ack_values = acks.split(" ")
    data = data.split(" ")
    # print("acks: ", ack_values)
    # print("data: ", data)
    j = 0
    for i in range(len(ack_values)):
        try:
            # print("Yo: " , int(str(ack_values[i])), int(str(data[j])))
            if(int(str(ack_values[i])) != int(str(data[j]))):
                dropped_packets.append(int(data[j]))
                no_drop = False
        except ValueError:
            # Handle the case where data[j] cannot be converted to an integer
            print("Unable to convert to int:", data[j])
        
        j += 1
        if(j > len(data)):
            break


def sendPackets():
    global sender_window_size_csv,window_size,seq_number,curr_packet_number,packet_size,dropped_sequences_csv,total_sent,prev_ack,no_drop,dropped_packets
    
    to_send = []
    sender_window_size_csv.write("{},{}\n".format(window_size, time.time()))
    # print ("window_size: ", window_size)
    x = max_seq_number - (curr_packet_number*packet_size+1)
    window_size = min(window_size,total_packets-total_sent)
    for i in range(window_size):
        wrapAround()
        seq_number = curr_packet_number*packet_size+1
        print("Seq Number: ", seq_number)
        to_send.append(str(seq_number))
            # sendIndividualPacket(str(seq_number))
        # else:
        #     if window_size > 1:
        #         window_size = int(window_size / 2)
        #     print("DROPPED", str(seq_number))
        #     dropped_sequences_csv.write("{},{}\n".format(seq_number, time.time()))

        curr_packet_number = curr_packet_number + 1
    sendWindow(to_send)
    total_sent += len(to_send)
    if(len(dropped_packets) >= 100):
        retransmission(1)
    # send stage
    # for packet in to_send:
    #     # print("SND ", packet)
        
    # print("length: ", len(dropped_packets))
    # print(dropped_packets)
    
    if (no_drop):
        window_size = window_size + 1
    no_drop = True

def initialize_map():
    global retransmission_dict
    i = 65536
    while(i > 0):
        retransmission_dict[i] = 0
        i -= 1

def wrapAround():
    global curr_packet_number,max_seq_number,dropped_packets,retransmission_dict,total_sent,total_packets,no_drop,prev_ack

    if curr_packet_number*packet_size > max_seq_number - 1:
        curr_packet_number = 0
        if len(dropped_packets) > 0:
            # retransmission(0)
            retransmission_dict.clear()
            initialize_map()


if response == b'success':
    print("Let the games begin!!!")
    start = time.time()
    initialize_map()
    while(total_sent < total_packets):
        sendPackets()
    
    # retransmission(0)
    print(total_sent)
    
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

