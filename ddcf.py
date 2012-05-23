from __future__ import division
# DDCF (Windows)
# Dynamic DNS Client for CloudFlare
# Released under the MIT license.
# By: Katie G. <katie@eitak.se>
# r5 (2012-22-05)

# This program requires Python 2, and is tested and built on 2.7.2 (It should work with >2.6)
# It will NOT work on Python 3.
# If your path to the Python executable is different than what I have set it to,
#  it's a good idea to change it to what it is.

# SETUP
#--------------------
# These HAVE to be set.
emailAddress		= ""		# Set this to your CloudFlare Email.
APIkey			= "" 	# Set this to your API key.
# These do not have to be set.
defaultHostname		= "" 		# Set this to your default hostname
defaultIPURL		= None		# This doesn't need to be changed. (Seriously.) It requires you to recode this script.

# USING
#--------------------
# See documentation at
#  http://git.eitak.se/ddcf/doc.html
#
# REMEMBER TO SETUP THE PROGRAM ABOVE!
#
# > CF Limitations
# You can only use 300 API calls per function per hour.
# Records you plan on adding will ONLY work with A and CNAME. No MX, AAAA, etc.
# 
# > Basic commands
# ddcf u & ddcf update 		<-- Updates a record or records.
# ddcf a & ddcf add		<-- Adds a record (See doc.)
# ddcf r & ddcf remove		<-- Removes a record
# ddcf ip               <-- Shows current IP address
# ddcf help 			<-- Displays help message

# PROGRAM
#  Don't edit this unless you know what you are doing.
#--------------------
import sys
import urllib
import httplib
import platform
import json

#Version check
platformVersion = platform.python_version_tuple()
if platformVersion[0] != "2":
	print("Errno 1: Python version not supported. Please use Python v2.")
	sys.exit(1)

# Check for CLI parameters
try:
	cmd = sys.argv[1]
	arg1Set = True
except IndexError:
	arg1Set = False

def check_command(a):
	if a == "u" or a == "update":
		return True
	elif a == "a" or a == "add":
		return True
	elif a == "r" or a == "remove" or a == "rm":
		return True
	elif a == "h" or a == "help":
		return True
	elif a == "f" or a == "force":
		return True
	elif a == "s" or a == "stats":
		return True
	elif a == "ip" or a == "getip":
		return True
	else:
		return False

def parse_response(a):
	return json.loads(a)

