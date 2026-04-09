from do_trans import ui,write_to_log
import os
import sys


def play():
    video_file = ui(data={"limit_func":True,"desc":"输入要合并的视频文件","type":"keyword","display_key":"视频","allow_none":False})[0]
    audio_file = ui(data={"limit_func":True,"desc":"输入要合并的音频文件","type":"keyword","display_key":"音频","allow_none":False})[0]
    output_file_name = ui(data={"limit_func":True,"desc":"输入合并后的输出文件名，不输入则使用视频的文件名","type":"keyword","display_key":"输出文件名","allow_none":True})[0]
    if output_file_name == None:
        output_file_name = os.path.basename(video_file)
    output_file = ui(data={"limit_func":True,"desc":"输入合并后的输出文件目录，不输入目录则使用视频所在目录","type":"keyword","display_key":"输出文件目录","allow_none":True})[0]
    if output_file == None:
        output_file = os.path.dirname(video_file)
    outputname = os.path.join(output_file, output_file_name)
    do_mix(video_file,audio_file,outputname)

        

def do_mix(video,audio,outputname):
    # params ='-i '+ '"' + org +'" '+ res + ' -c:v '+ coder + ' -preset ' +target_speed + target_q + target_audio +'"'+ tar +'"'
    params = '-i  "'+ video +'" -i "' + audio + '" -c:v copy -c:a copy -strict experimental "'+ outputname +'"'
    path_01= "ffmpeg {params}".format(params=params)
    if sys.platform != 'win32':
        path_01 = './'+ path_01
    print(path_01)
    try:
        r_v = os.system(path_01)
        return r_v
    except:
        pass

if __name__ == '__main__':
    play()
