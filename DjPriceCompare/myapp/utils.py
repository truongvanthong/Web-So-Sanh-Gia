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

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import numpy as np

def check_val_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}

from fuzzywuzzy import fuzz


# Thiết lập options cho Chrome headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")


# Khởi tạo driver
service = Service(ChromeDriverManager().install())
sendo_driver = webdriver.Chrome(options=chrome_options, service=service)
dienmaycholon_driver = webdriver.Chrome(options=chrome_options, service=service)
chotot_driver = webdriver.Chrome(options=chrome_options, service=service)
dienmayxanh_driver = webdriver.Chrome(options=chrome_options, service=service)
# ****************************************Format**********************************************

from deep_translator import GoogleTranslator
from selenium.common.exceptions import NoSuchElementException

def translator(text):
    """
    Dịch văn bản từ ngôn ngữ hiện tại sang tiếng Anh.
    # Đối với các trang quốc tế: Amazon, ...
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
        name2 = name.replace(" ", "+")
        dienmayxanh_url = f'https://www.dienmayxanh.com/tim-kiem?key={name2}'

        res = requests.get(dienmayxanh_url, headers=headers)
        print("\nSearching in Điện Máy Xanh...")
        soup = BeautifulSoup(res.text, 'html.parser')

        dienmayxanh_page = soup.select('a.main-contain')
        dienmayxanh_page_length = int(len(dienmayxanh_page))        
        
        matching_products = []  # List to store matching products
        for i in range(0, dienmayxanh_page_length):
            dienmayxanh_name = soup.select('a.main-contain>h3')[i].getText().strip().upper()
   
            similarity_score = fuzz.ratio(name.upper(), dienmayxanh_name)
            # print(f"Similarity Score: {similarity_score}")
                
            if similarity_score >= 10:
                dienmayxanh_name = soup.select('a.main-contain>h3')[i].getText().strip()
                # print(f"Name: {dienmayxanh_name}")

                dienmayxanh_images = soup.select('a.main-contain')
                if dienmayxanh_images:
                    if dienmayxanh_images[i].find('img').get('src'):
                        dienmayxanh_image = dienmayxanh_images[i].find('img')['src']
                    elif dienmayxanh_images[i].find_all('img', class_='lazyload'):
                        dienmayxanh_image = dienmayxanh_images[i].find_all('img', class_='lazyload')[0]['data-src']
                    elif dienmayxanh_images[i].find_all('img', class_='lazyloaded'):
                        dienmayxanh_image = dienmayxanh_images[i].find_all('img', class_='lazyloaded')[0]['data-src']  
                    else:
                        dienmayxanh_image = '0'
                else:
                    dienmayxanh_image = '0'
                
                try:
                    # Robust empty price check
                    if not soup.select('a.main-contain>strong.price')[i].getText().strip() or soup.select('a.main-contain>strong.price')[i].getText().strip() == ' ':
                        dienmayxanh_price = '0'
                    else:
                        dienmayxanh_price = soup.select('a.main-contain>strong.price')[i].getText().strip().upper()
                        dienmayxanh_price = dienmayxanh_price.strip('₫')
                        dienmayxanh_price = re.sub("[^0-9]", "", dienmayxanh_price)
                except:
                    continue        

                product = {
                    "name": dienmayxanh_name,
                    "price": dienmayxanh_price,
                    "image": dienmayxanh_image,
                    "link": dienmayxanh_url
                }

                # Kiểm tra xem sản phẩm nào price=0 thì không lưu vào matching_products và xoá product đó
                if product["price"] == '0':
                    continue

                matching_products.append(product)
          
        # Nếu không có sản phẩm nào thì trả về None
        if not matching_products:
            raise Exception("Không tìm thấy sản phẩm!") 
      

        dienmayxanh_price_float = [float(ele['price']) for ele in matching_products]  
        thresh = np.quantile(dienmayxanh_price_float, q = 0.55)
        
        # remome thresh 
        dienmayxanh_price = [ele['price'] for ele, price_float  in zip(matching_products, dienmayxanh_price_float) if price_float>=thresh]    
        
        # Name
        # ' '.join(element_names[0].get_text().replace("\n", "").split())
        dienmayxanh_name = [ele["name"] for ele, price_float in zip(matching_products, dienmayxanh_price_float) if price_float>=thresh]
                
        # Image
        # element_image[0].attrs['src']
        dienmayxanh_image = [ele["image"] for ele, price_float in zip(matching_products, dienmayxanh_price_float) if price_float>=thresh]
        
        # Lọc giá bé nhất
        dienmayxanh_price_float = [ele for ele in dienmayxanh_price_float if ele>=thresh]
        # min(enumerate(a), key=lambda x: x[1])[0]
        index_min = min(enumerate(dienmayxanh_price_float), key=lambda x: x[1])[0]
        
        dienmayxanh_name = dienmayxanh_name[index_min]
        dienmayxanh_price = dienmayxanh_price[index_min]
        dienmayxanh_image = dienmayxanh_image[index_min]
        
        
        print("Điện Máy Xanh:")
        print("Tên Sản Phẩm:", dienmayxanh_name)
        print("Giá:", dienmayxanh_price)
        print("Link Ảnh:", dienmayxanh_image)
        print("Link:", dienmayxanh_url)
        print("---------------------------------")
    
        return dienmayxanh_price, dienmayxanh_name[0:50], dienmayxanh_image, dienmayxanh_url

    except Exception as e:
        print(f"Lỗi: {e}")
        print("Điện Máy Xanh: No product found!")
        print("---------------------------------")
        dienmayxanh_price = '0'
        dienmayxanh_name = '0'
        dienmayxanh_image = '0'
        dienmayxanh_url = '0'
        return dienmayxanh_price, dienmayxanh_name[0:50], dienmayxanh_image, dienmayxanh_url
# ******************************************************************************************************

# ****************************************Điện Máy Xanh*****************************************
# def dienmayxanhx(name):
    try:
        name2 = name.replace(" ", "+")
        dienmayxanh_url = f'https://www.dienmayxanh.com/tim-kiem?key={name2}'

        res = requests.get(dienmayxanh_url, headers=headers)
        print("\nSearching in Điện Máy Xanh...")
        soup = BeautifulSoup(res.text, 'html.parser')

        dienmayxanh_page = soup.select('a.main-contain')
        dienmayxanh_page_length = int(len(dienmayxanh_page))        
        
        matching_products = []  # List to store matching products
        for i in range(0, dienmayxanh_page_length):
            dienmayxanh_name = soup.select('a.main-contain>h3')[i].getText().strip().upper()
   
            similarity_score = fuzz.ratio(name.upper(), dienmayxanh_name)
            # print(f"Similarity Score: {similarity_score}")
                
            if similarity_score >= 10:
                dienmayxanh_name = soup.select('a.main-contain>h3')[i].getText().strip()
                # print(f"Name: {dienmayxanh_name}")

                dienmayxanh_images = soup.select('a.main-contain')
                if dienmayxanh_images:
                    if dienmayxanh_images[i].find('img').get('src'):
                        dienmayxanh_image = dienmayxanh_images[i].find('img')['src']
                    elif dienmayxanh_images[i].find_all('img', class_='lazyload'):
                        dienmayxanh_image = dienmayxanh_images[i].find_all('img', class_='lazyload')[0]['data-src']
                    elif dienmayxanh_images[i].find_all('img', class_='lazyloaded'):
                        dienmayxanh_image = dienmayxanh_images[i].find_all('img', class_='lazyloaded')[0]['data-src']  
                    else:
                        dienmayxanh_image = '0'
                else:
                    dienmayxanh_image = '0'
                
                try:
                    # Robust empty price check
                    if not soup.select('a.main-contain>strong.price')[i].getText().strip() or soup.select('a.main-contain>strong.price')[i].getText().strip() == ' ':
                        dienmayxanh_price = '0'
                    else:
                        dienmayxanh_price = soup.select('a.main-contain>strong.price')[i].getText().strip().upper()
                        dienmayxanh_price = dienmayxanh_price.strip('₫')
                        dienmayxanh_price = re.sub("[^0-9]", "", dienmayxanh_price)
                except:
                    continue        

                product = {
                    "name": dienmayxanh_name,
                    "price": dienmayxanh_price,
                    "image": dienmayxanh_image,
                    "link": dienmayxanh_url
                }

                # Kiểm tra xem sản phẩm nào price=0 thì không lưu vào matching_products và xoá product đó
                if product["price"] == '0':
                    del product
                else:
                    matching_products.append(product)
          
        # Nếu không có sản phẩm nào thì trả về None
        if not matching_products:
            return None  
      
        dienmayxanh_price = matching_products[0]["price"]
        dienmayxanh_name= matching_products[0]["name"]
        dienmayxanh_image= matching_products[0]["image"]
        dienmayxanh_url= matching_products[0]["link"]
        print("Điện Máy Xanh:")
        print("Tên Sản Phẩm:", dienmayxanh_name)
        print("Giá:", dienmayxanh_price)
        print("Link Ảnh:", dienmayxanh_image)
        print("Link:", dienmayxanh_url)
        print("---------------------------------")
    
        return dienmayxanh_price, dienmayxanh_name[0:50], dienmayxanh_image, dienmayxanh_url

    except Exception as e:
        print(f"Lỗi: {e}")
        print("Điện Máy Xanh: No product found!")
        print("---------------------------------")
        dienmayxanh_price = '0'
        dienmayxanh_name = '0'
        dienmayxanh_image = '0'
        dienmayxanh_url = '0'
        return dienmayxanh_price, dienmayxanh_name[0:50], dienmayxanh_image, dienmayxanh_url
# ******************************************************************************************************

#  ****************************************Amazon**********************************************
def amazon(name):
    try:
        global amazon
        name = translator(name)
        name1 = name.replace(" ", "-")
        name2 = name.replace(" ", "+")
        amazon = f'https://www.amazon.in/{name1}/s?k={name2}'
        amazon_link = amazon
        print(amazon_link)
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
            
            # Tính toán độ tương đồng giữa tên sản phẩm và tên sản phẩm tìm kiếm
            similarity_score = fuzz.ratio(name, amazon_name)
            # print(f"Similarity Score: {similarity_score}")
            if similarity_score >= 10:
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

# # *************************Chợ Tốt*************************
# def chotot(name):
#     try:
#         # Chuẩn bị URL
#         name2 = name.replace(" ", "-")
#         chotot_url = f'https://www.chotot.com/mua-ban?q={name2}'

#         chotot_driver.get(chotot_url) 
#         # driver.implicitly_wait(10)  # Chờ đợi element xuất hiện 
#         print("---------------------------------")
#         print("\nSearching in Chợ Tốt...")
#         soup = BeautifulSoup(chotot_driver.page_source, 'lxml')
        
#         # Tìm kiếm element
#         element_name = soup.select("h3.commonStyle_adTitle__g520j")

#         element_price = soup.select("p.AdBody_adPriceNormal___OYFU")
        
#         element_image = soup.select("picture.webpimg-container img")


#         # Lấy thông tin sản phẩm   
               
#         # Giá
#         chotot_price = [ele.get_text().strip(' đ').strip().replace(".", "") for ele in element_price]
#         chotot_price_float = [float(ele) for ele in chotot_price]
#         thresh = np.quantile(chotot_price_float, q = 0.1)
#         # remome thresh 
#         chotot_price = [ele for ele, price_float  in zip(chotot_price, chotot_price_float) if price_float>=thresh]    
        
#         # Name
#         # ' '.join(element_names[0].get_text().replace("\n", "").split())
#         chotot_name = [' '.join(ele.get_text().replace("\n", "").split()) for ele, price_float in zip(element_name, chotot_price_float) if price_float>=thresh]
                
#         # Image
#         # element_image[0].attrs['src']
#         chotot_image = [ele.attrs['src'] for ele, price_float in zip(element_image, chotot_price_float) if price_float>=thresh]
        
#         # Lọc giá bé nhất
#         chotot_price_float = [ele for ele in chotot_price_float if ele>=thresh]
#         # min(enumerate(a), key=lambda x: x[1])[0]
#         index_min = min(enumerate(chotot_price_float), key=lambda x: x[1])[0]
        
#         chotot_name = chotot_name[index_min]
#         chotot_price = chotot_price[index_min]
#         chotot_image = chotot_image[index_min]
        
#         print("Chợ Tốt:")
#         print("Tên Sản Phẩm:", chotot_name)
#         print("Giá:", chotot_price)
#         print("Link Ảnh:", chotot_image)
#         print("Link:", chotot_url)
#         print("---------------------------------")

#         return chotot_price, chotot_name[0:50], chotot_image, chotot_url

#     except Exception as e:
#         print(f"Lỗi: {e}")
#         chotot_price = '0'
#         chotot_name = '0'
#         chotot_image = '0'
#         chotot_url = '0'
#         return chotot_price, chotot_name, chotot_image, chotot_url
    
# # ******************************************


# *************************Chợ Tốt*************************
# *************************Chợ Tốt*************************
def chotot(name):
    try:
        # Chuẩn bị URL
        name2 = name.replace(" ", "-")
        chotot_url = f'https://www.chotot.com/mua-ban?q={name2}'

        chotot_driver.get(chotot_url) 
        chotot_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        chotot_driver.implicitly_wait(10)  # Chờ đợi element xuất hiện 

        print("---------------------------------")
        print("\nSearching in Chợ Tốt...")
        soup = BeautifulSoup(chotot_driver.page_source, 'lxml')
        
        elements = soup.select("div.ListAds_ListAds__rEu_9.col-xs-12.no-padding li.AdItem_wrapperAdItem__S6qPH.AdItem_big__70CJq")
        chotot_name = []
        chotot_price = []
        chotot_image = []
        if len(elements) == 0:
            raise Exception("Không tìm thấy sản phẩm!")
            
        for ele in elements:
            try:
                image_element = ele.select_one("picture.webpimg-container img")
                if image_element is not None:
                    image_element = image_element.get("src")
                else:   
                    continue
                
                name_element = ele.select_one("h3.commonStyle_adTitle__g520j")
                if name_element is not None:
                    name_element = name_element.get_text()
                else:
                    name_element = '0'
                    
                price_element = ele.select_one("p.AdBody_adPriceNormal___OYFU")
                if price_element is not None:
                    price_element = price_element.get_text().strip(' đ').strip().replace(".", "")
                else:
                    price_element = '0'
 
                chotot_name.append(name_element)
                chotot_price.append(price_element)
                chotot_image.append(image_element)
            except:
                pass

        
        chotot_check_vald_product = [check_val_float(ele) for ele in chotot_price]
        if not any(chotot_check_vald_product):
            raise Exception("Không tìm thấy sản phẩm!")
        
        # Lọc ra những giá trị không hợp lệ
        
        chotot_name = [ele for ele, check in zip(chotot_name, chotot_check_vald_product) if check]
        chotot_price = [ele for ele, check in zip(chotot_price, chotot_check_vald_product) if check]    
        chotot_image = [ele for ele, check in zip(chotot_image, chotot_check_vald_product) if check]
        
        chotot_price_float = [float(ele) for ele in chotot_price]
        thresh = np.quantile(chotot_price_float, q = 0.55)
        # remome thresh 
        chotot_price = [ele for ele, price_float  in zip(chotot_price, chotot_price_float) if price_float>=thresh]    
        
        # Name
        chotot_name = [ele for ele, price_float in zip(chotot_name, chotot_price_float) if price_float>=thresh]
                
        # Image
        # element_image[0].attrs['src']
        chotot_image = [ele for ele, price_float in zip(chotot_image, chotot_price_float) if price_float>=thresh]
        
        # Lọc giá bé nhất
        chotot_price_float = [ele for ele in chotot_price_float if ele>=thresh]
        
        # Check if chotot_price_float is not empty
        if chotot_price_float:
            index_min = min(enumerate(chotot_price_float), key=lambda x: x[1])[0]   
            
            chotot_name = chotot_name[index_min]
            chotot_price = chotot_price[index_min]
            chotot_image = chotot_image[index_min]
            
            print("Chợ Tốt:")
            print("Tên Sản Phẩm:", chotot_name)
            print("Giá:", chotot_price)
            print("Link Ảnh:", chotot_image)
            print("Link:", chotot_url)
            print("---------------------------------")

            return chotot_price, chotot_name[0:50], chotot_image, chotot_url        
        else:
            print("chotot_price_float is empty")
            return '0', '0', '0', '0'

    except Exception as e:
        print(f"Lỗi: {e}")
        chotot_price = '0'
        chotot_name = '0'
        chotot_image = '0'
        chotot_url = '0'
        return chotot_price, chotot_name, chotot_image, chotot_url
    
# ******************************************
    
# ******************************************

def sendo(name):
    try:
        # Chuẩn bị URL
        name2 = name.replace(" ", "+")
        sendo_url = f"https://www.sendo.vn/tim-kiem?q={name2}"
        print("Searching in Sen đỏ...")
        sendo_driver.get(sendo_url)
        
        
        # Tìm kiếm danh sách element
        name_elements = WebDriverWait(sendo_driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.d7ed-Vp2Ugh._0032-Zwkt7j"))
                         )
        # Tìm kiếm danh sách element giá sản phẩm
        price_elements = WebDriverWait(sendo_driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span._0032-GpBMYp._0032-npoTU_.d7ed-CLUDGW.d7ed-AHa8cD.d7ed-giDKVr"))
                        )
        # Tìm kiếm danh sách element ảnh sản phẩm
        image_elements = WebDriverWait(sendo_driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.d7ed-a1ulZz img"))
                        )

        # # Kiểm tra số lượng element
        num_elements = len(name_elements)
        # print(num_elements)
        if num_elements != len(price_elements) or num_elements != len(image_elements):
            print("Sendo: Số lượng element không khớp!")
            return []

        # Lấy danh sách sản phẩm
        products = []

        for i in range(num_elements):
            # Lấy tên sản phẩm
            sendo_name = name_elements[i].text

            # Lấy giá sản phẩm
            sendo_price = price_elements[i].text.strip('đ')
            # '900000đ-999000 xử lý chỉ lấy giá ở sau dấu "-"
            sendo_price = sendo_price.split("-")[-1]
            sendo_price = sendo_price.replace(".", "")
                            

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

            products.append(product)

        sendo_price_float = [float(ele["price"]) for ele in products]
        thresh = np.quantile(sendo_price_float, q = 0.55)
        # remome thresh
        products = [ele for ele in products if float(ele["price"])>=thresh]
        
        # Lọc giá bé nhất
        sendo_price_float = [float(ele["price"]) for ele in products]
        # min(enumerate(a), key=lambda x: x[1])[0]
        index_min = min(enumerate(sendo_price_float), key=lambda x: x[1])[0]

        sendo_name = products[index_min]["name"]
        sendo_price = products[index_min]["price"]
        sendo_image = products[index_min]["image"]

        print("Sendo:")
        print("Tên Sản Phẩm:", sendo_name)
        print("Giá:", sendo_price)
        print("Link Ảnh:", sendo_image)
        print("Link:", sendo_url)
        print("---------------------------------")
        
        return sendo_price, sendo_name[0:50], sendo_image, sendo_url
        
                                         
    except Exception as e:
        print(f"Lỗi: {e}")
        sendo_price = '0'
        sendo_name = '0'
        sendo_link = '0'
        sendo_image = '0'
        return sendo_price, sendo_name, sendo_image, sendo_link
    
# **************************************************************************

# *************************Điện máy chợ lớn*************************
def dienmaycholon(name):
    try:
        # Chuẩn bị URL
        name2 = name.replace(" ", "-")
        dienmaycholon_url = f"https://dienmaycholon.vn/tu-khoa/{name2}"
        # print(dienmaycholon_url)
        dienmaycholon_driver.get(dienmaycholon_url) 
        dienmaycholon_driver.implicitly_wait(10)  # Chờ đợi element xuất hiện 
        print("---------------------------------")
        print("\nSearching in Điện Máy Chợ Lớn...")
        soup = BeautifulSoup(dienmaycholon_driver.page_source, 'lxml')
        
        elements = soup.select(".list_product_cat .product")
        dienmaycholon_name = []
        dienmaycholon_price = []
        dienmaycholon_image = []
        if len(elements) == 0:
            raise Exception("Không tìm thấy sản phẩm!")
            
        for ele in elements:
            try:
                image_element = ele.select_one("a.img_pro img")
                if image_element is not None:
                    image_element = (image_element.attrs['src'] or image_element.attrs['data-src'])
                    if image_element.startswith("//"):
                        image_element = "https:" + image_element
                    else:
                        image_element = "https://" + image_element   
                
                    if image_element.__contains__("base64"):
                        continue
                else:   
                    continue
                
                name_element = ele.select_one("h3.name_pro")
                if name_element is not None:
                    name_element = ' '.join(name_element.get_text().replace("\n", "").split())
                else:
                    name_element = '0'
                    
                price_element = ele.select_one("div.price_sale")
                if price_element is not None:
                    price_element = price_element.get_text().strip('đ').split(":")[-1].strip().replace(".", "")
                else:
                    price_element = '0'
 
                dienmaycholon_name.append(name_element)
                dienmaycholon_price.append(price_element)
                dienmaycholon_image.append(image_element)
            except:
                pass
        
       
        # Lấy thông tin sản phẩm   
               
        # Giá
        
        dienmaycholon_check_vald_product = [check_val_float(ele) for ele in dienmaycholon_price]
        if not any(dienmaycholon_check_vald_product):
            raise Exception("Không tìm thấy sản phẩm!")
    
        # Lọc ra những giá trị không hợp lệ

        dienmaycholon_name = [ele for ele, check in zip(dienmaycholon_name, dienmaycholon_check_vald_product) if check]
        dienmaycholon_price = [ele for ele, check in zip(dienmaycholon_price, dienmaycholon_check_vald_product) if check]        
        dienmaycholon_image = [ele for ele, check in zip(dienmaycholon_image, dienmaycholon_check_vald_product) if check]
         
        dienmaycholon_price_float = [float(ele) for ele in dienmaycholon_price]        
        thresh = np.quantile(dienmaycholon_price_float, q = 0.55)
        # remome thresh 
        dienmaycholon_price = [ele for ele, price_float  in zip(dienmaycholon_price, dienmaycholon_price_float) if price_float>=thresh]    
        
        # Name
        dienmaycholon_name = [ele for ele, price_float in zip(dienmaycholon_name, dienmaycholon_price_float) if price_float>=thresh]
                
        # Image
        # element_image[0].attrs['src']
        dienmaycholon_image = [ele for ele, price_float in zip(dienmaycholon_image, dienmaycholon_price_float) if price_float>=thresh]
        
        # Lọc giá bé nhất
        dienmaycholon_price_float = [ele for ele in dienmaycholon_price_float if ele>=thresh]
        # min(enumerate(a), key=lambda x: x[1])[0]
        index_min = min(enumerate(dienmaycholon_price_float), key=lambda x: x[1])[0]
        
        dienmaycholon_name = dienmaycholon_name[index_min]
        dienmaycholon_price = dienmaycholon_price[index_min]
        dienmaycholon_image = dienmaycholon_image[index_min]
        
        
        print("Điện Máy Chợ Lớn:")
        print("Tên Sản Phẩm:", dienmaycholon_name)
        print("Giá:", dienmaycholon_price)
        print("Link Ảnh:", dienmaycholon_image)
        print("Link:", dienmaycholon_url)
        print("---------------------------------")

        return dienmaycholon_price, dienmaycholon_name[0:50], dienmaycholon_image, dienmaycholon_url

    except Exception as e:
        print(f"Lỗi: {e}")
        dienmaycholon_price = '0'
        dienmaycholon_name = '0'
        dienmaycholon_image = '0'
        dienmaycholon_url = '0'
        return dienmaycholon_price, dienmaycholon_name, dienmaycholon_image, dienmaycholon_url
    
# ******************************************

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
        # print("Driver path", str(settings.BASE_DIR)+'\chromedriver.exe')
        wd = webdriver.Chrome('chromedriver.exe', options=CO)

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
