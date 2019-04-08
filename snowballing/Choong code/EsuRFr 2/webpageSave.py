# Citation expansion
# webpageSave.py
#
# support functions for saving webpages
#
# miewkeen
# April 2013

import codecs
import re

#===================
import sys  
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
  
class Render(QWebPage):  
    def __init__(self, url):  
        self.app = QApplication(sys.argv)  
        QWebPage.__init__(self)  
        self.loadFinished.connect(self._loadFinished)  
        self.mainFrame().load(QUrl(url))  
        self.app.exec_()  
        self.wait
    def _loadFinished(self, result):  
        self.frame = self.mainFrame()  
        self.app.quit()    
    def wait(self, secs=100):
        deadline = time.time() + secs
        while time.time() < deadline:
            time.sleep(0.1)
        self.app.processEvents()

def pageWithJSSave(url,filepath):
    """ save webpages with javascript (e.g sciencedirect)"""
    r = Render(url)  
    content = r.frame.toHtml()  
    print "============ pageWithJSSave: Saving to %s ===============" %filepath
    try:
        f=codecs.open(filepath,"w","utf=8")
        f.write(content)
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        f=codecs.open(filepath,"w")
        f.write(content)
    f.close()
    return 0

#=====================

def pageWithCookiesSave(url,filepath):
    """ save webpages which needs cookies (e.g. NEJM)"""
    import urllib2
    import urllib
    from cookielib import CookieJar

    try:
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        response = opener.open(url)
        content = response.read()
        print "============ pageWithCookiesSave: Saving to %s ===============" %filepath
        try:
            f = codecs.open(filepath,"wb","utf=8")
            f.write(content)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            f = codecs.open(filepath,"wb")
            f.write(content)
        f.close()
        return 0
    except:
        return 1

#=====================

def pageWithFrame(url,filepath):
    """save webpages which use frames (e.g. onlinewiley for cochrane)"""
    from BeautifulSoup import BeautifulSoup
    import urllib2
    #UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
    try:
        req = urllib2.Request(url) #req=urllib2.Request(url, headers={'User-Agent': UA})
        hdl = urllib2.urlopen(req)
        html=hdl.read()
        hdl.close()
        soup = BeautifulSoup(html, convertEntities="html")        
        for tag in soup:
            if not hasattr(tag,'iframe'):
                continue
            if tag.iframe.get('id') == 'pdfDocument':
                newurl = tag.iframe.get('src')            
        code = 1
        if newurl is not None:
            code = pageWithCookiesSave(newurl,filepath)
        return code    
    except:
        return 1
        
#=====================

def simplePageSave(url,filepath):
    """from url save as html"""
    import urlparse
    import urllib2
    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
    try:
        req = urllib2.Request(url, headers={'User-Agent': UA})
        r = urllib2.urlopen(req)
        content = r.read()
        print "============ simplePageSave: Saving to %s ===============" %filepath
        try:
            f=codecs.open(filepath,"w","utf=8")
            f.write(content)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            f=codecs.open(filepath,"w")
            f.write(content)
        return 0
    except:
        return 1
        
#=====================
def sorted_ls(path):
    import os    
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))
    
def savewithBrowser(url,filepath):
    """save using mozilla browser with selenium"""
    from selenium import webdriver
    import time
    import os
    sfpath = os.path.dirname(filepath) #get the file directory
    #sfname = os.path.basename(filepath) #get the savename
    try:
        profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', ('application/pdf'))
        profile.set_preference('browser.download.dir', sfpath)
        profile.set_preference("browser.download.folderList",2)
        browser = webdriver.Firefox(firefox_profile=profile)    
        print "============ savewithBrowser: Saving to %s ===============" %filepath
        #browser = webdriver.Firefox() # Get local session of firefox
        browser.get(url)
        time.sleep(0.5)
        browser.close()
        result = sorted_ls(sfpath)   ###BEWARE: This is assumed that is successfully downloaded
        os.rename(sfpath+"/"+result[-1],filepath)#os.rename(result[-1],sfname) ###BEWARE
        return 0    
    except:
        return 1


#=====================

