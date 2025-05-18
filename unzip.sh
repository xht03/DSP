#!/bin/bash

# 遍历records目录中的所有zip文件并解压
for zipfile in *.zip; do
    # 检查文件是否存在
    if [ -f "$zipfile" ]; then
        # 提取文件名（不含扩展名）作为目录名
        dirname="${zipfile%.zip}"
        
        # 创建目录（如果不存在）
        mkdir -p "$dirname"
        
        # 解压文件到对应目录
        echo "正在解压 $zipfile 到 $dirname/"
        unzip -o "$zipfile" -d "$dirname"
        rm -f "$zipfile" # 删除原始 zip 文件
        
        echo "完成解压: $zipfile"
        echo "-----------------------------"
    fi
done

echo "所有 zip 文件解压完成"