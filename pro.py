import datetime
import math
import threading
import time
import pymysql
import requests
import schedule
from bs4 import BeautifulSoup
from flask import Flask, request, render_template
import re

def dbconnect():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='localDB', charset='utf8')
    return conn


try:
    connection = dbconnect()
    if connection:
        print("DB 접속 완료")
    else:
        print("DB 접속 실패")
except Exception as e:
    print("DB 접속 중 오류 발생 : ", str(e))

# k스타트업
def insert1(conn):
    global flag_type_tags, txt_list, li_list, sql, sqls
    conn = dbconnect()
    url1 = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    response1 = requests.get(url1)
    html_content1 = response1.text
    soup1 = BeautifulSoup(html_content1, 'html.parser')
    if soup1:
        custom_search_wrap = soup1.find_all('div', 'custom_search-wrap')
        # print(custom_search_wrap)
        ann_cont_list = soup1.find_all('div', 'slide')

        for slide in ann_cont_list:
            ann_cont = slide.find('div', 'ann_cont')
            ann_top_list = slide.find_all('div', 'ann_top')
            tit_wrap_list = ann_cont.find_all('div', 'tit_wrap')
            ul_list = ann_cont.find_all('ul')

            # 링크 받아서 제목에서 클릭하면 실행되게 해야함
            links = slide.find_all('a')
            for link in links:
                href = link.get('href')
                hrefs = href.strip("javascript:go_view(" + ");")

            for ul in ul_list:
                li_list = ul.find_all('li')
                if len(li_list) >= 3:
                    second_li = li_list[1].text.strip()
                    third_li = li_list[2].text.strip()

            for ann_top in ann_top_list:
                txt_list = ann_top.find_all('p', 'txt')
                flag_type_tags = ann_top.find_all('span')
                if len(flag_type_tags) >= 0:
                    tags = flag_type_tags[0].text.strip()
            for tit_wrap in tit_wrap_list:
                tit_list = tit_wrap.find_all('p', 'tit')

                site = 'k스타트업'
                support = flag_type_tags[0].text.strip()
                name = tit_list[0].text.strip()
                r_date = 'null'  # 사이트에서 등록일을 받아오는 태그를 조회하면 등록된 데이터가 없다고해서 null값으로 지정했습니다.
                d_dates = txt_list[0].text.strip()
                d_date = d_dates.strip("마감일자")
                re_min = li_list[0].text.strip()
                agency = li_list[1].text.strip()
                view = li_list[2].text.strip()
                views = view.strip("조회 ")

                cur = conn.cursor()
                check_sql = f"SELECT COUNT(*) FROM localdb.crawling WHERE 링크 = '{hrefs}' ;"
                cur.execute(check_sql)
                result = cur.fetchone()
                count = result[0]

                # 크롤링 데이터 table 존재여부 체크
                if count == 0:
                    # 신규 데이터
                    print("INSERT-> " + hrefs)
                    sql = (
                        f"INSERT INTO localdb.crawling (사이트,지원분야,지원사업명,등록일,마감일,관련부처,수행기관,조회수, 링크, 입력일시) VALUES ( '{site}', '{support}', '{name}', '{r_date}', '{d_date}', '{re_min}', '{agency}', '{views}','{hrefs}', NOW() )")
                    cur.execute(sql)
                elif count != 0:  # 링크가 중복되는게 있으면 1이상 나와서 데이터가 변경된 사항이 있는지 체크한다.
                    # 존재 데이터
                    check_sql = (
                        f"SELECT count(*) FROM crawling WHERE 지원사업명 = '{name}' AND 마감일 = '{d_date}' AND 관련부처 = '{re_min}' AND 수행기관 = '{agency}' ")
                    cur.execute(check_sql)
                    result = cur.fetchone()
                    count_data = result[0]

                    # 데이터의 변경 사항 체크
                    if count_data == 0:
                        # 변경 시 해당 row의 데이터 UPDATE 처리
                        print("UPDATE-> " + hrefs)
                        sqls = (
                            f"UPDATE localdb.crawling SET 지원사업명 = '{name}', 마감일 = '{d_date}', 관련부처 = '{re_min}', 수행기관 = '{agency}', 수정일시 = NOW() WHERE 링크 = '{hrefs}'")
                        cur.execute(sqls)
            conn.commit()

