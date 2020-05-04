'''Experiment profile for cloudlab experiments'''

import geni.portal as portal
import geni.rspec.pg as pg

N = 8 # CONFIGURE
BHOST = 'bulletin'

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

M = 2 * N

''' Node Creation '''

# Create Nodes
nodes = []
for n in range(0, M):
    node = request.XenVM('node' + str(n))
    nodes += [node]

bulletin = request.XenVM(BHOST)


''' Networking '''


request.Link(members=(nodes + [bulletin]))


''' VM SETUP '''

# Node Execute Scripts
for n in range(0, M):

    node = nodes[n]

    output = "/local/repository/startup_output.txt"

    nodehost = 'node' + str(n)
    NPORT = '50050'

    i = 0
    if n >= N:
        i = 1
    j = n % N

    node.addService(pg.Execute(shell="sh", command="/local/repository/node.sh " + str(n) + ' ' + str(NPORT) + " >> " + output))

# Bulletin Execute Scripts
bulletin.addService(pg.Execute(shell="sh", command="/local/repository/bulletin.sh"  + " >> " + output))

''' Print Resulting RSpec '''

pc.printRequestRSpec(request)
