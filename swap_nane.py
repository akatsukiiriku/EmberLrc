import os
import sys

swap_debug = False

def rename_swap(root_path):
    abs_path = root_path + "\\"
    files = sorted(os.listdir(root_path))
    for file in files:
        # 跳过已重新命名的文件
        #if " - " in file:
        #    continue

        if file.find(".") == -1:
            print("file name do not include \".\": " + file)
            continue

        if file.find("-") == -1:
            print("file name do not include \"-\": " + file)
            continue
       
        # 分割文件名后缀，获取文件名
        file_prefix = os.path.splitext(file)[0]
        file_suffix = os.path.splitext(file)[1]
        if swap_debug:
            print("file_prefix: " + file_prefix)
            print("file_suffix: " + file_suffix)

        # 获取歌手名和歌曲名
        song = file_prefix.split("-")[0].strip()
        singer = file_prefix.split("-")[1].strip()
        if swap_debug:
            print("singer: " + singer)
            print("song: " + song)

        # 拼接新命名
        old_name = abs_path + file
        new_name = abs_path + singer + " - " + song + file_suffix
        print(old_name + " ----> " + new_name)
        if swap_debug:
            continue
        os.rename(old_name, new_name)
    print("rename option finish")
    #end

if __name__ == "__main__":
    print('??')
    if len(sys.argv) <= 1:
        root_path = "."
    else:
        root_path = sys.argv[1]
    #rename_normal(root_path)
    #rename_spec(root_path)
    rename_swap(root_path)
