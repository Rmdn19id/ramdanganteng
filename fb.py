# Mr.Rm19

import mechanize
import requests
import bs4
import logging
import argparse
import sys

print "\033[92m 91m TOOLS BY Mr.Rm19"
print "\033[92m 92m Ramdan19id@gmail.com "
print " root@data"
reload(sys)
sys.setdefaultencoding('utf8')

class create:
    def __init__(self):
        logging.basicConfig(
            level={
                True: logging.DEBUG,
                False: logging.INFO
            }[arg.level],
            format='\r%(levelname)s:%(name)s: %(message)s'
        )
        self.create_total = 0
        self.blacklist_email = ['@datasoma', '@geroev', '@cliptik', '@khtyler']
        self.temp_email_url = 'https://temp-mail.org/en/'

        self.__main__()

    def _browser_options(self):
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.set_handle_equiv(True)
        br.set_handle_referer(True)
        br.set_handle_redirect(True)
        br.set_handle_refresh(
            mechanize._http.HTTPRefreshProcessor(),
            max_time = 5
        )
        br.addheaders = [('User-agent', "Mozilla/5.0 (Linux; Android 5.0; ASUS_T00G Build/LRX21V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36")]

        return br

    # info account
    def _get_info_account(self):
        logging.info('looking for account information')
        res = requests.get('https://randomuser.me/api').json()

        pwd = res['results'][0]['login']['password']
        return {
            'username':  res['results'][0]['login']['username'],
            'password':  pwd + '0000' if len(pwd) < 6 else pwd,
            'firstname': res['results'][0]['name']['first'],
            'lastname':  res['results'][0]['name']['last'],
            'gender':    '1' if res['results'][0]['gender'] == 'female' else '2',
            'date':      res['results'][0]['dob']['date'].split('T')[0].split('-')
        }

    # facebook
    def _create_account_facebook(self, email):
        data = self._get_info_account()

        self._password = data['password']
        logging.info('name: %s', data['firstname'] + ' ' + data['lastname'])
        logging.info('create a facebook account')
        self.br.open('https://mbasic.facebook.com/reg/?cid=102&refid=8')

        self.br.select_form(nr=0)
        self.br.form['firstname'] = data['firstname'] + ' ' + data['lastname']
        try:
            self.br.form['reg_email__'] = email
        except mechanize._form_controls.ControlNotFoundError as ex:
            logging.warning(str(ex))
            return False

        self.br.form['sex'] = [data['gender']]
        self.br.form['birthday_day'] = [data['date'][2][1:] if data['date'][2][0] == '0' else data['date'][2]]
        self.br.form['birthday_month'] = [data['date'][1][1:] if data['date'][1][0] == '0' else data['date'][1]]
        self.br.form['birthday_year'] = [data['date'][0]]
        self.br.form['reg_passwd__'] = data['password']
        self.br.submit()

        for i in range(3):
            self.br.select_form(nr=0)
            self.br.submit()

        return True

    def _check_email_fb(self, email):
        r = requests.post('https://mbasic.facebook.com/login/identify/?ctx=recover',
                data={ 'email': email }
            )

        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        if soup.title.text != 'Temukan Akun Anda':
            logging.error('registered email!')
            return False

        return True

    def _confirmation_code(self, url):
        logging.info('confirm account')
        ask = raw_input(' KETIK : RAMDANGANTENG $root@data ')
        self.br.open(url)

        if ask:
            self.br.select_form(nr=0)
            self.br.form['phone-name'] = ask
            self.br.submit()
            logging.info('new telephone number added !')
        else:
            logging.warning('skipped !')

        return True

    # mail
    def _open_temp_mail(self):
        return self.br.open(self.temp_email_url).read()

    def _find_email(self, text):
        soup = bs4.BeautifulSoup(
            text,
            'html.parser'
        )
        return soup.find(class_='mail opentip').attrs['value']

    def _read_message(self, text):
        soup = bs4.BeautifulSoup(
            text,
            'html.parser'
        )
        view = soup.find('tbody').find('td')

        if view:
            url_message = view.a['href']
            logging.info('read email from %s', view.a.text)
            r2 = self.br.open(url_message).read()

            mess = bs4.BeautifulSoup(r2, 'html.parser')
            subject_ = mess.find(class_='pm-subject')
            message_ = mess.find(class_='pm-text')

            logging.info('your code: %s', subject_.text.split()[0])

            if self._confirmation_code(message_.a['href']):
                return True

    def _save_to_file(self, email, password):
        with open('akun.txt', 'a') as f:
            f.write('%s|%s\n' % (email, password))

    def __main__(self):
        while True:
            self.br = self._browser_options()
            logging.info('searching new emails')

            email_found, check, max_ = False, True, 0
            while True:
                res_em = self._open_temp_mail()
                self._mail = self._find_email(res_em)

                if '@' + self._mail.split('@')[1].split('.')[0] in self.blacklist_email:
                    logging.error('blacklist email: %s', self._mail)
                    break

                if not email_found:
                    logging.info('obtained email: %s', self._mail)
                    if self._check_email_fb(self._mail):
                        if self._create_account_facebook(self._mail):
                            logging.info('waiting for incoming email')
                            email_found = True
                
                if max_ == 10:
                    logging.error('no response !')
                    break
                    
                if check and email_found:
                    if self._read_message(res_em):
                        self.create_total += 1
                        logging.info('account created:\n\t   email: %s\n\t   password: %s', self._mail, self._password)
                        self._save_to_file(self._mail, self._password)
                        check = False
                    max_ += 1
                    
                else:
                    break

            if self.create_total == arg.count:
                logging.info('finished\n')
                break

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument( '-c', metavar='<COUNT>', type=int, dest='count',
        help='number of accounts you want to make')
    parse.add_argument('--debug', action='store_true', dest='level',
        help='set logging level to debug')
    arg = parse.parse_args()

    if arg.count:
        try:
            print ('') # new line
            create()
        except KeyboardInterrupt:
            logging.error('user interrupt..\n')
        except Exception as exc:
            logging.critical(str(exc) + '\n')
    else:
        parse.print_help()