def display_help():
	# Display help message
	# Check if argv[2] is set, and do that.
	try:
		command = sys.argv[2]
		commandSet = True
	except IndexError:
		commandSet = False
	if commandSet is False:
		# Vanilla help message
		print("ddcf Help")
		print("")
		print("For additional syntax help, use ddcf help <command>")
		print("Commands:")
		print("    u,  update          Updates record(s)")
		print("    f,  force           Updates record according to IP argument")
		print("    a,  add             Adds an A or CNAME record")
		print("    r,  rm, remove      Removes a record")
		print("    s,  stats           Shows the stats for the domain")
		print("    ip, getip           Retrieves and displays your crrent IP.")
		print("    st, support         Support tools (see `ddcf help st')")
		print("    h,  help            Displays this message")
		print("")
		print("You can read the online documentation at")
		print("  http://eitak.se/ddcf/doc.html")
		sys.exit(0)
	else:
		# Checks command against commands, and does that.
		if check_command(command) is False:
			#Command doesn't exist
			print("Errno 3: Help on command `"+command+"' is unavailable. The command does not exist.")
			sys.exit(3)
		else:
			if command == "u" or command == "update":
				#Update help
				print("ddcf update Help")
				print("")
				print("Command u & update")
				print("    Updates hostname's record according to IP retrieved.")
				print("")
				print("Syntax")
				print("    ddcf update [<hostname>]")
				print("")
				print("    If <hostname> is set, the default hostname is overridden.")
				print("")
				print("Note: If you try this on a CNAMEd zone, it will return success, but it will not update the record.")
				print("See also:")
				print("    ddcf help force")
				sys.exit(0)
			elif command == "f" or command == "force":
				print("ddcf force Help")
				print("")
				print("Command f & force")
				print("    Forces hostname to IP argument. Only works on A records.")
				print("")
				print("Syntax")
				print("    ddcf force <ip> [<hostname>]")
				print("")
				print("    <ip> argument is not validated. Make sure it's correct BEFORE you execute it.")
				print("      This CANNOT change A records with CNAME records or vice versa. It will fail to change it.")
				print("    If <hostname> isn't set, program will use default hostname.")
				print("")
				print("See also:")
				print("    ddcf help update")
				sys.exit(0)
			elif command == "a" or command == "add":
				print("ddcf add Help")
				print("")
				print("Command a & add")
				print("    Adds a CNAME or A record to the DNS zone.")
				print("")
				print("Syntax")
				print("    ddcf add <hostname|X> <name> <A|CNAME> <destination|X>")
				print("")
				print("    X will automatically fill in the argument.")
				print("      X in the destination argument requires type A.")
				print("      X in the hostname will use default.")
				print("    A records point to IPs.")
				print("    CNAME records point to other hosts.")
				sys.exit(0)
			elif command == "r" or command == "rm" or command == "remove":
				print("ddcf remove Help")
				print("")
				print("Command r, rm & remove")
				print("")
				print("Syntax")
				print("    ddcf remove <hostname|X> <record>")
				print("")
				print("    X will automatically fill in the <hostname> argument with default.")
				print("    The <record> argument must be the full DNS entry.")
				print("      Example:")
				print("        `sub.example.com'")
				print("      NOT:")
				print("        `sub'")
				print("")
				print("Warning: This will remove ALL records (MX, AAAA, A, CNAME, TXT, SPF, etc)")
				print("  for the record. For specific records, use the CloudFlare main site.")
				sys.exit(0)
			elif command == "stats" or command == 's':
				print("ddcf stats Help")
				print("")
				print("Command s & stats")
				print("    Shows stats for entire account. (Per hostname isn't handled by the API.)")
				print("")
				print("Syntax")
				print("    ddcf stats [<interval>]")
				print("")
				print("    <interval> Values:")
				print("      10:  1 year (Between 366s and 1 day ago)")
				print("      20:  30 days (Between 31 and 1 day ago)")
				print("      30:  7 days (Between 8 days and 1 day ago) [DEFAULT]")
				print("      40:  24 hours (Between 2 days and 1 day ago)")
				print("        PRO ONLY")
				print("      100: 24 hours (Between 24 hours and 0 minutes ago)")
				print("      110: 12 hours (Between 12 hours and 0 minutes ago)")
				print("      120: 6 hours (Between 6 hours and 0 minutes ago)")
				sys.exit(0)
			elif command == "ip" or command == "getip":
				print("ddcf getip Help")
				print("")
				print("Command ip & getip")
				print("    Retrieves your IP and displays it onscreen.")
				print("")
				print("Syntax")
				print("    ddcf getip")
				sys.exit(0)
#Main variables
fbIPURL = "canhazip.com" # Fallback IP check URL
CFAPI = "/api_json.html" #Main CloudFlare API URL

#Check Setup
if emailAddress is None:
	print("Errno 5: Email Address is not set. Please set it before continuing.")
	sys.exit(5)
if APIkey is None:
	print("Errno 6: API Key is not set. Please set it before continuing.")
	sys.exit(6)

#Set IP url
if defaultIPURL is None:
	ipurl = fbIPURL
else:
	ipurl = defaultIPURL

def do_getip():
	#GetIP
	print("Starting GetIP Process...")
	print("Getting your IP...")
	ipck = httplib.HTTPConnection(ipurl)
	ipck.request("GET","/")
	ip1 = ipck.getresponse()
	if ip1.status != 200:
		print("Errno 40: IP URL invalid.")
		print("Returned with response code:"+ str(ip1.status))
		sys.exit(40)
	ip2 = ip1.read()
	ip = ip2.split("</script>\n")[3].split("\n")[0]
	print("Your current IP: "+ip)
	exit(0)

