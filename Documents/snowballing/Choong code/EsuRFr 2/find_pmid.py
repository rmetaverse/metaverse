# module: citation
# find_pmid.py
# find pmid or PMCid from a list of urls
#
# February 2013
# miewkeen
#


import string
import re
import sys


def refineID(ID):
    refine_pattern = '(.+?)(?=%20)'
    refine_re = re.compile(refine_pattern)
    result = refine_re.search(ID)
    refinedID = ID
    if result is not None:
        refinedID = result.group()
    return refinedID

def pmid_find(url):
    pmid = ''
    pmid_pattern = '(?<=http://www.ncbi.nlm.nih.gov/pubmed/)(.+?)$'
    pmid_re = re.compile(pmid_pattern)
    result = pmid_re.search(url)
    if result is not None:
        pmid = re.sub('/','',result.group())
        pmid = refineID(pmid)
    return pmid
                
def pmcid_find(url):
    pmcid = ''
    pmcid_pattern = '(?<=http://www.ncbi.nlm.nih.gov/pmc/articles/)(.+?)$'
    pmcid_pattern2 = '(?<=https://www.pubmedcentral.nih.gov/pmc/articles/)(.+?)$'
    pmcid_re = re.compile(pmcid_pattern)
    pmcid_re2 = re.compile(pmcid_pattern2)
    
    result = pmcid_re.search(url)
    if result is not None:
        pmcid = re.sub('/','',result.group())
    else:
        result2 = pmcid_re2.search(url)
        if result2 is not None:
            pmcid = re.sub('/','',result2.group())
    pmcid = refineID(pmcid)
    return pmcid

def findIDs(urls):
    """find pmid and pmcid given a list of urls"""
    pmidflag = False
    pmcidflag = False
    pmidresult = ''
    pmcidresult = ''
    for url in urls:
        #print url
        if not pmidflag:
            result1 = pmid_find(url)
            if len(result1)>0:
                pmidresult = result1
                pmidflag = True
           
        if not pmcidflag:
            result2 = pmcid_find(url)
            if len(result2)>0:
                pmcidresult = result2
                pmcidflag = True

    return [pmidresult, pmcidresult]
   
def findIDsAll(urls):
    """find pmid and pmcid given a list of urls"""
    pmidresult = []
    pmcidresult = []
    for url in urls:
        result1 = pmid_find(url)
        if len(result1)>0:
            pmidresult.append(result1)                
        result2 = pmcid_find(url)
        if len(result2)>0:
            pmcidresult.append(result2)
    return [list(set(pmidresult)), list(set(pmcidresult))]
    
if __name__ == "__main__":
    
    sys.exit(0)
