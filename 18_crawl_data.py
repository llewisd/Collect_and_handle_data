from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os


bot = webdriver.Edge(executable_path='msedgedriver.exe')
bot.get('https://fptshop.com.vn/may-tinh-xach-tay?sort=ban-chay-nhat&trang=10')
bot.maximize_window()

# Lấy danh sách sản phẩm
products = WebDriverWait(bot, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".cdt-product")))

# Lặp qua từng phần tử
data = []
for i in range(0,len(products)):
     print(f'Đang crawl item thứ {i+1} ...')
     # Lấy kích thước màn hình (inch)
     try:
          screen = products[i].find_element(By.CSS_SELECTOR,'span[data-title="Màn hình"]').get_attribute('textContent')
          screen = float(re.search(r"[-+]?(?:\d*\.*\d+)", screen).group())
     except:
          screen = None
     # Lấy CPU 
     try:
          cpu = products[i].find_element(By.CSS_SELECTOR,'span[data-title="CPU"]').get_attribute('textContent')
     except:
          cpu = None
     # Lấy RAM (GB)
     try:
          ram = products[i].find_element(By.CSS_SELECTOR,'span[data-title="RAM"]').get_attribute('textContent')
          ram = int(re.search(r"[-+]?(?:\d*\.*\d+)", ram).group())
     except:
          ram = None
     # Lấy dung lượng ổ cứng (GB)
     try:
          ssd = products[i].find_element(By.CSS_SELECTOR,'span[data-title="Ổ cứng"]').get_attribute('textContent')
          ssd = int(re.search(r"[-+]?(?:\d*\.*\d+)", ssd).group())
     except:
          ssd = None
     # Lấy card đồ họa
     try:
          gpu = products[i].find_element(By.CSS_SELECTOR,'span[data-title="Đồ họa"]').get_attribute('textContent')
          # gpu = re.search(r'\S+', gpu).group()
     except:
          gpu = None
     # Lấy trọng lượng (kg)
     try:
          weight = products[i].find_element(By.CSS_SELECTOR,'span[data-title="Trọng lượng"]').get_attribute('textContent')
          weight = float(re.search(r"[-+]?(?:\d*\.*\d+)", weight).group())
          if weight > 10: weight /= 1000
          name = products[i].find_element(By.CSS_SELECTOR,'.cdt-product__name').get_attribute('textContent')
          if 'Laptop' in name:
               name = name.replace('Laptop','')
          elif 'Máy tính xách tay' in name:
               name = name.replace('Máy tính xách tay','')
          else: pass
     except:
          weight = None
     # Lấy tên máy tính
     try:
          name = name.strip()
          name = re.search(r'\S+', name).group().lower()
     except:
          name = None
     # Lấy khuyến mãi (đồng)
     try:
          discount = products[i].find_element(By.CSS_SELECTOR,'.badge-primary').get_attribute('textContent').replace('.','')
          discount = int(re.search(r"[-+]?(?:\d*\.*\d+)", discount).group())
     except:
          discount = 0
     # Lấy giá (đồng)
     try:
          price = products[i].find_element(By.CSS_SELECTOR,'.progress').get_attribute('textContent').replace('.','')
          price = int(re.search(r"[-+]?(?:\d*\.*\d+)", price).group())
     except:
          price = products[i].find_element(By.CSS_SELECTOR,'.price').get_attribute('textContent').replace('.','')
          price = int(re.search(r"[-+]?(?:\d*\.*\d+)", price).group())

     # Click products
     click_item = products[i].find_element(By.CSS_SELECTOR,'.cdt-product__name')
     original_window = bot.current_window_handle
     click_item.click()
     new_window = bot.current_window_handle
     bot.switch_to.window(new_window)
     try:
          link = WebDriverWait(bot, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".re-link.js--open-modal")))
     except: 
          bot.back()
          bot.switch_to.window(original_window)
          products = WebDriverWait(bot, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".cdt-product")))
          continue
     # Lấy thời gian bảo hành (tháng)
     try:
          warranty = bot.find_element(By.CSS_SELECTOR,'.l-pd-policy > .l-pd-policy__item:nth-child(2) > p').get_attribute('textContent')
          warranty = int(re.search(r"[-+]?(?:\d*\.*\d+)", warranty).group())
     except:
          warranty = None
     # Lấy FGold (dùng để đổi Voucher khi thanh toán)
     try:
          fgold = bot.find_element(By.CSS_SELECTOR,'.btn-loyalty.tooltip.tooltip-right.tooltip-dark > strong').get_attribute('textContent')
          fgold = float(re.search(r"[-+]?(?:\d*\.*\d+)", fgold).group())
     except:
          fgold = 0
     # Lấy Trả góp (đồng/tháng)
     try:
          installment = bot.find_element(By.CSS_SELECTOR,'.st-price > .st-price__right span:nth-child(2) strong').get_attribute('textContent')
          installment = int(float(re.search(r"[-+]?(?:\d*\.*\d+)", installment).group()) * 1000000)
     except:
          installment = 0
     # # Lấy số lượng đánh giá
     try:
          evaluation = bot.find_element(By.CSS_SELECTOR,'.st-rating__link > a:nth-child(1)').get_attribute('textContent')
          evaluation = int(re.search(r"[-+]?(?:\d*\.*\d+)", evaluation).group())
     except:
          evaluation = 0
     # Lấy số lượng hỏi đáp
     try:
          answer = bot.find_element(By.CSS_SELECTOR,'.st-rating__link > a:last-child').get_attribute('textContent')
          answer = int(re.search(r"[-+]?(?:\d*\.*\d+)", answer).group())
     except:
          answer = 0
     # Lấy số sao 
     try:
          star = bot.find_elements(By.CSS_SELECTOR,'.st-rating__star > li span.icon-star.fill')
          star = len(star)
     except:
          star = 0

     # Click vào link để lấy thông số kỹ thuật
     link.click()
     # Lấy hệ điều hành
     try:
          os = WebDriverWait(bot, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".c-modal__row:nth-last-child(2) > .st-table tr:nth-child(1) td:last-child"))).get_attribute('textContent').lower()
     except:
          os = None

     # Phần bổ sung
     # Lấy phần Thiết kế (2): kích thước (mm), màu sắc 
     # Lấy phần Bộ xử lý (5): hãng cpu, loại cpu, tốc độ cpu (GHz), số nhân, số luồng
     # Lấy phần RAM (4): loại RAM, tốc độ RAM (MHz), số khe cắm rời, số ram onboard
     # Lấy màn hình (5): công nghệ màn hình, độ phân giải, loại màn hình,tần số quét, tấm nền, độ phủ màu
     # Lấy âm thanh (1): số lượng loa
     # Lấy bàn phím (3): kiểu bàn phím, bàn phím số, đèn bàn phím
     # Lấy sạc (2): loại pin, power supply
     size = color = cpu_branch = cpu_type = cpu_speed = cpu_core = cpu_thread = \
     ram_type = ram_speed = ram_track = ram_onboard = screen_tech = screen_resolution = screen_scan = \
     screen_plate = screen_coverage = screen_type = speaker = keyboard_type = keyboard_number = keyboard_lamp = \
     battery_type = battery_supply = None

     fields = bot.find_elements(By.CSS_SELECTOR,'.c-modal__content > .c-modal__row')
     for field in fields:
          title_element = field.find_element(By.CSS_SELECTOR,'.st-table-title')
          title = title_element.get_attribute('textContent')
          if title == 'Thông tin hàng hóa': 
               continue
          # Lấy phần Thiết kế (2): kích thước (mm), màu sắc
          elif title == 'Thiết kế & Trọng lượng':
               rows = field.find_elements(By.CSS_SELECTOR, 'table:nth-child(2) > tbody tr')
               for row in rows:
                    title_td = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    text_td = title_td.get_attribute('textContent')
                    if text_td == 'Kích thước':
                         try:
                              size = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              size = None
                    elif text_td == 'Màu sắc':
                         try:
                              color = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              color = None
                    else: continue
          # Lấy phần Bộ xử lý (5): hãng cpu, loại cpu, tốc độ cpu (GHz), số nhân, số luồng
          elif title == 'Bộ xử lý':
               rows = field.find_elements(By.CSS_SELECTOR, 'table > tbody tr')
               for row in rows:
                    title_td = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    text_td = title_td.get_attribute('textContent')
                    if text_td == 'Hãng CPU':
                         try:
                              cpu_branch = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              cpu_branch = None
                    elif text_td == 'Loại CPU':
                         try:
                              cpu_type = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              cpu_type = None
                    elif text_td == 'Tốc độ CPU':
                         try:
                              cpu_speed = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                              cpu_speed = float(re.search(r"[-+]?(?:\d*\.*\d+)", cpu_speed).group())
                         except:
                              cpu_speed = None
                    elif text_td == 'Số nhân':
                         try:
                              cpu_core = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                              cpu_core = int(re.search(r"[-+]?(?:\d*\.*\d+)", cpu_core).group())
                         except:
                              cpu_core = None
                    elif text_td == 'Số luồng':
                         try:
                              cpu_thread = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                              cpu_thread = int(re.search(r"[-+]?(?:\d*\.*\d+)", cpu_thread).group())
                         except:
                              cpu_thread = None
                    else: continue
          # Lấy phần RAM (4): loại RAM, tốc độ RAM (MHz), số khe cắm rời, số ram onboard
          elif title == 'RAM':
               rows = field.find_elements(By.CSS_SELECTOR, 'table > tbody tr')
               for row in rows:
                    title_td = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    text_td = title_td.get_attribute('textContent')
                    if text_td == 'Loại RAM':
                         try:
                              ram_type = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              ram_type = None
                    elif text_td == 'Tốc độ RAM':
                         try:
                              ram_speed = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              ram_speed = None
                    elif text_td == 'Số khe cắm rời':
                         try:
                              ram_track = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              ram_track = None
                    elif text_td == 'Số RAM onboard':
                         try:
                              ram_onboard = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              ram_onboard = None
                    else: continue
          # Lấy màn hình (5): công nghệ màn hình, độ phân giải,  tần số quét, tấm nền, độ phủ màu
          elif title == 'Màn hình':
               rows = field.find_elements(By.CSS_SELECTOR, 'table > tbody tr')
               for row in rows:
                    title_td = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    text_td = title_td.get_attribute('textContent')
                    if text_td == 'Công nghệ màn hình':
                         try:
                              screen_tech = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              screen_tech = None
                    elif text_td == 'Độ phân giải':
                         try:
                              screen_resolution = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              screen_resolution = None
                    elif text_td == 'Tần số quét':
                         try:
                              screen_scan = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              screen_scan = None
                    elif text_td == 'Loại màn hình':
                         try:
                              screen_type = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              screen_type = None
                    elif text_td == 'Tấm nền':
                         try:
                              screen_plate = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              screen_plate = None
                    elif text_td == 'Độ phủ màu':
                         try:
                              screen_coverage = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              screen_coverage = None
                    else: continue
          # Lấy âm thanh (1): số lượng loa
          elif title == 'Âm thanh':
               rows = field.find_elements(By.CSS_SELECTOR, 'table > tbody tr')
               for row in rows:
                    title_td = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    text_td = title_td.get_attribute('textContent')
                    if text_td == 'Số lượng loa':
                         try:
                             speaker = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                             speaker = None
                    else: continue
          # Lấy bàn phím (3): kiểu bàn phím, bàn phím số, đèn bàn phím
          elif title == 'Bàn phím & TouchPad':
               rows = field.find_elements(By.CSS_SELECTOR, 'table > tbody tr')
               for row in rows:
                    title_td = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    text_td = title_td.get_attribute('textContent')
                    if text_td == 'Kiểu bàn phím':
                         try:
                              keyboard_type = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              keyboard_type = None
                    elif text_td == 'Bàn phím số':
                         try:
                              keyboard_number = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              keyboard_number = None
                    elif text_td == 'Đèn bàn phím':
                         try:
                              keyboard_lamp = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              keyboard_lamp = None
                    else: continue
          # Lấy sạc (2): loại pin, power supply
          elif title == 'Thông tin pin & Sạc':
               rows = field.find_elements(By.CSS_SELECTOR, 'table > tbody tr')
               for row in rows:
                    title_td = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
                    text_td = title_td.get_attribute('textContent')
                    if text_td == 'Loại PIN':
                         try:
                              battery_type = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              battery_type = None
                    elif text_td == 'Power Supply':
                         try:
                              battery_supply = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').get_attribute('textContent')
                         except:
                              battery_supply = None
                    else: continue
          else: continue

     data.append({'branch': name, 'screen': screen, 'CPU': cpu, 'RAM': ram, 'memory': ssd, 'graphic card': gpu, 'weight': weight, 'discount': discount,
                  'warranty': warranty, 'fgold': fgold, 'installment': installment,
                  'evaluation': evaluation, 'answer': answer, 'star': star , 
                  'size': size, 'color': color, 'cpu_branch': cpu_branch, 'cpu_type': cpu_type, 
                   'cpu_speed': cpu_speed, 'cpu_core': cpu_core, 'cpu_thread': cpu_thread ,
                    'ram_type': ram_type, 'ram_speed': ram_speed, 'ram_track': ram_track,
                    'ram_onboard': ram_onboard , 'screen_tech': screen_tech, 'screen_resolution': screen_resolution, 
                    'screen_plate': screen_plate, 'screen_scan': screen_scan, 'screen_coverage': screen_coverage, 
                    'screen_type': screen_type,'speaker': speaker, 'keyboard_type': keyboard_type, 'keyboard_number': keyboard_number,
                    'keyboard_lamp': keyboard_lamp, 'battery_type': battery_type, 'battery_supply': battery_supply ,'os': os, 'price': price })
     bot.back()
     bot.switch_to.window(original_window)
     products = WebDriverWait(bot, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".cdt-product")))

df = pd.DataFrame.from_dict(data)
df.to_csv('laptop.csv', index=False)