def do_stats():
	#Stats
	print("Starting Stats Process...")
	try:
		intv = sys.argv[2]
	except IndexError:
		#print("Defaulting interval to 30 (1 week)")
		intv = "30"
	apio = httplib.HTTPSConnection("www.cloudflare.com")
	#print("Starting API call..")
	query = "?a=stats&tkn="+APIkey+"&u="+emailAddress+"&interval="+intv
	apio.request("GET",CFAPI+query)
	api = apio.getresponse()
	if api.status != 200:
		print("Errno 22: CloudFlare API connection failed.")
		print("Returned with response code: "+ str(api.status))
		sys.exit(22)
	respo = parse_response(api.read())
	#print("API call done.")
	#Parse respo
	if respo['result'] == "error":
		print("Errno 23: API error. Response follows.")
		print(respo['msg'])
		sys.exit(23)
	#Now we parse out and display respo.
	stats = respo['response']['result']['objs'][0]
	tb = stats['trafficBreakdown']
	tb1 = tb['pageviews']
	tb2 = tb['uniques']
	if intv == "10":
		ints = "year"
	elif intv == "20":
		ints = "30 days"
	elif intv == "30":
		ints = "7 days"
	elif intv == "40":
		ints = "24 to 48 hours"
	elif intv == "100":
		ints = "24 hours"
	elif intv == "110":
		ints = "12 hours"
	elif intv == "120":
		ints = "6 hours"
	print("---------------------")
	print("Stats for Email: "+emailAddress)
	print("Showing the last "+ints)
	print("---------------------")
	print("")
	print("> Traffic Breakdown")
	print("Type    | Views		Uniques")
	print("--------+------------------------------------------")
	print("Regular | "+str(tb1['regular'])+"		"+str(tb2['regular']))
	print("Crawler | "+str(tb1['crawler'])+"		"+str(tb2['crawler']))
	print("Threats | "+str(tb1['threat'])+"		"+str(tb2['threat']))

	#Escapes db0 error.
	if tb2['regular'] == 0:
		regu = 1;
	else:
		regu = tb2['regular']
	if tb1['regular'] == 0:
		regv = 1;
	else:
		regv = tb1['regular']
	if tb2['threat'] == 0:
		thru = 1;
	else:
		thru = tb2['threat']
	if tb1['threat'] == 0:
		thrv = 1;
	else:
		thrv = tb1['threat']
	if tb2['crawler'] == 0:
		crau = 1;
	else:
		crau = tb2['crawler']
	if tb1['crawler'] == 0:
		crav = 1;
	else:
		crav = tb1['crawler']

	# Calculate the ratios
	regr = str((regu/regv)*100).split(".")[0]
	crar = str((crau/crav)*100).split(".")[0]
	thrr = str((thru/thrv)*100).split(".")[0]
	print("  Views-Uniques Ratios >>")
	print("    Regular | "+regr+"%")
	print("    Crawler | "+crar+"%")
	print("    Threats | "+thrr+"%")
	print("")
	bs = stats['bandwidthServed']
	bsCF = str(bs['cloudflare']).split(".")[0]
	bsU = str(bs['user']).split(".")[0]
	try:
		bsR = str((int(bsCF)/int(bsU))*100/2).split(".")[0]
		bsD = str(int(bsCF)-int(bsU)).split(".")[0]
	except ZeroDivisionError:
		print("Errno 30: Divide by zero error.")
		sys.exit(30)
	rs = stats['requestsServed']
	try:
		rsR = str((rs['cloudflare']/rs['user'])*100/2).split(".")[0]
		rsD = str(rs['cloudflare']-rs['user']).split(".")[0]
	except ZeroDivisionError:
		print("Errno 31: Divide by zero error.")
		sys.exit(31)
	print("> Bandwidth & Requests Served")
	print("Type       | Bandwidth (in kB)	Requests")
	print("-----------+----------------------------------------")
	print("CloudFlare | "+bsCF+"		"+str(rs['cloudflare']))
	print("User       | "+bsU+"		"+str(rs['user']))
	print("  CloudFlare Saved You >>")
	print("    Bandwidth | "+bsR+"% by "+bsD+"kB")
	print("    Requests  | "+rsR+"% by "+rsD+" requests")
	sys.exit(0)

