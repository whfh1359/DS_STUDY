import pandas as pd
import time
import requests
from selenium import webdriver

# explicitly wait 사용하려면 다음 3줄 공식처럼 외우기
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
#headless 옵션 추가한다
print("#1. selenium get url")
options = webdriver.ChromeOptions()
options.add_argument("headless")

# 전체 데이터 크롤링
url = "https://store.musinsa.com/app/"
driver = webdriver.Chrome("../driver/chromedriver", options=options)
#웹 페이지 전체가 로딩 될 때까지 10초간 대기하고, 10초안에 로딩 완료되면 다음 코드 실행
driver.implicitly_wait(10) 
driver.get(url)

# headless떄문에 화면 최대화 하는 것 추가
print("#2. maximize window")
driver.maximize_window()

print("#3. best item")
# 인기 => 후드 집업
best_link = driver.find_element_by_css_selector("#ui-id-2 > ul:nth-child(1) > li:nth-child(1) > a").get_attribute("href")
# 인기 => 후드 집업 링크 => 새 탭으로 열기
driver.execute_script("window.open('{}')".format(best_link))
driver.switch_to_window(driver.window_handles[1])
print("#4. tab open ok! I'm waiting..")
time.sleep(3)

print("#5. item option check")
# 단독 상품 선택
WebDriverWait(driver, 5).\
until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btn_exclusive"))).click() #5초는 시간
# 세일 상품 선택
WebDriverWait(driver, 5).\
until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btn_sale"))).click() #5초는 시간
# 최소 ~최대 금액 설정
WebDriverWait(driver, 5).\
until(EC.presence_of_element_located((By.CSS_SELECTOR, "#minPrice"))).send_keys("10000")

WebDriverWait(driver, 5).\
until(EC.presence_of_element_located((By.CSS_SELECTOR, "#maxPrice"))).send_keys("100000")

WebDriverWait(driver, 5).\
until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btn_price_search"))).click()
print("#6. item option check done! I'm waiting")
time.sleep(3)

print("#7. outers crawling start")

# 부모 태그
outers = driver.find-element_by_css_selector("#searchList > li")

# 전체 데이터 크롤링 - tqdm 뺀다, tqdm은 jupyter notebook 에서 확인하기 위한 용도
datas = []

for idx, outer in enumerate(outers[:3]):
    title = outer.find_element_by_css_selector("p.list_info > a").get_attribute("title")
    price = outer.find_element_by_css_selector("p.price").text.split(" ")[1][:-1]
    sale = outer.find_element_by_css_selector(".icon_new").text.split(" ")[1][:-1]
    link = outer.find_element_by_css_selector("p.list_info > a").get_attribute("href")
    img = outer.find_element_by_css_selector("img").get_attribute("data-original")
    print(img)
    datas.append({
        "title" : title,
        "price" : price,
        "sale" : sale,
        "link" : link,
        "img" : img
    })
    print("#8. idx : {}, title: {}".format(idx, title))
driver.quit()
df = pd.DataFrame(datas)
df.to_excel("./musinsa/musinsa.xlsx", encoding = "utf-8")
print("#9. crawling Done! driver quit & excel save")


print("10. img download")
# 이미지 다운로드
for idx, rows in df.iterrows():
    thumb_link = rows["img"]
    response = requests.get(thumb_link)
    name = str(idx) + "_" + rows["title"]
    with open ("./musinsa/{}.png" .format(name), "wb") as f: #write binary
        f.write(response.content)
print("#11. img download done!")
print("#12. Good Job!")
