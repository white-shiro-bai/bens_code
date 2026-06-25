# -*- coding: utf-8 -*
# author: unknowwhite@outlook.com
# wechat: Ben_Xiaobai
import sys
sys.path.append("./")
import os
import subprocess
import re
import multiprocessing
import datetime
from collections import Counter
from prettytable import PrettyTable

def ui(data):
    while True:
        print("\n<------------------------------------------------------------------------------------------------>")
        if 'desc' in data:
            print(data['desc'])
        if data["type"] == "option":
            if 'limit_func' in data and data['limit_func'] is True:
                display_keys = []
            else:
                display_keys = ['~back','~refresh','~home','~exit']
            key_map = {"~back":"~back","~home":"~home","~refresh":"~refresh"}
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
    dirdate = datetime.datetime.now().strftime("%Y-%m-%d")
    dirpath = os.path.join('log', dirdate)
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, filename+'.log')
    tofile = open(filepath, mode='a+', encoding='utf-8')
    content = str(datetime.datetime.now()) + ',' + defname + ',' + result
    print(content, file=tofile)
    print(content)

def _ffmpeg_cmd():
    # 优先使用当前目录下的 ffmpeg，与 os.system 行为一致
    local = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg')
    if os.path.exists(local):
        return local
    return 'ffmpeg'

