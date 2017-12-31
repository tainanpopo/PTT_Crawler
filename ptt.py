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
    article_beauty = []

    # 如網頁忙線中,則休息一秒
    if res.status_code != 200:
        article_beauty.append('PTT忙線中!')
        time.sleep(1)
    else:
    	# 找到每個文章的link
        for article in soup.select('.r-ent a'):
            title = article.text.strip()
            # 限定分類是正妹的文章
            if title[0:4] == '[正妹]':
                url = 'https://www.ptt.cc' + article['href']
                title = article.text.strip()
                res = requests.get(url)
                soup = BeautifulSoup(res.text, 'html.parser')
                # 利用regular expression找出是否有來自imgur.com的圖片
                if len(soup.findAll('a', {'href':re.compile('http[s]?://[i.]*imgur.com/\w+\.(?:jpg|png|gif)')})) > 0:
                    for index, img_url in enumerate(soup.findAll('a', {'href':re.compile('http[s]?://[i.]*imgur.com/\w+\.(?:jpg|png|gif)')})):
                        try:
                    	    article_beauty.append(img_url['href'])
                        except:
                            print('失敗!')
                else:
                	pass
            else:
            	pass
    num = len(article_beauty)
    return article_beauty, num

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
            url = content[random.randint(0, number)]
            line_bot_api.push_message(
                uId, 
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url))
        except Exception as e:
            line_bot_api.reply_message(
            event.reply_token,[
                TextSendMessage(text = 'PTT忙線中!'),
                StickerSendMessage(package_id = 2,sticker_id = 18)])
    elif text == 'Info':
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(text = '指令 : \nGossiping : 八掛版\n' + 'NBA : NBA版\n' +  'Beauty : 表特版'),
            StickerSendMessage(package_id = 1,sticker_id = 120)])
    else:
        line_bot_api.reply_message(
            event.reply_token,[
                TextSendMessage(text = '請打指令 : \nGossiping, NBA, Beauty, Info'),
                StickerSendMessage(package_id = 1,sticker_id = 113)])

if __name__ == "__main__":
   app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))