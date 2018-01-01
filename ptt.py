from flask import Flask, request, abort
import os, random, requests, re, time
from bs4 import BeautifulSoup

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import*

app = Flask(__name__)

line_bot_api = LineBotApi('Your Channel Access Token')
handler = WebhookHandler('Your Channel Secret')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK' 

def ptt_gossiping():
    rs = requests.session()
    load = {
        'from': '/bbs/Gossiping/index.html',
        'yes': 'yes'
    }
    res = rs.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
    soup = BeautifulSoup(res.text, 'html.parser')
    article_gossiping = []
    index_list = []
    index_url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    index_list.append(index_url)

    # 在最新頁面抓取所有文章
    while index_list:
        index = index_list.pop(0)
        res_next = rs.get(index, verify=False)
        soup_next = BeautifulSoup(res_next.text, 'html.parser')

        # 如網頁忙線中,則先將網頁加入index_list
        if res_next.status_code != 200:
            index_list.append(index)
        else:
            for r_ent in soup_next.find_all(class_="r-ent"):
                try:
                    # 在class<"r-ent">中尋找url
                    link = r_ent.find('a')['href']
                    if link:
                        # 確定得到url再去抓標題跟文章連結
                        title = r_ent.find(class_="title").text.strip()
                        url_link = 'https://www.ptt.cc' + link
                        # 排除最下方的置底文章
                        if (title[0:4] != '[公告]') and (title[0:4] != '[尋人]') and (title[0:4] != '[協尋]') and (title[0:4] != '[爆卦]') and (title[0:4] != 'Fw: '):
                            article_gossiping.append({
                                'url_link': url_link,
                                'title': title
                            })
                        else:
                        	pass
                    else:
                    	pass
                except Exception as e:
                    # print('本文已被刪除')
                    print('delete', e)
    num = len(article_gossiping)
    content = ''
    for index, article in enumerate(article_gossiping, 0):
       	if index == num:
            return content
        else:
        	content = '{}\n{}\n\n'.format(article.get('title', None), article.get('url_link', None))
    return content

def ptt_NBA():
    rs = requests.session()
    res = rs.get('https://www.ptt.cc/bbs/NBA/index.html', verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    article_nba = []
    content = ''
    # 如網頁忙線中,則休息一秒
    if res.status_code != 200:
        content = 'PTT忙線中!'
        time.sleep(1)
    else:
        for r_ent in soup.find_all(class_="r-ent"):
            try:
                # 在class<"r-ent">中尋找url
                link = r_ent.find('a')['href']
                if link:
                    # 確定得到url再去抓標題跟文章連結
                    title = r_ent.find(class_="title").text.strip()
                    url_link = 'https://www.ptt.cc' + link
                    # 排除最下方的置底文章
                    if (title[0:4] != '[公告]') and (title[0:4] != '[情報]'):
                        article_nba.append({
                            'url_link': url_link,
                            'title': title
                        })
                    else:
                        pass
                else:
                    pass
            except Exception as e:
                print('delete', e)
    num = len(article_nba)
    for index, article in enumerate(article_nba, 0):
       	if index == num:
            return content
        else:
        	content = '{}\n{}\n\n'.format(article.get('title', None), article.get('url_link', None))
    return content
def ptt_Beauty():
    rs = requests.session()
    res = rs.get('https://www.ptt.cc/bbs/Beauty/index.html', verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    # 利用按鈕先找出上一頁的網址
    last_page_url = soup.select('.btn.wide')[1]['href']
    # 得到url中間的數字
    now_page_number = get_page_number(last_page_url)
    article_beauty = []
    article_list = []
    # 抓出最新3頁的所有文章連結放到article_list
    for link in range(now_page_number - 2, now_page_number + 1):
        now_page_url = 'https://www.ptt.cc/bbs/Beauty/index{}.html'.format(link)
        res = requests.get(now_page_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        for article in soup.select('.r-ent a'):
            title = article.text.strip()
            # 限制分類，提升圖片品質
            if '[正妹]' in title and not '[神人]' in title:
                article_list.append('https://www.ptt.cc' + article['href'])
            else:
                pass

    article_num = len(article_list)
    # 隨機選擇一篇文章
    article_url = article_list[random.randint(0, article_num)]
    article_res = requests.get(article_url)
    article_soup = BeautifulSoup(article_res.text, 'html.parser')
    # 利用regular expression找出此篇文章中是否有來自imgur.com的圖片
    if len(article_soup.findAll('a', {'href':re.compile('http[s]?://[i.]*imgur.com/\w+\.(?:jpg|png|gif)')})) > 0:
        for index, img_url in enumerate(article_soup.findAll('a', {'href':re.compile('http[s]?://[i.]*imgur.com/\w+\.(?:jpg|png|gif)')})):
            try:
            	# 將該文章中的所有圖片放進article_beauty
                article_beauty.append(img_url['href'])
            except:
                print('失敗!')
    else:
        pass

    num = len(article_beauty)
    return article_beauty, num

def get_page_number(content): #找page按鈕的url中間的數字
    start_index = content.find('index')
    end_index = content.find('.html')
    page_number = content[start_index + 5: end_index]
    return int(page_number) + 1

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text           
    if text == 'Gossiping': 
        uId = event.source.user_id
        content = ptt_gossiping()
        line_bot_api.push_message(
            uId, 
            TextSendMessage(text = content))
    elif text == 'NBA':
        uId = event.source.user_id
        content = ptt_NBA()
        line_bot_api.push_message(
            uId, 
            TextSendMessage(text = content))
    elif text == 'Beauty':
        try:
            uId = event.source.user_id
            (content, number) = ptt_Beauty()
            # 從article_beauty中隨機選擇一張圖片
            url = content[random.randint(0, number)]
            print(url)
            line_bot_api.push_message(
                uId, 
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url))
        except Exception as e:
            line_bot_api.reply_message(
            event.reply_token,[
                TextSendMessage(text = '資料更新中!'),
                StickerSendMessage(package_id = 2,sticker_id = 18)])
    elif text == 'Info':
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(text = '指令 : \nGossiping : 八卦版\n' + 'NBA : NBA版\n' + 'Beauty : 表特版\n' +
            	                   '注意 : \n有時候等比較久屬於正常狀況，\n' + '若30秒後無反應請再按一次。'),
            StickerSendMessage(package_id = 1,sticker_id = 120)])
    else:
        line_bot_api.reply_message(
            event.reply_token,[
                TextSendMessage(text = '請打指令 : \nGossiping, NBA, Beauty, Info'),
                StickerSendMessage(package_id = 1,sticker_id = 113)])

if __name__ == "__main__":
   app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))