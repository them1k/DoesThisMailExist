import argparse
import os
import sys
import random
import re
import time
import requests
import zipfile
import shutil
import dns.resolver
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from colorama import init, Fore, Style

# Colorcitos
init(autoreset=True)

ASCII_ART = f"""
{Fore.GREEN}
______                                         
|  _  \                                        
| | | |___   ___  ___                          
| | | / _ \ / _ \/ __|                         
| |/ / (_) |  __/\__ \                         
|___/ \___/ \___||___/                         
                                               
                                               
 _____ _     _       _____                _ _  
|_   _| |   (_)     |  ___|              (_) | 
  | | | |__  _ ___  | |__ _ __ ___   __ _ _| |         _       
  | | | '_ \| / __| |  __| '_ ` _ \ / _` | | |        |E]
{Fore.GREEN}  | | | | | | \__ \ | |__| | | | | | (_| | | |      {Fore.RED}.-|=====-.{Style.RESET_ALL}
{Fore.GREEN}  \_/ |_| |_|_|___/ \____/_| |_| |_|\__,_|_|_|      {Fore.RED}| | MAIL |{Style.RESET_ALL} 
                                                    {Fore.RED}|________|___{Style.RESET_ALL}
{Fore.GREEN}                                                         ||
 _____     _     _  ___                                  ||
|  ___|   (_)   | ||__ \                                 ||   www                %%%
| |____  ___ ___| |_  ) |                         vwv    ||   )_(,;;;,        ,;,\_/ www
|  __\ \/ / / __| __|/ /                          )_(    ||   \|/ \_/         )_(\|  (_)
| |___>  <| \__ \ |_|_|                           \|   \ || /\\\|/  |/         \| \|// | 
\____/_/\_\_|___/\__(_)  _________________________\|// \\\||//_\V/_\|//_______\\\|//V/\\\|/__{Style.RESET_ALL}\n{Fore.MAGENTA}\t\t\t\t\t\t\t\t\t\tby @themik{Style.RESET_ALL}
"""

ASCII_ART_G = f"""
{Fore.GREEN}
   _____                   _                       _  __ _           
  / ____|                 | |                     (_)/ _(_)          
 | |  __  ___   ___   __ _| | ___  __   _____ _ __ _| |_ _  ___ _ __ 
 | | |_ |/ _ \ / _ \ / _` | |/ _ \ \ \ / / _ \ '__| |  _| |/ _ \ '__|
 | |__| | (_) | (_) | (_| | |  __/  \ V /  __/ |  | | | | |  __/ |   
  \_____|\___/ \___/ \__, |_|\___|   \_/ \___|_|  |_|_| |_|\___|_|   
                      __/ |                                          
                     |___/                                           {Style.RESET_ALL}
"""

ASCII_ART_M = f"""
{Fore.GREEN}
  __  __ _                           __ _                    _  __ _           
 |  \/  (_)                         / _| |                  (_)/ _(_)          
 | \  / |_  ___ _ __ ___  ___  ___ | |_| |_  __   _____ _ __ _| |_ _  ___ _ __ 
 | |\/| | |/ __| '__/ _ \/ __|/ _ \|  _| __| \ \ / / _ \ '__| |  _| |/ _ \ '__|
 | |  | | | (__| | | (_) \__ \ (_) | | | |_   \ V /  __/ |  | | | | |  __/ |   
 |_|  |_|_|\___|_|  \___/|___/\___/|_|  \__|   \_/ \___|_|  |_|_| |_|\___|_|   
                                                                               
                                                                             {Style.RESET_ALL}
"""  

ascii_art_printed = {'1': False, '2': False}

def print_ascii_art(option):
    if not ascii_art_printed[option]:
        if option == '1':
            print(ASCII_ART_G)
        elif option == '2':
            print(ASCII_ART_M)
        ascii_art_printed[option] = True

