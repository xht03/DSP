#!/bin/bash
# filepath: /home/keats/DSP/select.sh

# 需要筛选的ID列表
ids=("21300240018" "21307110316" "21307130050" "21307130052" "21307130121" "21307130150" "22300240004" "23300240026")

src_base="Data"
dst_base="selectedData"

mkdir -p "$dst_base"

for subdir in "$src_base"/*; do
    [ -d "$subdir" ] || continue
    for id in "${ids[@]}"; do
        # 支持 - 或 _ 作为分隔符
        for file in "$subdir"/${id}-*.dat "$subdir"/${id}_*.dat; do
            [ -e "$file" ] || continue
            echo "移动: $file -> $dst_base/"
            cp "$file" "$dst_base/"
        done
    done
done

echo "筛选完成！"