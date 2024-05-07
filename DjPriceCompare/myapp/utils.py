import imp
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.conf import settings
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}

from fuzzywuzzy import fuzz

# ****************************************Format**********************************************

from deep_translator import GoogleTranslator
from selenium.common.exceptions import NoSuchElementException

def translator(text):
    """
    Dịch văn bản từ ngôn ngữ hiện tại sang tiếng Anh.
    # Đối với các trang quốc tế: Amazon, GadgetsNow, Reliance Digital
    """
    
    type_trans = GoogleTranslator(source='auto', target='en')
    trans = type_trans.translate(text)
    return trans

def no_accent_vietnamese(s):
    s = s.lower()
    s = re.sub('[áàảãạăắằẳẵặâấầẩẫậ]', 'a', s)
    s = re.sub('[éèẻẽẹêếềểễệ]', 'e', s)
    s = re.sub('[óòỏõọôốồổỗộơớờởỡợ]', 'o', s)
    s = re.sub('[íìỉĩị]', 'i', s)
    s = re.sub('[úùủũụưứừửữự]', 'u', s)
    s = re.sub('[ýỳỷỹỵ]', 'y', s)
    s = re.sub('đ', 'd', s)
    return s

def convert(a):
    b = a.replace(" ", '')
    c = b.replace("INR", '')
    d = c.replace(",", '')
    d = d.replace("`", '')
    f = d.replace("₹", '')
    f1 = f.replace(".", '')
    f2 = f1.replace("₫", '')
    g = int(float(f2))
    return g

def format_price(price):
    """Formats a price number into a string with commas, currency symbol, and handles potential decimals.

  Args:
      price: The price as a number (float or int).

  Returns:
      A string representing the formatted price.
  """
    # Handle potential decimals
    if isinstance(price, float):
        price_str = "{:,.2f}".format(price)  # Two decimal places for floats
    else:
        price_str = "{:,}".format(price)  # No decimal places for integers

    return price_str + "đ"  # Add currency symbol (đ)
# **********************************************************************************************


# ****************************************Điện Máy Xanh*****************************************
def dienmayxanh(name):
    try:
        global dienmayxanh
        #name=no_accent_vietnamese(name)
        name1 = name.replace(" ", "-")
        name2 = name.replace(" ", "+")
        dienmayxanh = f'https://www.dienmayxanh.com/tim-kiem?key={name2}'
        dienmayxanh_link = dienmayxanh
        res = requests.get(
            f'https://www.dienmayxanh.com/tim-kiem?key={name2}', headers=headers)
        print("\nSearching in Điện Máy Xanh...")
        soup = BeautifulSoup(res.text, 'html.parser')
        #print(soup)
        dienmayxanh_page = soup.select('a.main-contain')
        #print(dienmayxanh_page)
        dienmayxanh_page_length = int(len(dienmayxanh_page))
        # print(dienmayxanh_page_length)
        for i in range(0, dienmayxanh_page_length):
            name1 = name.upper()
            dienmayxanh_name = soup.select(
                'a.main-contain>h3')[i].getText().strip().upper()
            similarity_score = fuzz.ratio(name.upper(), dienmayxanh_name)
            if similarity_score > 5:
                dienmayxanh_name = soup.select(
                    'a.main-contain>h3')[i].getText().strip()       
                
                dienmayxanh_images = soup.select('a.main-contain')
                
                # Kiểm tra xem có ảnh được trả về không
                if dienmayxanh_images:
                    # Nếu có ảnh, thực hiện lấy đường link ảnh
                    if dienmayxanh_images[i].find('img').get('src'):
                        dienmayxanh_image = dienmayxanh_images[i].find('img')['src']
                    elif dienmayxanh_images[0].find_all('img', class_='lazyload'):
                        dienmayxanh_image = dienmayxanh_images[0].find_all('img', class_='lazyload')[0]['data-src']
                    else:
                        # Nếu không có cả 'src' và 'data-src', gán một giá trị mặc định
                        dienmayxanh_image = '0'
                else:
                    # Nếu không có ảnh, gán một giá trị mặc định
                    dienmayxanh_image = '0'
                                
                dienmayxanh_price = soup.select(
                    'a.main-contain>strong.price')[i].getText().strip().upper()
                dienmayxanh_price=dienmayxanh_price.strip('₫')
                print("Điện Máy Xanh:")
                print("Tên Sản Phẩm:", dienmayxanh_name)
                print("Giá:", dienmayxanh_price)
                print("Link Ảnh:", dienmayxanh_image)
                print("Link:", dienmayxanh_link)
                
                print("---------------------------------")
                break
            else:
                i += 1
                i = int(i)
                if i == dienmayxanh_page_length:
                    dienmayxanh_price = '0'
                    print("Điện Máy Xanh : No product found!")
                    print("-----------------------------")
                    break

        return dienmayxanh_price, dienmayxanh_name[0:50], dienmayxanh_image, dienmayxanh_link
    except:
        print("Điện Máy Xanh: No product found!")
        print("---------------------------------")
        dienmayxanh_price = '0'
        dienmayxanh_name = '0'
        dienmayxanh_link = '0'
        dienmayxanh_image = '0'
    return dienmayxanh_price, dienmayxanh_name[0:50], dienmayxanh_image, dienmayxanh_link

