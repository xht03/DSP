#!/bin/bash


dirname=$(basename "$(pwd)")    # 当前目录名
count=1

# 查找所有.m4a文件并重命名
shopt -s nullglob
for file in *.m4a; do
    number=$(printf "%02d" $count)  # 格式化计数为两位数
    new_name="22307110206-${dirname}-${number}.m4a"
    
    # 重命名文件（检查目标文件是否已存在）
    if [ "$file" != "$new_name" ]; then
        if [ -e "$new_name" ]; then
            echo "警告: $new_name 已存在，跳过重命名 $file"
        else
            echo "重命名: '$file' -> '$new_name'"
            mv "$file" "$new_name"
        fi
    fi
    
    # 增加计数器
    ((count++))
done

# 如果count仍为1，说明没有处理任何文件
if [ $count -eq 1 ]; then
    echo "当前目录中没有找到.m4a文件"
else
    echo "所有.m4a文件已重命名完成"
fi