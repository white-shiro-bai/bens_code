<!--
 * @Date: 2021-11-26 14:34:48
 * @Author: unknowwhite@outlook.com
 * @WeChat: Ben_Xiaobai
 * @LastEditTime: 2021-12-07 16:15:51
 * @FilePath: \bens_code\README.md
-->
调用ffmpeg压缩视频文件


# 用途
替代Mac下handbrake，Win下Mediacoder等收费转码软件。

预制一些参数，更加易用。也没有收费软件不购买不能转4K的问题。

提供了简单的集群转码功能。多台电脑一起转。

提供了截图功能，可以批量对视频进行截图。

# 特性

1.可以把所有FFmpeg支持的格式规范成H264/H265+AAC的MP4视频。

2.已经转过的文件会自动跳过不会重新转码或覆盖

3.可以支持不同操作系统的多台电脑同时转同一个文件夹，不会重转或覆盖。

4.自适应宽高比，转多个尺寸的时候不用分开设定大小

# 使用方法：

1.安装对应系统的Python3版本。https://www.python.org/downloads/

2.安装依赖库 pip install -r requirements.txt 如果系统之前装过python2 则运行 pip3 install -r requirements.txt

3.准备对应操作系统的ffmpeg，可以直接把对应操作系统的ffmpeg放到同目录下即可。如果没有独立编译好的，可以用官方版 下载地址 http://ffmpeg.org/download.html

4.运行do_trans.py根据提示操作即可

# 集群使用方法：

1.确定一台电脑创建NFS或CIFS共享文件夹，所有电脑均可正常读写该文件夹。

2.在任意一台电脑上按照使用方法开始转码。

3.确定转码开始后，再在下一台电脑上重复步骤2，直到所有电脑都参与进转码。

# 已知问题：

1.iphone6和iphone6plus等机型拍摄的竖屏视频，因为采用了横屏存+播放时旋转的方式，在原尺寸以外的尺寸上转码会出现比例不对的情况。

# 迭代计划：

1.支持降帧率

2.提供各系统的单文件版本，运行前不再需要安装。

3.支持iphone6等机型的竖屏视频

4.支持自定义参数

5.完善交互逻辑，提高无脑操作的便利性