def savewklinkBrowser(url,filepath):
    from selenium import webdriver
    import time
    profile = webdriver.firefox.firefox_profile.FirefoxProfile()
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', ('application/pdf'))
    profile.set_preference('browser.download.dir', filepath)
    profile.set_preference("browser.download.folderList",2)
    profile.native_events_allowed=True
    browser = webdriver.Firefox(firefox_profile=profile)
    browser.get(wklink)
    link=browser.find_element_by_id("site-right")
    action=webdriver.ActionChains(browser).move_to_element(link).perform()

    action.click()
    action.perform()
    return

#=====================

def getDirectedURL(url):
    """ get directed url"""
    import urllib2, urllib
    from cookielib import CookieJar

    try:
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        response = opener.open(url)
        return response.url
    except:
        return url
        
#=====================

def pdfhtml2pdf(url):
    import re
    newurl = url
    pdfhtml_pattern = '.full.pdf+html$'
    pdfhtml_re = re.compile(pdfhtml_pattern)
    pdfhtml_result = pdfhtml_re.search(url)
        
    if pdfhtml_result is not None:
        newurl = re.sub('+html','',url)
    return newurl

#=====================

def findlink(url):
    """Try to find the full text link to pdf"""
    import urlparse
    import urllib2
    import re
    from BeautifulSoup import BeautifulSoup
    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
    fulltextlink = []
    try:
        req = urllib2.Request(url, headers={'User-Agent': UA})
        r = urllib2.urlopen(req)
        html = r.read()
        r.close()
        soup = BeautifulSoup(html, convertEntities="html")

        for a in soup.findAll('a',href=True):
            if a.get('title')=="View PDF" or a.get('title')=="Download PDF":
                linkUrl = pdfhtml2pdf(a['href'])
                if urlparse.urlsplit(linkUrl).scheme == '':
                    linkUrl = urlparse.urljoin(url,linkUrl)
                fulltextlink.append(linkUrl)
            if a.get('class')=="linkPDF":
                linkUrl = pdfhtml2pdf(a['href'])
                if urlparse.urlsplit(linkUrl).scheme == '':
                    linkUrl = urlparse.urljoin(url,linkUrl)
                fulltextlink.append(linkUrl)
            if a.get('rel') == "view-full-text.pdf":
                linkUrl = pdfhtml2pdf(a['href'])
                if urlparse.urlsplit(linkUrl).scheme == '':
                    linkUrl = urlparse.urljoin(url,linkUrl)
                fulltextlink.append(linkUrl)
            if a.string == "Full Text (PDF)" or a.string == "Download-PDF":
                linkUrl = pdfhtml2pdf(a['href'])
                if urlparse.urlsplit(linkUrl).scheme == '':
                    linkUrl = urlparse.urljoin(url,linkUrl)
                fulltextlink.append(linkUrl)
                        
    except:
        pass
    
    return fulltextlink

#=====================
#/highwire/filestream/172962/field_highwire_article_pdf/0/18.full.pdf    

def bmjhighwire(url,filepath):    
    code = 1
    
    import urlparse
    import urllib2
    import re
    from BeautifulSoup import BeautifulSoup
    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'        
    highwire_pattern = '/highwire/filestream/(.*).full.pdf$'
    highwire_re = re.compile(highwire_pattern)
    try:
        req = urllib2.Request(url, headers={'User-Agent': UA})
        r = urllib2.urlopen(req)
        html = r.read()
        r.close()
        soup = BeautifulSoup(html, convertEntities="html")
        links = []
        for a in soup.findAll('a',href=True):
            links.append(a['href'])
        for link in links:
            highwire_result = highwire_re.search(link)        
            if highwire_result is not None:
                code = pageWithCookiesSave(link,filepath)
                break
    except:
        pass
    return code

#=====================
from os.path import basename
from urlparse import urlsplit

def url2name(url):
    return basename(urlsplit(url)[2])

def download(url, localFileName = None):
    localName = url2name(url)
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    if r.info().has_key('Content-Disposition'):
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url: 
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)
    if localFileName: 
        # we can force to save the file as specified name
        localName = localFileName
    f = open(localName, 'wb')
    f.write(r.read())
    f.close()

#=====================
