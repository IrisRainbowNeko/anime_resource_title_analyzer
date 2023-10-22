from pynyaasi.nyaasi import NyaaSiClient, CategoryType
from analyze_title import TitleAnalyzer
from tqdm import tqdm

analyzer = TitleAnalyzer()
client = NyaaSiClient()

num = 100

anime_list = []
for i, item in enumerate(client.iter_items('', category=CategoryType.ANIME_RAW)):
    anime_list.append(item)
    if i>num:
        break

title_list = [item.title for item in anime_list]
for title in title_list:
    fansub, real_title, res, ep = analyzer.analyze(title)
    print(title)
    print(f'Fansub: \033[32m{fansub}\033[0m, Title: \033[33m{real_title}\033[0m, Res: \033[34m{res}\033[0m, EP: \033[35m{ep}\033[0m')
    #print(f'"{x}",')