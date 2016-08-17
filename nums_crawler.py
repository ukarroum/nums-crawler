""""
 * ************* Nums Crawler ***************
 *
 * Ecrit par Yassir Karroum [ukarroum17@gmail.com] [https://github.com/ukarroum]
 * Le 4 aout 2016
 *
 * Un simple script qui permet de récupérer des numéros de téléphone marocains en masse depuis des sites d'annonce en ligne.
 */
"""
from torPythonInt import *
from bs4 import BeautifulSoup
from stem.util import term
import io
import sys

OKGREEN = '\033[92m'
BOLD = '\033[1m'
ENDC = '\033[0m'


def souk_ma_crawler(begin=1, n=10):
    """
        Souk.ma Crawler : Permet de récupérer les numéros de téléphone disponible sur Souk.ma.

    :param begin: Par où commencer la récupération (numéro de page).
    :param n: Nombre de numéros souhaités
    :return: Liste contenant les numéros.
    """

    nums = []
    iterations = {'success': 0, 'failure': 0}
    page = begin

    new_identity()

    while len(nums) < n:

        soup = BeautifulSoup(get_html("http://www.souk.ma/fr/Maroc/&p="+str(page)), "html.parser")

        if "Sorry, there are no Web results for this search!" in soup:
            print(term.format("Vous atteint la limite des résultats de recherche .\n", term.Color.RED))
            break

        if len(soup.find_all('div', class_="desc")):
            iterations["success"] += 1
        else:
            iterations["failure"] += 1
            new_identity()
            continue

        for div in soup.find_all('div', class_="desc"):
            if div.h2:
                annonce = BeautifulSoup(get_html(div.h2.a['href']), "html.parser")

                try:
                    if annonce.find_all('div', class_="userinfo-pro"):
                        if annonce.find_all('div', class_="inner")[0].contents[7].text[0] == '0':
                            nums.append(annonce.find_all('div', class_="inner")[0].contents[7].text)

                    elif annonce.find_all('div', class_="userinfo"):
                        if annonce.find_all('i', class_="icon-envelope")[1].parent.parent.text[0] == '0':
                            nums.append(annonce.find_all('i', class_="icon-envelope")[1].parent.parent.text)
                except:
                    continue

            sys.stdout.write("\r" + OKGREEN + "Avancement : " + str(len(nums)) + " / " + str(n) + ENDC)
            sys.stdout.flush()

            if len(nums) >= n:
                break

        print()
        page += 1

    if use_tor:
        print(term.format("Arret de Tor.\n", term.Attr.BOLD))
        kill_tor()

    return nums[:n]


def save_file(links, file):
    if file == sys.stdout:
        f = sys.stdout
    else:
        f = open(file, 'w')

    for link in links:
        if not link:
            continue
        f.write(link + '\n')


if __name__ == "__main__":

    nums = set(souk_ma_crawler(1, 500))

    save_file(nums, "out")

