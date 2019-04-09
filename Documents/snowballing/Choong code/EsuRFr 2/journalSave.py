# Citation
# journalSave.py
#
# support functions for saving webpages from publishers
#
# miewkeen
# April 2013

from webpageSave import *
import re

def url2websave(url, filenameloc):    
    code = 1
    dxdoi_pattern = 'dx.doi.org/'
    dxdoi_re = re.compile(dxdoi_pattern)
    dxdoi_result = dxdoi_re.search(url)
        
    if dxdoi_result is None:
        code = simplePageSave(url,filenameloc+".html")
    return code
    
def url2parsepdf(url, filenameloc):
    """from url, parse, find pdf link and save as pdf"""
    code = 1
    newlinks = findlink(url)
    if len(newlinks)>1:
            print "multiple links:\n"
            for newlink in newlinks:
                print "\t %s\n" %(newlink)
    if len(newlinks)>0:
        for newlink in newlinks:
            code = url2journalsave(newlink, filenameloc)            
            if code == 0:
                break
        if code == 1:
            #last try
            code = pageWithCookiesSave(newlinks[0],filenameloc+".pdf") #only save the first link
    return code
    
def url2pdf(url,filenameloc): #outputloc):
    """save as pdf from urllink"""
    try:
        remoteFile = urlopen(Request(url)).read()
        memoryFile = StringIO(remoteFile)
        pdfFile = PdfFileReader(memoryFile)

        writer = PdfFileWriter()

        for pageNum in xrange(pdfFile.getNumPages()):
            currentPage = pdfFile.getPage(pageNum)
            writer.addPage(currentPage)
        
        outputStream = open(filenameloc+".pdf","wb")
        writer.write(outputStream)
        outputStream.close()
        print "============ url2pdf: Saving to %s ===============" %(filenameloc+".pdf")
        return 0
    except: #HTTPError, e:
        #return 1
        print "============ url2pdf ==========="
        code = pageWithCookiesSave(url,filenameloc+".pdf")
        return code

def url2journalsave(url, filenameloc):
    code = 1
    code = jstor(url,filenameloc)
    if code == 1:
        code = nejm(url,filenameloc)
    if code == 1:
        code =cochrane(url,filenameloc)
    if code == 1:
        code = oxford(url,filenameloc)
    if code == 1:
        code = springer(url, filenameloc)
    if code == 1:
        code = nature(url, filenameloc)
    if code == 1:
        code = bmj(url,filenameloc)
    if code == 1:
        code = scid(url,filenameloc)

    return code

def jstor(url,filenameloc):
    code = 1
    # ---------- JSTOR (pdf) ----------- #
    #from jstor http://www.jstor.org/stable/xxx to http://www.jstor.org/stable/pdfplus/xxx.pdf
    jstor_pattern = '(?<=www.jstor.org/stable)(.+)'
    jstor_re = re.compile(jstor_pattern)
    jstor_result = jstor_re.search(url)
    
    if jstor_result is not None:
        name = jstor_result.group()
        jstorurl = "http://www.jstor.org/stable/pdfplus/" + name.strip() + ".pdf"
        code = url2pdf(jstorurl, filenameloc+".pdf")
    return code
    
def nejm(url,filenameloc):
    code = 1
    # ---------- NEJM (pdf) ----------- #
    #http://www.nejm.org/doi/full/10.1056/xxx to http://www.nejm.org/doi/pdf/10.1056/xxx
    nejm_pattern = '(.*)(?=(/doi/(abs|full|pdf)/))'
    nejm_re = re.compile(nejm_pattern)
    nejm_result = nejm_re.search(url)
    
    if nejm_result is not None:
        nejm2_pattern = '(?:(?<=/doi/abs/)|(?<=/doi/full/)|(?<=/doi/pdf/))(.*)$'
        nejm2_re = re.compile(nejm2_pattern)
        nejm2_result = nejm2_re.search(url)
        if nejm2_result is not None:
            nejmurl = nejm_result.group() + "/doi/pdf/" + nejm2_result.group()
            code = pageWithCookiesSave(nejmurl,filenameloc+".pdf")
    
    return code
    
def cochrane(url,filenameloc):
    code = 1
    # ---------- COCHRANE (pdf) ----------- #
    wileycochrane_pattern = '(?<=onlinelibrary.wiley.com)(.+)(?=pdf/standard)'
    wileycochrane_re = re.compile(wileycochrane_pattern)
    wileycochrane_result = wileycochrane_re.search(url)
    
    if wileycochrane_result is not None:
        code = pageWithFrame(url,filenameloc+".pdf")
    if code == 1:
        wileycochrane2_pattern = '(?=onlinelibrary.wiley.com)(.+)(?=pdf|abstract|full)'
        wileycochrane2_re = re.compile(wileycochrane2_pattern)
        wileycochrane2_result = wileycochrane2_re.search(url)
        
        if wileycochrane2_result is not None:
            wileycochraneurl2 = "http://" + wileycochrane2_result.group() + "pdf"
            code = pageWithFrame(wileycochraneurl2,filenameloc+".pdf")
    return code
    
