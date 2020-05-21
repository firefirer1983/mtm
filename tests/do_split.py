from pathlib import Path
from mtm.utils.string_fmt import (
    is_partial_dir,
    check_file_with_ext,
    parse_unique_id,
)
from mtm.components.splitter import split_audio

repo_path = "/home/xy/misc/cache/youtube"

to_split_dirs = [
    "/home/xy/misc/cache/youtube/宮崎駿  吉他演奏 鋼琴音樂 純音樂 適合放鬆  睡眠 舒眠 療癒 看書 讀書  PIANO MUSIC RELAX MUSIC MIYAZAKI HAYAO roses-b5K192_hilA",
    # "/home/xy/misc/cache/youtube/宮崎駿  無廣告 學習音樂 閱讀和學習 集中的音樂  放松 读书 工作 舒眠钢琴音乐 放松音乐 睡眠音乐 学习音乐 看书音乐 roses-PJ1QwhNL72A",
    # "/home/xy/misc/cache/youtube/海浪声音  马尔代夫海滩适合冥想的海洋声音 Wave Sounds  Maldives Beach Ocean Sound for Meditation-J7OSA6Kw2-s",
    # "/home/xy/misc/cache/youtube/专心读书工作用BGM 小鸟叫的声音最适合作为专注读书或工作用的BGM Bird Chirping Sound for study and working-Eqp0d-Uoeqk",
    # "/home/xy/misc/cache/youtube/下雨聲  森林里的下雨聲大自然的聲音療愈放鬆 Rain Sounds  Rain in the Forest Natures Sound Healing Relaxing-JAKdceOziLM",
    # "/home/xy/misc/cache/youtube/水流的聲音  治療疲勞冥想放鬆（3小時版）Relaxing water sound nature sound meditation 3 hours long-2DUWs4WO__Y",
    # "/home/xy/misc/cache/youtube/海浪聲音  沙灘邊令人放鬆的海浪聲 Sound of sandy beach  Relax sleep-ed3DnP2nbrw",
    # "/home/xy/misc/cache/youtube/睡眠用・冥想用BGM「神秘的下雨音」學習放鬆睡眠BGMSleep Meditation Rain Sound-lz6yCQBWSU8",
    # "/home/xy/misc/cache/youtube/下雨 · 大自然声音感受暴風雨狂风暴雨的声音 Thunderstorm Sound Rain sound Natural sound-Jwhss4LOGE0",
    # "/home/xy/misc/cache/youtube/放鬆療愈音樂 下雨的聲音睡眠 讀書 冥想 工作 BGMRelaxation healing music  Rain sound for sleep meditation-VhuaXzsm_O0",
    # "/home/xy/misc/cache/youtube/宮崎駿  水晶音樂 純音樂 高畫質加長版  適合睡眠 舒眠 靜坐 冥想 放鬆 看書 減壓  PIANO MUSIC RELAX MUSIC MIYAZAKI HAYAO roses-v0ADJy2Menk",
    # "/home/xy/misc/cache/youtube/宮崎駿  無廣告 學習音樂 閱讀和學習 集中的音樂  放松 读书 工作 舒眠钢琴音乐 放松音乐 睡眠音乐 学习音乐 看书音乐 roses-PJ1QwhNL72A",
    # "/home/xy/misc/cache/youtube/療愈 · 自然音農村下雨的聲音 讀書 睡眠 冥想用 工作用bgmRain  cricket insect sound-YkXOLiZLFho",
    # "/home/xy/misc/cache/youtube/海浪声音  泰国普吉岛海滩适合学习工作的声音 Wave Sound  Thailand Phuket Beach Nature Sound for Studying-lT8lT1sjxVk",
    # "/home/xy/misc/cache/youtube/水流聲音  風鈴聲音  舒服到想睡覺的放鬆聲音Water Sound  Wind Chime Sound  Comfortable to sleep sound-r2EXpMHEtB8",
    # "/home/xy/misc/cache/youtube/洞窟河流的声音  睡眠冥想放松集中力维持的大自然声音 River sound in the cave  Sleep Meditation Relax Focus-CxQByCIzZ64",
    # "/home/xy/misc/cache/youtube/海浪聲音  加勒比海灘的海洋聲音學習與工作的好聲音Wave Sounds  Caribbean Beach Good for Studying and Working-AXVTYeFDbuM",
    # "/home/xy/misc/cache/youtube/在台灣台北的民宿錄製舒壓的下雨聲睡覺放鬆禪修冥想Raining sound Record in Taipei Taiwan-Yol5fROT890",
    # "/home/xy/misc/cache/youtube/Relaxing River Sounds  Peaceful Forest River  3 Hours Long  HD 1080p  Nature Video-IvjMgVS6kng",
    # "/home/xy/misc/cache/youtube/大自然声音小雨落在雨伞上的声音读书 睡眠 冥想用 工作用bgm Rain sound on the umbrella relax study focus work-ebnVse36UhY",
    # "/home/xy/misc/cache/youtube/放鬆音樂 深度睡眠放鬆音樂治療音樂舒壓按摩音樂 睡眠音樂療癒音樂鋼琴音樂波音鋼琴曲輕音樂輕快BGM純音樂钢琴曲轻音乐放松音乐 纯音乐轻快钢琴音乐-fPz2tZibAAQ",
    # "/home/xy/misc/cache/youtube/疗愈・工作用BGM提高专注力的下雨声工作音乐学习音乐 Raining Sounds  Focus Music  For Working and Studying-MwA8rmwoLvE",
    # "/home/xy/misc/cache/youtube/睡眠音乐 · 疲劳回复下雨 BGM Sleep Music Healing Music Raining Sounds-sVld3uKBMzE",
    # "/home/xy/misc/cache/youtube/下雨白噪音  睡眠 與 放鬆音樂 3小時版-4ugMwV6JKXE",
    # "/home/xy/misc/cache/youtube/学习工作音乐  提高集中力记忆力（1小时30分钟）Study work music  Focus concentration and memory 15 hour-LEixnEKdwTM",
    # "/home/xy/misc/cache/youtube/白噪音讓人放鬆幫助睡眠的音樂 與 下雨聲-h5UpkFgpkCE",
    # "/home/xy/misc/cache/youtube/3 HOURS Relaxing Music with Water Sounds Meditation-luRkeDCoxZ4",
    # "/home/xy/misc/cache/youtube/等你下課 周杰倫  鋼琴版工作讀書專注用的音樂 Waiting for you by Jay Chou   Working Reading  Relaxing Piano Music-3ynRsI5wtDo",
    # "/home/xy/misc/cache/youtube/Relax24NoRain  Gentle Stream-gmar4gh5nIw",
    # "/home/xy/misc/cache/youtube/莫扎特HD乾淨無廣告版 6小時多首寶寶古典音樂盒  布拉姆斯 莫札特 貝多芬搖籃曲  BABY CLASSICAL MUSIC-L0skErRNc5Y",
    # "/home/xy/misc/cache/youtube/療愈 · 大自然打雷聲音  暴風雨 bgm 讀書 睡眠 冥想 作業用bgm Thunder storm Natural Sound Relaxation Focus-_1n5_HknzTo",
    # "/home/xy/misc/cache/youtube/放鬆音樂深度睡眠放鬆音樂治療音樂舒壓按摩音樂 睡眠音樂療癒音樂鋼琴音樂波音鋼琴曲輕音樂輕快BGM純音樂钢琴曲轻音乐放松音乐 纯音乐轻快钢琴音乐-ObO6XEQSWak",
    # "/home/xy/misc/cache/youtube/疗愈的自然音雨水打落石头的声音读书睡眠冥想用工作用bgmRaining Sound Natural Sound Healing Sound-HHKpPEMxNpw",
    # "/home/xy/misc/cache/youtube/癒愈的自然音睡眠和放鬆的大自然聲音  下雨的聲音 Sleep and Relax Nature Sounds from the Farm Village-cWU1o-misXI",
    # "/home/xy/misc/cache/youtube/作業用・勉強用BGM集中力・記憶力を向上させるヒーリングピアノ曲集1時間30分-Vn4wxZlaFYc",
    # "/home/xy/misc/cache/youtube/營火燃燒的聲音  晚上森林的營火療愈的聲音睡眠冥想 Campfire Burning Sound  Healing Voice Sleep Meditation-9JRQkrNwXKo",
    # "/home/xy/misc/cache/youtube/下雨聲  台北城市下雨的聲音放鬆睡覺 Rain Sounds  Taipei City Rain Sounds Relax Sleep-DEqgTkRMYso",
    # "/home/xy/misc/cache/youtube/專注學習工作BGM純下雨的聲音讀書 專注 冥想 工作用bgmFocus Sound Rain Sound-6xpqNMfRnUc",
    # "/home/xy/misc/cache/youtube/海浪声音  美丽的岛屿海鸥海浪的声音睡眠工作学习用Wave Sounds  Beautiful islands seagull Sleep work study use-usAAuGIBZTg",
    # "/home/xy/misc/cache/youtube/30分钟 · 下雨的声音读书音乐放松睡眠工作背景音乐冥想bgm A relaxing music raining music-SUabnM-0We4",
    # "/home/xy/misc/cache/youtube/令人放松的瀑布声小型瀑布的流水声帮助专心读书放松睡眠的bgmWaterfall sound  Relax sound Sleeping music-mApstMXkhbw",
    # "/home/xy/misc/cache/youtube/下雨 · 大自然聲音在車裡聴下雨的聲音讀書 睡眠 冥想用 工作用bgm Rain sound in the car relax and focus-S7R_h1qRc2E",
    # "/home/xy/misc/cache/youtube/癒愈 · 自然音「森林下雨聲音小鳥聲音」 讀書 睡眠 冥想用 工作用bgmRain Sound in the forest  Bird chirp sound-HmCm3kgyFks",
    # "/home/xy/misc/cache/youtube/水流的聲音河流流水的聲音讀書 睡眠 冥想用bgm River water sound Natural Sound-aewgrdzblJk",
    # "/home/xy/misc/cache/youtube/轻松的音乐深度睡眠三角洲双耳波   音乐放松和缓解压力-ghzxtpkgRX8",
    # "/home/xy/misc/cache/youtube/Beautiful Piano Music for working  studyingFlight of The Silverbird  旋律超优美的钢琴音乐  读书工作用bgm-SVqaafea7WA",
    # "/home/xy/misc/cache/youtube/下雨的聲音  放鬆音樂沉澱心情聽了好睡覺 Raining Sound Relax music Good for Sleeping-CU2777IVMGU",
    # "/home/xy/misc/cache/youtube/BAMBOO WATER FOUNTAIN  Relax  Get Your Zen On  White Noise  Tinnitus Relief-aJaZc4E8Y4U",
    # "/home/xy/misc/cache/youtube/無廣告音樂清除負能量冥想靜心冥想和治療音樂放鬆音樂深度睡眠放鬆音樂治療音樂舒壓按摩音樂 睡眠音樂療癒音樂鋼琴音樂波音鋼琴曲輕音樂輕快BGM純音樂钢琴曲轻音乐-G8GWtGZuHSk",
]


def list_all_splittable_dir():
    splittable = []
    for d in Path(repo_path).iterdir():
        if not is_partial_dir(d):
            splittable.append(d)
    return splittable


DURATION_MAX = 15 * 60


def split_it(dir_path):
    unique_id = parse_unique_id(str(dir_path))
    for file_path in dir_path.iterdir():
        if check_file_with_ext("m4a", file_path):
            split_pattern = (
                str(dir_path) + ".part.{:04d}" + "/" + unique_id + "." + "m4a"
            )
            print("try to split %s, with %s" % (str(file_path), split_pattern))
            split_audio(file_path, DURATION_MAX, split_pattern)


if __name__ == "__main__":
    for d in [Path(p) for p in to_split_dirs]:
        split_it(d)