# ******************************************************************************************************


# ****************************************Amazon**********************************************
def amazon(name):
    try:
        global amazon
        name = translator(name)
        name1 = name.replace(" ", "-")
        name2 = name.replace(" ", "+")
        amazon = f'https://www.amazon.in/{name1}/s?k={name2}'
        amazon_link = amazon
        res = requests.get(
            f'https://www.amazon.in/{name1}/s?k={name2}', headers=headers)
        print("\nSearching in amazon...")
        soup = BeautifulSoup(res.text, 'html.parser')
        amazon_page = soup.select('.a-color-base.a-text-normal')
        amazon_page_length = int(len(amazon_page))
        for i in range(0, amazon_page_length):
            name = name.upper()
            amazon_name = soup.select(
                '.a-color-base.a-text-normal')[i].getText().strip().upper()
            if name in amazon_name:
                amazon_name = soup.select(
                    '.a-color-base.a-text-normal')[i].getText().strip()
                amazon_images = soup.select(
                    '.a-section.aok-relative.s-image-fixed-height')
                amazon_image = amazon_images[0].find_all(
                    'img', class_='s-image')[0]
                amazon_image = amazon_image['src']
                amazon_price = soup.select(
                    '.a-price-whole')[i].getText().strip().upper()
                print("Amazon:")
                print("Tên Sản Phẩm:", amazon_name)
                print("Giá:", amazon_price)
                print("Link Ảnh:", amazon_image)
                print("Link:", amazon_link)
                print("---------------------------------")
                break
            else:
                i += 1
                i = int(i)
                if i == amazon_page_length:
                    amazon_price = '0'
                    print("amazon : No product found!")
                    print("-----------------------------")
                    break

        return amazon_price, amazon_name[0:50], amazon_image, amazon_link
    except:
        print("Amazon: No product found!")
        print("---------------------------------")
        amazon_price = '0'
        amazon_name = '0'
        amazon_link = '0'
        amazon_image = '0'
    return amazon_price, amazon_name[0:50], amazon_image, amazon_link
# ====================================================================================


#********************************************Chợ tốt**********************************************************************