def download_and_extract(url, extract_to):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    with zipfile.ZipFile(local_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(local_filename)

def setup_chrome_driver(force_update=False):
    driver_path = "./chrome-linux64/chromedriver"
    
    if force_update or not Path(driver_path).is_file():
        print("Downloading the latest Chromedriver...")
        url = "https://googlechromelabs.github.io/chrome-for-testing/#stable"
        response = requests.get(url)
        if response.status_code != 200:
            print("Error getting the Chrome download page.")
            sys.exit(1)

        soup = BeautifulSoup(response.content, 'html.parser')
        status_ok_section = soup.find('section', class_='status-ok', id='stable')

        if not status_ok_section:
            print("Error: The 'status-ok' section with ID 'stable' was not found.")
            sys.exit(1)

        version_element = status_ok_section.find('code')

        if not version_element:
            print("Error: The <code> element inside 'status-ok' was not found.")
            sys.exit(1)

        version = version_element.text.strip()
        chrome_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chrome-linux64.zip"
        driver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/linux64/chromedriver-linux64.zip"

        print("Descargando chrome-linux64...")
        download_and_extract(chrome_url, ".")

        print("Descargando chromedriver-linux64...")
        download_and_extract(driver_url, ".")

        os.makedirs("./chrome-linux64", exist_ok=True)
        os.rename("./chromedriver-linux64/chromedriver", "./chrome-linux64/chromedriver")
        os.chmod("./chrome-linux64/chromedriver", 0o755)
        shutil.rmtree("./chromedriver-linux64", ignore_errors=True)

    folder = './chrome-linux64'
    
    def apply_folder_rights(folder):
        os.chmod(folder, 0o755)
        
        for root, dirs, files in os.walk(folder):
            for d in dirs:
                dir_path = os.path.join(root, d)
                os.chmod(dir_path, 0o755)
            
            for f in files:
                file_path = os.path.join(root, f)
                os.chmod(file_path, 0o755)
    
    apply_folder_rights(folder)
    
    return driver_path

def read_emails(filename):
    with open(filename, 'r') as file:
        emails = [line.strip() for line in file.readlines()]
    return emails

def get_spf_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            for txt_record in rdata.strings:
                txt_record = txt_record.decode()
                if txt_record.startswith('v=spf1'):
                    return txt_record
    except Exception as e:
        print(f"{Fore.RED}\nError while checking SPF records for {domain}: {e}{Style.RESET_ALL}")
    return None
        
def get_mail_server(email):
    try:
        known_domains = {
            'gmail.com': 'google',
            'googlemail.com': 'google',
            'outlook.com': 'microsoft',
            'hotmail.com': 'microsoft',
            'live.com': 'microsoft'
        }
        
        domain = email.split('@')[1]
        if domain in known_domains:
            return known_domains[domain]

        spf_record = get_spf_record(domain)
        if spf_record:
            if 'include:_spf.google.com' in spf_record:
                return 'google'
            elif 'include:spf.protection.outlook.com' in spf_record:
                return 'microsoft'
            elif 'include:_spf.googlemail.com' in spf_record:
                return 'google'
            elif 'include:spf-a.google.com' in spf_record:
                return 'google'
            elif 'include:spf.messagingengine.com' in spf_record:
                return 'google'
            elif 'include:spf.mailgun.org' in spf_record:
                return 'google'
            elif 'include:23.103.224.0/19' in spf_record:
                return 'microsoft'
            elif 'include:206.191.224.0/19' in spf_record:
                return 'microsoft'
            elif 'include:40.103.0.0/16' in spf_record:
                return 'microsoft'
        return 'unknown'
    except Exception as e:
        print(f"{Fore.RED}\nError while checking SPF records for {email}: {e}{Style.RESET_ALL}")
        return 'unknown'

def check_google_account(driver, email, wait_times):
     
    try:
        print(f"{Fore.BLUE}Checking if the account \"{email}\" exists in Google...{Style.RESET_ALL}")

        driver.get("https://accounts.google.com/")
    
        email_elem = WebDriverWait(driver, wait_times['element_presence']).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=email]"))
        )
        email_elem.send_keys(email)
        email_elem.send_keys(Keys.RETURN)
    
        random_wait = random.uniform(wait_times['random_time_min'], wait_times['random_time_max'])
        time.sleep(random_wait)

        try:
            WebDriverWait(driver, wait_times['url_check']).until(
                lambda d: re.search(r"\/v\d+\/signin\/challenge\/pwd", d.current_url) or
                          re.search(r"\/signin\/challenge\/recaptcha", d.current_url)
            )
            result = True
        except TimeoutException:
            result = False
    
        if result:
            print(f"{Fore.GREEN}The account \"{email}\" exists.\n{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}The account \"{email}\" does not exist.\n{Style.RESET_ALL}")
    
    except (WebDriverException, Exception) as e:
        print(f"{Fore.RED}Lost connection to the browser or proxy. Error: {e}. Returning to the main menu.{Style.RESET_ALL}")
        driver.quit()  # Ensure the driver is closed
        return None  # Return None to indicate failure
    
    return result