def oxford(url,filenameloc):
    code = 1
    # ---------- OXFORDJOURNALS (pdf) ----------- #
    #from http://cid.oxfordjournals.org/content/51/12/1435.short 
    #to http://cid.oxfordjournals.org/content/51/12/1435.full.pdf
    #@#oxford_pattern = '(?<=oxfordjournals.org)(.+)(?=short$)'
    oxford_pattern = '.short$'
    oxford_re = re.compile(oxford_pattern)
    oxford_result = oxford_re.search(url)
    
    if oxford_result is not None:
        oxfordurl = re.sub('short','full.pdf',url)
        code = pageWithCookiesSave(oxfordurl,filenameloc+".pdf")
    
    if code == 1:
        #@#oxford2_pattern = '(?<=oxfordjournals.org)(.+)(?=full$)'
        oxford2_pattern = '.full$'
        oxford2_re = re.compile(oxford2_pattern)
        oxford2_result = oxford2_re.search(url)
        
        if oxford2_result is not None:
            oxfordurl = re.sub('full','full.pdf',url)
            code = pageWithCookiesSave(oxfordurl,filenameloc+".pdf")
    
    if code == 1:
        oxford3_pattern = '.full.pdf\+html$'
        oxford3_re = re.compile(oxford3_pattern)
        oxford3_result = oxford3_re.search(url)
        
        if oxford3_result is not None:
            oxfordurl = re.sub('\+html','',url)
            code = pageWithCookiesSave(oxfordurl,filenameloc+".pdf")
    
    if code == 1:
        oxford4_pattern = '.full.pdf.html$'
        oxford4_re = re.compile(oxford4_pattern)
        oxford4_result = oxford4_re.search(url)
        
        if oxford3_result is not None:
            oxfordurl = re.sub('.html','',url)
            code = pageWithCookiesSave(oxfordurl,filenameloc+".pdf")
            
    return code

def springer(url, filenameloc):
    code = 1
    # ---------- SPRINGERLINK (pdf) ----------- #
    springer_pattern = 'link.springer.com/content/pdf/'
    springer_re = re.compile(springer_pattern)
    springer_result = springer_re.search(url)
    
    if springer_result is not None:
        code = pageWithCookiesSave(url,filenameloc+".pdf")
        
    if code == 1:
        springer2_pattern = '(?<=link.springer.com/article/)(.+)$'
        springer2_re = re.compile(springer2_pattern)
        springer2_result = springer2_re.search(url)
        if springer2_result is not None:
            name = springer2_result.group()
            springerurl = 'http://link.springer.com/content/pdf/' + name
            code = pageWithCookiesSave(springerurl,filenameloc+".pdf")
            
    return code
    
def nature(url, filenameloc):
    code = 1
    # ---------- NATURE (pdf) ----------- #
    nature_pattern = 'http://www.nature.com/(.*)(/(full|abs)/)(.*).html$'
    nature_re = re.compile(nature_pattern)
    nature_result = nature_re.search(url)
    
    if nature_result is not None:
        natureurl1 = re.sub('full|abs','pdf',url)
        natureurl = re.sub('.html','.pdf',natureurl1)
        code = pageWithCookiesSave(natureurl,filenameloc+".pdf")

    return code

def bmj (url, filenameloc):
    code = 1
    # ---------- BMJ (pdf) ----------- #
    bmj_pattern = 'www.bmj.com'
    bmj_re = re.compile(bmj_pattern)
    bmj_result = bmj_re.search(url)    
    if bmj_result is not None:
        code = bmjhighwire(url,filenameloc)
    return code
    
def scid(url, filenameloc):
    code = 1
    # ---------- SCIENCEDIRECT (html) ----------- #
    scid_pattern = 'www.sciencedirect.com'
    scid_re = re.compile(scid_pattern)
    scid_result = scid_re.search(url)    
    if scid_result is not None:            
        import urlparse
        import urllib2
        from BeautifulSoup import BeautifulSoup
        UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
        try:
            req = urllib2.Request(url, headers={'User-Agent': UA})
            r = urllib2.urlopen(req)
            html = r.read()
            r.close()
            soup = BeautifulSoup(html, convertEntities="html")
            for a in soup.findAll('a',href=True):
                if a.get('id') == "pdfLink":
                    newlink = a['href']
                    code = url2pdf(newlink,filenameloc)
                    if code == 1:
                        code = savewithBrowser(newlink,filenameloc+".pdf")
        except:
            code = pageWithJSSave(url,filenameloc+".html")
                
    return code
    
if __name__ == "__main__":
    sys.exit()