def chotot(name):
    try:
        # Chuẩn bị URL
        name2 = name.replace(" ", "+")
        chotot_url = f'https://www.chotot.com/mua-ban?q={name2}'

        # Thiết lập options cho Chrome headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        # Khởi tạo driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.get(chotot_url)

        # Tìm kiếm danh sách element sản phẩm
        product_elements = driver.find_elements(By.CSS_SELECTOR, "div.ListAds_ListAds__rEu_9")

        products = []
        for product_element in product_elements:
            # Lấy thông tin sản phẩm
            try:
                name_element = product_element.find_element(By.CSS_SELECTOR, "h3.commonStyle_adTitle__g520j")
                price_element = product_element.find_element(By.CSS_SELECTOR, "p.AdBody_adPriceNormal___OYFU")
                image_element = product_element.find_element(By.CSS_SELECTOR, "picture.webpimg-container img")

                chotot_name = name_element.text
                chotot_price = price_element.text.strip('đ')
                chotot_image = image_element.get_attribute("src")

                # Lưu thông tin vào dictionary
                product = {
                    "name": chotot_name,
                    "price": chotot_price,
                    "image": chotot_image,
                    "link": chotot_url
                }
                products.append(product)
            except NoSuchElementException:
                # Bỏ qua nếu element không tồn tại
                pass

        driver.quit()  # Đóng trình duyệt

        # In thông tin sản phẩm (nếu có)
        if products:
            for product in products:
                print("Chợ tốt:")
                print("Tên Sản Phẩm:", product["name"])
                print("Giá:", product["price"])
                print("Link Ảnh:", product["image"])
                print("Link:", product["link"])
                print("---------------------------------")
        else:
            print("chotot: No product found!")
            print("---------------------------------")

        return products

    except Exception as e:
        print(f"Lỗi: {e}")
        return []
# *********************************************************************************************************


# *****************************************Sen Đỏ*****************************
def sendo(name):
    try:
        # Chuẩn bị URL
        name2 = name.replace(" ", "+")
        sendo_url = f"https://www.sendo.vn/tim-kiem?q={name2}"

        # Khởi tạo driver (headless Chrome)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.get(sendo_url)
        
        
        # Tìm kiếm danh sách element
        name_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.d7ed-Vp2Ugh._0032-Zwkt7j"))
                         )
        # Tìm kiếm danh sách element giá sản phẩm
        price_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span._0032-GpBMYp._0032-npoTU_.d7ed-CLUDGW.d7ed-AHa8cD.d7ed-giDKVr"))
                        )
        # Tìm kiếm danh sách element ảnh sản phẩm
        image_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.d7ed-a1ulZz img"))
                        )

        # # Kiểm tra số lượng element
        num_elements = len(name_elements)
        # print(num_elements)
        if num_elements != len(price_elements) or num_elements != len(image_elements):
            print("sendo: Số lượng element không khớp!")
            driver.quit()
            return []

        # Lấy danh sách sản phẩm
        products = []
        min_price = float('inf')  # Khởi tạo giá trị min_price là vô cùng
        cheapest_product = None
        for i in range(num_elements):
            # Lấy tên sản phẩm
            sendo_name = name_elements[i].text

            # Lấy giá sản phẩm
            sendo_price = price_elements[i].text.strip('đ')

            # Chuyển đổi giá thành số (xóa dấu chấm)
            try:
                price_num = int(sendo_price.replace('.', ''))
            except ValueError:
                print(f"Lỗi chuyển đổi giá: {sendo_price}")
                continue  # Bỏ qua sản phẩm này nếu không thể chuyển đổi giá

            # Lấy link ảnh sản phẩm
            image_src = image_elements[i].get_attribute("data-src")
            if not image_src:
                image_src = image_elements[i].get_attribute("src")

            # Lưu thông tin vào dictionary
            product = {
                "name": sendo_name,
                "price": sendo_price,
                "image": image_src,
                "link": sendo_url
            }

            # Kiểm tra giá và cập nhật sản phẩm rẻ nhất
            if price_num < min_price:
                min_price = price_num
                cheapest_product = product

        # Thêm sản phẩm rẻ nhất vào danh sách (nếu có)
        if cheapest_product:
            products.append(cheapest_product)

        driver.quit()  # Đóng trình duyệt

        # In thông tin sản phẩm (nếu có)
        if products:
            for product in products:
                print("Sendo:")
                print("Tên Sản Phẩm:", product["name"])
                print("Giá:", product["price"])
                print("Link Ảnh:", product["image"])
                print("Link:", product["link"])
                print("---------------------------------")
        else:
            print("sendo: No product found!")
            print("---------------------------------")

        return products

    except Exception as e:
        print(f"Lỗi: {e}")
        return []
    
# **************************************

