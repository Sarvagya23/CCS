import socket
import threading
import bisect
import time

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

# display client's IP address and port number
# print(f"Connected to client: {client_address[0]}:{client_address[1]}")

packets_received = []
packet_counter = 0
last_prcoessed = 0
max_sequence_number = 65536
packet_size = 1

def cal_metrics():
    global last_prcoessed
    global packets_received
    last_processed_seq_no = packets_received[last_prcoessed]
    dropped_packets = 0
    for i in range(last_prcoessed + 1, last_prcoessed + 1000):
        if packets_received[i] == last_processed_seq_no + packet_size:
            last_processed_seq_no = packets_received[i]
        else:
            dropped_packets = dropped_packets + 1
            last_processed_seq_no = last_processed_seq_no + packet_size
    print("Packet {} - {}: Dropped Packet - {}, Good Put - {}".format(last_prcoessed, last_prcoessed+1000, (dropped_packets)/1000, (1-((dropped_packets)/1000))))

seq_f = open("sequence_received.csv", "w")
seq_f.write("seqno,tp\n")

def handle_client_connection(client_socket): 
    global packet_counter
    global last_prcoessed
    global packets_received
    request = client_socket.recv(1024)
    print ('Received {}'.format(request))
    if request == b'network':
        client_socket.send(b'success')
        while True:
            seq_no = client_socket.recv(1024)
            if not seq_no:  # no data received within timeout period
                try:
                    clientsocket, addr = server_socket.accept()
                    seq_no = client_socket.recv(1024)
                    print("Sequence number: ", seq_no)
                    print("Connection resumed from %s" % str(addr))
                    break
                except:
                    time.sleep(1)
                # print('Client stopped sending data. Closing socket.')
                # client_socket.close()
                # break
            seq_no = seq_no.decode()
            bisect.insort(packets_received, int(seq_no))
            # print(packets_received)
            if packet_counter == 1000:
                packet_counter = 0
                cal_metrics()
                if len(packets_received) >= max_sequence_number / packet_size:
                    packets_received = []
                    last_prcoessed = 0
                else:
                    last_prcoessed = last_prcoessed + 1000

            seq_f.write("{},{}\n".format(seq_no, time.time()))

            client_socket.send(str.encode(str(int(seq_no))))
            # print(packets_received)
            packet_counter = packet_counter + 1

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
        client_sock.close()
        break