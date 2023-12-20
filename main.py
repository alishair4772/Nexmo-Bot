import time
from functions import NexmoBot

APIKEY = "live_yyG35GmvN0qQDSqkHuYqYA1BGo0KUh4mz8wMt8pCpVKA"
billingZip = 29451
VCCFile = "VCC.txt"
state = "CA"
paypalState = "CA"
EmailsFile = "emails.txt"
city = "Isle of palms"
twoCaptchaAPI = "5a57742b5a84d7e5a6860c701c4419a4"
bot = NexmoBot()
for card,email in zip(bot.getCardNumbers(VCCFile=VCCFile),bot.getEmail(EmailFile=EmailsFile)):
    userData = bot.formData(email=email[0],password=email[1],zipCode=billingZip,city=city)
    bot.launchChrome(use_proxy=True,user_agent=False,headless=False)
    if bot.signUpNexmo(url="https://dashboard.nexmo.com/sign-up",email=userData['email'],password=userData['password'],
                    firstName=userData['firstName'],lastName=userData['lastName']) is False:
        try:
            bot.anti_captcha()
        except:
            pass
    if bot.checkEmailSent() is False:
        bot.quitBrowser()
        continue
    time.sleep(20)
    verificationUrl = bot.getVerificationUrl(email=email[0],password=email[1])
    number = bot.requestNumber()
    bot.verifyPhone(url=verificationUrl,phoneNumber=number['number'],APIKEY=APIKEY,temporaryNumberID=number['temporaryNumberId'],twoCaptchaApi=twoCaptchaAPI)
    bot.postLogin()
    bot.UpgradePaypal(creditCard=card[0],expiryMonth=card[1],expiryYear=card[2],cvv=card[3],city=city,address1=userData['address'],postalCode=billingZip,email=email[0],password=email[1],
                firstName=userData['firstName'],lastName=['lastName'],phone=number['number'],state=state,paypalState=paypalState)
    bot.BuyNumber()
    apikey = bot.getAPISecretKeys()
    tollNumber = bot.getTollNumber()
    bot.saveTxt(APIKEY=apikey['APIKEY'],TOLLNUMBER=tollNumber['tollNumber'],MOBILENUMBER=tollNumber['mobileNumber'],SECRETKEY=apikey['secretKey'])
    bot.quitBrowser()