# *************************Điện máy chợ lớn*************************
def dienmaycholon(name):
    try:
        # Chuẩn bị URL
        name2 = name.replace(" ", "+")
        dienmaycholon_url = f"https://dienmaycholon.vn/tu-khoa/{name2}"

        # Khởi tạo driver (headless Chrome)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.get(dienmaycholon_url)
        
        
        # Tìm kiếm danh sách element
        name_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3.name_pro"))
                            )

        # Tìm kiếm danh sách element giá sản phẩm
        price_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.price_sale"))
                        )

        # Tìm kiếm danh sách element ảnh sản phẩm
        image_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.img_pro img"))
                        )

        # # Kiểm tra số lượng element
        num_elements = len(name_elements)
        # print(num_elements)
        if num_elements != len(price_elements) or num_elements != len(image_elements):
            print("Điện máy chợ lớn: Số lượng element không khớp!")
            driver.quit()
            return []

        # Lấy danh sách sản phẩm
        products = []
        min_price = float('inf')  # Khởi tạo giá trị min_price là vô cùng
        cheapest_product = None
        for i in range(num_elements):
            # Lấy tên sản phẩm
            dienmaycholon_name = name_elements[i].text

            # Lấy giá sản phẩm
            dienmaycholon_price = price_elements[i].text.strip('đ')

            # Chuyển đổi giá thành số (xóa dấu chấm)
            try:
                price_num = int(dienmaycholon_price.replace('.', ''))
            except ValueError:
                print(f"Lỗi chuyển đổi giá: {dienmaycholon_price}")
                continue  # Bỏ qua sản phẩm này nếu không thể chuyển đổi giá

            # Lấy link ảnh sản phẩm
            image_src = image_elements[i].get_attribute("src")
            if not image_src:
                image_src = image_elements[i].get_attribute("data-src")

            # Lưu thông tin vào dictionary
            product = {
                "name": dienmaycholon_name,
                "price": dienmaycholon_price,
                "image": image_src,
                "link": dienmaycholon_url
            }

            # Kiểm tra giá và cập nhật sản phẩm rẻ nhất
            if price_num < min_price:
                min_price = price_num
                cheapest_product = product

        # Thêm sản phẩm rẻ nhất vào danh sách (nếu có)
        if cheapest_product:
            products.append(cheapest_product)

        driver.quit()  # Đóng trình duyệt

        # In thông tin sản phẩm (nếu có)
        if products:
            for product in products:
                print("Điện máy chợ lớn:")
                print("Tên Sản Phẩm:", product["name"])
                print("Giá:", product["price"])
                print("Link Ảnh:", product["image"])
                print("Link:", product["link"])
                print("---------------------------------")
        else:
            print("Điện máy chợ lớn: No product found!")
            print("---------------------------------")

        return products

    except Exception as e:
        print(f"Lỗi: {e}")
        return []
    
# ******************************************



def gadgetsnow(name):
    try:
        global gadgetsnow
        name = translator(name)
        name1 = name.replace(" ", "-")
        name2 = name.replace(" ", "+")
        gadgetsnow = f'https://shop.gadgetsnow.com/mtkeywordsearch?SEARCH_STRING={name2}'
        gadgetsnow_link = gadgetsnow
        res = requests.get(
            f'https://shop.gadgetsnow.com/mtkeywordsearch?SEARCH_STRING={name2}', headers=headers)
        print("\nSearching in gadgetsnow...")
        soup = BeautifulSoup(res.text, 'html.parser')
        gadgetsnow_page = soup.select('.product-name')
        gadgetsnow_page_length = int(len(gadgetsnow_page))

        for i in range(0, gadgetsnow_page_length):
            name = name.upper()
            gadgetsnow_name = soup.select(
                '.product-name')[i].getText().strip().upper()
            if name in gadgetsnow_name:
                gadgetsnow_name = soup.select(
                    '.product-name')[i].getText().strip()
                images = soup.select('.product-img-align')[i]
                image = images.select('.lazy')[0]
                gadgetsnow_image = image['data-original']
                gadgetsnow_price = soup.select('.offerprice')[
                    i].getText().strip().upper()
                gadgetsnow_price = "".join(gadgetsnow_price)
                gadgetsnow_price = gadgetsnow_price[1:]
                print("GadgetSnow:")
                print(gadgetsnow_name)
                gadgetsnow_price = "₹"+gadgetsnow_price
                print("---------------------------------")
                break
            else:
                i += 1
                i = int(i)
                if i == gadgetsnow_page_length:
                    gadgetsnow_price = '0'
                    print("GadgetSnow : No product found!")
                    print("-----------------------------")
                    break

        return gadgetsnow_price, gadgetsnow_name[0:50], gadgetsnow_image, gadgetsnow_link
    except:
        print("GadgetSnow: No product found!")
        print("---------------------------------")
        gadgetsnow_price = '0'
        gadgetsnow_name = '0'
        gadgetsnow_image = '0'
        gadgetsnow_link = '0'
    return gadgetsnow_price, gadgetsnow_name[0:50], gadgetsnow_image, gadgetsnow_link

