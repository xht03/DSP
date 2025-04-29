#!/bin/bash

# 重命名并转换
for dir in */; do
    if [ -d "$dir" ]; then
        dir=${dir%/}  # Remove trailing slash
        echo "Processing directory: $dir"
        cp -f convert.sh "./$dir/convert.sh"
        cp -f rename.sh "./$dir/rename.sh"
        # chmod +x "./$dir/rename.sh"
        chmod +x "./$dir/convert.sh"
        cd "$dir" || exit
        ./convert.sh
        ./rename.sh
        rm -f ./convert.sh
        rm -f ./rename.sh
        cd ..
    fi
done

# 集中到Data目录
mkdir -p Data
find . -name "*.dat" -type f -exec mv {} Data/ \;
