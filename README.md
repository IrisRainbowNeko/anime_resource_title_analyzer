# 分析番剧标题等信息

本工具目前可以根据番剧发布组提供的标题 (如 nyaa.si)，分析得到实际的:
+ 字幕组
+ 番剧标题
+ 分辨率
+ 第几集

## 使用方法
安装相关依赖:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

分析一组标题:
```python
from analyze_title import TitleAnalyzer

title_list = ["[Anime Land] One Piece 1080 (WEBRip 1080p Hi10P AAC) RAW [C79BE92B].mp4",
        "[MonoNocturno] Ragna Crimson 03 (BS11 1920x1080 x264 AAC).mp4",
        "[Koi-Raws] MF Ghost - 03 「カマボコストレート」 (ANIMAX 1920x1080 x264 AAC).mkv",
        "[Koi-Raws] SPY×FAMILY (2023) - 28 「任務と家族／華麗なるボンドマン／子ども心／目覚まし」 (TX 1920x1080 x264 AAC).mkv",
        "Kusuriya no Hitorigoto S01E03 1080p AMZN WEB-DL DDP2.0 H 264-VARYG (The Apothecary Diaries)",
        "【喵萌奶茶屋】★07月新番★[不死少女·殺人笑劇 / Undead Girl Murder Farce][01-13][1080p][繁日雙語][招募翻譯]",
        "[DBD-Raws][Go! Princess 光之美少女/Go! 公主光之美少女/Go! Princess Precure/Go! プリンセスプリキュア][01-50TV全集+特典映像][1080P][BDRip][HEVC-10bit][FLAC][MKV]",
        "[Shiniori-Raws] Bakumatsu Rock (BD 1280x720 x264 10bit AAC)",
    ]

analyzer = TitleAnalyzer()

for title in title_list:
    fansub, real_title, res, ep = analyzer.analyze(title)
    print(title)
    print(f'Fansub: \033[32m{fansub}\033[0m, Title: \033[33m{real_title}\033[0m, Res: \033[34m{res}\033[0m, EP: \033[35m{ep}\033[0m')
```

分析结果:
```
Fansub: Anime Land, Title: One Piece, Res: 1920x1080, EP: 1080
Fansub: MonoNocturno, Title: Ragna Crimson, Res: 1920x1080, EP: 03
Fansub: Koi - Raws, Title: MF Ghost, Res: 1920x1080, EP: 03
Fansub: Koi - Raws, Title: SPY×FAMILY  , Res: 1920x1080, EP: 28
Fansub: None, Title: Kusuriya no Hitorigoto, Res: 1920x1080, EP: None
Fansub: 喵萌奶茶屋, Title: 不死少女·殺人笑劇 / Undead Girl Murder Farce, Res: 1920x1080, EP: 01-13
Fansub: DBD - Raws, Title: Go! Princess 光之美少女/Go! 公主光之美少女/Go! Princess Precure/Go! プリンセスプリキュア, Res: 1920x1080, EP: None
Fansub: Shiniori - Raws, Title: Bakumatsu Rock, Res: 1280x720, EP: None
```