import re
from typing import List, Tuple

import spacy

class TitleAnalyzer:
    Fansub_tag = ['NNP', 'NNS', 'NN', 'HYPH', 'CD']
    nn_words = ['NN', 'NNS', 'NNP']

    pattern_SE = r'(S\d+E?\d*|Season\d*|EP?\d+)'
    pattern_number = r'^\d+$'
    pattern_res = '(\d+x\d+|\d{3,4}p?)'
    pattern_ep = r'^v?\d+$'

    res_map = {2160:'3840x2160', 1440:'2560x1440', 1080:'1920x1080', 720:'1280x720', 480:'640x480'}

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def find_Fansub(self, text):
        words_tag = self.get_words_tag(self.nlp(text))

        reject_idx = []
        for idx, (word, tag) in enumerate(words_tag):
            if tag not in self.Fansub_tag:
                reject_idx.append(idx)
        if len(reject_idx) == 0:
            return ' '.join(word[0] for word in words_tag)
        for idx in reject_idx:
            if idx+1 == len(words_tag) or not words_tag[idx+1][1] == 'HYPH':
                return None
            return ' '.join(word[0] for word in words_tag)

    def find_title(self, text):
        pattern_brackets = r'\((.*?)\)'
        text_in = re.findall(pattern_brackets, text)
        # 剩余文本
        text_out = re.sub(pattern_brackets, '', text).strip()

        title_tags = self.get_words_tag(self.nlp(text_out))

        # find available <HYPH>
        start = 2
        idx_HYPH = -1
        for idx, (word, tag) in enumerate(title_tags[start:]):
            ridx = idx+start
            if tag == 'HYPH':
                if title_tags[ridx-1][1] in self.nn_words and title_tags[ridx+1][1] in self.nn_words and \
                        not re.match(self.pattern_SE, title_tags[ridx+1][0]):  # 分隔符后面可能有 Season 标识
                    continue
                idx_HYPH = ridx
                break

        idx_CD = self.index_tag(title_tags, ['CD'], start=start)

        # find SE index
        idx_SE = -1
        for idx, (word, tag) in enumerate(title_tags):
            if re.match(self.pattern_SE, word):
                idx_SE = idx
                break

        idx_end = self.min_available(idx_HYPH, idx_CD, idx_SE)
        ep = self.find_episodes(title_tags)

        if idx_end != -1:
            se, rest = self.find_se(title_tags[:idx_end])
            if rest[-1][0] == '-':
                rest = rest[:-1]
            return ' '.join(word[0] for word in rest), None, ep
        return None, text_out, ep

    def find_title_in_brackets(self, text_list):
        for text in text_list:
            title_tags = self.get_words_tag(self.nlp(text))
            if len(title_tags)>2:
                for idx, (word, tag) in enumerate(title_tags):
                    if tag == 'SYM':
                        if title_tags[idx-1][1] in self.nn_words and title_tags[idx+1][1] in self.nn_words:
                            return text
        return None

    def find_episodes_in_brackets(self, text_list):
        ep = None
        for text in text_list:
            title_tags = self.get_words_tag(self.nlp(text))
            ep_ = self.find_episodes(title_tags)
            if ep_ is not None:
                ep = ep_
        return ep

    def find_se(self, title_tags):
        se_word, rest_word = [], []
        for idx, (word, tag) in enumerate(title_tags):
            if re.match(self.pattern_SE, word):
                se_word.append(title_tags[idx])
            else:
                rest_word.append(title_tags[idx])
        return se_word, rest_word

    def find_episodes(self, words_tags):
        ep_high_p, ep_low_p = [], []
        for idx, (word, tag) in enumerate(words_tags):
            if re.match(self.pattern_ep, word):
                try:
                    if words_tags[idx+1][1] in ['HYPH', 'SYM']:
                        if words_tags[idx+2][1] == 'CD':
                            if not word.startswith('0') and words_tags[idx+2][0].startswith('0'):
                                ep_high_p.append(words_tags[idx+2][0])
                                continue
                            return word+words_tags[idx+1][0]+words_tags[idx+2][0]
                        else:
                            continue
                except:
                    pass
                if len(word) == 2 or word.startswith('0'):
                    ep_high_p.append(word)
                else:
                    ep_low_p.append(word)
        if len(ep_high_p)>0:
            return ep_high_p[0]
        elif len(ep_low_p)>0:
            return ep_low_p[0]
        else:
            return None

    def index_tag(self, words_tag: List[Tuple[str, str]], tags: List[str], start=0):
        for idx, (word, tag) in enumerate(words_tag[start:]):
            if tag in tags:
                return idx+start
        return -1

    def split_title(self, text):
        # 使用正则表达式查找"[ ]"中间的内容
        pattern = r'\[(.*?)\]'
        matches = re.findall(pattern, text)
        # 剩余文本
        remaining_text = re.sub(pattern, '', text)

        return matches, remaining_text.strip()

    def find_resolution(self, text: str):
        res_list = re.findall(self.pattern_res, text.lower())
        for res in res_list:
            if res.endswith('p'):
                return self.res_map[int(res[:-1])]
            elif 'x' in res:
                return res
            else:
                try:
                    return self.res_map[int(res)]
                except:
                    pass

    def analyze(self, title):
        title = title.replace('【', '[')
        title = title.replace('】', ']')

        text_in_list, text_out = self.split_title(title)
        fansub = None
        if len(text_in_list)>0:
            fansub = self.find_Fansub(text_in_list[0])

        real_title, maybe_title, ep = self.find_title(text_out) if len(text_out)>0 else (None, None, None)
        if real_title is None:
            real_title = self.find_title_in_brackets(text_in_list)

        # 标题可能没有什么好用的标识，格式太乱，找不到也没办法了
        if real_title is None:
            real_title = maybe_title

        res = self.find_resolution(title)

        if ep is None:
            ep = self.find_episodes_in_brackets(text_in_list)

        return fansub, real_title, res, ep

    @staticmethod
    def print_word_tag(doc, color='32'):
        tag = ""
        for word in list(doc.sents)[0]:
            # print(word, word.tag_)
            tag += f"{word}+<{word.tag_}> "
        print(f'\033[{color}m'+tag+'\033[0m')

    @staticmethod
    def get_words_tag(doc):
        sents = list(doc.sents)
        words_tag = [(str(word), word.tag_) for words in sents for word in words]
        words_tag = TitleAnalyzer.fix_CD(words_tag)
        return words_tag

    @staticmethod
    def fix_CD(words_tag):
        for idx, (word, tag) in enumerate(words_tag):
            if re.match(TitleAnalyzer.pattern_number, word):
                words_tag[idx] = (word, 'CD')
        return words_tag

    @staticmethod
    def min_available(*idx):
        idx = [x for x in idx if x != -1]
        return min(idx) if len(idx)>0 else -1

