# -*- coding: utf-8 -*
# author: unknowwhite@outlook.com
# wechat: Ben_Xiaobai
import sys
sys.path.append("./")
sys.setrecursionlimit(10000000)
import os
import multiprocessing
from pymediainfo import MediaInfo
import datetime
from prettytable import PrettyTable

def ui(data):
    while True:
        print("\n<------------------------------------------------------------------------------------------------>")
        if 'desc' in data:
            print(data['desc'])
        if data["type"] == "option":
            if 'limit_func' in data and data['limit_func'] is True:
                #限制使用返回等功能
                display_keys = []
            else:    
                display_keys = ['~back','~refresh','~home','~exit']
            key_map = {"~back":"~back","~home":"~home","~refresh":"~refresh"} #
            if len(data["data"]) != 0:
                tb = PrettyTable(field_names=data["data"][0].keys())
                tb.padding_width = 1
                for item in data["data"]:
                    display_keys.append(str(item[data["display_key"]]))
                    row = []
                    for content in item.keys():
                        row.append(str(item[content]))
                    tb.add_row(row)
                    key_map[str(item[data["display_key"]])] = str(item[data["func_key"]])
                print(tb)
            else:
                print('无可用数据')    
            print('可供输入的'+data["display_key"]+"有：",display_keys)
            key_in = input("请输入选择的 "+data["display_key"]+" 并按回车键确认：")
            if key_in == "~back":
                return '~back','~menu'
            elif key_in == "~refresh":
                return '~refresh','~menu'
            elif key_in == "~exit":
                print("程序结束")
                exit()
            elif key_in == "~home":
                return '~home','~menu'
            elif key_in =="" and 'limit_func' in data and data['limit_func'] is True:
                continue
            elif key_in =="":
                return '~refresh','~menu'
            elif key_in not in display_keys and ',' not in key_in:
                print("\n<------------------------------------------------------------------------------------------------>\n 你输入的",key_in,"不是一个有效的输入，好好看选项，不然会报错的！")
                continue
            if ',' in key_in:
                key_out = []
                for key in key_in.split(','):
                    key_out.append(key_map[key])
                print("你输入的"+data["display_key"]+"是:",key_in,"执行的是：",','.join(key_out))
                return ','.join(key_out),key_in
            elif key_in[0] =='~':
                print("你输入的"+data["display_key"]+"是:",key_in,"执行的是：",key_in)
                return key_in,key_in
            else:
                print("你输入的"+data["display_key"]+"是:",key_in,"执行的是：",key_map[key_in])
                return key_map[key_in],key_in
        elif data["type"] == "keyword":
            key_in = input("请输入 "+data["display_key"]+" 并按回车键确认：")
            if key_in == "~exit":
                print("程序结束")
                exit()
            elif data["allow_none"] is False and key_in == '':
                print("\n<------------------------------------------------------------------------------------------------>\n "+data["display_key"] +" 选项不可以输入空字符，会报错的！")
                continue
            print("你输入的"+data["display_key"]+"是:",key_in,"执行的是：",key_in)
            if key_in != '' and key_in[0] == '~':
                return key_in,'~menu'
            return key_in,key_in
        elif data["type"] == "show":
            if len(data["data"]) != 0:
                tb = PrettyTable(field_names=data["data"][0].keys())
                tb.padding_width = 1
                for item in data["data"]:
                    row = []
                    for content in item.keys():
                        row.append(str(item[content]))
                    tb.add_row(row)
                print(tb)
                return None,None
            else:
                print('无可用数据')
                return None,None

def write_to_log(filename, defname, result):
    # 输出日志，filename是.py的的名字，def是方法名，result是要记录的内容
    dirdate = datetime.datetime.now().strftime("%Y-%m-%d")
    dirpath = os.path.join('log', dirdate)
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, filename+'.log')
    tofile = open(filepath, mode='a+', encoding='utf-8')
    content = str(datetime.datetime.now()) + ',' + defname + ',' + result
    print(content, file=tofile)
    print(content)

def GetFileInfo(filename):
    #调用mediainfo识别视频类型
    media_info = MediaInfo.parse(filename)
    data2 = media_info.to_data()
    if len(data2['tracks'])>=3:
        org_width = data2['tracks'][1]['width']
        org_height = data2['tracks'][1]['height']
        if data2['tracks'][0].__contains__('frame_rate'):
            org_fps = data2['tracks'][0]['frame_rate']
        else:
            org_fps = 0
    else:
        org_width = None
        org_height = None
        org_fps = None
    return org_width,org_height,org_fps

