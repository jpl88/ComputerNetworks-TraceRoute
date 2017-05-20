#Justin Lee(jpl88)
#EECS 325 Project #2

#Imports
import math
import urllib2
import socket
import time
import select

#Definitions
PORTNUMBER = 33434 #Default Traceroute Port Num.
MAXTTL = 32
ICMPPROTOCOL = socket.getprotobyname('icmp')
UDPPROTOCOL = socket.getprotobyname('udp')

#Referenced Code From: https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your
def probe(hostname):
    #Address, Send & Receive Socket Setup
    destAddress = socket.gethostbyname(hostname)
    recvSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMPPROTOCOL)
    recvSocket.bind(("", PORTNUMBER))
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDPPROTOCOL)
    sendSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, MAXTTL)
    #Input length: 1472 b/c Max size 1500, 20 IP header and 8 ICMP header
    datagramInput = "x" * 1472
    #Send into sendSocket
    numBytes = sendSocket.sendto(datagramInput, (hostname, PORTNUMBER))
    #Initial Hops is set to 0
    hops = 0
    #Initial ttl is set to 1
    ttl = 1
    #Start Timer
    initialTime = time.time()
    #Referenced Code From: https://gist.github.com/pklaus/856268
    while True:
        #5 Second until timeout
        timeOut = 5
        ready = select.select([recvSocket], [], [], timeOut)
        elapsedTime = time.time() - initialTime
        if ready[0] == []: # Timeout
            break
        #Get Packet and read the current address from the packet
        try:
            packet, currentAddress = recvSocket.recvfrom(4096)
            currentAddress = currentAddress[0]
        #If error skip the hostname
        except socket.error:
            pass
        #Calculate hops
        hops = MAXTTL - ord(packet[36])
        #If MaxTTL is reached go to the next.
        if currentAddress == destAddress or ttl > MAXTTL:
            break
    #Close the Send and Recv Sockets
    sendSocket.close()
    recvSocket.close()
    #Try and print if no error
    try:
        currentAddress
    except NameError:
        print "Error skipping site %s" % hostname
    else:
        #Print output to console
	print "Traceroute for: %s" % (hostname)
	print "IP Address: %s" % (currentAddress)
	print "Bytes sent: %d" % (numBytes)
	print "RTT: %s" % (elapsedTime)
	print "Total Hops: %s" % (hops)
	print "ICMP Datagram Length: %s" % (len(packet)-28)

# eographicalDistance finds & prints the distance in miles from Case to the router
def geographicalDistance(input_name):
    #Socket Initialization
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Setup Connection to freegeoIP.net
	host = 'freegeoip.net'
	port = 80
	remote_ip = socket.gethostbyname(host)
	s.connect((remote_ip, port))
    #Format and send Get message to freegeoIP.net
    message = "http://freegeoip.net/xml/{}".format(socket.gethostbyname(input_name))
    response = urllib2.urlopen(message)
    #Retrive XML file
    reply = response.read()
	#Parse through XML file to get Lat and long
	latitude = ''
	longitude = ''
	latLine = None
	longLine = None
	latLineCheck = "<Latitude>"
	longLineCheck = "<Longitude>"
	#Find Lat and Log from XML file
	lines = reply.splitlines()
	for line in lines:
		if (len(line) > 10):
			if (line[1:11] == latLineCheck):
				latLine = line
			if (line[1:12] == longLineCheck):
				longLine = line
    #Get Lat Line from Lat
	in_nums = False
	for c in latLine:
		if (c == '>'):
			in_nums = True
		elif (c == '<'):
			in_nums = False
		elif (in_nums):
			latitude += str(c)
    #Get Long Line from Long
	in_nums = False
	for c in longLine:
		if (c == '>'):
			in_nums = True
		elif (c == '<'):
			in_nums = False
		elif (in_nums):
			longitude += str(c)
    #Assign Valies
	latitude = float(latitude)
	longitude = float(longitude)
	# Calculate Distance from My location 41.5042, -81.6084 Case Lat and Long
	dist = latLongDistance(41.5042, -81.6084, latitude, longitude)
	print "Geographical Distance: {} miles".format(dist)

# Referenced Code From: John D. Cook's blog returns distance in miles given 2 lat/long coordinates
def latLongDistance(lat1, long1, lat2, long2):
	# Convert latitude & longitude to spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
    #Latitude = 90 - phi
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    # longitude = theta
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    # Compute spherical distance from spherical coordinates Formula taken from blog
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth
    earth_rad = 3959 # miles
    return (arc*earth_rad)

#Main method that analyzes a text file
def main(target):
    #Reads hostnames from a target text file
    inputFile = open(target, 'r')
    line = inputFile.readline().rstrip()
    while line != '':
        probe(line)
        geographicalDistance(line)
        line = inputFile.readline().rstrip()

#Runes the main method for the target.txt file
if __name__ == "__main__":
    main('targets.txt')
