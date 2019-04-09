# esurfr.py
# Evidence Discovery using Microsoft Academic Search (MAS)
#
# extract list
# search MAS
# retrieve from results
# download full text
#
# miewkeen
# 2012-2014

import sys, os, getopt
import csv
import re
from random import randint
from time import sleep
import string

import util
import preprocess_string

import api
from config import APP_ID


query = {"FulltextQuery":'', "ResultObjects":"Publication", "PublicationContent":"AllInfo", "StartIdx":"1", "EndIdx":"30"}

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)
                
def GSqueryparam(url, number):
    """pass extra parameter = num which set the results per page"""
    insert = '?num=' + str(number) + '&'
    newurl = re.sub(r'\?',insert,url)
    return newurl
    
def usage():
    print "esurfr"
    print "Usage: preprocessString.py  [options...] string"
    print "    -c, --character=NUMBER           no of character to remove (default: 4)"
    print "    -g, --page=NUMBER                no of result per page (default: 20)"
    print "    -n, --numeric=yes/no             remove numeric (default: yes)"
    print "    -p, --preprocess=yes/no          Preprocess: Yes (default: yes)"
    print "    -i, --input_path=PATH            Path for Input files (default: ./input)"
    print "    -o, --output_path=PATH           Path for Output(or result) files (default: ./output)"
    print "    -r, --result=FILE                Result file (default: ./output/referencesdataMAS.csv)"
    print "    -a, --audit=FILE                 Audit file (default: ./output/doneMAS.txt)"
    print "    -h/--help                        This help text"
    sys.exit(2) 


