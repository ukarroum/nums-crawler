""""
 * ************* Nums Crawler ***************
 *
 * Ecrit par Yassir Karroum [ukarroum17@gmail.com] [https://github.com/ukarroum]
 * Le 4 aout 2016
 *
 * Un simple script qui permet de récupérer des numéros de téléphone marocains en masse depuis des sites d'annonce en ligne.
 */
"""
from bs4 import BeautifulSoup
import stem.process
from stem.util import term
import pycurl
import io
import sys

OKGREEN = '\033[92m'
BOLD = '\033[1m'
ENDC = '\033[0m'

SOCKS_PORT = 7000

tor_process = 0
use_tor = False   # Si tor est utilisé le parametre devient true

use_contry_code = True
country_code = "fr"  # Un choix arbitraire qui est du à un nombre plutot elevé des relais francais.


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

""" ============== Tor ============== """

""" Ces 3 fonctions ont été "grandement" inspirés de : https://stem.torproject.org/tutorials/to_russia_with_love.html"""


def init_tor():

    global tor_process

    if use_contry_code:
        tor_process = stem.process.launch_tor_with_config(
            config={
                'SocksPort': str(SOCKS_PORT),
                'ExitNodes': '{'+country_code+'}'
            }
        )
    else:
        tor_process = stem.process.launch_tor_with_config(
            config={
                'SocksPort': str(SOCKS_PORT)
            }
        )

    global use_tor
    use_tor = True


def kill_tor():

    tor_process.kill()


def get_html(url):
    """
    Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
    """

    output = io.BytesIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)

    if use_tor:
        query.setopt(pycurl.PROXY, 'localhost')
        query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
        query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)

    query.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0')
    query.setopt(pycurl.WRITEFUNCTION, output.write)

    try:
        query.perform()
        return output.getvalue()
    except pycurl.error as exc:
        return "Unable to reach %s (%s)" % (url, exc)


def new_identity():
    if use_tor:
        print(term.format("Nouvelle identite : "+get_ip()+"\n", term.Color.BLUE))
        kill_tor()
        init_tor()
    else:
        print(term.format("Lancement de Tor.\n", term.Attr.BOLD))
        init_tor()


def get_ip():

    soup = BeautifulSoup(get_html("http://whatismyipaddress.com/"), "html.parser")

    return soup.find(id="section_left").find_all('div')[1].a.string


if __name__ == "__main__":

    nums = set(souk_ma_crawler(1, 500))

    # for num in nums:
    # print(num)

    save_file(nums, "out2")

