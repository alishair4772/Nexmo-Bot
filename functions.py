import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import names
import random_address
from selenium.webdriver.support.ui import Select
import random
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from imap_tools import MailBox
from imap_tools import AND
from bs4 import BeautifulSoup
import logging
import sys
from twocaptcha import TwoCaptcha
from anticaptchaofficial.recaptchav2proxyless import *
from datetime import datetime
import zipfile

class NexmoBot():

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)01d %(levelname)s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            console_handler
        ]
    )

    def useragent_rotate(self):
        with open("userAgents.txt", "r") as f:
            lines = f.readlines()
            return random.choice(lines)

    def proxy_rotate():
        with open("proxies.txt", "r") as f:
            lines = f.readlines()
            line = random.choice(lines)
            splitedLine = line.split(':')
            output = {
                'address': splitedLine[0],
                'port': splitedLine[1],
                'user': splitedLine[2],
                'pass': splitedLine[3].replace('\n', '')
            }
            return output

    proxy = proxy_rotate()
    PROXY_HOST = proxy['address']
    PROXY_PORT = proxy['port']
    PROXY_USER = proxy['user']
    PROXY_PASS = proxy['pass']

    def manifest_json(self):
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        return manifest_json

    def background_js(self, PROXY_HOST=PROXY_HOST, PROXY_PORT=PROXY_PORT, PROXY_USER=PROXY_USER, PROXY_PASS=PROXY_PASS):
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                  },
                  bypassList: ["localhost"]
                }
              };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
        return background_js


    def get_chromedriver(self, use_proxy, user_agent, headless):

        chrome_options = Options()

        if use_proxy:
            pluginfile = 'proxy_auth_plugin.zip'

            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", self.manifest_json())
                zp.writestr("background.js", self.background_js())
            chrome_options.add_extension(pluginfile)
        if user_agent:
            chrome_options.add_argument('--user-agent=%s' % self.useragent_rotate())
        if headless:
            chrome_options.add_argument('---headless')

        driver = webdriver.Chrome(options=chrome_options)

        return driver



    def launchChrome(self,use_proxy,user_agent,headless):
        print(f"{datetime.now()} : LAUNCHING CHROME")
        self.driver = self.get_chromedriver(use_proxy=use_proxy, user_agent=user_agent, headless=headless)
        self.driver.maximize_window()

    def proxy_rotate(self):
        with open("proxies.txt", "r") as f:
            lines = f.readlines()
            return str(random.choice(lines))

    # def launchChrome(self,proxy,extension):
    #     logging.info("LAUNCHING CHROME")
    #     self.options = Options()
    #     if proxy:
    #         self.options.add_argument(f'--proxy-server={self.proxy_rotate()}')
    #     if extension:
    #         self.options.add_extension('./plugin.zip')
    #
    #
    #     self.driver = webdriver.Chrome(options=self.options)
    #     self.driver.maximize_window()
    def getUrl(self,url):
        logging.info(f"GETTING URL: {url}")
        self.driver.get(url)

    def getEmail(self,EmailFile):
        txt = open(EmailFile)
        lines = txt.readlines()
        userPassList = []
        for i in lines:
            stripedLine = i.strip()
            splitLine = stripedLine.split('|')
            userPassList.append((splitLine[0],splitLine[1]))
        return userPassList

    def getVerificationUrl(self,email,password):

        logging.info("GETTING VERIFICATION EMAIL")
        with MailBox('outlook.office365.com').login(email, password, 'INBOX') as mailbox:
            for msg in mailbox.fetch(AND(subject="Vonage APIs - Verify your email address")):
                body = msg.html
                soup = BeautifulSoup(body, 'lxml')
                url = soup.find('a',class_='reset-password-btn')
                urlList = url.get_attribute_list('href')
                return urlList[0]
    def formData(self,email,password,zipCode,city):

        first_name = names.get_first_name()
        last_name = names.get_first_name()
        addressDict = random_address.real_random_address()
        address = addressDict['address1']
        state = addressDict['state']

        output = {'firstName': first_name, 'lastName': last_name, 'email': email,'password':password, 'address': address, 'city': city,
                  'state': state, 'zipCode': zipCode}

        return output
    def signUpNexmo(self,email,password,firstName,lastName,url):
        self.getUrl(url)
        firstName_ = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//input[@placeholder="First name"]')))
        firstName_.send_keys(firstName)
        lastName_ = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//input[@placeholder="Last name"]')))
        lastName_.send_keys(lastName)
        email_ = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//input[@placeholder="Email"]')))
        email_.send_keys(email)
        password_ = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//input[@id="password"]')))
        password_.send_keys(password)
        createAccountButton = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@id="submitButton"]')))
        self.driver.execute_script("arguments[0].click();", createAccountButton)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(),'You')]")))
            return True
        except:
            return False
    def checkEmailSent(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(),'You')]")))
            return True
        except:
            return False
    def getSMSverification(self,url):
        self.getUrl(url)
        WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//input')))
        email_ = self.driver.find_element(By.XPATH,'(//input)[1]')

    def requestNumber(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'x-api-key': 'live_yyG35GmvN0qQDSqkHuYqYA1BGo0KUh4mz8wMt8pCpVKA'}
        body = {
            'serviceId' : 161
        }
        endpoint = f"https://www.smsredux.com/api/v2/temporary"

        response = requests.post(endpoint, headers=headers,data=body)
        jsonResponse = response.json()
        number = jsonResponse['data']['number']
        temporaryNumberId = jsonResponse['data']['temporaryNumberId']
        output = {
        'number': number,
        'temporaryNumberId': temporaryNumberId
        }
        return output
    def retrieveSMS(self,APIKEY,temporaryNumberid):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'x-api-key': APIKEY}
        parameter = {
            'temporaryNumberId': temporaryNumberid
        }
        endpoint = f"https://www.smsredux.com/api/v2/temporary/{parameter['temporaryNumberId']}"

        req = requests.get(params=parameter,url=endpoint,headers=headers)
        jsonRespone = req.json()
        code = jsonRespone['data']['sms']['code']
        return code
    def verifyPhone(self,url,phoneNumber,APIKEY,temporaryNumberID,twoCaptchaApi):
        self.getUrl(url)
        dropDown = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//span[@id="countryDropdownTest"]')))
        self.driver.execute_script("arguments[0].click();", dropDown)
        time.sleep(0.5)
        unitedStates=  self.driver.find_element(By.XPATH,"//span[@title='United States']")
        self.driver.execute_script("arguments[0].click();", unitedStates)
        phoneNumber_ = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//input[@placeholder="Phone number"]')))
        phoneNumber_.send_keys(phoneNumber)
        twoFa = self.driver.find_element(By.XPATH,'//span[@class="Vlt-checkbox__icon"]')
        self.driver.execute_script("arguments[0].click();", twoFa)
        sendCode = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button')))
        self.driver.execute_script("arguments[0].click();", sendCode)
        # webdriver.support.wait.WebDriverWait(self.driver, 120).until(
        #     lambda x: x.find_element_by_css_selector('.antigate_solver.solved'))

        try:
            self.anti_captcha()
        except:
            pass
        time.sleep(20)
        logging.info("RETRIEVING SMS")
        code = self.retrieveSMS(APIKEY=APIKEY, temporaryNumberid=temporaryNumberID)
        enterCode= WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//input[@id="codeTest"]')))
        enterCode.send_keys(code)
        submit = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button')))
        self.driver.execute_script("arguments[0].click();", submit)
    def getCardNumbers(self,VCCFile):
        txt = open(VCCFile)
        lines = txt.readlines()
        VCCList = []
        for i in lines:
            stripedLine = i.strip()
            splitLine = stripedLine.split(':')
            expiryMonth = splitLine[1][:2]
            expiryYear = splitLine[1][2:]
            VCCList.append((splitLine[0], expiryMonth,expiryYear,splitLine[2]))
        return VCCList
    def postLogin(self):
        try:
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//button[@value="no"]')))
            no = self.driver.find_element(By.XPATH,'//button[@value="no"]')
            self.driver.execute_script("arguments[0].click();", no)
        except:
            pass

        sel = Select(self.driver.find_element(By.ID,'userJob'))
        sel.select_by_value("5")
        time.sleep(2)
        selectProduct=  self.driver.find_element(By.XPATH,'//div[@data-test-id="product-card"]')
        self.driver.execute_script("arguments[0].click();", selectProduct)
        upgrade = WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,'//span[@id="upgradeBadgeTest"]')))
        self.driver.execute_script("arguments[0].click();", upgrade)


    def Upgrade(self,creditCard,expiryMonth,expiryYear,cvv,address1,city,postalCode,email,firstName,lastName,phone,password):
        paypal = WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,'//li[@id="paymentOptionPAYPAL"]')))
        time.sleep(30)
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH,'//iframe[@name="braintree-hosted-field-number"]'))
        creditCard_ = WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,'//input[@id="credit-card-number"]')))
        logging.info("ADDING CARD")
        creditCard_.send_keys(creditCard)

        self.driver.switch_to.default_content()
        time.sleep(5)
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH,'//iframe[@name="braintree-hosted-field-expirationDate"]'))

        expirationDate = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="expiration"]')))
        expirationDate.send_keys(expiryMonth)
        expirationDate.send_keys(expiryYear)

        self.driver.switch_to.default_content()
        time.sleep(5)

        self.driver.switch_to.frame(self.driver.find_element(By.XPATH,'//iframe[@name="braintree-hosted-field-cvv"]'))

        cvv_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="cvv"]')))
        cvv_.send_keys(cvv)
        self.driver.switch_to.default_content()

        address1_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-textfield[@label="Address line 1"]')))
        address1_.send_keys(address1)

        city_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-textfield[@label="City"]')))
        city_.send_keys(city)

        postalCode_ = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-textfield[@id="billing-postal-code"]')))
        postalCode_.send_keys(postalCode)

        nextButton = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@label="Next"]')))
        self.driver.execute_script("arguments[0].click();", nextButton)
        time.sleep(2)
        checkbox = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//span[@class='Vlt-radio__icon']")))
        self.driver.execute_script("arguments[0].click();", checkbox)
        confirmAddress = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@label="Confirm address"]')))
        self.driver.execute_script("arguments[0].click();", confirmAddress)

        agreed = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-checkbox[@id="agreed"]')))
        self.driver.execute_script("arguments[0].click();", agreed)
        upgrade = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@label="Upgrade"]')))
        self.driver.execute_script("arguments[0].click();", upgrade)

        addfunds = WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@label="Add funds"]')))
        self.driver.execute_script("arguments[0].click();", addfunds)

        WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,'//h3[@id="paymentStatusTest"]')))
        logging.info("SUCCESS")
    def BuyNumber(self):
        buynumber = WebDriverWait(self.driver,40).until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'Buy Numbers')]")))
        self.driver.execute_script("arguments[0].click();", buynumber)
        searchButton = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//vwc-button[@id="searchButtonTest"]')))
        self.driver.execute_script("arguments[0].click();", searchButton)
        buy = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//vwc-button[@label="Buy"]')))
        self.driver.execute_script("arguments[0].click();", buy)
        confirmBuy = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'//button[@id="confirmBuyBtnTest"]')))
        self.driver.execute_script("arguments[0].click();", confirmBuy)
        WebDriverWait(self.driver,30).until(EC.invisibility_of_element_located((By.XPATH,'//button[@id="confirmBuyBtnTest"]')))
        time.sleep(10)
    def UpgradePaypal(self,creditCard,expiryMonth,expiryYear,cvv,address1,city,postalCode,email,firstName,lastName,phone,password,state,paypalState):
        paypal = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//li[@id="paymentOptionPAYPAL"]')))
        self.driver.execute_script("arguments[0].click();", paypal)

        logging.info("ADDING PAYPAL")

        address1_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-textfield[@label="Address line 1"]')))
        address1_.send_keys(address1)

        city_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-textfield[@label="City"]')))
        city_.send_keys(city)

        postalCode_ = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-textfield[@id="billing-postal-code"]')))
        postalCode_.send_keys(postalCode)

        state_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'(//input[@class="vivid-input-internal"])[5]')))
        state_.send_keys(state)

        nextButton = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@label="Next"]')))
        self.driver.execute_script("arguments[0].click();", nextButton)
        time.sleep(2)
        checkbox = WebDriverWait(self.driver,20).until(EC.element_to_be_clickable((By.XPATH,"//span[@class='Vlt-radio__icon']")))
        self.driver.execute_script("arguments[0].click();", checkbox)
        confirmAddress = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@label="Confirm address"]')))
        self.driver.execute_script("arguments[0].click();", confirmAddress)

        agreed = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-checkbox[@id="agreed"]')))
        self.driver.execute_script("arguments[0].click();", agreed)
        upgrade = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//vwc-button[@label="Upgrade"]')))
        self.driver.execute_script("arguments[0].click();", upgrade)

        enterEmail = WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="email"]')))
        enterEmail.send_keys(email)
        next = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//button[@id="btnNext"]')))
        self.driver.execute_script("arguments[0].click();", next)
        cardNumber = WebDriverWait(self.driver,60).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="cardNumber"]')))
        time.sleep(1)
        cardNumber.send_keys(creditCard)
        time.sleep(1)
        WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="cardExpiry"]')))
        expiry = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="cardExpiry"]')))
        expiry.click()
        time.sleep(3)
        expiry.send_keys(expiryMonth)
        time.sleep(1)
        expiry.send_keys(expiryYear)
        cvvInput = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="cardCvv"]')))
        cvvInput.send_keys(cvv)
        time.sleep(1)
        firstName_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="firstName"]')))
        firstName_.send_keys(firstName)
        lastName_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="lastName"]')))
        lastName_.send_keys(lastName)
        address_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="billingLine1"]')))
        address_.send_keys(address1)
        time.sleep(1)
        cityPaypal = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="billingCity"]')))
        cityPaypal.send_keys(city)
        time.sleep(1)
        sel = Select(self.driver.find_element(By.XPATH,'//select[@id="billingState"]'))
        sel.select_by_value(paypalState)
        time.sleep(1)
        zipcode = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="billingPostalCode"]')))
        zipcode.send_keys(postalCode)
        phone_ = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="phone"]')))
        phone_.send_keys(phone)
        password1 = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//input[@id="password"]')))
        password1.send_keys(password)
        pay = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Pay in USD')]")))
        self.driver.execute_script("arguments[0].click();", pay)
        time.sleep(30)
    def quitBrowser(self):
        logging.info("QUITTING BROWSER")
        self.driver.quit()
    def saveTxt(self,APIKEY,SECRETKEY,TOLLNUMBER,MOBILENUMBER):
        with open('accounts.txt', 'a') as file:
            file.write(f"={APIKEY}:{SECRETKEY}:{TOLLNUMBER}:{MOBILENUMBER} \n")


    def anti_captcha(self):

        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key("b0bfb7ea4afa36d960715a15ad7b8910")
        solver.set_website_url(self.driver.current_url)
        solver.set_website_key("6LfoMC0UAAAAADuyf9jhTXIkgt9Ln3pTrOJlzZ0z")

        g_response = solver.solve_and_return_solution()
        if g_response != 0:
            logging.info("g-response: " + g_response)

        else:
            logging.info("task finished with error " + solver.error_code)


        self.driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="";')
        time.sleep(0.5)
        self.driver.execute_script("""
          document.getElementById("g-recaptcha-response").innerHTML = arguments[0]
        """, g_response)
        time.sleep(2)
        text = self.driver.find_element(By.XPATH,'//textarea[@id="g-recaptcha-response"]')
        text.submit()

    def getAPISecretKeys(self):
        apiSettings = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'API Settings')]")))
        self.driver.execute_script("arguments[0].click();", apiSettings)

        api_key = WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,'//div[@class="api-key Vlt-form__group"]')))
        value = api_key.get_attribute('value')

        secretKey = WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,'//div[@class="api-secret"]/div/div[@class="Vlt-input"]')))
        key = secretKey.get_attribute('value')

        output = {
            'APIKEY' : value.replace("=",''),
            'secretKey': key
        }
        return output
    def getTollNumber(self):
        yourNumber = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,'(//a[@href="/your-numbers"])[1]')))
        self.driver.execute_script("arguments[0].click();", yourNumber)
        finalList = []

        mobileNumber = WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH,'(//span[@class="flex-col"])[1]'))).text
        splitedNumber = mobileNumber.split(" ")
        finalList.append(splitedNumber[1].replace("\nUnited",''))
        try:
            tollNumber = WebDriverWait(self.driver,20).until(EC.presence_of_element_located((By.XPATH,'(//span[@class="flex-col"])[2]'))).text
            splitedtoll = tollNumber.split(" ")
            finalList.append(splitedtoll[1].replace("\nUnited",''))
        except:
            finalList.append("NONE")

        output = {
            'mobileNumber': finalList[0],
            'tollNumber': finalList[1]
        }
        return output
