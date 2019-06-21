import requests
import random
import config


class TicketRob:
    """Get the ticket at the high season from website"""

    def __init__(self):
        # Keep the cookie
        self.session = requests.Session()
        # Fake as an web browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/65.0.3325.181 Safari/537.36'
        })
        # Set all urls to login
        self.index_url = 'https://kyfw.12306.cn/otn/login/init'
        self.captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image'
        self.login_url = 'https://kyfw.12306.cn/passport/web/login'
        self.check_captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        self.uamtk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        self.auth_url = 'https://kyfw.12306.cn/otn/uamauthclient'

        # Data for authorization image
        self.point = {
            '1': '35,43',
            '2': '108,43',
            '3': '185,43',
            '4': '254,43',
            '5': '34,117',
            '6': '108,117',
            '7': '180,117',
            '8': '258,117',
        }

    def get_point(self, image_num):
        """
        Join image points
        :param image_num: image title '1,2'
        :return: the joined points of image '35,43,108,43'
        """

        image_num = image_num.split(',')
        temp = []

        for item in image_num:  # ['1','2']
            temp.append(self.point[item])

        return ','.join(temp)

    def log_in(self, username, password):
        """Login check process"""

        data = {
            'username': username,
            'password': password,
            'appid': 'otn'
        }

        # 1. Keep the cookie for login
        self.session.get(self.index_url)
        # 2. Get the authorization image
        self.get_captcha()
        # 3. Check the response of authorization image
        res = self.check_captcha()
        if res:
            response = self.session.post(self.login_url, data=data)
            if response.json()['result_code'] == 0:
                # 4. Get the response token for username and password
                tk = self.get_token()
                # 5. Check the authorization based on token
                auth_res = self.get_auth(tk)
                if auth_res:
                    return True
        print("Authorization failed. Please refer to the above reason.")
        return False

    def get_captcha(self):
        """Get the authorization image"""

        data = {
            'login_site': 'E',
            'module': 'login',
            'rand': 'sjrand',
            str(random.random()): ''
        }

        response = self.session.get(self.captcha_url, params=data)
        with open('./images/captcha.jpg', 'wb') as f:
            f.write(response.content)

    def check_captcha(self):
        """Check the authorization image"""

        data = {
            'answer': self.get_point(input('Please input the correct image number>>>:')),
            'login_site': 'E',
            'rand': 'sjrand'
        }

        # Check if image authorization pass
        response = self.session.post(self.check_captcha_url, data=data)
        if response.json()['result_code'] == '4':
            return True
        else:
            print("Wrong Authorization image! Please retry.")
            return False

    def get_token(self):
        """Get the authorization token"""

        uamtk_data = {
            'appid': 'otn'
        }

        response = self.session.post(self.uamtk_url, data=uamtk_data)
        return response.json()['newapptk']

    def get_auth(self, tk):
        """Get the authorization based on the token"""

        auth_data = {
            'tk': tk
        }

        response = self.session.post(self.auth_url, data=auth_data)
        if response.json()['result_code'] == 0:
            return True
        else:
            print("Wrong username or password! Please retry.")
            return False


if __name__ == '__main__':
    ticket = TicketRob()
    print(ticket.log_in(config.username, config.password))