def croma(name):
    try:
        global croma
        name1 = name.replace(" ", "-")
        name2 = name.replace(" ", "+")
        croma = f"https://www.croma.com/search/?q={name2}:relevance:ZAStatusFlag:true:excludeOOSFlag&text={name2}"
        source = croma
        croma_link = croma
        wait_imp = 10
        CO = webdriver.ChromeOptions()
        CO.add_experimental_option('useAutomationExtension', False)
        CO.add_argument('--ignore-certificate-errors')
        CO.add_argument('--start-maximized')
        print("Driver path", str(settings.BASE_DIR)+'\chromedriver.exe')
        wd = webdriver.Chrome(r''+str(settings.BASE_DIR) +
                              '\chromedriver.exe', options=CO)

        wd.get(source)
        wd.implicitly_wait(wait_imp)

        try:
            elementname = WebDriverWait(wd, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "h3.product-title.plp-prod-title"))
            )
            elementprice = WebDriverWait(wd, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.amount"))
            )
            imgelement = WebDriverWait(wd, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.product-img.plp-card-thumbnail img"))
            )
        except:
            wd.quit()

        croma_name = elementname.text
        croma_price = elementprice.text
        croma_image = imgelement.get_attribute("src")
        return croma_price, croma_name[0:50], croma_image, croma_link
    except:
        print("Croma: No product found!")
        print("---------------------------------")
        croma_price = '0'
        croma_name = '0'
        croma_image = '0'
        croma_link = '0'
    return croma_price, croma_name[0:50], croma_image, croma_link

def reliance(name):
    try:
        global reliance
        name = translator(name)
        name1 = name.replace(" ", "-")
        name2 = name.replace(" ", "+")
        reliance = f'https://www.reliancedigital.in/search?q={name2}:relevance'
        reliance_link = reliance
        res = requests.get(
            f'https://www.reliancedigital.in/search?q={name2}:relevance', headers=headers)
        print("\nSearching in reliance...")
        soup = BeautifulSoup(res.text, 'html.parser')
        reliance_page = soup.select('.sp__name')
        article_block = soup.find_all('div', class_='slider-text')
        reliance_data = article_block[0].getText().strip(
        )[article_block[0].getText().strip().index('₹')+1:]
        reliance_price = ""
        for i in reliance_data:
            if i.isnumeric() or i == ',':
                reliance_price += i
            else:
                break
        images = soup.find_all('img', class_='img-responsive')
        reliance_image = "https://www.reliancedigital.in/" + \
            images[0]['data-srcset']
        reliance_page_length = int(len(reliance_page))
        for i in range(0, reliance_page_length):
            name = name.upper()
            reliance_name = soup.select('.sp__name')[
                i].getText().strip().upper()
            if name in reliance_name:
                reliance_name = soup.select('.sp__name')[i].getText().strip()
                print("Reliance:", reliance_price)
                print(reliance_name)
                print(reliance_image)
                print("₹"+reliance_price)
                print("---------------------------------")
                break
            else:
                i += 1
                i = int(i)
                if i == reliance_page_length:
                    reliance_price = '0'
                    print("reliance : No product found!")
                    print("-----------------------------")
                    break

        return reliance_price, reliance_name[0:50], reliance_image, reliance_link
    except:
        print("Reliance: No product found!")
        print("---------------------------------")
        reliance_price = '0'
        reliance_image = '0'
        reliance_name = '0'
        reliance_link = '0'
    return reliance_price, reliance_name[0:50], reliance_image, reliance_link



