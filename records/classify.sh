#!/bin/bash
# 将文件按照第一个-之后的编号分类到对应文件夹

# 设置源目录(包含.dat文件的目录)

# SOURCE_DIR="/home/keats/DSP/records/23300240033-陈颖妍-录音/23300240033-陈颖妍-录音"
# SOURCE_DIR="/home/keats/DSP/records/23300240026-余恩瀚-录音"
# SOURCE_DIR="/home/keats/DSP/records/22300240008-曹奕伦-录音/22300240008-曹奕伦-录音"
# SOURCE_DIR="/home/keats/DSP/records/22307110206-records/22307110206-records"
# SOURCE_DIR="/home/keats/DSP/records/21300240018-董婷婷-录音/voices"
# SOURCE_DIR="/home/keats/DSP/records/22300240004-陈佳鹏-录音/voices"

SOURCE_DIR="/home/keats/DSP/selectedData"

# 设置目标基础目录
TARGET_BASE_DIR="/home/keats/DSP/newData"

# 创建目标基础目录
mkdir -p "$TARGET_BASE_DIR"

# 查找所有.dat文件
echo "开始分类文件..."
count=0

for file in "$SOURCE_DIR"/*.dat; do
    # 检查文件是否存在
    [ -f "$file" ] || continue
    
    # 获取文件基本名(不包含路径)
    filename=$(basename "$file")
    
    # 从文件名中提取类别编号 (第一个'-'或'_'后的部分)
    if [[ "$filename" == *_*_* ]]; then
        # 形如 id_wordidx_idx.dat
        category=$(echo "$filename" | cut -d'_' -f2)
    elif [[ "$filename" == *-*-* ]]; then
        # 形如 id-wordidx-idx.dat
        category=$(echo "$filename" | cut -d'-' -f2)
    else
        echo "无法识别类别: $filename"
        continue
    fi
    
    # 创建对应的目录
    mkdir -p "$TARGET_BASE_DIR/$category"
    
    # 复制文件到对应目录
    cp "$file" "$TARGET_BASE_DIR/$category/"
    echo "已分类: $filename -> $TARGET_BASE_DIR/$category/"
    
    ((count++))
done

echo "分类完成！共处理 $count 个文件"
echo "分类结果保存在 $TARGET_BASE_DIR 目录"