from fileinput import close
import re
import os
import sys
from tkinter.messagebox import NO
from mutagen.id3 import ID3, TIT2, TPE1, USLT, APIC
from mutagen.flac import FLAC, Picture
import chardet

version = '0.1.2'
#print('EmbedLrc   ', version, sep='')

supportAudioTypes = ['.mp3', '.flac']
supportLrcTypes = ['.lrc']

singer = ''
sond = ''

def ScanFiles(directory):
    filelist = []
    allObjects = [
        os.path.normpath(os.path.join(directory.strip(), filename)) for filename in os.listdir(directory)]
    for m in allObjects:
        if os.path.isfile(m):
            filelist.append(m)
        elif os.path.isdir(m):
            filelist.extend(ScanFiles(m))
        else:
            pass
    return filelist


def GetMatchFiles(filelist, regexs):
    matchedFiles = []
    for regex in regexs:
        pattern = re.compile(regex)
        matchedFiles.extend(m for m in filelist if pattern.match(m))
    return matchedFiles


def CreateMap(filelist):
    tempMap = {}
    for file in filelist:
        subffix = os.path.splitext(file)[-1]
        tempMap[os.path.basename(file)[:-len(subffix)]] = file
    return tempMap

supportAudioTypes = ['.+\\' + m for m in supportAudioTypes]
supportLrcTypes = ['.+\\' + m for m in supportLrcTypes]

fileList = []
args = sys.argv[1:]
for arg in args:
    if os.path.isdir(arg):
        fileList.extend(ScanFiles(arg))
    elif arg == 'EmbedLrc.py':
        pass
    else:
        print('Error:{0} is not a directory!'.format(arg))

if not fileList:
    print('No file input!')
    sys.exit(1)

def ModifyMP3File(file, lyric, image):
    audio = ID3(file)
    #print(audio.pprint)

    # 修改演出者(艺术家)
    audio.delall('TPE1')
    audio['TPE1'] = TPE1(
        encoding = 3,   # LATIN1[0], UTF16[1], UTF16BE[2], UTF8[3]
        text = singer
    )

    # 修改歌名
    audio.delall('TIT2')
    audio['TIT2'] = TIT2(
        encoding = 3,
        text = song
    )

    # 歌词
    audio.delall('USLT')
    #audio.add(USLT(text=lrctext, encoding=3))
    audio['USLT'] = USLT(
        encoding = 3,
        text = lyric
    )

    # 封面
    audio.delall('APIC')
    if image != None:
        audio['APIC'] = APIC(
            encoding = 3,
            data = image
        )

    audio.delall('TALB')    # 专辑
    audio.delall('TRCK')    # 音轨
    audio.delall('TPOS')    # 唱碟编号
    audio.delall('TDRC')    # 录制时间
    audio.delall('TYER')    # 录制年份
    audio.delall('TPUB')    # 发行人
    audio.delall('TCOM')    # 作曲家
    audio.delall('TPE2')    # 伴奏
    audio.delall('TCON')    # 流派
    audio.delall('TPE3')    # 指挥
    audio.delall('COMM')    # 评论
    audio.delall('TIT1')    # 分组
    audio.delall('TCOP')    # 版权
    audio.delall('TEXT')    # 歌曲作者
    audio.delall('TIME')    # 时间
    audio.delall('TOAL')    # 原唱片集
    audio.delall('TOFN')    # 原文件名
    audio.delall('TOLY')    # 原歌词作者
    audio.delall('TOPE')    # 原艺术家
    # audio.delall('TLAN')    # 语言

    audio.save()
    #print(audio.pprint)

def DeleteFlacTags(flac, tags):
    tag = tags
    if tag.lower() in flac.tags:
        flac.pop(tag.lower())
    elif tag.upper() in flac.tags:
        flac.pop(tag.upper())

