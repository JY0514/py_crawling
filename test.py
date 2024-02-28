# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# # 웹드라이버 경로 설정 및 실행 (여기서는 Chrome을 예로 들었습니다. 실제 경로를 입력해주세요.)
# driver = webdriver.Chrome('/path/to/chromedriver')
#
# # 웹 페이지 로드
# driver.get('https://www.iris.go.kr/contents/retrieveBsnsAncmView.do')
#
# # 원하는 'a' 태그를 선택. (여기서는 특정 id를 가진 'a' 태그를 예로 들었습니다.)
# # 만약 특정 클래스를 가진 'a' 태그를 찾으려면 (By.CLASS_NAME, 'class_name') 를 사용하세요.
# element = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, 'some_id'))
# )
#
# # 'a' 태그 클릭
# element.click()
#
# # 이후 원하는 작업 수행
#
# # 웹드라이버 종료
# driver.quit()