def do_remove():
	#REMOVE
	print("Starting Remove Process...")
	try:
		zone = sys.argv[2]
		name = sys.argv[3]
	except IndexError:
		print("Errno 19: Missing arguments. See `ddcf help remove' for help.")

	if zone == "X":
		zone = defaultHostname
		print("Set zone to default hostname. Continuing with unknown results.")
	apio = httplib.HTTPSConnection("www.cloudflare.com")
	print("--------------------")
	print("Note: the record you are removing must be the full DNS name.")
	print("Example:")
	print("    `sub.example.com'")
	print("NOT:")
	print("    `sub'")
	print("")
	print("Removing: "+name)
	print("from zone: "+zone)
	print("")
	print("Another note: It will remove ALL DNS records for what you requested. This includes MX and TXT.")
	print("--------------------")

	# User intervention
	yn = raw_input("Are you sure [y/N]? ")
	if yn == "N" or yn == "n":
		print("Aborting..")
		sys.exit(0)
	yn2 = raw_input("Seriously, are you sure!? ")
	if yn2 == "N" or yn2 == "n":
		print("Aborting..")
		sys.exit(0)

	# API handler
	print("Starting API call..")
	query = "?a=rec_del&tkn="+APIkey+"&u="+emailAddress+"&zone="+zone+"&name="+name
	apio.request("GET",CFAPI+query)
	api = apio.getresponse()
	if api.status != 200:
		print("Errno 20: CloudFlare API connection failed.")
		print("Returned with response code: "+ str(api.status))
		sys.exit(20)
	respo = parse_response(api.read())
	print("API call done.")
	#Parse respo
	if respo['result'] == "error":
		print("Errno 21: API error. Response follows.")
		print(respo['msg'])
		sys.exit(21)
	elif respo['result'] == "success":
		print("Success.")
		sys.exit(0)

def do_add():
	print("Starting Add Process...")
	#Add

	#Arg check
	try:
		zone = sys.argv[2]
	except IndexError:
		print("Errno 12: No arguments set. See `ddcf help add' for help.")
		sys.exit(12)

	try:
		name = sys.argv[3] # Record name
		rect = sys.argv[4] # Record type
		cont = sys.argv[5] # Record content
	except IndexError:
		print("Errno 13: Missing arguments. See `ddcf help add' for help.")
		sys.exit(13)
	try:
		state = sys.argv[6]
	except IndexError:
		print("Defaulting CloudFlare mode to `on'.")
		state = "1"

	# If cont is X, we can get the current IP.
	if cont == "X":
		fip = False
	else:
		fip = True

	# If zone is X, we can use default hostname. This may not work.
	if zone == "X":
		zone = defaultHostname
		print("Set active zone to default hostname. Continuing with unknown results.")

	# CF object
	apio = httplib.HTTPSConnection("www.cloudflare.com")

	#IP Handler
	if fip is False and rect == "A":
		ipck = httplib.HTTPConnection(ipurl)
		print("Getting your IP...")
		ipck.request("GET","/")
		ip1 = ipck.getresponse()
		if ip1.status != 200:
			print("Errno 15: IP URL invalid.")
			print("Returned with response code:"+ str(ip1.status))
			sys.exit(15)
		ip2 = ip1.read()
		cont = ip2.split("</script>\n")[2]
		print("Got your IP.")
	elif fip is False and rect == "CNAME":
		print("Errno 18: Cannot use retrivable IP for CNAME record.")
		sys.exit(18)
	print("Starting API call.")

	#API handler
	query = "?a=rec_set&tkn="+APIkey+"&u="+emailAddress+"&zone="+zone+"&type="+rect+"&content="+cont+"&name="+name+"&service_mode="+state
	apio.request("GET",CFAPI+query)
	api = apio.getresponse()
	if api.status != 200:
		print("Errno 16: CloudFlare API connection failed.")
		print("Returned with response code: "+ str(api.status))
		sys.exit(16)
	respo = parse_response(api.read())
	print("API call done.")
	#Parse respo
	if respo['result'] == "error":
		print("Errno 17: API error. Response follows.")
		print(respo['msg'])
		sys.exit(17)
	elif respo['result'] == "success":
		print("Success.")
		sys.exit(0)