if __name__ == '__main__':
    title_list = ["[Anime Land] One Piece 1080 (WEBRip 1080p Hi10P AAC) RAW [C79BE92B].mp4",
        "[MonoNocturno] Ragna Crimson 03 (BS11 1920x1080 x264 AAC).mp4",
        "[MonoNocturno] Ragna Crimson 02 (BS11 1920x1080 x264 AAC).mp4",
        "[MonoNocturno] Ragna Crimson 01 (BS11 1920x1080 x264 AAC).mp4",
        "[NanakoRaws] One Piece - 843 (BS8 1920x1080 x265 AAC).mkv (include JPsub)",
        "[Ohys-Raws] Potion-danomi de Ikinobimasu! - 03 (EX 1280x720 x264 AAC).mp4",
        "[Ohys-Raws] Bokura no Ame-iro Protocol - 03 (EX 1280x720 x264 AAC).mp4",
        "[New-raws] Kusuriya no Hitorigoto - 03 [1080p] [NF].mkv",
        "[New-raws] Kusuriya no Hitorigoto - 02 [1080p] [NF].mkv",
        "[New-raws] Kusuriya no Hitorigoto - 01 [1080p] [NF].mkv",
        "[NanakoRaws] One Piece - 1080 (WEB-DL 1920x1080 x264 AAC).mkv (include JPsub)",
        "[New-raws] One Piece -1080 [1080p] [WEB].mkv",
        "[7³ACG] Vinland Saga 2 ヴィンランド・サガ Season 2 [BDRip 1080p x265 FLAC]",
        "[Koi-Raws] Hikikomari Kyuuketsuki no Monmon - 03 「ひきこもり吸血姫の闇」 (MX 1920x1080 x264 AAC).mp4",
        "[Koi-Raws] Saihate no Paladin - Tetsusabi no Yama no Ou - 03 「最後の王」 (MX 1920x1080 x264 AAC).mp4",
        "[Koi-Raws] MF Ghost - 03 「カマボコストレート」 (ANIMAX 1920x1080 x264 AAC).mkv",
        "[Koi-Raws] SPY×FAMILY (2023) - 28 「任務と家族／華麗なるボンドマン／子ども心／目覚まし」 (TX 1920x1080 x264 AAC).mkv",
        "Kusuriya no Hitorigoto S01E03 1080p AMZN WEB-DL DDP2.0 H 264-VARYG (The Apothecary Diaries)",
        "Kusuriya no Hitorigoto S01E02 1080p AMZN WEB-DL DDP2.0 H 264-VARYG (The Apothecary Diaries)",
        "Kusuriya no Hitorigoto S01E01 1080p AMZN WEB-DL DDP2.0 H 264-VARYG (The Apothecary Diaries)",
        "Chuunibyou Demo Koi ga Shitai 2012 Season Collection 1080p BluRay x264 10bit FLAC-Shiniori",
        "Chuunibyou Demo Koi ga Shitai 2012 Season Collection 720p BluRay x264 10bit AAC-Shiniori",
        "【喵萌奶茶屋】★07月新番★[不死少女·殺人笑劇 / Undead Girl Murder Farce][01-13][1080p][繁日雙語][招募翻譯]",
        "[TRC] The Great Cleric - S01 [English Dub] [CR WEB-RIP 1080p HEVC-10 AAC]",
        "[Koi-Raws] Megumi no Daigo - Kyuukoku no Orange - 04 「不破特別救助隊」 (NTV 1920x1080 x264 AAC).mkv",
        "[ReinForce] Kono Subarashii Sekai ni Bakuen wo! (BDRip 1920x1080 x264 FLAC)",
        "[Ohys-Raws] Kanojo, Okarishimasu S3 (TBS 1920x1080 x264 AAC)",
        "[Ohys-Raws] Nanatsu no Maken ga Shihai Suru (BS11 1920x1080 x264 AAC)",
        "[Ohys-Raws] Maou Gakuin no Futekigousha II (AT-X 1920x1080 x264 AAC)",
        "[Ohys-Raws] Sugar Apple Fairy Tale S2 (AT-X 1920x1080 x264 AAC)",
        "[DBD-Raws][Go! Princess 光之美少女/Go! 公主光之美少女/Go! Princess Precure/Go! プリンセスプリキュア][01-50TV全集+特典映像][1080P][BDRip][HEVC-10bit][FLAC][MKV]",
        "[Shiniori-Raws] Bakumatsu Rock (BD 1280x720 x264 10bit AAC)",
    ]

    analyzer = TitleAnalyzer()

    for title in title_list:
        fansub, real_title, res, ep = analyzer.analyze(title)
        print(title)
        print(f'Fansub: \033[32m{fansub}\033[0m, Title: \033[33m{real_title}\033[0m, Res: \033[34m{res}\033[0m, EP: \033[35m{ep}\033[0m')
