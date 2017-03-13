import socket
import struct
import sys
import datetime
import argparse
from collections import defaultdict
from time import localtime, strftime

__project__ = 'Chatem'
__author__ = 'Theo Linnemann'

USER_DB = defaultdict()
SYSTEM_UN = "System"
SYSTEM_MESSAGES = ["Socket bound, service up. Awaiting connections.","Incoming connection! Accepting.","WARNING: Target user not found! User will be registered and assimilated.",
                   "Target user found. Retrieving user data...","Target user data retrieved. Transmitting...", "User data transmission complete."]

def unpack_registration(reg_buff):
    tuple = struct.unpack('!16s16s16s', reg_buff[:48])
    (UID, user_addr, DID) = tuple
    UID = UID.decode('utf-8')
    user_addr = user_addr.decode('utf-8')
    DID = DID.decode('utf-8')
    return (UID, user_addr, DID)


def pack_registration_response(resp, dest_addr):
    header_buff = bytearray(18)
    dest_addr = dest_addr + ' ' * (16 - len(dest_addr))
    header_buff = struct.pack('!H16s', resp, dest_addr.encode('utf-8'))
    return header_buff

def printIncomingMessage(user, message):
    print(strftime("%a, %d %b %Y %X ", localtime()))
    print(user + ': ' + message)
    print('')

def main(argv):
    # READY THE PARSER FOR PARSING THE PARSEE'S
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', help="Specify the port to bind the directory service to..", type=int)

    args = parser.parse_args()

    printIncomingMessage(SYSTEM_UN,SYSTEM_MESSAGES[0])
    print("------------------------------------------------------------------------------------------------------------")
    while True:
        port = args.port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.bind(("127.0.0.1", port))
        s.listen(15)

        c, a = s.accept()

        printIncomingMessage(SYSTEM_UN, SYSTEM_MESSAGES[1])

        incoming_data = c.recv(4096)

        uid, target_add, DID = unpack_registration(incoming_data)
        uip, userport = target_add.split(":")
        full_target_a = (uip, int(userport))

        USER_DB[uid] = target_add

        if DID in USER_DB:
            printIncomingMessage(SYSTEM_UN, SYSTEM_MESSAGES[3])

            return_addr = USER_DB[DID]
            printIncomingMessage(SYSTEM_UN, SYSTEM_MESSAGES[4])
            response_to_send = pack_registration_response(400, return_addr)

            c.sendto(response_to_send, full_target_a)

            c.shutdown(0)
            c.close()
            printIncomingMessage(SYSTEM_UN, SYSTEM_MESSAGES[5])

        else:
            printIncomingMessage(SYSTEM_UN, SYSTEM_MESSAGES[2])
            response_to_send = pack_registration_response(600, "!REGISTERED")
            c.sendto(response_to_send, full_target_a)
            c.shutdown(0)
            c.close()


if __name__ == "__main__":
    run_date = datetime.datetime.now()
    print('Running...', __project__, 'by', __author__, 'on', run_date.strftime("%m-%d-%Y"))
    main(sys.argv[1:])
    sys.exit(0)