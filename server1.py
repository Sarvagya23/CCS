import socket
import threading
import bisect
import time
import random

# define the IP address and port number
IP_ADDRESS = '0.0.0.0'
PORT = 8000

# create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Check if needed or not
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the socket object to the IP address and port number
server_socket.bind((IP_ADDRESS, PORT))

# listen for incoming connections
server_socket.listen(1)

# accept incoming connections
print("Waiting for client to connect on port: ", PORT)

seq_f = open("sequence_received.csv", "w")
seq_f.write("seqno,tp\n")

receiver_window_size_csv = open("receiver_window_size.csv", "w")
receiver_window_size_csv.write("window_size,timestamp\n")

# display client's IP address and port number
# print(f"Connected to client: {client_address[0]}:{client_address[1]}")

packets_received = []
packet_counter = 0
last_prcoessed = 0
max_sequence_number = 65536
min_buffer_size = 1024
buffer_size = 4096
max_buffer_size = 32768
packet_size = 1
dropped_packets = []
total_dropped_packets = 0


def sendWindow(to_send,client_socket):
    global prev_ack,max_seq_number,dropped_packets
    data  = ""
    for packet in to_send:
        data += str(packet) + " "
        seq_f.write("{},{}\n".format(packet, time.time()))
    data = data[:-1]
    # print("data: ",data)
    client_socket.send(str.encode(data))

def modifyBufferSize(flag):
    global buffer_size,min_buffer_size,max_buffer_size
    if(flag and (random.randint(1, 100) == 1)):
        buffer_size = min(buffer_size*2 , max_buffer_size)
        receiver_window_size_csv.write("{},{}\n".format(buffer_size, time.time()))
    elif(random.randint(1, 100) == 1):
        buffer_size = max(3*(buffer_size)//4,min_buffer_size)
        receiver_window_size_csv.write("{},{}\n".format(buffer_size, time.time()))

def cal_metrics():
    global last_prcoessed,packets_received,total_dropped_packets
    last_processed_seq_no = packets_received[last_prcoessed]
    dropped_packets = 0
    no_drop = True
    for i in range(last_prcoessed + 1, last_prcoessed + 1000):
        # print(packets_received[i], last_processed_seq_no)
        last_processed_seq_no = last_processed_seq_no % 65536
        if packets_received[i] == last_processed_seq_no + packet_size:
            last_processed_seq_no = packets_received[i]
        # elif((last_processed_seq_no + packet_size - packets_received[i]) > 60000):
            # dropped_packets += (max_sequence_number-last_processed_seq_no)+packets_received[i]
            last_processed_seq_no = packets_received[i]
        else:
            dropped_packets = dropped_packets + 1
            last_processed_seq_no = packets_received[i]
            modifyBufferSize(1)
            no_drop = False
        if no_drop:
            modifyBufferSize(0)
    # print("packets dropped: ", dropped_packets)
    total_dropped_packets += dropped_packets
    print("Packet {} - {}: Dropped Packet - {}, Good Put - {}".format(last_prcoessed, last_prcoessed+1000, (dropped_packets)/1000, (1-((dropped_packets)/1000))))


def handle_client_connection(client_socket): 
    global packet_counter,last_prcoessed,packets_received,buffer_size,dropped_packets
    request = client_socket.recv(1024)
    print ('Received {}'.format(request))
    # to_send = []
    if request == b'network':
        client_socket.send(b'success')
        while True:
            to_send = []

            seq_win = client_socket.recv(buffer_size)
            # print("seq win: ", seq_win)
            if not seq_win:  # no data received within timeout period
                # try:
                #     clientsocket, addr = server_socket.accept()
                #     seq_no = client_socket.recv(1024)
                #     print("Sequence number: ", seq_no)
                #     print("Connection resumed from %s" % str(addr))
                #     break
                # except:
                #     time.sleep(1)
                print('Client stopped sending data. Closing socket.')
                client_socket.close()
                break
            seq_window = seq_win.decode().split(" ")
            for seq_no in seq_window:
                # print("Seq no: ", seq_no)
                # bisect.insort(packets_received, int(seq_no))
                packets_received.append(int(seq_no))
                to_send.append(str(seq_no))
            
            sendWindow(to_send,client_socket)
            packet_counter += len(to_send)
            # print("Packets received: ", len(packets_received))
            # print("Packet Counter: ", packet_counter)
            if packet_counter >= 1000:
                # print("Packets received: ", packets_received)
                packet_counter = 0
                cal_metrics()
                if len(packets_received) >= max_sequence_number / packet_size:
                    packets_received = []
                    last_prcoessed = 0
                else:
                    last_prcoessed = last_prcoessed + 1000


            # client_socket.send(str.encode(str(int(seq_no))))
            # print(packets_received)
            # print("Packet_counter: ", packet_counter)

while True:
    client_sock, address = server_socket.accept()
    print ('Accepted connection from {}:{}'.format(address[0], address[1]))
    try: 
        client_handler = threading.Thread(

            target=handle_client_connection,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()
        client_handler.join() 
    except: 
        print("Client left.")
        client_sock.close()
        # seq_f.close()
    finally:
        print("All of the client's data is received")
        # print("Total dropped packets: ", total_dropped_packets)
        print("Average good put is: ", (10000000-total_dropped_packets)/10000000)
        client_sock.close()
        break