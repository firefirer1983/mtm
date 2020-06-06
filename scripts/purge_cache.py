import os

from mtm.utils.dir_tools import rm_dir_safe

purge_dirs = [
    "/home/xy/misc/mtm/cache/youtube/专心读书工作用BGM 小鸟叫的声音最适合作为专注读书或工作用的BGM Bird Chirping Sound for study and working-Eqp0d-Uoeqk",
    "/home/xy/misc/mtm/cache/youtube/下雨 · 大自然声音感受暴風雨狂风暴雨的声音 Thunderstorm Sound Rain sound Natural sound-Jwhss4LOGE0",
    "/home/xy/misc/mtm/cache/youtube/放鬆療愈音樂 下雨的聲音睡眠 讀書 冥想 工作 BGMRelaxation healing music  Rain sound for sleep meditation-VhuaXzsm_O0",
    "/home/xy/misc/mtm/cache/youtube/莫扎特HD乾淨無廣告版 6小時多首寶寶古典音樂盒  布拉姆斯 莫札特 貝多芬搖籃曲  BABY CLASSICAL MUSIC-L0skErRNc5Y",
    "/home/xy/misc/mtm/cache/youtube/令人放松的瀑布声小型瀑布的流水声帮助专心读书放松睡眠的bgmWaterfall sound  Relax sound Sleeping music-mApstMXkhbw",
    "/home/xy/misc/mtm/cache/youtube/下雨的聲音  放鬆音樂沉澱心情聽了好睡覺 Raining Sound Relax music Good for Sleeping-CU2777IVMGU",
]

if __name__ == '__main__':
    for d in purge_dirs:
        if not os.path.exists(str(d)):
            continue
        rm_dir_safe(str(d))