# ----------------------------------------------------------------------------
# 비즈인포
def insert2(conn):
    url2 = "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do"
    response2 = requests.get(url2)
    html_content2 = response2.text
    soup2 = BeautifulSoup(html_content2, 'html.parser')

    tbody = soup2.find('tbody')
    if tbody:
        tr_list = tbody.find_all('tr')
        conn = dbconnect()
        cur = conn.cursor()
        for tr in tr_list:
            td_list = tr.find_all('td')
            values = [td.text.strip() for td in td_list]
            site = '비즈인포'
            support = values[1]
            name = values[2]
            r_date = values[6]
            date_pattern = re.compile(r'\d{4}-\d{2}-\d{2} ~')
            d_dates = values[3]
            d_date = date_pattern.sub('', d_dates.text.strip())
            re_min = values[4]
            agency = values[5]
            views = values[7]

            links = tr.find_all('a')
            for link in links:
                href = link.get('href')
                hrefs = href.strip("view.do?")

                cur = conn.cursor()
                check_sql = f"SELECT COUNT(*) FROM localdb.crawling WHERE 링크 = '{hrefs}' ;"
                cur.execute(check_sql)
                result = cur.fetchone()
                count = result[0]

                # 크롤링 데이터 table 존재여부 체크
                if count == 0:
                    # 신규 데이터
                    print("INSERT-> " + hrefs)
                    sql = (
                        f"INSERT INTO localdb.crawling (사이트,지원분야,지원사업명,등록일,마감일,관련부처,수행기관,조회수, 링크, 입력일시) VALUES ( '{site}', '{support}', '{name}', '{r_date}', '{d_date}', '{re_min}', '{agency}', '{views}','{hrefs}', NOW() )")
                    cur.execute(sql)
                elif count != 0:  # 링크가 중복되는게 있으면 1이상 나와서 데이터가 변경된 사항이 있는지 체크한다.
                    # 존재 데이터
                    check_sql = (
                        f"SELECT count(*) FROM crawling WHERE 지원사업명 = '{name}' AND 마감일 = '{d_date}' AND 관련부처 = '{re_min}' AND 수행기관 = '{agency}' ")
                    cur.execute(check_sql)
                    result = cur.fetchone()
                    count_data = result[0]

                    # 데이터의 변경 사항 체크
                    if count_data == 0:
                        # 변경 시 해당 row의 데이터 UPDATE 처리
                        print("UPDATE-> " + hrefs)
                        sqls = (
                            f"UPDATE localdb.crawling SET 지원사업명 = '{name}', 마감일 = '{d_date}', 관련부처 = '{re_min}', 수행기관 = '{agency}', 수정일시 = NOW() WHERE 링크 = '{hrefs}'")
                        cur.execute(sqls)
            conn.commit()

# iris
def insert3(conn):
    url3 = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
    response3 = requests.get(url3)
    html_content3 = response3.text
    soup3 = BeautifulSoup(html_content3, 'html.parser')

    main = soup3.find('main')
    site = 'iris'
    support = 'R&D'
    forms = main.find_all('div', 'form-row')
    sub = main.find_all('span', 'inst_title')

    for form, item in zip(forms, sub):
        names = form.find('strong', 'title')
        name = names.text.strip()
        a_tag = names.find('a')
        if a_tag:  # a 태그가 있다면
            href = a_tag.get('onclick')
            numbers = re.findall(r'\d+', href)
            hrefs = numbers[0]

        ancmDe = form.find('span', 'ancmDe')
        date = ancmDe.text.strip()
        r_date = date.replace("공고일자 :", "")
        d_date = 'null'
        views = 'null'

        re_min = item.text.strip().split(' > ')[0]
        agency = item.text.strip().split(' > ')[1]

        cur = conn.cursor()
        check_sql = f"SELECT COUNT(*) FROM localdb.crawling WHERE 링크 = '{hrefs}' ;"
        cur.execute(check_sql)
        result = cur.fetchone()
        count = result[0]

        # 크롤링 데이터 table 존재여부 체크
        if count == 0:
            # 신규 데이터
            print("INSERT-> " + hrefs)
            sql = (
                f"INSERT INTO localdb.crawling (사이트,지원분야,지원사업명,등록일,마감일,관련부처,수행기관,조회수, 링크, 입력일시) VALUES ( '{site}', '{support}', '{name}', '{r_date}', '{d_date}', '{re_min}', '{agency}', '{views}','{hrefs}', NOW() )")
            cur.execute(sql)
        elif count != 0:  # 링크가 중복되는게 있으면 1이상 나와서 데이터가 변경된 사항이 있는지 체크한다.
            # 존재 데이터
            check_sql = (
                f"SELECT count(*) FROM crawling WHERE 지원사업명 = '{name}' AND 마감일 = '{d_date}' AND 관련부처 = '{re_min}' AND 수행기관 = '{agency}' ")
            cur.execute(check_sql)
            result = cur.fetchone()
            count_data = result[0]

            # 데이터의 변경 사항 체크
            if count_data == 0:
                # 변경 시 해당 row의 데이터 UPDATE 처리
                print("UPDATE-> " + hrefs)
                sqls = (
                    f"UPDATE localdb.crawling SET 지원사업명 = '{name}', 마감일 = '{d_date}', 관련부처 = '{re_min}', 수행기관 = '{agency}', 수정일시 = NOW() WHERE 링크 = '{hrefs}'")
                cur.execute(sqls)

    conn.commit()

