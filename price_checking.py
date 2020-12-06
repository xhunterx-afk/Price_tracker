import requests
from bs4 import BeautifulSoup
import smtplib, ssl
import time
from email.message import EmailMessage

# Storing old price in a list
old_price = []
# Giving the user inputs to enter
Url = input("Enter a url: ")
user_agent = input("Enter your uer agent\n"
                   "To get your user info google the following:\n"
                   "- My user agent")
# letting the user choose the type of shop wether amazon or ebay
shop_type = input("please choose in between ebay or amazon: ")

# user email and the send email(
#I added sender mail so if people want to make a site with people I mean me)

user_email = input("please Enter your E-mail: ")
test_mail = "*********@gmail.com"
password = input("Enter a password: ")

# getting the price/image/name of product and exctracting them
def check_price():
    page = requests.get(Url, headers=user_agent)
    soup = BeautifulSoup(page.text, "html.parser")
    # If the user input was amazon this code will run
    if shop_type == "amazon":
      # try if error accure
        try:
            # Getting the price and changing it from sting to float
            price = soup.find(id="price_inside_buybox").get_text()
            converted_price = float(price.strip('€' + '\n' + '$' + '\xa0')
                                    .replace(',', ''))
        except AttributeError:
            print("!!!!!!This Item does not have a price!!!!!!!\n")
        # Getting image_link/product_name 
        image_dec = soup.find(id="imgTagWrapperId")
        img_title = image_dec.find('img', alt=True)
        product = img_title['alt']
        image_link = image_dec.find('img')
        image_base = image_link['data-a-dynamic-image']
        # getting the full length of image_link
        if image_base[78] == 'g':
            image_link = image_base[2:79]
        else:
            image_link = image_base[2:77]
    # If user input was ebay
    elif shop_type == "ebay":
        try:
            # Getting image_link/product_name 
            price = soup.find(id="prcIsum").get_text()
            converted_price = float(price.strip('€' + '\n' + '$' + ','))
        except AttributeError:
            print("!!!price not found!!!\n")
        image_desc = soup.find(itemprop="image")
        product = image_desc.get('alt')
        image_link = image_desc.get('src')
    # entering the price in the old_price if the price changes
    old_price.append(converted_price)

    if old_price[0] > converted_price:
        old_price.pop()
        old_price.append(converted_price)
        send_mail()

    elif old_price[0] < converted_price:
        old_price.pop()
        old_price.append(converted_price)
        send_mail()

    return product, old_price[0], image_link

# sending the mail with the product_name/product_image/price
def send_mail():
    product, price, image_link = check_price()
    img_data = requests.get(image_link).content

    context = ssl.create_default_context()

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(user_email, password)

    msg = EmailMessage()
    msg["From"] = test_mail
    msg["To"] = user_email
    msg["Subject"] = f"Price of your {product.title()} has Changed!!!"
    msg["Bcc"] = user_email

    msg.set_content(f"Your {product} price has changed to (EUR {price}), please check \n \n {Url}")
    msg.add_attachment(img_data, maintype='image', subtype='png', disposition='inline')

    server.send_message(msg)
    print("Hey message have been sent")
    server.quit()

# keep running the code every 60 min and checking for error with printing the kind of error the user have done
while True:
    try:
        check_price()
        send_mail()
        time.sleep(60000)
    except TypeError:
        print("Your input is not identified")
        break
    except UnboundLocalError or IndexError:
        print("1- There have been an error getting the price please check the link\n")
        print("2- You have entered the wrong type of shop")
        break
    except NameError:
        print("We are sorry there is no shop in that name our current app.")
        break
    except AttributeError:
        print("There is no such URL!!!!")
        break
    except requests.exceptions.MissingSchema:
        print("There is no such URL")
        break
    except smtplib.SMTPAuthenticationError:
        print("your password/username dose not match")
        break
