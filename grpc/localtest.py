import node
import bulletin
import logging
import argparse

from addr_config import *

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Node")
    parser.add_argument('-o', '--old', action='store', type=int, required=True, 
        help="Number of old committee members")
    parser.add_argument('-n', '--new', action='store', type=int, required=True, 
        help="Number of new committee members")
    args = parser.parse_args()

    king_port = 50050
    initial_port = king_port + 1

    king = "localhost:%d" % king_port
    old_addrs = ["localhost:%d" % (initial_port + i) for i in range(args.old)]
    new_addrs = ["localhost:%d" % (initial_port + args.old + i) for i in range(args.new)]

    config = AddrConfig(king, old_addrs, new_addrs)

    nodes = []
    for addr in [king] + old_addrs + new_addrs:
        nodes.append(node.serve(addr, config, loop=False))

    board = bulletin.BulletinBoard(config)
    board.refresh()