def check_microsoft_account(driver, email, wait_times):
    
    try:
        print(f"Verifying if the account \"{email}\" exists in Microsoft Office 365...")

        try:
            driver.get("https://login.microsoftonline.com/")
        
            email_elem = WebDriverWait(driver, wait_times['element_presence']).until(
                EC.presence_of_element_located((By.ID, "i0116"))
            )
        
            email_elem.send_keys(email)
            email_elem.send_keys(Keys.RETURN)

            random_wait = random.uniform(wait_times['random_time_min'], wait_times['random_time_max'])
            time.sleep(random_wait)
        
            try:
                error_elem = WebDriverWait(driver, wait_times['url_check']).until(
                    EC.presence_of_element_located((By.ID, "usernameError"))
                )
                print(f"{Fore.RED}The account \"{email}\" does not exist in Microsoft Office 365.\n{Style.RESET_ALL}")
                return False
            except TimeoutException:
                pass

            try:
                current_url = driver.current_url
                if "oauth20_authorize.srf" in current_url:
                    print(f"{Fore.GREEN}The account \"{email}\" exists in Microsoft Office 365.\n{Style.RESET_ALL}")
                    return True
                else: 
                    WebDriverWait(driver, wait_times['element_presence']).until(
                        EC.presence_of_element_located((By.ID, "i0118"))
                    )
                    print(f"{Fore.GREEN}The account \"{email}\" exists in Microsoft Office 365 as ADFS or Federated account.\n{Style.RESET_ALL}")
                    return True
            except TimeoutException:
                print(f"{Fore.YELLOW}Unable to determine the account status for \"{email}\". Please check manually.\n{Style.RESET_ALL}")
                return False

        except TimeoutException:
            print(f"{Fore.RED}Timeout occurred while verifying the account \"{email}\".\n{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}\n[!] Error verifying account \"{email}\" in Microsoft Office 365.\n{Style.RESET_ALL}")
            print(str(e))
            return False
            
    except (WebDriverException, Exception) as e:
        print(f"{Fore.RED}Lost connection to the browser or proxy. Error: {e}. Returning to the main menu.{Style.RESET_ALL}")
        driver.quit()  # Ensure the driver is closed
        return None  # Return None to indicate failure
    
    return result        
def save_results(filename, results):
    with open(filename, 'w') as file:
        for email, exists in results.items():
            file.write(f"{email}: {exists}\n")

def update_application():
    repo_url = "https://github.com/them1k/DoesThisMailExist"
    branch = "main"
    local_dir = "./"
    
    print(f"{Fore.BLUE}\nUpdating the application from {repo_url} (branch: {branch})...{Style.RESET_ALL}")
    
    temp_dir = "./temp_repo"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    os.makedirs(temp_dir, exist_ok=True)
    
    zip_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
    download_and_extract(zip_url, temp_dir)

    extracted_folder = f"{temp_dir}/DoesThisMailExist-{branch}"
    
    for item in os.listdir(extracted_folder):
        s = os.path.join(extracted_folder, item)
        d = os.path.join(local_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    shutil.rmtree(temp_dir)
    
    print(f"{Fore.GREEN}\nApplication successfully updated!{Style.RESET_ALL}")

def get_proxy_list(url="https://www.free-proxy-list.net/"):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    proxy_list = []

    table = soup.find("table", class_="table table-striped table-bordered")
    if not table:
        print(f"{Fore.RED}\nError: La tabla de proxies no se encontró en la página.{Style.RESET_ALL}")
        return []

    rows = table.find("tbody").find_all("tr")
    if not rows:
        print(f"{Fore.RED}\nError: No se encontraron filas en la tabla de proxies.{Style.RESET_ALL}")
        return []

    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 7:
            ip = columns[0].text.strip()
            port = columns[1].text.strip()
            google = columns[5].text.strip()
            https = columns[6].text.strip()

            # Filtering only proxies with "yes" in "Google" and "HTTPS"
            if google.lower() == 'yes' and https.lower() == 'yes':
                proxy = f"http://{ip}:{port}"
                proxy_list.append(proxy)

    return proxy_list

def is_proxy_accessible(proxy):
    try:
        response = requests.get('http://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=5)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass
    return False

def auto_verify():
    default_email_list_path = "emails.txt"
    
    email_list_path = input(f"\nEnter the path to read the email list file {Fore.GREEN}[{default_email_list_path}]{Style.RESET_ALL}: ").strip()
    if not email_list_path:
        email_list_path = default_email_list_path
    elif not os.path.isfile(email_list_path):
        print(f"{Fore.RED}\nError: The file {email_list_path} does not exist.{Style.RESET_ALL}")
    
    if not os.path.isfile(email_list_path):
        print(f"{Fore.RED}\nError: The file {email_list_path} does not exist.{Style.RESET_ALL}")
        return

    with open(email_list_path, 'r') as file:
        emails = [line.strip() for line in file.readlines()]

    if not emails:
        print(f"{Fore.RED}Error: The email list is empty.{Style.RESET_ALL}")
        return

    first_email = emails[0]
    server = get_mail_server(first_email)

    if server == 'google':
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.GREEN}\nThe email server is Google. Proceeding with Google account verification.{Style.RESET_ALL}\n {ASCII_ART_G}")
        verify_accounts('1')
    elif server == 'microsoft':
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.GREEN}\nThe email server is Microsoft. Proceeding with Microsoft account verification.{Style.RESET_ALL}\n {ASCII_ART_M}")
        verify_accounts('2')
    else:
        print(f"{Fore.RED}\nUnable to determine the email server for {first_email}. Please check manually.{Style.RESET_ALL}")