def do_force():
	print("Starting Force Process...")
	# Force
	# CF object
	apio = httplib.HTTPSConnection("www.cloudflare.com")

	#Get argv[2]
	try:
		ip = sys.argv[2]
	except IndexError:
		print("Errno 9: IP argument is unset. This argument MUST be set to use force. See `ddcf help force' for help.")
		sys.exit(9)

	#host handler
	try:
		hN = sys.argv[3]
	except IndexError:
		hN = defaultHostname
	print("Starting API call")

	#API handler
	query = "?a=DIUP&tkn="+APIkey+"&u="+emailAddress+"&ip="+ip+"&hosts="+hN
	apio.request("GET",CFAPI+query)
	api = apio.getresponse()
	if api.status != 200:
		print("Errno 10: CloudFlare API connection failed.")
		print("Returned with response code: "+ str(api.status))
		sys.exit(10)
	respo = parse_response(api.read())
	print("API call done.")
	#Parse respo
	if respo['result'] == "error":
		print("Errno 11: API error. Response follows.")
		print(respo['msg'])
		sys.exit(11)
	elif respo['result'] == "success":
		print("Success.")
		sys.exit(0)

def do_update():
	print("Starting Update Process...")
	#Update
	# IP object
	ipck = httplib.HTTPConnection(ipurl)
	# CF object
	apio = httplib.HTTPSConnection("www.cloudflare.com")

	#IP Handler
	print("Getting your IP...")
	ipck.request("GET","/")
	ip1 = ipck.getresponse()
	if ip1.status != 200:
		print("Errno 6: IP URL invalid.")
		print("Returned with response code:"+ str(ip1.status))
		sys.exit(6)
	ip2 = ip1.read()
	ip = ip2.split("</script>\n")[3].split("\n")[0]
	print("Got your IP, starting API call.")

	#Arg handler
	try:
		hN = sys.argv[2]
	except IndexError:
		hN = defaultHostname

	#API handler
	query = "?a=DIUP&tkn="+APIkey+"&u="+emailAddress+"&ip="+ip+"&hosts="+hN
	apio.request("GET",CFAPI+query)
	api = apio.getresponse()
	if api.status != 200:
		print("Errno 7: CloudFlare API connection failed.")
		print("Returned with response code: "+ str(api.status))
		sys.exit(7)
	respo = parse_response(api.read())
	print("API call done.")
	#Parse respo
	if respo['result'] == "error":
		print("Errno 8: API error. Response follows.")
		print(respo['msg'])
		sys.exit(8)
	elif respo['result'] == "success":
		print("Success.")
		sys.exit(0)

if arg1Set is False:
	# If no command is set, display help.
	display_help()
else:
	# Command is set, so check if exists.
	if check_command(cmd) is False:
		# If it doesn't, exist with Errno 2.
		print("Errno 2: Command does not exist. See `ddcf help' for list of commands.")
		sys.exit(2)
	else:
		# If it does, parse it and execute it's function.
		if cmd == "u" or cmd == "update":
			#Update
			do_update()
		elif cmd == "ip" or cmd == "getip":
			#GetIP
			do_getip()
		elif cmd == "f" or cmd == "force":
			#Force
			do_force()
		elif cmd == "a" or cmd == "add":
			#Add
			do_add()
		elif cmd == "r" or cmd == "rm" or cmd == "remove":
			#Remove
			do_remove()
		elif cmd == "s" or cmd == "stats":
			#Stats
			do_stats()
		elif cmd == "h" or cmd == "help":
			#Help
			display_help()
		else:
			# Something went wrong..
			print("Errno 4: Something went wrong when trying to execute the command.")
			sys.exit(4)