def get_org_ratio(org_width,org_height):
    ratio = round(int(org_width)/int(org_height),2)
    if ratio >= 16/9:
    #如果这是一个超宽视频，则适配屏幕宽度
        main = 0
    elif ratio <16/9 and ratio >1:
    #如果这是一个不宽的横屏视频，则适配视频高度
        main = 0
    elif ratio <=1 and ratio > 9/16 :
        main = 1
    #如果这是一个不高的竖屏视频，则适配竖屏视频的宽度
    elif ratio <= 9/16 :
        main = 1
    #如果这是一个很高的书评视频，则适配竖屏视频的高度
    return main

def avoid_odd(odd):
    #如遇奇数，自动+1，防止转码参数里出现奇数
    if odd%2 ==0:
        return odd
    else:
        return odd+1

def play():
    print('已知问题：iPhone6,6p拍摄的竖屏视频无法正常识别方向，转码只能转原尺寸，缩尺寸时会出错')
    info_list = []
    srcdir = ui(data={"limit_func":True,"desc":"输入要转码的目录","type":"keyword","display_key":"来源目录","allow_none":False})[0]
    tardir = ui(data={"limit_func":True,"desc":"输入要输出的目录，如留空则默认存放在输入目录的encode下","type":"keyword","display_key":"输出目录","allow_none":True})[0]
    if not tardir or tardir =='':
        tardir = os.path.join(srcdir,"encoded") #输出的目录
    tread_str = ui(data={"limit_func":True,"desc":"输入同时转码的数量，建议等同CPU的数量。如果源文件分辨率很小，则可以最高3倍于CPU的数量。不输入默认同时只转码1个","type":"keyword","display_key":"同时转码数","allow_none":True})[0]
    tread = int(tread_str) if tread_str and tread_str !='' else 1
    target_res = ui(data={"limit_func":True,"desc":"选择要输出的尺寸，可以用逗号隔开多选，大尺寸可以转小尺寸，小尺寸不会放大","type":"option","display_key":"func_id","func_key":"res","data":[{"func_id":1,"res":"org","func_name":"原始分辨率"},{"func_id":2,"res":"4k","func_name":"最大3840x2160"},{"func_id":3,"res":"2k","func_name":"最大2560x1440"},{"func_id":4,"res":"fullhd","func_name":"最大1920x1080"},{"func_id":5,"res":"hd","func_name":"最大1280x720"},{"func_id":6,"res":"xga","func_name":"最大1024x576"},{"func_id":7,"res":"sd","func_name":"最大848x480"},{"func_id":8,"res":"360","func_name":"最大640x360"}]})[0]
    res_list = {"4k":[3840,2160],"2k":[2560,1440],"fullhd":[1920,1080],"hd":[1280,720],"xga":[1024,768],"sd":[852,480],"360":[640,360]}
    target_coder = ui(data={"limit_func":True,"desc":"选择要输出的格式，可以用逗号隔开多选","type":"option","display_key":"func_id","func_key":"coder","data":[{"func_id":1,"coder":"libx264","func_name":"x264（更快更通用，推荐）"},{"func_id":2,"coder":"libx265","func_name":"x265（理论上会更小，但非常看片源）"}]})[0]
    target_q = ui(data={"limit_func":True,"desc":"选择要压缩的质量（单选）","type":"option","display_key":"func_id","func_key":"q","data":[{"func_id":1,"q":" -crf 24 ","func_name":"相对较好的视频质量（推荐）"},{"func_id":2,"q":" -crf 25 ","func_name":"视频网站常用的压缩质量，有一定马赛克或模糊"},{"func_id":3,"q":" -crf 26 ","func_name":"低质量视频网站的压缩质量，马赛克较为频繁，肉眼可见的画质变差"},{"func_id":4,"q":" -crf 22 ","func_name":"一般BDRip和DVDRip的质量，画质干净，不放在一起对比基本就是原盘质量"},{"func_id":5,"q":" -crf 18 ","func_name":"视觉无损，除非原片质量非常高，否则用不上"}]})[0]
    target_speed = ui(data={"limit_func":True,"desc":"选择算法复杂度（单选）","type":"option","display_key":"func_id","func_key":"s","data":[{"func_id":1,"s":"veryslow","func_name":"压得慢压的小（推荐）"},{"func_id":2,"s":"slower","func_name":"压得不是最小，但是会快一些"},{"func_id":3,"s":"slow","func_name":"稍微有点意义的压缩"},{"func_id":4,"s":"medium","func_name":"压了个寂寞，仅在缩小画面时用"}]})[0]
    target_audio = ui(data={"limit_func":True,"desc":"选择需要的音频质量（单选）","type":"option","display_key":"func_id","func_key":"a","data":[{"func_id":1,"a":" -c:a copy ","func_name":"直接拷贝音频（推荐）"},{"func_id":2,"a":"  -c:a aac -vbr 1 ","func_name":"尽可能压缩声音，基本能听"},{"func_id":3,"a":"  -c:a aac -vbr 6 ","func_name":"尽可能高音质（除非音源好，不然没必要）"},{"func_id":4,"a":"  -c:a aac -vbr 3 ","func_name":"普通音质"}]})[0]
    with_args = ui(data={"limit_func":True,"desc":"转码输出文件是否包含参数信息","type":"option","display_key":"func_id","func_key":"func_id","data":[{"func_id":1,"func_name":"包含参数，方便对比转码质量（推荐）"},{"func_id":2,"func_name":"不包含参数，不支持同时转多版本"}]})[0]
    #拿到目录下的所有文件
    job_list = []#所有文件
    for maindir, subdir, file_name_list in os.walk(srcdir):
        # print("1:",maindir) #当前主目录
        # print("2:",subdir) #当前主目录下的所有目录
        # print("3:",file_name_list)  #当前主目录下的所有文件
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)#合并成源文件完整路径
            if tardir not in apath:
                org = GetFileInfo(filename=apath)
                if org[0] and org[1]:
                    main_side = get_org_ratio(org_width=org[0],org_height=org[1])
                    for res in target_res.split(','):
                        if res in res_list:
                            if org[main_side] >= res_list[res][0]:
                                if main_side == 0 and org[0]/org[1] >1:#横屏视频，适配横边
                                    tar_res = ' -s {width}x{height} '.format(width=res_list[res][0],height=avoid_odd(int(org[1]/org[0]*res_list[res][0])))
                                elif main_side == 1 and org[0]/org[1] >1:#横屏视频，适配高边
                                    tar_res = ' -s {width}x{height} '.format(width=avoid_odd(int(org[0]/org[1]*res_list[res][1])),height=res_list[res][1])
                                elif main_side == 0 and org[0]/org[1] <=1:#竖竖屏视频，适配横边
                                    tar_res = ' -s {width}x{height} '.format(width=res_list[res][1],height=avoid_odd(int(org[0]/org[1]*res_list[res][0])))
                                elif main_side == 1 and org[0]/org[1] <=1:#竖屏视频，适配竖边
                                    tar_res = ' -s {width}x{height} '.format(width=avoid_odd(int(org[0]/org[1]*res_list[res][0])),height=res_list[res][0])
                            else:
                                res = 'org'
                                tar_res = ''
                        else:
                            res = 'org'
                            tar_res = ''
                        for coder in target_coder.split(','):
                            if with_args == '1' :
                                bpath = os.path.join(tardir,maindir.replace(srcdir+'\\','').replace(srcdir+'/','').replace(srcdir,''),filename+'_'+res+'_'+coder+'_'+target_q[-3:-1]+'_'+target_speed+'.mp4')
                            elif with_args == '2':
                                bpath = os.path.join(tardir,maindir.replace(srcdir+'\\','').replace(srcdir+'/','').replace(srcdir,''),filename.replace('.'+filename.split('.')[-1],'')+'.mp4')
                            outpath = os.path.join(tardir,maindir.replace(srcdir+'\\','').replace(srcdir+'/','').replace(srcdir,''))
                            # bpath = os.path.join(tardir,maindir.replace(srcdir+'\\','').replace(srcdir+'/','').replace(srcdir,''),res,coder,filename+'.mp4')
                            # outpath = os.path.join(tardir,maindir.replace(srcdir+'\\','').replace(srcdir+'/','').replace(srcdir,''),res,coder)
                            if not os.path.exists(outpath):
                                os.makedirs(outpath)
                            info_list.append({"org": apath,"tar":bpath,"target_q":target_q,"target_speed":target_speed,"target_audio":target_audio,"res":tar_res,"coder":coder})

    print(info_list)
    p = multiprocessing.Pool(processes = tread)
    for keys in info_list:
        p.apply_async(func=do_trans, kwds=keys)
    p.close()
    p.join()



def do_trans(org,tar,target_q,target_speed,target_audio,res,coder):
    if not os.path.exists(tar):
        params ='-i '+ '"' + org +'" '+ res + ' -c:v '+ coder + ' -preset ' +target_speed + target_q + target_audio +'"'+ tar +'"'
        path_01= "ffmpeg {params}".format(params=params)
        if sys.platform != 'win32':
            path_01 = './'+ path_01
        print(path_01)
        r_v = os.system(path_01)
        return r_v

if __name__ == "__main__":
    play()
