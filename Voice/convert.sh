#!/bin/bash

# Convert m4a to wav and then to raw
for file in *.m4a
do
    filename="${file%.m4a}"

    ffmpeg -i "$file" -ar 8000 -ac 1 -f wav temp.wav
    sox temp.wav -t raw -e signed -b 16 -c 1 "$filename.dat"

    rm temp.wav
    echo "Converted $file to $filename.dat"
    echo "-----------------------------"
done