def get_file_info(filename):
    """用 ffmpeg -i 读取视频宽高帧率和时长"""
    try:
        result = subprocess.run(
            [_ffmpeg_cmd(), '-i', filename],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        stderr = result.stderr
        video_match = re.search(r'Video:.*?(\d{2,})x(\d{2,})', stderr)
        if not video_match:
            return None, None, None, None
        width = int(video_match.group(1))
        height = int(video_match.group(2))
        fps_match = re.search(r'(\d+(?:\.\d+)?)\s+(?:fps|tbr)', stderr)
        fps = float(fps_match.group(1)) if fps_match else None
        dur_match = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', stderr)
        duration = None
        if dur_match:
            h = int(dur_match.group(1))
            m = int(dur_match.group(2))
            s = float(dur_match.group(3))
            duration = h * 3600 + m * 60 + s
        return width, height, fps, duration
    except Exception:
        return None, None, None, None

def _detect_crop_at_time(filename, seek_time, verbose=False):
    """在指定时间点用 cropdetect 取裁切参数，返回 (w,h,x,y) 或 None"""
    try:
        ffmpeg = _ffmpeg_cmd()
        # skip=0 写在参数里但新版 ffmpeg 的 cropdetect 默认 skip=2（跳过前两帧）
        # 给 -vframes 5 保证 skip 之后还有帧被分析，取最后一个结果（最稳定）
        cmd = [ffmpeg, '-loglevel', 'verbose',
               '-ss', str(seek_time), '-i', filename,
               '-vframes', '5', '-vf', 'cropdetect=24:2:0', '-f', 'null', '-']
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        stderr = result.stderr
        if verbose:
            for line in stderr.splitlines():
                if 'cropdetect' in line.lower() or 'crop=' in line:
                    print("    [dbg]", line)
        matches = re.findall(r'crop=(\d+):(\d+):(\d+):(\d+)', stderr)
        if matches:
            w, h, x, y = matches[-1]
            return (int(w), int(h), int(x), int(y))
    except Exception as e:
        if verbose:
            print("    [dbg] exception:", e)
    return None

def get_crop_consensus(filename, duration, orig_width, orig_height, verbose=False):
    """
    取 0~90% 共 10 个时间点做黑边检测，8 个及以上一致才认定为有效黑边。
    返回 (crop_tuple, confidence_count, best_candidate, best_count)。
    crop_tuple 满足条件时有值，否则为 None；best_candidate 始终返回得票最多的候选。
    """
    percentages = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    results = []
    if verbose:
        print("  原始分辨率: {}x{}".format(orig_width, orig_height))
    for pct in percentages:
        seek = duration * pct
        crop = _detect_crop_at_time(filename, seek, verbose=verbose)
        if verbose:
            if crop:
                print("  {:.0f}%({:.1f}s): {}x{}".format(pct*100, seek, crop[0], crop[1]))
            else:
                print("  {:.0f}%({:.1f}s): 无结果".format(pct*100, seek))
        if crop:
            results.append(crop)
    if not results:
        return None, 0, None, 0
    counts = Counter(results)
    best, count = counts.most_common(1)[0]
    # 有效黑边：8/10 一致且裁切后比原始小
    if count >= 7 and (best[0] < orig_width or best[1] < orig_height):
        return best, count, best, count
    # 未达标：返回得票最多的候选供参考，但不认定为有效黑边
    candidate = best if (best[0] < orig_width or best[1] < orig_height) else None
    return None, 0, candidate, count

def get_org_ratio(org_width, org_height):
    ratio = round(int(org_width)/int(org_height), 2)
    if ratio >= 16/9:
        main = 0
    elif ratio < 16/9 and ratio > 1:
        main = 0
    elif ratio <= 1 and ratio > 9/16:
        main = 1
    elif ratio <= 9/16:
        main = 1
    return main

def avoid_odd(odd):
    if odd % 2 == 0:
        return odd
    else:
        return odd + 1

def _compute_scale(eff_w, eff_h, res_key, res_list):
    """
    根据有效宽高和目标分辨率键计算缩放参数。
    返回 (actual_res_key, scale_w, scale_h)，
    scale_w/scale_h 为 0 表示不缩放（原始尺寸）。
    """
    if res_key not in res_list:
        return 'org', 0, 0
    main_side = get_org_ratio(eff_w, eff_h)
    target_long = res_list[res_key][0]
    target_short = res_list[res_key][1]
    ratio = eff_w / eff_h
    ref_dim = eff_w if main_side == 0 else eff_h
    if ref_dim < target_long:
        return 'org', 0, 0
    if main_side == 0 and ratio > 1:
        sw = target_long
        sh = avoid_odd(int(eff_h / eff_w * target_long))
    elif main_side == 1 and ratio > 1:
        sw = avoid_odd(int(eff_w / eff_h * target_short))
        sh = target_short
    elif main_side == 0 and ratio <= 1:
        sw = target_short
        sh = avoid_odd(int(eff_w / eff_h * target_long))
    else:
        sw = avoid_odd(int(eff_w / eff_h * target_long))
        sh = target_long
    return res_key, sw, sh


def do_trans(org, tardir, srcdir, res_key, target_q, target_speed, target_audio, coder, with_args, do_crop=False, encode_filter='all'):
    if not os.path.exists(org):
        print("跳过（文件不存在）:", org)
        return

    org_width, org_height, org_fps, duration = get_file_info(org)
    if not org_width or not org_height:
        return

    res_list = {"4k":[3840,2160],"2k":[2560,1440],"fullhd":[1920,1080],
                "hd":[1280,720],"xga":[1024,768],"sd":[852,480],"360":[640,360]}

    # encode_filter 2/3/4 都需要先做黑边检测来决定是否跳过
    crop_params = None
    crop_pct_val = 100.0
    if encode_filter != 'all' or do_crop:
        if duration:
            crop_params, _, _, _ = get_crop_consensus(org, duration, org_width, org_height)
        if crop_params:
            crop_pct_val = crop_params[0] * crop_params[1] / (org_width * org_height) * 100.0

    # 根据 encode_filter 决定是否跳过，以及最终是否裁切
    has_crop = crop_params is not None
    if encode_filter == 'no_crop':
        if has_crop:
            print("跳过（有黑边，仅转无黑边文件）:", org)
            return
        actual_do_crop = False
    elif encode_filter == 'crop':
        if not has_crop:
            print("跳过（无黑边，仅转有黑边文件）:", org)
            return
        actual_do_crop = do_crop
    elif encode_filter == 'crop_lt90':
        if not has_crop or crop_pct_val >= 90.0:
            print("跳过（无黑边或裁切后>=90%，仅转裁切后<90%的文件）:", org)
            return
        actual_do_crop = do_crop
    else:
        actual_do_crop = do_crop

    # 若 actual_do_crop 但检测无结果，则不裁切
    if actual_do_crop and not crop_params:
        actual_do_crop = False

    if actual_do_crop:
        eff_w, eff_h, cx, cy = crop_params
    else:
        eff_w, eff_h, cx, cy = org_width, org_height, 0, 0
        crop_params = None  # 确保下面不走裁切分支

    actual_res_key, sw, sh = _compute_scale(eff_w, eff_h, res_key, res_list)

    # 构建输出路径
    rel = os.path.dirname(org)
    for prefix in [srcdir+'\\', srcdir+'/', srcdir]:
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    filename = os.path.basename(org)
    q_tag = target_q.strip()[-3:-1].strip() if len(target_q.strip()) >= 3 else target_q.strip()
    if with_args == '1':
        bpath = os.path.join(tardir, rel, filename+'_'+actual_res_key+'_'+coder+'_'+q_tag+'_'+target_speed+'.mp4')
    else:
        bpath = os.path.join(tardir, rel, re.sub(r'\.[^.]+$', '', filename)+'.mp4')

    if os.path.exists(bpath):
        return

    outpath = os.path.join(tardir, rel)
    os.makedirs(outpath, exist_ok=True)

    # 构建 -vf 或 -s 参数
    if crop_params and sw:
        vf_param = '-vf "crop={cw}:{ch}:{cx}:{cy},scale={sw}:{sh}"'.format(
            cw=eff_w, ch=eff_h, cx=cx, cy=cy, sw=sw, sh=sh)
        res_param = ''
    elif crop_params:
        vf_param = '-vf "crop={cw}:{ch}:{cx}:{cy}"'.format(cw=eff_w, ch=eff_h, cx=cx, cy=cy)
        res_param = ''
    elif sw:
        vf_param = ''
        res_param = '-s {sw}x{sh}'.format(sw=sw, sh=sh)
    else:
        vf_param = ''
        res_param = ''

    params = '-i "{org}" {res} {vf} -c:v {coder} -preset {speed} {q} {audio} "{tar}"'.format(
        org=org, res=res_param, vf=vf_param,
        coder=coder, speed=target_speed, q=target_q, audio=target_audio, tar=bpath)
    cmd = '{ffmpeg} {params}'.format(ffmpeg=_ffmpeg_cmd(), params=params)
    print(cmd)
    try:
        r_v = os.system(cmd)
        return r_v
    except:
        pass


def do_snap(org, tardir, srcdir, gap):
    if not os.path.exists(org):
        print("跳过（文件不存在）:", org)
        return
    rel = os.path.dirname(org)
    for prefix in [srcdir+'\\', srcdir+'/', srcdir]:
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    filename = os.path.basename(org)
    outpath = os.path.join(tardir, rel)
    os.makedirs(outpath, exist_ok=True)
    bpath = os.path.join(tardir, rel, filename)
    if os.path.exists(bpath):
        return
    params = '-i "{org}" -r {gap} -q:v 2 -f image2 "{tar}-%3d.jpg"'.format(org=org, tar=bpath, gap=gap)
    cmd = '{ffmpeg} {params}'.format(ffmpeg=_ffmpeg_cmd(), params=params)
    print(cmd)
    try:
        r_v = os.system(cmd)
        return r_v
    except:
        pass


def do_detect(org, tardir, srcdir):
    """黑边检测，始终返回结果 dict（无黑边也返回，crop 列标记 N）"""
    if not os.path.exists(org):
        return None
    org_width, org_height, _, duration = get_file_info(org)
    if not org_width or not org_height or not duration:
        print("[跳过] {}（无法读取视频信息）".format(org))
        return None
    print("[检测] {}".format(org))
    total = 10
    org_pixels = org_width * org_height
    crop_params, confidence, candidate, cand_count = get_crop_consensus(
        org, duration, org_width, org_height, verbose=True)
    if crop_params:
        cw, ch, cx, cy = crop_params
        pct = "{:.1f}%".format(cw * ch / org_pixels * 100)
        print("[有黑边 {}/{}] {}".format(confidence, total, org))
        return {
            "file": os.path.basename(org),
            "org_size": "{}x{}".format(org_width, org_height),
            "crop_size": "{}x{}".format(cw, ch),
            "crop_pct": pct,
            "crop_param": "crop={}:{}:{}:{}".format(cw, ch, cx, cy),
            "confidence": "{}/{}".format(confidence, total),
            "do_crop": "Y",
        }
    elif candidate:
        cw, ch, cx, cy = candidate
        pct = "{:.1f}%".format(cw * ch / org_pixels * 100)
        print("[参考 {}/{}] {}".format(cand_count, total, org))
        return {
            "file": os.path.basename(org),
            "org_size": "{}x{}".format(org_width, org_height),
            "crop_size": "{}x{}".format(cw, ch),
            "crop_pct": pct,
            "crop_param": "crop={}:{}:{}:{}".format(cw, ch, cx, cy),
            "confidence": "{}/{}".format(cand_count, total),
            "do_crop": "N",
        }
    else:
        print("[无黑边] {}".format(org))
        return {
            "file": os.path.basename(org),
            "org_size": "{}x{}".format(org_width, org_height),
            "crop_size": "-",
            "crop_pct": "-",
            "crop_param": "-",
            "confidence": "-",
            "do_crop": "N",
        }


def play():
    print('已知问题：iPhone6,6p拍摄的竖屏视频无法正常识别方向，转码只能转原尺寸，缩尺寸时会出错')
    srcdir = ui(data={"limit_func":True,"desc":"输入要处理的目录","type":"keyword","display_key":"来源目录","allow_none":False})[0]
    tardir = ui(data={"limit_func":True,"desc":"输入要输出的目录，如留空则默认存放在输入目录的encode下","type":"keyword","display_key":"输出目录","allow_none":True})[0]
    if not tardir or tardir == '':
        tardir = os.path.join(srcdir, "encoded")
    tread_str = ui(data={"limit_func":True,"desc":"输入同时处理的数量，建议等同CPU数量。不输入默认1","type":"keyword","display_key":"同时处理数","allow_none":True})[0]
    tread = int(tread_str) if tread_str and tread_str != '' else 1
    func_code = ui(data={"limit_func":True,"desc":"选择要实现的功能","type":"option","display_key":"func_id","func_key":"coder","data":[
        {"func_id":1,"coder":"encode","func_name":"转码"},
        {"func_id":2,"coder":"snap","func_name":"截图"},
        {"func_id":3,"coder":"detect","func_name":"黑边检测"}
    ]})[0]

    do_crop = False
    target_res = target_coder = target_q = target_speed = target_audio = with_args = gap = None

    if func_code == 'encode':
        target_res = ui(data={"limit_func":True,"desc":"选择要输出的尺寸，可以用逗号隔开多选，大尺寸可以转小尺寸，小尺寸不会放大","type":"option","display_key":"func_id","func_key":"res","data":[
            {"func_id":1,"res":"org","func_name":"原始分辨率"},{"func_id":2,"res":"4k","func_name":"最大3840x2160"},
            {"func_id":3,"res":"2k","func_name":"最大2560x1440"},{"func_id":4,"res":"fullhd","func_name":"最大1920x1080"},
            {"func_id":5,"res":"hd","func_name":"最大1280x720"},{"func_id":6,"res":"xga","func_name":"最大1024x576"},
            {"func_id":7,"res":"sd","func_name":"最大848x480"},{"func_id":8,"res":"360","func_name":"最大640x360"}]})[0]
        target_coder = ui(data={"limit_func":True,"desc":"选择要输出的格式，可以用逗号隔开多选","type":"option","display_key":"func_id","func_key":"coder","data":[
            {"func_id":1,"coder":"libx264","func_name":"x264（更快更通用，推荐）"},
            {"func_id":2,"coder":"libx265","func_name":"x265（理论上会更小，但非常看片源）"}]})[0]
        target_q = ui(data={"limit_func":True,"desc":"选择要压缩的质量（单选）","type":"option","display_key":"func_id","func_key":"q","data":[
            {"func_id":1,"q":" -crf 24 ","func_name":"相对较好的视频质量（推荐）"},
            {"func_id":2,"q":" -crf 25 ","func_name":"视频网站常用的压缩质量，有一定马赛克或模糊"},
            {"func_id":3,"q":" -crf 26 ","func_name":"低质量视频网站的压缩质量，马赛克较为频繁，肉眼可见的画质变差"},
            {"func_id":4,"q":" -crf 22 ","func_name":"一般BDRip和DVDRip的质量，画质干净，不放在一起对比基本就是原盘质量"},
            {"func_id":5,"q":" -crf 18 ","func_name":"视觉无损，除非原片质量非常高，否则用不上"},
            {"func_id":6,"q":" -crf 28 ","func_name":"x265默认"},
            {"func_id":7,"q":" -crf 29 ","func_name":"有影就行的质量"}]})[0]
        target_speed = ui(data={"limit_func":True,"desc":"选择算法复杂度（单选）","type":"option","display_key":"func_id","func_key":"s","data":[
            {"func_id":1,"s":"veryslow","func_name":"压得慢压的小（推荐）"},
            {"func_id":2,"s":"slower","func_name":"压得不是最小，但是会快一些"},
            {"func_id":3,"s":"slow","func_name":"稍微有点意义的压缩"},
            {"func_id":4,"s":"medium","func_name":"压了个寂寞，仅在缩小画面时用"},
            {"func_id":5,"s":"faster","func_name":"压缩比不高，缩小画面或者做无压缩的代理文件时用"}]})[0]
        target_audio = ui(data={"limit_func":True,"desc":"选择需要的音频质量（单选）","type":"option","display_key":"func_id","func_key":"a","data":[
            {"func_id":1,"a":" -c:a copy ","func_name":"直接拷贝音频（推荐）"},
            {"func_id":2,"a":"  -c:a aac -vbr 1 ","func_name":"尽可能压缩声音，基本能听"},
            {"func_id":3,"a":"  -c:a aac -vbr 6 ","func_name":"尽可能高音质（除非音源好，不然没必要）"},
            {"func_id":4,"a":"  -c:a aac -vbr 3 ","func_name":"普通音质"}]})[0]
        with_args = ui(data={"limit_func":True,"desc":"转码输出文件是否包含参数信息","type":"option","display_key":"func_id","func_key":"func_id","data":[
            {"func_id":1,"func_name":"包含参数，方便对比转码质量（推荐）"},
            {"func_id":2,"func_name":"不包含参数，不支持同时转多版本"}]})[0]
        crop_choice = ui(data={"limit_func":True,"desc":"转码时是否自动检测并裁切黑边（10个时间节点7个一致才裁切）","type":"option","display_key":"func_id","func_key":"func_id","data":[
            {"func_id":1,"func_name":"是，自动检测并裁切黑边"},
            {"func_id":2,"func_name":"否，保留原始画面"}]})[0]
        do_crop = (crop_choice == '1')
        encode_filter = ui(data={"limit_func":True,"desc":"选择要转码的文件范围","type":"option","display_key":"func_id","func_key":"f","data":[
            {"func_id":1,"f":"all",      "func_name":"转码全部文件"},
            {"func_id":2,"f":"no_crop",  "func_name":"只转码不需要切黑边的文件（检测无黑边则转码，有黑边则跳过）"},
            {"func_id":3,"f":"crop",     "func_name":"只转码需要切黑边的文件（检测有黑边则转码，无黑边则跳过）"},
            {"func_id":4,"f":"crop_lt90","func_name":"只转码需要切黑边且裁切后像素<90%的文件"}]})[0]
    elif func_code == 'snap':
        gap = ui(data={"limit_func":True,"desc":"请输入截图的间隔，单位秒，可以支持小数点","type":"keyword","display_key":"截图间隔（秒）","allow_none":False})[0]

    # 收集文件路径列表，不读取视频信息
    job_list = []
    for maindir, subdir, file_name_list in os.walk(srcdir):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            if tardir in apath:
                continue
            if func_code == 'encode':
                for res in target_res.split(','):
                    for coder in target_coder.split(','):
                        job_list.append({
                            "org": apath, "tardir": tardir, "srcdir": srcdir,
                            "res_key": res, "coder": coder,
                            "target_q": target_q, "target_speed": target_speed,
                            "target_audio": target_audio, "with_args": with_args,
                            "do_crop": do_crop, "encode_filter": encode_filter
                        })
            elif func_code == 'snap':
                job_list.append({"org": apath, "tardir": tardir, "srcdir": srcdir, "gap": gap})
            elif func_code == 'detect':
                job_list.append({"org": apath, "tardir": tardir, "srcdir": srcdir})

    p = multiprocessing.Pool(processes=tread)
    if func_code == 'encode':
        for keys in job_list:
            p.apply_async(func=do_trans, kwds=keys)
        p.close()
        p.join()
    elif func_code == 'snap':
        for keys in job_list:
            p.apply_async(func=do_snap, kwds=keys)
        p.close()
        p.join()
    elif func_code == 'detect':
        async_results = [p.apply_async(func=do_detect, kwds=keys) for keys in job_list]
        p.close()
        p.join()
        all_results = [v for v in (r.get() for r in async_results) if v is not None]
        if all_results:
            out_path = os.path.join(srcdir, 'focus_list.txt')
            with open(out_path, 'w', encoding='utf-8') as f:
                tb = PrettyTable(field_names=["file","org_size","crop_size","crop_pct","crop_param","confidence","do_crop"])
                tb.padding_width = 1
                tb.align = 'l'
                for item in all_results:
                    tb.add_row([item["file"], item["org_size"], item["crop_size"], item["crop_pct"],
                                item["crop_param"], item["confidence"], item["do_crop"]])
                f.write(str(tb))
            has_crop = sum(1 for i in all_results if i["do_crop"] == "Y")
            print("检测完成，结果已写入:", out_path)
            print("共 {} 个文件，其中 {} 个含黑边".format(len(all_results), has_crop))
        else:
            print("未检测到任何有效视频文件")


if __name__ == "__main__":
    play()
