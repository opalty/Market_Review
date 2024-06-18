import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 크롬 드라이버 설정
chrome_options = Options()

# 웹 드라이버 서비스 설정
service = Service(ChromeDriverManager().install())

# 웹 드라이버 시작
driver = webdriver.Chrome(service=service, options=chrome_options)

# 네이버 지도 페이지로 이동
driver.get("https://m.place.naver.com/place/13304144/review/visitor?entry=plt")

# 페이지가 로드될 때까지 대기
wait = WebDriverWait(driver, 10)

# '더보기' 버튼을 반복적으로 클릭하여 모든 리뷰 로드
while True:
    try:
        more_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'fvwqf')))
        driver.execute_script("arguments[0].click();", more_button)
        time.sleep(1)  # 페이지 로드 시간 대기
    except Exception:
        break

# 모든 리뷰 요소 추출
reviews = driver.find_elements(By.CLASS_NAME, 'zPfVt')
review_list = [review.text for review in reviews]

# 크롬 드라이버 종료
driver.quit()

# 리뷰 데이터를 CSV 파일로 저장
csv_file = 'reviews.csv'
with open(csv_file, 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Review'])  # CSV 파일의 첫 번째 행은 열 제목
    for review in review_list:
        writer.writerow([review])

print(f"Total {len(review_list)} reviews have been saved to {csv_file}")