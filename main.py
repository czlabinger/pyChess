import canopen
import time
from waiting import wait

def wait_until(var, value):
    if var == value:
        return True
    return False


def main():

    network = canopen.Network()
    network.connect(channel='can0', interface='socketcan')

    network.scanner.search()
    # We may need to wait a short while here to allow all nodes to respond
    time.sleep(0.05)
    for node_id in network.scanner.nodes:
        print(f"Found node {node_id}!")
        node = add_node(node_id)

    node.rpdo.read()
    node.tpdo.read()


    # [3000/3020/...][0/1/2/...][(0)/1/2/...]

    ###### Betrieb freigeben ######

    # DONE: WAIT SPOS 2 = 1
    wait(lambda: wait_until(node.sdo[0x3020][1][2], 1), timeout_seconds=120, waiting_for="SPOS 2 = 1 (MC = 1)")

    # 1.
    node.tpdo[3000][1][1] = 0 # START = 0
    node.tpdo[3000][1][2] = 0 # HOM = 0
    node.tpdo.save()

    # 2.
    node.tpdo[3000][0][0] = 1 # ENABLE = 1
    node.tpdo.save()

    #DONE: WAIT SCON 0 = 1
    wait(lambda: wait_until(node.sdo[0x3020][0][0], 1), timeout_seconds=120, waiting_for="SCON 0 = 1 (ENABLED = 1)")

    # 3.
    node.tpdo[3000][0][1] = 1 # STOP = 1
    node.tpdo.save()

    #DONE: WAIT SCON 1 = 1
    wait(lambda: wait_until(node.sdo[0x3020][0][1], 1), timeout_seconds=120, waiting_for="SCON 1 = 1 (OPEN = 1)")

    ####### Referenzfahrt durchfuehren ######

    #DONE: WAIT SPOS 1 = 0, SPOS 2 = 1
    #TODO: SET CPOS 1, 2 = 0 // Maybe optional
    #TODO: SET CPOS 3, 4 = 0 // Maybe optional

    wait(lambda: wait_until(node.sdo[0x3020][1][1], 0), timeout_seconds=120, waiting_for="SPOS 1 = 0 (ACK = 0)")
    wait(lambda: wait_until(node.sdo[0x3020][1][2], 1), timeout_seconds=120, waiting_for="SPOS 2 = 1 (MC = 1)")


    # 1.
    node.tpdo[3000][1][2] = 1 # HOM = 1
    node.tpdo.save()

    # 2.
    #DONE: WAIT SPOS 1 = 1
    wait(lambda: wait_until(node.sdo[0x3020][1][1], 1), timeout_seconds=120, waiting_for="SPOS 1 = 1 (ACK = 1)")
    node.tpdo[3000][1][2] = 0 # HOM = 0
    node.tpdo.save()
    #DONE: WAIT SPOS 2, 7 = 1
    wait(lambda: wait_until(node.sdo[0x3020][1][2], 1), timeout_seconds=120, waiting_for="SPOS 2 = 1 (MC = 1)")
    wait(lambda: wait_until(node.sdo[0x3020][1][7], 1), timeout_seconds=120, waiting_for="SPOS 7 = 1 (REF = 1)")

    ####### Satzselektion #######

    #DONE: WAIT SPOS 1 = 0, SPOS 2 = 1
    wait(lambda: wait_until(node.sdo[0x3020][1][1], 0), timeout_seconds=120, waiting_for="SPOS 1 = 0 (ACK = 0)")
    wait(lambda: wait_until(node.sdo[0x3020][1][2], 1), timeout_seconds=120, waiting_for="SPOS 2 = 1 (MC = 1)")
    node.tpdo[3000][1][1] = 0
    node.tpdo[3000][1][2] = 0
    node.tpdo[3000][1][3] = 0
    node.tpdo[3000][1][4] = 0
    node.tpdo.save()


    # 1.
    node.tpdo[3000][0][6] = 0 # Satzselektion
    node.tpdo.save()

    # 2.
    node.tpdo[3001][0] = 3 # Satznummer z.B.: 3
    node.tpdo.save()

    # 3.
    node.tpdo[3000][1][1] = 1 # START = 1
    node.tpdo.save()

    #DONE: CHECK SPOS 2 = 0
    print(node.sdo[0x3020][1][2])

    #DONE: WAIT SPOS 2 = 1
    wait(lambda: wait_until(node.sdo[0x3020][1][2], 1), timeout_seconds=120, waiting_for="SPOS 2 = 1 (MC = 1)") # Fahrt zu ende

    # 4.
    #DONE: WAIT SPOS 1 = 1
    wait(lambda: wait_until(node.sdo[0x3020][1][1], 1), timeout_seconds=120, waiting_for="SPOS 1 = 1 (ACK = 1)")
    node.tpdo[3000][1][1] = 0 # START = 0

    network.disconnect()

if __name__ == "__main__":
    main()
