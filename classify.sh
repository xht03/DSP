#!/bin/bash
# 将文件按照第一个-之后的编号分类到对应文件夹

# 设置源目录(包含.dat文件的目录)
SOURCE_DIR="/home/keats/DSP/records/21307130453-蒋瑜贤-录音/21307130453-蒋瑜贤-录音"
# 设置目标基础目录
TARGET_BASE_DIR="/home/keats/DSP/Data"

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
    
    # 从文件名中提取类别编号 (第一个'-'后的部分)
    # 例如从 "22307110206-00-01.dat" 中提取 "00"
    # category=$(echo "$filename" | cut -d'_' -f2)
    category=$(echo "$filename" | cut -d'-' -f2)
    
    # 创建对应的目录
    mkdir -p "$TARGET_BASE_DIR/$category"
    
    # 复制文件到对应目录
    cp "$file" "$TARGET_BASE_DIR/$category/"
    echo "已分类: $filename -> $TARGET_BASE_DIR/$category/"
    
    ((count++))
done

echo "分类完成！共处理 $count 个文件"
echo "分类结果保存在 $TARGET_BASE_DIR 目录"