if __name__ == "__main__":
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:g:n:p:i:o:r:a:vh", 
            ["character=", "page=", "numeric=", "preprocess=", "input_path=", "output_path=", "result=", "audit", "verbose", "help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()

    character = 4
    itemperpage = 20
    numeric = "yes"
    preprocess = True
    inputpath = "./input/"
    outputpath = "./output/"
    outputfile = "./output/referencesdataMAS.csv"
    donefile = "./output/doneMAS.txt"

    
    verbose = False 
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
        elif o in ("-c", "--character"):
            character = a        
        elif o in ("-g", "--page"):
            itemperpage = a
        elif o in ("-n", "--numeric"):
            numeric = a
        elif o in ("-p", "--preprocess"):
            preprocess = a
        elif o in ("-i", "--input_path"):
            inputpath = a
        elif o in ("-o", "--output_path"):
            outputpath = a
        elif o in ("-r", "--result"):
            outputfile = a
        elif o in ("-a", "--audit"):
            outputfile = a
        else:
            assert False, "unhandled option"

    #if len(args) < 1:
    #    usage()


    # Get the list of citations that have been done
    orilist = open(donefile).readlines()
    donelist = open(donefile).read().splitlines() #list of citations done
    
    fdone = open(donefile,"w")
    fdone.writelines(orilist) #write a sequence of strings to a file
    #------------------------------------------------------------------#
    
    # from pdf in folder, get references
    from os import listdir
    from os.path import isfile, join
    allfiles = [ f for f in listdir(inputpath) if isfile(join(inputpath,f)) ]
    
    ofile  = open(outputfile, "wb")
    writer = csv.writer(ofile, delimiter=',')
    
    # search GS and get pmid/pmcid from GS
    for afile in allfiles:        
        filename = afile.split('.')[0].split('_')[0] #[2] use numbers instead of PMID as ref
        filetype = afile.split('.')[-1]
        
        if filename not in donelist:
            #donelist.append(filename) #move to the end
            
            reflist = util.extract_references_refext2(inputpath+afile, filetype) #extract_references2#extract_references_parscitori2#extract_references_toci_txt2
            # reflist is in unicode
            print "======================================"
            print "Extracted references from %s" %filename
            
            if reflist is not None:
                #======== create folder ========#
                outputpathloc = outputpath + filename + "/"
                ensure_dir(outputpathloc)                
                
                #======== preprocess ========#
                reflistori = reflist
                if preprocess:        
                    newreflist = []
                    for r in reflist:
                        newreflist.append(preprocess_string.processing(r,character,numeric))
                    reflist = newreflist
                    print "======================================"
                    print "Preprocessed strings"
                    sys.stdout.flush()
                
                refcount = 0
                for (index, r) in enumerate(reflist):
                    if len(r) > 0:
                        refcount += 1
                        print "======================================"
                        print "Search string: [%s]" % r.encode('utf-8')        
                        if len(string.split(r))<100:                            
                            #articles = scholar_singleton.txt(r, '', 10)      
                            query['FulltextQuery'] = r
                            try:
                                mas = api.MAS(APP_ID)
                                resp = mas.request(query)
                            except Exception, e:
                                print e
                                sleep(60) #wait for one minute
                                mas = api.MAS(APP_ID)
                                resp = mas.request(query)
                        else:    
                            print "Truncated search string"
                            query['FulltextQuery'] = ' ' .join(string.split(r)[0:100])
                            try:
                                mas = api.MAS(APP_ID)
                                resp = mas.request(query)
                            except Exception, e:
                                print e
                                sleep(60) #wait for one minute
                                mas = api.MAS(APP_ID)
                                resp = mas.request(query)
                        ###$$$EXTRA$$$###                    
                        #*MAS*#
                        articles = []
                        if resp['Result'] is not None:
                            for masres in resp['Result']:
                                articles.append(masres['Title'])
                            
                            result, idx = util.find_bestMAS(r, articles, preprocess, character, numeric) #*MAS*# need to change the type in find_best for "Articles"
                        else:
                            result = []
                    
                        if len(result) == 0:
                            #search gscholar using only first 10 (preprocessed) words                                
                            if len(string.split(r))>8:
                                print "=====second search===="
                                #*MAS*#sleep(randint(15,35))
                                #*MAS*#articles = scholar_singleton.txt(' ' .join(string.split(r)[0:8]), '', 10)
                                query['FulltextQuery'] = ' ' .join(string.split(r)[0:8])
                                try:
                                    mas = api.MAS(APP_ID)
                                    resp = mas.request(query)
                                except Exception, e:
                                    print e
                                    sleep(60) #wait for one minute
                                    mas = api.MAS(APP_ID)
                                    resp = mas.request(query)
                                articles = []
                                if resp['Result'] is not None:
                                    for masres in resp['Result']:
                                        articles.append(masres['Title'])
                                    result, idx = util.find_bestMAS(r, articles, preprocess, character, numeric) #*MAS*#need to change
                                else:
                                    result = []
                                    
                        if len(result)!= 0:                            
                            # ======== Bibtex info ======== #
                            #"@article","title","author","journal","volume","number","pages","year","publisher"
                            title = resp['Result'][idx]['Title']
                            doi = resp['Result'][idx]['DOI']
                            authors = []
                            for aut in resp['Result'][idx]['Author']:                                
                                authors.append([aut['FirstName'], aut['MiddleName'], aut['LastName']])
                            if resp['Result'][idx]['Journal'] is not None:
                                journal = resp['Result'][idx]['Journal']['FullName']
                            else:
                                journal = ''
                            year = resp['Result'][idx]['Year']
                            link = resp['Result'][idx]['FullVersionURL']
                            
                            '''
                            # ======== search pubmed ======== #
                            rJT = [] #journal title
                            rDP = [] #date of publication
                            rTI = [] #title
                            rAU = [] #author
                            rSO = [] #citation info
                            rPMID = [] #pmid
                            #*MAS*#                            
                            if len(doi) > 0:
                                print "Searching pubmed with doi: %s" %doi
                                record = pubmed.searchparse(doi, 1) # search pubmed with search_term and get the records"
                                if record is not None:
                                    for rcd in record:
                                        # get the citation info
                                        rJT = (rcd.get("JT","?"))
                                        rDP = (rcd.get("DP","?"))
                                        rTI = (rcd.get("TI","?"))
                                        rAU = (rcd.get("AU","?"))
                                        rSO = (rcd.get("SO","?"))
                                        rPMID = (rcd.get("PMID","?"))
                                else:
                                    print "Can't find pubmed using doi"
                            else:
                                print "NOT found pubmedID : %s" %reflistori[index].encode('utf-8')
                            '''
                            # ======== find and save fulltext ========#    
                            savename = refcount #if len(rPMID) == 0 else rPMID
                            print "====savename = %s" %savename
                            outputpathlocname = outputpathloc + str(savename)
                            from fulltextsave import fulltextsaveMAS
                            returnkey = fulltextsaveMAS(link, outputpathlocname) 
                            
                            #returnkey is False if no fulltext is saved
                            #returnkey is True if fulltext is saved
                            
                            # ======== save results ========#
                            # save the results
                            results = list()
                            results.append(filename)
                            results.append(reflistori[index].encode('utf-8'))
                            results.append(doi)
                            results.append(title.encode('utf-8'))
                            results.append(authors)
                            results.append(journal.encode('utf-8'))
                            results.append(year)
                            results.append(link)
                            #results.append(rPMID)
                            #results.append(rTI)
                            #results.append(rAU)
                            #results.append(rJT)
                            #results.append(rDP)
                            #results.append(rSO)
                            writer.writerow(results)
                            
                            
                        else:
                            print "NOT found in MAS %s" % reflistori[index].encode('utf-8')
                            results = list()
                            results.append(filename)
                            results.append(reflistori[index].encode('utf-8'))
                            results.append("NOT found in MAS")
                            writer.writerow(results)
                               
                        sys.stdout.flush()
                        #*MAS*#sleep(randint(10,50))
                
                print "Total references found for %s = %s" %(filename, refcount)
                
            else:
                print "NOT able to process reference list %s" %afile
                results = list()
                results.append(filename)
                results.append("NOT able to process reference list")
                writer.writerow(results)
            
            
            donelist.append(filename)
            fdone.write(filename+'\n')
            
    ofile.close()
    fdone.close()
    
    sys.exit(0)

