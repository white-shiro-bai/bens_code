# -*- coding: utf-8 -*
# author: unknowwhite@outlook.com
# wechat: Ben_Xiaobai
import sys
sys.path.append("./")
sys.setrecursionlimit(10000000)
import os
import hashlib
import shutil
from pymediainfo import MediaInfo
import json
import multiprocessing

srcdir = "D:\\youtube-dl" #需要压缩的目录
tardir = srcdir+"\\encoded" #输出的目录
tread = 2 #需要并发的线程数


def do_trans(org,tar):
    params ='-i '+ '"' + org +'" ' + '-c:v libx264 -preset veryslow' + ' -crf 25 ' + ' -c:a aac -vbr 1 '  +'"'+ tar +'"'
    path_01= "ffmpeg.exe {params}".format(params=params)
    print(path_01)
    r_v = os.system(path_01)
    return r_v
def trans_all():
    #拿到目录下的所有文件
    result = []#所有的文件
    for maindir, subdir, file_name_list in os.walk(srcdir):
        # print("1:",maindir) #当前主目录
        # print("2:",subdir) #当前主目录下的所有目录
        # print("3:",file_name_list)  #当前主目录下的所有文件
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)#合并成一个完整路径
            bpath = os.path.join(tardir,maindir.replace(srcdir+'\\','').replace(srcdir,''),filename+'.mp4')
            outpath = os.path.join(tardir,maindir.replace(srcdir+'\\','').replace(srcdir,''))
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            result.append({"org": apath,"tar":bpath})
    p = multiprocessing.Pool(processes = tread)
    for keys in result:
        p.apply_async(func=do_trans, kwds=keys)
    p.close()
    p.join()

if __name__ == "__main__":
    trans_all()
