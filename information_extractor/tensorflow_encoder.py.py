import tensorflow_hub as hub
import numpy as np
import tensorflow
import os
import gensim
from gensim.parsing.preprocessing import remove_stopwords
from gensim.parsing.preprocessing import strip_punctuation
from gensim.parsing.preprocessing import strip_multiple_whitespaces
#from gensim.parsing.preprocessing import stem_text
from operator import itemgetter
#import sqlite3
import pandas as pd
import time
from sklearn import preprocessing
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import random,time
import itertools
import requests
from io  import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import mysql.connector
#import urllib.request as urllib2
import ssl
import re
import spacy
#python -m spacy download en_core_web_lg
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class Article_matcher():
    def __init__(self,module_url):
        self.cooperate_action_code,self.cooperate_action_list=self.initialize_CA_vars()
        self.embed=self.load_universal_encoder(module_url)
        self.connect_database()
        
    def __del__(self):
        self.mycursor.close()
        self.mydb.close()

    def initialize_CA_vars(self):
        cooperate_action_code=["ANN","ARR" ,"ASSM" ,"BB" 	,"BKRP" ,"BON" ,"BR" ,
                                "CAPRD" 	,"AGM" 	,"CONSD" 	,"CONV" 	,"CTX" 	,
                                "CURRD","DIST" 	,"DIV" 	, "DMRGR ","DRIP" ,"DVST" ,"ENT" 	,"FRANK" ,"FTT" 	,"FYCHG" ,                           
                                "INCHG" ,"ISCHG" ,"LAWST","LCC" ,"LIQ" 	,"LSTAT" ,"LTCHG" ,"MKCHG" ,"MRGR" 	,"NLIST" ,
                                "ODDLT","PID" ,"PO" ,"PRCHG" ,"PRF" ,"PVRD" 	,"RCAP"  ,"REDEM" ,	"RTS" ,"SCCHG" ,"SCSWP" ,
                                "SD" ,"SECRC" ,"TKOVR","IPO"]

        cooperate_action_list=[ "Acquisition","Announcement","Arrangement","Assimilation","Buy Back","Bankruptcy","Bonus","Bonus Issue","Bonus Rights",
                                    "Cash Dividend","Class Action","Conversion of convertible bonds","Coupon Payment","Delisting","Dutch Auction",
                                    "Early Redemption","Final Redemption","General Announcement","Initial Public Offering","Lottery",
                                    "Name Change","Odd lot Tender","Optional Dividend","Optional Put","Other Event","Partial Redemption",
                                    "Par Value Change","Reverse Stock Split","Rights Auction","Rights Issue","Scheme of Arrangement",
                                    "Scrip Dividend","Scrip Issue","Spin-Off","Spin Off","Stock Dividend","Subscription Offer","Tender Offer",
                                    "Warrant Exercise","Warrant Expiry","Warrant Issue",
                                        "Capital Reduction",
                                        "Company Meeting","board meeting"
                                        "Consolidation" ,"stock split",
                                        "Conversion",
                                        "Certificate Exchange",
                                        "Currency Redenomination",
                                        "Distribution",
                                        "Dividend",
                                        "Demerger",
                                        "Dividend Reinvestment Plan",
                                        "Divestment",
                                        "Entitlements",
                                        "Franking",
                                        "Financial Transaction Tax",
                                        "Financial Year Change",
                                        "International Code Change",
                                        "Incorporation Change",
                                        "Issuer Name Change",
                                        "Lawsuit",
                                        "Local Code Change",
                                        "Liquidation",
                                        "Listing Status Change",
                                        "Lot Change",
                                        "Market Segment Change",
                                        "Merger",
                                        "New Listing",
                                        "Odd Lot Offer",
                                        "Property Income Distribution",
                                        "Purchase Offer",
                                        "Primary Exchange Change",
                                        "Preferential Offer",
                                        "Parvalue Redenomination",
                                        "Return of Capital",
                                        "Preference Redemption",
                                        "Rights",
                                        "Security Description Change",
                                        "Security Swap",
                                        "Subdivision",
                                        "Security Reclassification",
                                        "Takeover","Equity"]

        return cooperate_action_code,cooperate_action_list

            
    def load_universal_encoder(self,module_url):
        print("--------------------------------loading_model------------------------------------------")
        embed = hub.Module(module_url)
        print("model loaded")
        return embed


    
    def connect_database(self):
        self.mydb = mysql.connector.connect(host='database-1.chm9rhozwggi.us-east-1.rds.amazonaws.com',
                                         database='pythanos_main',
                                         user='admin',
                                         password='SIH_2020')

        self.mycursor = self.mydb.cursor()
     
        
    def get_articles(self):
        #self.mycursor.execute("SELECT id,url,content,ranks FROM articles where news_checked is NULL and content is not NULL")
        self.mycursor.execute("SELECT id,url,content,ranks,company_name FROM articles where news_checked is NULL and content is not NULL")
        articles_database = pd.DataFrame(self.mycursor.fetchall(),columns=["id","url","content","ranks","company_name"])
        self.mycursor.execute("UPDATE articles set news_checked=0 where news_checked is NULL")
        self.mydb.commit()
        
        return articles_database

    def update_articles_table(self,articles_database):
        print("updating database")
        for action,url,matches in zip(articles_database["action"].tolist(),articles_database["url"].tolist(),articles_database["matches"].tolist()):
         #   print("updating database")
            a=(matches,action,url)
            self.mycursor.execute("UPDATE articles set news_checked=%s,ca_name=%s WHERE news_checked=0 and url=%s",a)
        #self.mycursor.execute("UPDATE crawler_2 set ca_checked=1 where ca_checked=0")
        self.mydb.commit()
        print("database updated")

    def clean_database(self,articles_database):
        articles_database=articles_database.iloc[articles_database['content'].notna().tolist()]
        
        articles_database=articles_database.iloc[articles_database['content'].notnull().tolist()]
        
        articles_database=articles_database.drop(articles_database[articles_database['content'] == ''].index)
        
        articles_database=articles_database[~articles_database['content'].duplicated()]
        
        articles_database['content']=articles_database['content'].str.lower()
        
        articles_database["present"]=False
        articles_database["action"]="" 
        
        return articles_database

    def cooperate_actions_lists_and_code(self,cooperate_action_list,cooperate_action_code):
        
        cooperate_action_list=[x.lower() for x in cooperate_action_list]
        
        cooperate_action_code=[x.lower() for x in cooperate_action_code]
        
        cooperate_action=pd.DataFrame(cooperate_action_list,columns=['CA'])
        
        cooperate_action["CA"]=cooperate_action["CA"].str.lower()
        
        return cooperate_action,cooperate_action_code


    

    def find_actions(self,articles_database,cooperate_action,cooperate_action_code):
        articles_database["action"]="" 
        articles_database["content"]=articles_database["content"].map(str)

        for i in cooperate_action["CA"]:
 
            articles_database["present"]=articles_database["present"] | articles_database["content"].str.contains(i, case=False)
            
            articles_database.loc[articles_database["content"].str.contains(i, case=False),["action"]]+=","+i
            
        articles_database.reset_index(inplace = True)

        for i in cooperate_action_code:
            for num,sentence in enumerate(articles_database["content"]):
                if i in list(gensim.utils.tokenize(sentence)):
                    articles_database.loc[num,['present']]=True
                    articles_database.loc[num,['action']]+=","+i
        
        articles_database=articles_database.loc[articles_database["present"]]
        articles_database=articles_database.loc[articles_database["company_name"].str.len()>0]
        articles_database=articles_database.loc[articles_database["action"].str.len()>0]
        #articles_database["company_name"] = articles_database["company_name"].str[1:]
        return articles_database

   

    def remove_stopwords_from_database(self,articles_database):
        links=articles_database['url'].tolist()
        messages=articles_database['content'].tolist()
        CA_names=articles_database['action'].tolist()
        stop_words_removed=[]

        for message in messages:
            message = strip_punctuation(message)
            #message=stem_text(message)
            message = strip_multiple_whitespaces(message)
            stop_words_removed.append(remove_stopwords(message))
        return links,stop_words_removed,CA_names



    def run_universal_encoder(self,stop_words_removed):
        similarity_input_placeholder = tensorflow.placeholder(tensorflow.string, shape=(None))
        similarity_message_encodings = self.embed(similarity_input_placeholder)
        corr=None
        message_embeddings_=None

        chunks = [stop_words_removed[x:x+1000] for x in range(0, len(stop_words_removed), 1000)]

        with tensorflow.Session() as session:
            session.run(tensorflow.global_variables_initializer())
            session.run(tensorflow.tables_initializer())

            for sentences in chunks:
                if message_embeddings_ is None :
                    message_embeddings_ = session.run(similarity_message_encodings, feed_dict={similarity_input_placeholder: sentences})
                else :
                    message_embeddings_=np.append(message_embeddings_,session.run(similarity_message_encodings, feed_dict={similarity_input_placeholder: sentences}),axis=0)
            message_embeddings_ = preprocessing.normalize(message_embeddings_, norm='l2')          
            corr = np.inner(message_embeddings_, message_embeddings_)
        return corr
    
    def check_matching_count_of_articles(self,articles_database,corr,stop_words_removed,links,threshold=0.92):
        already_checked=[]
        articles_database["matches"]=0
        for i in range(len(stop_words_removed)):
                if len(np.where(corr[i]>threshold)[0].tolist())>1:
                    for n,m in zip(np.where(corr[i]>threshold)[0].tolist(),itemgetter(*np.where(corr[i]>threshold)[0].tolist())(stop_words_removed)):
                        print(n,np.where(corr[i]>threshold)[0].tolist())
                        articles_database.loc[articles_database.url.str.contains(links[n],case=False),"matches"]=len(np.where(corr[i]>threshold)[0].tolist()) 
                else:
                    n=np.where(corr[i]>threshold)[0].tolist()[0]
                    articles_database.loc[articles_database.url.str.contains(links[n],case=False),"matches"]=1                    
        print("----------------")
        print(articles_database.loc[articles_database['matches'] > 0 ])
        return articles_database


    
    def run_article_matching(self):
        
        #articles_database=self.load_database(["tenderfoot","tenderfoot_three"])
        articles_database=self.get_articles()
        if len(articles_database)==0:
            print("no articles found")
            return
        articles_database=self.clean_database(articles_database)
        cooperate_action_code,cooperate_action_list=self.initialize_CA_vars()
        cooperate_action,cooperate_action_code=self.cooperate_actions_lists_and_code(self.cooperate_action_list,self.cooperate_action_code)
        articles_database=self.find_actions(articles_database,cooperate_action,cooperate_action_code)
        links,stop_words_removed,CA_names=self.remove_stopwords_from_database(articles_database)
        corr=self.run_universal_encoder(stop_words_removed)
        articles_database=self.check_matching_count_of_articles(articles_database,corr,stop_words_removed,links,threshold=0.92)
        self.update_articles_table(articles_database)
        return articles_database
    
        
    
   

    def fuzzy_logic(self):
        quality = ctrl.Antecedent(np.arange(0, 100, 1), 'suraj')
        service = ctrl.Antecedent(np.arange(0, 100, 1), 'abhijit')
        prev_score =  ctrl.Antecedent(np.arange(0, 100, 1), 'prev_score')
        score = ctrl.Consequent(np.arange(0, 100, 0.1), 'score')

        quality.automf(3)
        service.automf(3)
        prev_score.automf(3)
        
        # Triangle
        score['low'] = fuzz.trimf(score.universe, [0, 0, 25])
        score['medium'] = fuzz.trimf(score.universe, [25, 37.5, 50])
        score['fairly-medium'] = fuzz.trimf(score.universe, [ 50, 62.5,75])
        score['high'] = fuzz.trimf(score.universe, [75,100, 100])

        rule1 = ctrl.Rule(quality['poor'] | service['poor'] | prev_score['poor'] , score['low'])
        rule2 = ctrl.Rule(service['average'] | prev_score['average'] | quality['average'], score['medium'])
        rule3 = ctrl.Rule(service['poor'] | prev_score['average'] | quality['average'], score['fairly-medium'])
        rule4 = ctrl.Rule(service['good'] | quality['good'] | prev_score['good'], score['high'])

        self.scoring_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])

    def calc(self,quality,service,prev_score):
        scoring = ctrl.ControlSystemSimulation(self.scoring_ctrl)

        scoring.input['suraj'] = quality
        scoring.input['abhijit'] = service
        scoring.input['prev_score'] = prev_score
        scoring.compute()

        print (scoring.output['score'])


     def run_pdf_data_extraction(self):
        pdf_data=self.read_pdfs()
        if pdf_data is None:
            print("no pdf")
            return 
        cooperate_action,cooperate_action_code=self.cooperate_actions_lists_and_code(self.cooperate_action_list,self.cooperate_action_code)
        pdf_data=self.find_actions(pdf_data,cooperate_action,cooperate_action_code)
        self.update_pdf_database(pdf_data)
        
        """
        print(pdf_data)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for present,action,content in zip(pdf_data["present"],pdf_data["action"],pdf_data['content']):
            print(content)
            print("\n ---------------------------------------")
            if present:
                print("action found : "+ action+ "\n"+"content:\n"+content+"\n-----------------------------")
        """


    
    def update_pdf_database(self,pdf_data):

        for i,j in zip(pdf_data["action"].tolist(),pdf_data["url"].tolist()):
            a=(i,j)
            print(a)
            self.mycursor.execute("UPDATE crawler_2 set ca_type=%s WHERE file_url=%s",a)
        self.mycursor.execute("UPDATE crawler_2 set ca_checked=1 where ca_checked=0")
        self.mydb.commit()


    


    def read_pdfs(self):
        #context = ssl._create_unverified_context()
        pdf_links=self.get_pdf_links()
        if len(pdf_links)==0:
            print("no links")
            return 
        pdf_data= pd.DataFrame()
        pdf_data["content"]=""
        pdf_data["present"]=""
        pdf_data["action"]=""
        pdf_data["url"]=""
        print(len(pdf_links))
        for link in pdf_links:
            try:
            #pdf= urllib2.urlopen(link,context=context)
                r = requests.get(link,verify=False,stream=True,timeout=(5,20))
                with open('data.pdf', 'wb') as fd:
                    for chunk in r.iter_content(2000):
                        fd.write(chunk)
                print(link)
                pdf=self.pdf_to_text("data.pdf")
                pdf_data=pdf_data.append({"content":strip_multiple_whitespaces(pdf),"url":link},ignore_index=True)
                print("------------------------------")
                self.mycursor.execute("UPDATE crawler_2 set ca_checked=0 WHERE file_url=%s",(link,))
            except:
                self.mycursor.execute("UPDATE crawler_2 set url_error=1 WHERE file_url=%s",(link,))
                print("couldn't download from "+link)

            self.mydb.commit()
        return pdf_data  


    def pdf_to_text(self,path):
        pagenums = set()
        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)
        infile = open(path, 'rb')
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
        infile.close()
        converter.close()
        text = output.getvalue()
        output.close

        return text



    def get_pdf_links(self):
        self.mycursor.execute("SELECT file_url FROM crawler_2 where url_error=0 and ca_checked is NULL limit 100")
        pdf_links = pd.DataFrame(self.mycursor.fetchall())
        #self.mydb.commit()
        if len(pdf_links)==0:
            return []
        pdf_links=pdf_links[0].tolist()
        print("pdf links:",len(pdf_links))
        return pdf_links


        

if __name__ == "__main__":
    start=time.time()
    while True:
        try:
            matcher=Article_matcher("https://tfhub.dev/google/universal-sentence-encoder/1?tf-hub-format=compressed")
            break
        except :
            time.sleep(5)
            continue
    print("database_connected")   
    while True:
        articles_database=matcher.run_article_matching()
        print(time.time()-start)
        start=time.time()
    