# Pure P2P:
# h1: server
# h2, h3: peers
# h4: the peer who initiate the connection

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.cli import CLI
import time

class MyTopo( Topo ):  
    def __init__( self ):

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches for peer group 1
        Host1 = self.addHost( 'h1' )
        Host2 = self.addHost( 'h2' )
        Host3 = self.addHost( 'h3' )
        Host4 = self.addHost( 'h4' )
        Switch1 = self.addSwitch('s1')
        Switch2 = self.addSwitch('s2')

        # Add hosts and switches for peer group 2
        Host5 = self.addHost( 'h5' )
        Host6 = self.addHost( 'h6' )
        Host7 = self.addHost( 'h7' )
        Host8 = self.addHost( 'h8' )

        # Add links
        self.addLink( Host1, Switch1, cls=TCLink, bw=25)
        self.addLink( Host2, Switch1, cls=TCLink, bw=8)
        self.addLink( Host3, Switch2, cls=TCLink, bw=10)
        self.addLink( Host4, Switch2, cls=TCLink, bw=20)
        self.addLink( Switch1, Switch2)
        self.addLink( Host5, Switch1, cls=TCLink, bw=25)
        self.addLink( Host6, Switch2, cls=TCLink, bw=8)
        self.addLink( Host7, Switch1, cls=TCLink, bw=10)
        self.addLink( Host8, Switch2, cls=TCLink, bw=20)

topo = MyTopo()
net = Mininet(topo=topo, controller=OVSController)
net.start()
h1 = net.get('h1')
h2 = net.get('h2')
h3 = net.get('h3')
h4 = net.get('h4')
h5 = net.get('h5')
h6 = net.get('h6')
h7 = net.get('h7')
h8 = net.get('h8')
print h1.sendCmd('python server1.py')
print h2.sendCmd('python peer.py')
print h3.sendCmd('python peer.py')
print h5.sendCmd('python server2.py')
print h6.sendCmd('python peer.py')
print h7.sendCmd('python peer.py')
print h8.sendCmd('python peer.py')
time.sleep(5)
print h4.cmd('python query.py')


net.stop()
