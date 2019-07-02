#!/bin/bash
center_text()
{
    local terminal_width=$(tput cols)    # query the Terminfo database: number of columns
    local text="${1:?}"                  # text to center
    local glyph="${2:-=}"                # glyph to compose the border
    local padding="${3:-2}"              # spacing around the text

    local border=                        # shape of the border
    local text_width=${#text}

    # the border is as wide as the screen
    for ((i=0; i<terminal_width; i++))
    do
        border+="${glyph}"
    done

    printf "$border"

    # width of the text area (text and spacing)
    local area_width=$(( text_width + (padding * 2) ))

    # horizontal position of the cursor: column numbering starts at 0
    local hpc=$(( (terminal_width - area_width) / 2 ))

    tput hpa $hpc                       # move the cursor to the beginning of the area

    tput ech $area_width                # erase the border inside the area without moving the cursor
    tput cuf $padding                   # move the cursor after the spacing (create padding)

    printf "$text"                      # print the text inside the area

    tput cud1                           # move the cursor on the next line
}

clear

center_text 'This script will install whatever you need for the project' "="
printf '\n'
center_text "Your system need to up-to-date" " "
echo "   :please be patient there is 4 step left:"


cd ~
mkdir library
cd ~
apt-get update  > /dev/null 2>&1
apt-get upgrade -y
center_text "Done" " "

printf '\n'
center_text "Now,We will install all the requirement packages" " "
apt-get update  > /dev/null 2>&1

echo '- Install python depend packages'
echo "   :please be patient there is 3 step left:"
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

echo "- Install Oled library"
cd ~
echo "   :please be patient there is 2 step left:"
sudo apt-get install i2c-tools -y > /dev/null 2>&1
sudo apt-get install python-smbus > /dev/null 2>&1
sudo apt-get install python-pillow > /dev/null 2>&1
git clone https://github.com/nukem/ssd1306 library/peakutils
cd library/peakutils
sudo python setup.py install > /dev/null 2>&1

echo "- Install Peak Detection library"
cd ~
echo "   :please be patient there is 1 step left:"
git clone https://bitbucket.org/lucashnegri/peakutils/src/master/  library/peakutils
cd /library/peakutils
python setup.py install > /dev/null 2>&1
center_text "Done" " "

echo '- Configure microphone'
cd ~
echo "   :please be patient this is the final step"
cd ~/DATN_NGUYENTHANHTRUNG2
cd Setup_audio
sudo cp -r .asoundrc ~
center_text "Done" " "
cd ~
echo 'Thanks you for your patience to wait for this script to finish'
