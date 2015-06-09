# -*- coding: utf-8 -*-
"""
Created on Wed Mar 04 21:55:21 2015

@author: Efrem
"""

import pandas as pd
from bs4 import BeautifulSoup  
from collections import Counter
import os.path
import requests


def thread_list(max_number_of_pages = 10):   
    # get page source and create a BeautifulSoup object based on it
    print "Reading threadlist pages...",
    headers = {
        'User-Agent': "nobody",
        'From': 'BarefootEfrem@gmail.com' 
        }

    url_base = "http://www.letsrun.com/forum/forum.php"
    
    title = []
    thread_num = []
    first_timestamp = []
    last_timestamp = []
    author = []
    post_count = []
    
    
    for page_num in range(1,max_number_of_pages+1):
        print "%d " % page_num,   
        
        # http://www.letsrun.com/forum/forum.php?board=1&page=page_num
        payload = {'board': str(1), 'page':page_num-1}
        r = requests.get(url_base, headers=headers, params=payload)
        soup = BeautifulSoup(r.text)
        
        for row_tag in soup.select("li.row"):
            if row_tag.find(class_ = "title ") and row_tag.a['href'].split('=')[1]: 
                title.append(row_tag.select(".post_title")[0].get_text())
                author.append(row_tag.select('.post_author')[0].get_text())
                timestamp_tag = row_tag.select('.timestamp')[0]
                last_post_timestamp = pd.to_datetime(timestamp_tag.get_text())
                last_timestamp.append(last_post_timestamp)   
                
                post_count.append(int(row_tag.select('.post_count')[0].get_text()))
    
                link = row_tag.a['href']
                thread_num.append(link.split('=')[1])  
                
                """
                # retrieve date of original post from first page of thread
                r2 = requests.get(link)
                thread_soup = BeautifulSoup(r2.text)
                orig_post_time_tag = thread_soup.find(class_ = 'timestamp')
                if orig_post_time_tag:
                    first_timestamp.append(pd.to_datetime(orig_post_time_tag.get_text()))
                else:
                    title = "(deleted)" + title
                    first_timestamp.append(last_post_timestamp)
                """
    
    print "...done"
    
    df = pd.DataFrame({ u'Msg #' : thread_num,
#                        u'First post' : first_timestamp,
                        u'Last post': last_timestamp,
                        u'Author' : author,
                        u'Title' : title,
                        u'Count' : post_count})
                
    
    filename = "LRCtopics.csv"
    df.to_csv(filename, encoding='utf-8', index=False ) 

    return df
################

def scrape_thread(thread_num):
    # get page source and create a BeautifulSoup object based on it
    print "Scraping Thread %d Pages..." % thread_num,
    headers = {
        'User-Agent': "nobody",
        'From': 'BarefootEfrem@gmail.com' 
    }
    
    # http://www.letsrun.com/forum/flat_read.php?thread=[thread_num]&page=0
    url_base = "http://www.letsrun.com/forum/flat_read.php"
    page_num = 0
    next_page_url = url_base+"?thread="+str(thread_num)+"&page="+str(page_num)
    
    msg_id = []
    title = []
    author = []
    timestamp = []
    parent = [] 
    msg_text = []
    
    while next_page_url and (next_page_url != "#"):
        print "%d " % page_num,        
        r = requests.get(next_page_url, headers=headers)
        soup = BeautifulSoup(r.text)
        
        msg_id_tags = soup.select("ul.thread > a")
        msg_id.extend([tag.get('name') for tag in msg_id_tags])
        
        title_tags = soup.select("ul > li.subject > span.noskimwords.subject_line")            
        title.extend([tag.get_text() for tag in title_tags])
        
        author_tags = soup.select("ul > li.author_mobile")
        author.extend([tag.get_text().lstrip('\n') for tag in author_tags])
        
        timestamp_tags = soup.select("ul > li.subject > span.timestamp")
        timestamp.extend([pd.to_datetime(x.get_text()) for x in timestamp_tags])
        
        reply_to_tags = soup.select("ul > li.subject > span.in_reply_to > a")
        parent.extend([tag.get('href').split("#")[1] for tag in reply_to_tags])     
        
        text_tags = soup.select("#intelliTXT")
        msg_text.extend([tag.decode_contents() for tag in text_tags]) 
    
        nav_bar = soup.select("nav > ul.pagination")
        if nav_bar:
            next_page_tag = nav_bar[0].find('a', href=True, text=u"\xbb")
            next_page_url = next_page_tag['href']
        else:
            next_page_url = []
            
        page_num += 1
    
       
    msgs = zip(msg_id, parent, title, author, timestamp,  msg_text)
     
    df = pd.DataFrame(msgs, columns=[u'msg #',u'Reply-to',u'Title',u'Author',u'Time',u'Text'])
    
    filename = "LRCthread_%s.csv" % str(thread_num)
    df.to_csv(filename, encoding='utf-8', index=False )
    print "...done"

    return df


# ***** import an LRC thread either from local file (if file exists) or by scraping it from web forum ***
def Thread(thread_num):
    filename = "LRCthread_%d.csv" % thread_num
    if os.path.isfile(filename): 
        df = pd.read_csv(filename)
    else:
        df = scrape_thread(thread_num)
    return df
    



def word_ranking(thread):
    # take a look at Counter modulefor couting words of text.
    words = BeautifulSoup(' '.join(thread.Text)).get_text().split()
    wc = Counter(words)

    ranking = wc.most_common()
    df = pd.DataFrame(ranking,columns=['word', 'count'])
    total_wordcount = df['count'].sum()
    df['percent'] = df['count'] / total_wordcount * 100
    df = df.set_index('word')
    return df







def word_freq(thread_index):
    df_all = pd.DataFrame(columns = thread_index)
    
    for thread_num in thread_index:
        print('\nImporting thread %d...') % thread_num
        thread = Thread(thread_num)
        df = word_ranking(thread)
        df_all[thread_num] = df['percent']    
    return df_all    
   

tl = pd.read_csv('LRCtopics.csv')
popular = (tl.Count > 100) 
print tl[popular][['Msg #','Count']]
thread_index = tl['Msg #'][popular].tolist()
df_all = word_freq(thread_index)
df_all.to_pickle('word_counts.pkl')