def ModifyFlacFile(file, lyric, image):
    audio = FLAC(music_file)
    #print(audio.pprint)

    # 修改演出者(艺术家)
    DeleteFlacTags(audio, 'artist')
    audio['artist'] = singer

    # 修改歌名
    DeleteFlacTags(audio, 'title')
    audio['title'] = song

    # 歌词
    DeleteFlacTags(audio, 'lyrics')
    audio['lyrics'] = lyric

    # 封面
    if image != None:
        if audio.pictures:
            audio.pictures[0].type = 3
            audio.pictures[0].mime = 'image/jpeg'
            audio.pictures[0].desc = 'cover'
            audio.pictures[0].data = image
        else:
            pic = Picture()
            pic.type = 3
            pic.mime = 'image/jpeg'
            pic.desc = 'cover'
            pic.data = image
            audio.add_picture(pic)
        

    DeleteFlacTags(audio, 'album')          # 专辑
    DeleteFlacTags(audio, 'tracknumber')    # 音轨编号
    DeleteFlacTags(audio, 'tracktotal')     # 音轨编号
    DeleteFlacTags(audio, 'discnumber')     # 唱碟编号
    DeleteFlacTags(audio, 'disctotal')      # 唱碟总量
    DeleteFlacTags(audio, 'date')           # 录制时间
    DeleteFlacTags(audio, 'organization')   # 发行人
    DeleteFlacTags(audio, 'composer')       # 作曲家
    DeleteFlacTags(audio, 'albumartist')    # 伴奏
    DeleteFlacTags(audio, 'genre')          # 流派
    DeleteFlacTags(audio, 'conductor')      # 指挥
    DeleteFlacTags(audio, 'comment')        # 评论
    DeleteFlacTags(audio, 'contentgroup')   # 分组
    DeleteFlacTags(audio, 'language')       # 语言

    audio.save()
    #print(audio.pprint)

audioList = CreateMap(GetMatchFiles(fileList, supportAudioTypes))
lrcList = CreateMap(GetMatchFiles(fileList, supportLrcTypes))

pattern_deltimetags = re.compile(r'\[.*?\]')
pattern_dellinebreaks = re.compile(r'^\s$')

success = 0
failure = 0

for audioName in audioList.keys():
    if ' - ' in audioName:
        continue
    if audioName in lrcList.keys():
        print('Start to handle {0} ...'.format(audioName), end='')

        # 提取歌词内容
        lrc_content = '\0'
        with open(lrcList[audioName], 'rb') as lrc:
            lrcRawText = lrc.read()
            if len(lrcRawText) > 0:
                encoding = chardet.detect(lrcRawText)['encoding']
                lrc_content = lrcRawText.decode(encoding)
            else:
                lrc_content = 'No lyric.'
            lrc.close()

        #lrc_content = pattern_deltimetags.subn('', lrc_content)[0]
        lrc_content = pattern_dellinebreaks.subn('', lrc_content)[0]

        # 获取歌曲名和歌手名
        music_file = audioList[audioName]
        music_base_name = os.path.basename(music_file)
        music_file_name = os.path.splitext(music_base_name)[0]
        music_abs_path = os.path.abspath(os.path.dirname(music_file)) + os.path.sep
        music_subffix = os.path.splitext(music_file)[-1]

        song = music_file_name.split('-')[0].strip()
        song_sp = re.split('[(（]', song)
        if len(song_sp) > 1:
            song = song_sp[0].strip()

        singer = music_file_name.split('-')[-1].strip()
        singer_sp = re.split('[、+&]', singer)
        if len(singer_sp) > 1:
            singer = singer_sp[0].strip()

        music_old_name = music_abs_path + music_base_name
        music_new_name = music_abs_path + singer + ' - ' + song + music_subffix

        # 修改歌词文件名
        lrc_file = lrcList[audioName]
        lrc_base_name = os.path.basename(lrc_file)
        lrc_abs_path = os.path.abspath(os.path.dirname(lrc_file)) + os.path.sep
        lrc_subffix = os.path.splitext(lrc_file)[-1]
        lrc_old_name = lrc_abs_path + lrc_base_name
        lrc_new_name = lrc_abs_path + singer + ' - ' + song + lrc_subffix

        # 提取封面图片内容
        img_content = None
        img_name = music_abs_path + 'cover\\' +singer + '.jpg'
        if os.path.isfile(img_name):
            with open(img_name, 'rb') as img:
                img_content = img.read()
                img.close()
        else:
            print('Can\'t find cover file for {0} ...'.format(audioName), end='')
            failure += 1

        if music_subffix == '.mp3':
            ModifyMP3File(music_file, lrc_content, img_content)
        elif music_subffix == '.flac':
            ModifyFlacFile(music_file, lrc_content, img_content)
        else:
            print('failed!')
            continue

        # swap singer and song
        os.rename(music_old_name, music_new_name)
        os.rename(lrc_old_name, lrc_new_name)
        print('done!')
        success += 1
    else:
        print('Can\'t find lrc file for {0}'.format(audioName))
        failure += 1

print('success: ' + str(success) + ', failure: ' + str(failure))