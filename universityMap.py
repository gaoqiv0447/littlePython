import folium
import pandas as pd
from geopy.geocoders import Nominatim
import time
import os

# 读取大学列表
with open('universityList.txt', 'r', encoding='utf-8') as f:
    universities = f.read().splitlines()

# 初始化地理编码器
geolocator = Nominatim(user_agent="my_agent")

# 创建中国地图
m = folium.Map(location=[35.86166, 104.195397], zoom_start=4)

# 为每个大学获取经纬度并标注
for university in universities:
    try:
        # 添加"中国"以提高定位准确性
        location = geolocator.geocode(f"{university},中国")
        if location:
            # 添加红色圆点标记
            folium.CircleMarker(
                location=[location.latitude, location.longitude],
                radius=5,
                color='red',
                fill=True,
                popup=university
            ).add_to(m)
        # 添加延时避免请求过快
        time.sleep(1)
        print(f"已定位 {university}")
    except Exception as e:
        print(f"无法定位 {university}: {str(e)}")

# 保存地图
m.save("universityMap.html")

# 使用selenium将html转换为jpg
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('file://' + os.path.abspath("universityMap.html"))
time.sleep(2)  # 等待地图加载

# 获取页面尺寸并设置窗口大小
width = driver.execute_script("return document.documentElement.scrollWidth")
height = driver.execute_script("return document.documentElement.scrollHeight")
driver.set_window_size(width, height)

# 截图并保存
driver.save_screenshot("universityMap.jpg")
driver.quit()

print("地图已保存为universityMap.jpg")
