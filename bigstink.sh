#!/bin/bash

#Big stink is a wrapper for several tools in the Kali suite, intended to streamline pentesting and make it easier for newer pentesters 

RED='\033[0;31m'
NOCOLOR='\033[0m'

echo -e "${RED}_____________________________________________________________________________________________________________"
echo "    ...     ..         .                          ...              s       .                        .."
echo " .=*8888x <\"?88h.     @88>                    .x888888hx    :     :8      @88>                < .z@8\`\""
echo "X>  '8888H> '8888     %8P                    d88888888888hxx     .88      %8P      u.    u.    !@88E"
echo "88h. \`8888   8888      .         uL         8\" ... \`\"*8888%\`    :888ooo    .     x@88k u@88c.  '888E   u"
echo "8888 '8888    \"88>   .@88u   .ue888Nc..    !  \"   \` .xnxx.    -*8888888  .@88u  ^\"8888\"\"8888\"   888E u@8NL"
echo "\`888 '8888.xH888x.  ''888E\` d88E\`\"888E\`    X X   .H8888888%:    8888    ''888E\`   8888  888R    888E\`\"88*\""
echo "  X\" :88*~  \`*8888>   888E  888E  888E     X 'hn8888888*\"   >   8888      888E    8888  888R    888E .dN."
echo "~\"   !\"\`      \"888>   888E  888E  888E     X: \`*88888%\`     !   8888      888E    8888  888R    888E~8888"
echo " .H8888h.      ?88    888E  888E  888E     '8h.. \`     ..x8>  .8888Lu=    888E    8888  888R    888E '888&"
echo ":\`^\"88888h.    '!     888&  888& .888E      \`88888888888888f   ^%888*     888&   \"*88*\" 8888\"   888E  9888."
echo "^    \"88888hx.+\"      R888\" *888\" 888&       '%8888888888*\"      'Y\"      R888\"    \"\"   'Y\"   '\"888*\" 4888\""
echo "        ^\"**\"          \"\"    \`\"   \"888E         ^\"****\"\"                  \"\"                    \"\"    \"\""
echo "                             .dWi   \`88E"
echo "                             4888~  J8%"
echo "                              ^\"===*\""
echo -e "_____________________________________________________________________________________________________________${NOCOLOR}"
echo 
read -n 1 -s -r -p "Press any key to continue..."
echo
echo -e "${RED}_____________________________________________________________________________________________________________"
echo
echo -e "${NOCOLOR}Pick a smell! ^-^ (To list \"smells\", type the word! For help, type \"help\")"
echo -e "${RED}_____________________________________________________________________________________________________________"
echo 
echo

while [ "${userIn}" != "quit" ]; do

	echo -n -e "\033[0;31m>\033[0m "
	read -r -p "" userIn
	echo

	if [ "${userIn}" == "portscan" ]; then
		
		echo "Please enter an IP address:"
		read targetip
	
	elif [ "${userIn}" == "smells" ]; then
	
		echo "ODORS INCLUDE"
		echo "-------------"
		echo "portscan" 
		echo "asreproast"
		echo "kerbroast"
		echo "dhcpstarve"
		echo

	elif [ "${userIn}" == "asreproast" ]; then

		echo "Please enter target's domain controller's IP: "
		echo ""

		read targetip

		echo ""
		echo "Please enter the domain and username in the format \"DOMAIN/USERNAME\":"
		echo ""

		read domainuser

		impacket-GetNPUsers "${domainuser}" -dc-ip "${targetip}"
		echo

	elif [ "${userIn}" ==  "dhcpstarve" ]; then

		echo "It's about to get hungry... >:)"
		
		sleep 2

		python3 "dhcpspam.py"


	fi



done

