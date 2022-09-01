"""
Quick and dirty starting rookie WR and RB finder
"""
import string
import requests
import pandas
from bs4 import BeautifulSoup

ROOT = 'https://www.espn.com/nfl/story/_/id/29098001/2022-nfl-depth-charts-all-32-teams'

def conv_txt(orig):
    """
    Format proper nouns
    """
    return string.capwords(orig.replace("-", " "))

def extract(player_in):
    """
    Extract player name from html
    """
    player = player_in.replace("'", "").replace(".", "")
    parts = player.split(" ")
    status = " "
    if len(parts[-1]) == 1:
        status = parts[-1]
        parts = parts[0:-1]
    name = "-".join(parts).lower()
    return name, status

def get_pos(number):
    """
    Return position description
    """
    return ['starting RB', 'starting WR1', 'starting WR2', 'starting WR3',
            'backup RB'][number]

def gen_result():
    """
    Generate csv file of rookie running backs and wide receivers to consider
    """
    rootd = requests.get(ROOT)
    soup = BeautifulSoup(rootd.text, "html.parser")
    csv_info = {'Name': [], 'Team': [], 'Position': []}
    for atag in soup.find_all('a', href=True):
        if "depth" in atag['href']:
            if atag['href'].startswith("https://www.espn.com/nfl/team"):
                dfs =  pandas.read_html(atag['href'])
                tinfo = dfs[1].to_dict()
                pos_list = []
                status_list = []
                for pindx in range(1,5):
                    player = tinfo['Starter'][pindx]
                    name, status = extract(player)
                    pos_list.append(name)
                    status_list.append(status)
                backup_rb = extract(tinfo['2nd'][1])
                pos_list.append(backup_rb[0])
                status_list.append(backup_rb[1])
                teami = requests.get(atag['href'])
                soup1 = BeautifulSoup(teami.text, "html.parser")
                team_data = soup1.find_all('a', href=True)
                team_name = ""
                player_url_to_check = []
                for urlv in team_data:
                    info = urlv['href']
                    if info.startswith("/nfl/team/_/"):
                        partz = info.split("/")
                        if len(partz[-1]) > len(team_name):
                            team_name = partz[-1]
                    if info.startswith("http://www.espn.com/nfl/player/_/id/"):
                        name = info.split("/")[-1]
                        if name in pos_list:
                            player_url_to_check.append(info)
                print(team_name)
                rookie = []
                players = []
                for pr_url in player_url_to_check[0:5]:
                    rname = pr_url.split("/")[-1]
                    players.append(rname)
                    rinfo = requests.get(pr_url)
                    soup2 = BeautifulSoup(rinfo.text, "html.parser")
                    draftdata = soup2.find_all('div')
                    for draftl in draftdata:
                        if draftl.text.startswith("2022: "):
                            rookie.append(rname)
                for indx in range(0, 5):
                    if pos_list[indx] in rookie:
                        csv_info['Name'].append(conv_txt(pos_list[indx]))
                        csv_info['Team'].append(conv_txt(team_name))
                        csv_info['Position'].append(get_pos(indx))
    dframe = pandas.DataFrame(csv_info)
    dframe.to_csv('rookies.csv')

if __name__ == "__main__":
    gen_result()