# 서울경제진흥원
def insert4(conn):
    url4 = "https://seoul.rnbd.kr/client/c030100/c030100_00.jsp"
    response4 = requests.get(url4)
    html_content4 = response4.text
    soup4 = BeautifulSoup(html_content4, 'html.parser')

    if soup4:
        body = soup4.find('body')
        date_ranges = [p.text for p in body.find_all('p', 'date pc_tblind')]
        dates = [date_range.split(' ~ ') for date_range in date_ranges]
        site = '서울경제진흥원'
        support = 'R&D'
        re_min ='X'
        agency = 'X'
        t1 = body.find_all('td', 't1')
        links = [link.a.get('href') for link in t1]
        view = [td.text.strip() for td in body.find_all('td', 'm_tblind')]

        for i, t in enumerate(t1):
            r_date, d_date = dates[i]
            hrefs = links[i]
            views = view[i * 3 + 2]
            date_pattern = re.compile(r'\d{4}-\d{2}-\d{2} ~ \d{4}-\d{2}-\d{2}')
            name = date_pattern.sub('', t.text.strip())
            cur = conn.cursor()
            check_sql = f"SELECT COUNT(*) FROM localdb.crawling WHERE 링크 = '{hrefs}' ;"
            cur.execute(check_sql)
            result = cur.fetchone()
            count = result[0]

            # 크롤링 데이터 table 존재여부 체크
            if count == 0:
                # 신규 데이터
                print("INSERT-> " + hrefs)
                sql = (
                    f"INSERT INTO localdb.crawling (사이트,지원분야,지원사업명,등록일,마감일,관련부처,수행기관,조회수, 링크, 입력일시) VALUES ( '{site}', '{support}', '{name}', '{r_date}', '{d_date}', '{re_min}', '{agency}', '{views}','{hrefs}', NOW() )")
                cur.execute(sql)
            elif count != 0:  # 링크가 중복되는게 있으면 1이상 나와서 데이터가 변경된 사항이 있는지 체크한다.
                # 존재 데이터
                check_sql = (
                    f"SELECT count(*) FROM crawling WHERE 지원사업명 = '{name}' AND 마감일 = '{d_date}' AND 관련부처 = '{re_min}' AND 수행기관 = '{agency}' ")
                cur.execute(check_sql)
                result = cur.fetchone()
                count_data = result[0]

                    # 데이터의 변경 사항 체크
                if count_data == 0:
                    # 변경 시 해당 row의 데이터 UPDATE 처리
                    print("UPDATE-> " + hrefs)
                    sqls = (
                        f"UPDATE localdb.crawling SET 지원사업명 = '{name}', 마감일 = '{d_date}', 관련부처 = '{re_min}', 수행기관 = '{agency}', 수정일시 = NOW() WHERE 링크 = '{hrefs}'")
                    cur.execute(sqls)

        conn.commit()

app = Flask(__name__)

@app.route('/form')
def form():
    with app.app_context():
        conn = dbconnect()
        cur = conn.cursor()
        sql = 'SELECT * FROM localdb.crawling GROUP BY 링크 ORDER BY 번호 DESC'
        cur.execute(sql)
        result = cur.fetchall()
    update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_list = []
    for i in range(len(result)):
        data = {
            'number': result[i][0],
            'site': result[i][1],
            'support': result[i][2],
            'name': result[i][3],
            'r_date': result[i][4],
            'd_dates': result[i][5],
            're_min': result[i][6],
            'agency': result[i][7],
            'views': result[i][8],
            'link': result[i][9],
            'datetime': result[i][10],
            'last_time' : result[i][11]
        }
        data_list.append(data)

    current_page = request.args.get('page', default=1, type=int)
    total_page = (len(data_list) / 12)
    total_pages = math.trunc(total_page)
    return render_template('python_crowling.html', update_time=update_time, data_list=data_list,
                           current_page=current_page,
                           total_pages=total_pages)
def run_app():
    app.run(host="0.0.0.0", port="8080")
def main():
    conn = dbconnect()
    # insert2(conn)
    # insert1(conn)
    insert3(conn)
    # insert4(conn)

    update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("크롤링이 돌아가는 시간:", update_time)
    print('데이터 저장 실행중...')

schedule.every(10).seconds.do(main)
schedule.every(1).hours.do(main)

app_thread = threading.Thread(target=run_app)
app_thread.start()

while True:
    schedule.run_pending()
    time.sleep(1)