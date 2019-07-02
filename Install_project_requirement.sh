#!/bin/bash
center_text()
{
    local terminal_width=$(tput cols)
    local text="${1:?}"
    local glyph="${2:-=}"
    local padding="${3:-2}"

    local border=
    local text_width=${#text}

    for ((i=0; i<terminal_width; i++))
    do
        border+="${glyph}"
    done

    printf "$border"

    local area_width=$(( text_width + (padding * 2) ))

    local hpc=$(( (terminal_width - area_width) / 2 ))

    tput hpa $hpc

    tput ech $area_width
    tput cuf $padding

    printf "$text"

    tput cud1
}

countdown() {
  secs=$1
  shift
  msg=$@
  while [ $secs -gt 0 ]
  do
    printf "\r\033[KWaiting %.d seconds $msg" $((secs--))
    sleep 1
  done
  echo
}

clear

center_text 'This script will install whatever you need for the project' "="
printf '\n'
sleep 5
center_text "Your system need to up-to-date" " "
echo "   :please be patient there is 5 step left:"


cd ~
mkdir library
cd ~
apt-get update  > /dev/null 2>&1
apt-get upgrade -y
center_text "Done" " "

printf '\n'
center_text "Now,We will install all the requirement packages" " "
sleep 2
apt-get update  > /dev/null 2>&1

echo '- Install python depend packages'
echo "   :please be patient there is 4 step left:"
apt-get install python -y > /dev/null 2>&1
apt-get install python-dev -y > /dev/null 2>&1
apt-get install python-pip -y > /dev/null 2>&1
apt-get install python-setuptools > /dev/null 2>&1
apt-get install scipy -y > /dev/null 2>&1
apt-get install numpy -y > /dev/null 2>&1
pip install pyaudio > /dev/null 2>&1
apt-get install libjpeg-dev zlib1g-dev > /dev/null 2>&1
apt-get install git > /dev/null 2>&1
center_text "Done" " "
sleep 2

echo "- Install Oled library"
cd ~
echo "   :please be patient there is 3 step left:"
sudo apt-get install i2c-tools -y > /dev/null 2>&1
sudo apt-get install python-smbus > /dev/null 2>&1
sudo apt-get install python-pillow > /dev/null 2>&1
git clone https://github.com/nukem/ssd1306 library/peakutils
cd library/peakutils
sudo python setup.py install > /dev/null 2>&1
center_text "Done" " "
sleep 2

echo "- Install Peak Detection library"
cd ~
echo "   :please be patient there is 2 step left:"
git clone https://bitbucket.org/lucashnegri/peakutils/src/master/  library/peakutils
cd /library/peakutils
python setup.py install > /dev/null 2>&1
center_text "Done" " "
sleep 2

echo '- Configure microphone'
cd ~
echo "   :please be patient there is 1 step left:"
cd ~/DATN_NGUYENTHANHTRUNG2
cd Setup_audio
sudo cp -r .asoundrc ~
center_text "Done" " "
sleep 2

echo '- Install Bme280 and Uart library'
cd ~
echo "   :please be patient this is the final step:"
pip install pyserial > /dev/null 2>&1
pip install smbus > /dev/null 2>&1
center_text "Done" " "

echo 'Thanks you for your patience to wait for this script to finish'
countdown 10 "before reboot!
sudo reboot
