import argparse
import datetime
import select
import socket
import struct
import sys
import time
from time import localtime, strftime

__project__ = 'Chatem'
__author__ = 'Theo Linnemann'

SYSTEM_UN = "System"

def encode_message(seqnum, UID, DID, msg, version=150):
    header_buf = bytearray(36)

    UID = UID + ' ' * (16 - len(UID))
    DID = DID + ' '* (16 - len(DID))

    header_buf = struct.pack('!HH16s16s', version, seqnum, UID.encode('utf-8'), DID.encode('utf-8'))
    header_buf = header_buf + msg.encode('utf-8')

    return header_buf

def encode_registration(UID, user_address, DID):
    header_buf = bytearray(48)

    UID = UID + ' ' * (16 - len(UID))
    user_address = user_address + ' ' * (16 - len(user_address))
    DID = DID + ' ' * (16 - len(DID))

    header_buf = struct.pack('!16s16s16s', UID.encode('utf-8'), user_address.encode('utf-8'), DID.encode('utf-8'))

    return header_buf

def decode_message(msg_buf):
    t = struct.unpack('!HH16s16s', msg_buf[:36])
    (ver, seqnum, UID, DID) = t

    UID = UID.decode('utf-8')
    DID = DID.decode('utf-8')
    msg = msg_buf[36:].decode('utf-8')

    return (seqnum, UID, DID, msg)

def decode_registration(reg_buf):
    t = struct.unpack('!H16s', reg_buf[:18])
    (err_code, dest_IP) = t

    dest_IP = dest_IP.decode('utf-8')

    return (err_code, dest_IP)

def printIncomingMessage(user, message):
    print('>' + strftime("%a, %d %b %Y %X ", localtime()))
    print('>' + user + ': ' + message)
    print('>')

def chat(UID, DID, host_IP, dest_IP):
    seqnum = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dip,dp = dest_IP.split(":")
    target_address = (dip, int(dp))

    hip, hp = host_IP.split(":")
    our_addr = (hip, int(hp))

    sock.bind(our_addr)

    START_MESSAGE = "Socket bound. You have the con, Shepherd Commander."
    TComplete = "Transmission complete."
    printIncomingMessage(SYSTEM_UN,START_MESSAGE)

    print("------------------------------------------------------------------------------------------------------------")

    while True:
        r, w, x = select.select([sock, sys.stdin], [], [])

        if sys.stdin in r:
            m = input()
            p = encode_message(seqnum, UID, DID, m, version=150)
            sock.sendto(p, target_address)
            printIncomingMessage(SYSTEM_UN,TComplete)
            seqnum += 1

        if sock in r:
            m, sorc = sock.recvfrom(4096)
            seqnum, sid, destid, mess = decode_message(m)
            usr_from = sid.strip(" ")
            printIncomingMessage(usr_from,mess)

def register_and_lookup(uid, hip, did, dip):
    no_response = True
    target_ip, target_port = dip.split(":")
    directory_service = (target_ip, int(target_port))
    msg = encode_registration(uid, hip, did)
    while no_response:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(directory_service)
        try:
            TRY_REGISTRATION = "Trying to register..."
            printIncomingMessage(SYSTEM_UN,TRY_REGISTRATION)
            sock.sendto(msg, directory_service)
        except socket.error:
            UNKNOWN_SOCKET_ERROR = "WARNING: Packet send failure. Unknown socket error."
            printIncomingMessage(SYSTEM_UN,UNKNOWN_SOCKET_ERROR)
        except:
            UNKNOWN_ERROR = "WARNING: Unknown fatal error."
            printIncomingMessage(SYSTEM_UN,UNKNOWN_ERROR)

        bytes = sock.recv(4096)
        print(bytes)
        (err_code, dest_IP) = decode_registration(bytes)
        if err_code == 400:
                REGISTRATION_SUCCESS = "Registration successful."
                printIncomingMessage(SYSTEM_UN,REGISTRATION_SUCCESS)
                no_response = False
                sock.shutdown(0)
                sock.close()

                return dest_IP
        else:
            ERROR_MESSAGE = "Target user not found. Retrying in 5 seconds."
            printIncomingMessage(SYSTEM_UN,ERROR_MESSAGE)
            time.sleep(5)

def main(argv):
    # READY THE PARSER FOR PARSING THE PARSEE'S
    parser = argparse.ArgumentParser()
    parser.add_argument('-username', help="Specify your username.", type=str)
    parser.add_argument('-hostaddress', help="Specify the host address and port in standard format. Example: 192.168.1.2:5000.", type=str)
    parser.add_argument('-destinationaddress', help="Specify the destination address and port in standard format OR the target username. Example: 192.166.1.8:2000 OR Eve", type=str)
    parser.add_argument('-directoryaddress', help="Specify the address for the directory server and the port on which the service is running in standard format. Example 192.168.1.4:3000", type=str)

    args = parser.parse_args()

    ENABLE_DIR = True
    if ':' in args.destinationaddress:
        ENABLE_DIR = False

    # And we're off!
    if ENABLE_DIR:
        target_IP = register_and_lookup(args.username, args.hostaddress, args.destinationaddress, args.directoryaddress)
        chat(args.username, args.destinationaddress, args.hostaddress, target_IP)
    else:
        chat(args.username, args.destinationaddress, args.hostaddress, args.destinationaddress)

if __name__ == "__main__":
    run_date = datetime.datetime.now()
    print('Running...', __project__, 'by', __author__, 'on', run_date.strftime("%m-%d-%Y"))
    main(sys.argv[1:])
    sys.exit(0)