def get_curl_proxy_list():
    url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&anonymity=Anonymous,Transparent&timeout=700"
    response = requests.get(url)
    
    if response.status_code == 200:
        proxies = response.text.splitlines()
        return [f"http://{proxy}" for proxy in proxies if proxy]
    else:
        print(f"Error fetching proxies from Proxyscape: {response.status_code}")
        return []

def verify_accounts(option):
    default_email_list_path = "emails.txt"
    default_output_path = "output.txt"
    default_use_proxy = "no"
    
    # Define the base wait times
    base_wait_times = {
        'element_presence': 5,
        'url_check': 3,
        'random_time_min': 0.5,
        'random_time_max': 2 
    }
    
    # Increase wait times if using a free proxy
    proxy_wait_times = {
        'element_presence': base_wait_times['element_presence'] + 4,
        'url_check': base_wait_times['url_check'] + 4,
        'random_time_min': base_wait_times['random_time_min'] + 2,
        'random_time_max': base_wait_times['random_time_max'] + 2
    }
    
    platform = 'google' if option == '1' else 'microsoft'

    while True:
        list_path = input(f"\nEnter the path to read the email list file {Fore.GREEN}[{default_email_list_path}]{Style.RESET_ALL}: ").strip()
        if not list_path:
            list_path = default_email_list_path
        elif not os.path.isfile(list_path):
            print(f"Error: The file {list_path} does not exist.")
            continue

        output_path = input(f"\nEnter the path to save the results file {Fore.GREEN}[{default_output_path}]{Style.RESET_ALL}: ").strip()
        if not output_path:
            output_path = default_output_path

        use_proxy = input(f"\nDo you want to use a proxy? (yes/no) {Fore.GREEN}[{default_use_proxy}]{Style.RESET_ALL}: ").strip().lower()
        if not use_proxy:
            use_proxy = default_use_proxy

        proxy = None
        if use_proxy == 'yes':
            use_free_proxy = input(f"\nDo you want to use a free proxy list? (yes/no) {Fore.GREEN}[no]{Style.RESET_ALL}: ").strip().lower()

            if use_free_proxy == 'yes':
                print(f"\n{Fore.YELLOW}[!] DISCLAIMER [!]\nBy using a free proxy, we have to increment timings and cannot guarantee the privacy and reliability of the results.{Style.RESET_ALL}")
                proxy_source = input(f"\n[1] Free Proxy List \n[2] Proxyscape\n\nChoose your proxy source {Fore.GREEN}[1]{Style.RESET_ALL}: ").strip()
                if not proxy_source:
                    proxy_source = '1'

                if proxy_source == '1':
                    proxies = get_proxy_list()  # Free-Proxy-List
                elif proxy_source == '2':
                    proxies = get_curl_proxy_list()  # Proxyscape
                else:
                    print(f"{Fore.RED}\nInvalid option. Returning to the main menu.{Style.RESET_ALL}")
                    return

                if not proxies:
                    print(f"{Fore.RED}\nFailed to retrieve proxies. Returning to the main menu.{Style.RESET_ALL}")
                    return

                for proxy in proxies:
                    print(f"\nTesting proxy: {proxy}")

                    if not is_proxy_accessible(proxy):
                        print(f"{Fore.RED}\nThe proxy \"{proxy}\" is not accessible. Skipping...{Style.RESET_ALL}")
                        continue

                    print("\nConfiguring Chromedriver with proxy...")
                    driver_path = setup_chrome_driver()

                    options = webdriver.ChromeOptions()
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                    options.add_argument('--ignore-certificate-errors')
                    options.add_argument('--ignore-ssl-errors')
                    options.add_argument('--allow-insecure-localhost') 
                    options.add_argument(f'--proxy-server={proxy}')

                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=options)

                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                        'source': '''
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined
                            })
                        '''
                    })

                    emails = read_emails(list_path)
                    results = {}

                    # Use the increased wait times
                    wait_times = proxy_wait_times

                    if platform == 'google':
                        for email in emails:
                            exists = check_google_account(driver, email, wait_times)
                            results[email] = exists
                    elif platform == 'microsoft':
                        for email in emails:
                            exists = check_microsoft_account(driver, email, wait_times)
                            results[email] = exists

                    driver.quit()

                    save_results(output_path, results)
                    print(f"\n\n{Fore.GREEN}[*] Scan Completed with proxy {proxy}!\n[*] Results saved in {output_path}{Style.RESET_ALL}")
                    break

            else:
                proxy = input("\nEnter your proxy (format: http://user:pass@proxyserver:port or http://proxyserver:port or proxyserver:port): ").strip()

                if not is_proxy_accessible(proxy):
                    print(f"{Fore.RED}\nThe proxy \"{proxy}\" is not accessible. Please choose another option.{Style.RESET_ALL}")
                    continue

                print("\nConfiguring Chromedriver with proxy...")
                driver_path = setup_chrome_driver()

                options = webdriver.ChromeOptions()
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--allow-insecure-localhost') 
                options.add_argument(f'--proxy-server={proxy}')

                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=options)

                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    '''
                })

                emails = read_emails(list_path)
                results = {}

                # Use the base wait times
                wait_times = base_wait_times

                if platform == 'google':
                    for email in emails:
                        exists = check_google_account(driver, email, wait_times)
                        results[email] = exists
                elif platform == 'microsoft':
                    for email in emails:
                        exists = check_microsoft_account(driver, email, wait_times)
                        results[email] = exists

                driver.quit()

                save_results(output_path, results)
                print(f"\n{Fore.GREEN}[*] Scan Completed!\n[*] Results saved in {output_path}{Style.RESET_ALL}")

            break

        else:
            print("\nConfiguring Chromedriver without proxy...")
            driver_path = setup_chrome_driver()

            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--allow-insecure-localhost') 

            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)

            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            emails = read_emails(list_path)
            results = {}

            # Use the base wait times
            wait_times = base_wait_times

            if platform == 'google':
                for email in emails:
                    exists = check_google_account(driver, email, wait_times)
                    results[email] = exists
            elif platform == 'microsoft':
                for email in emails:
                    exists = check_microsoft_account(driver, email, wait_times)
                    results[email] = exists

            driver.quit()

            save_results(output_path, results)
            print(f"{Fore.GREEN}[*] Scan Completed!\n[*] Results saved in {output_path}{Style.RESET_ALL}")

        break


def main_menu():
    ascii_art_printed = {'1': False, '2': False}
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(ASCII_ART)
        print(f"{Fore.BLUE}\nWelcome to the Email Verifier Framework! Choose your option:\n")
        print(f"{Fore.YELLOW}[1] Verify Google accounts")
        print(f"{Fore.YELLOW}[2] Verify Microsoft accounts")
        print(f"{Fore.YELLOW}[3] I don't know the server, Do it for me!")
        print(f"{Fore.YELLOW}[4] Update Chromedriver")
        print(f"{Fore.YELLOW}[5] Update app")
        print(f"{Fore.YELLOW}[6] Exit\n")

        try:
            opcion = input("Select an option (1-6): ").strip()

            if opcion == '1':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_ascii_art(opcion)
                verify_accounts(opcion)
            elif opcion == '2':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_ascii_art(opcion)
                verify_accounts(opcion)
            elif opcion == '3':
                auto_verify()
            elif opcion == '4':
                setup_chrome_driver(force_update=True)
            elif opcion == '5':
                update_application()
            elif opcion == '6':
                print(f"{Fore.BLUE}\n[!]Exiting... (and installing spyware){Style.RESET_ALL}")
                time.sleep(1.5)
                print(f"{Fore.GREEN}[!] Object wit PID = 1 - Modified!{Style.RESET_ALL}\nNowhere to hide! ;) \n\n{Fore.RED}Bye!{Style.RESET_ALL}")
                time.sleep(1)
                sys.exit(0)
            else:
                print("\n{Fore.RED}Invalid option. Please select a number between 1 and 7.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}\nPress Enter to return to the menu...{Style.RESET_ALL}")
        
        except KeyboardInterrupt:
            print("\nInterrupted. Returning to the main menu...")
            continue  # Return to the main menu

if __name__ == "__main__":
    main_menu()

