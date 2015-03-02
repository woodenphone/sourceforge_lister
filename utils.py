#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     07/01/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import time
import os
import sys
import re
import mechanize
import cookielib
import logging
import urllib2
import httplib
import random
import HTMLParser
import json
import shutil
import pickle
import socket
import string



def setup_logging(log_file_path):
    # Setup logging (Before running any other code)
    # http://inventwithpython.com/blog/2012/04/06/stop-using-print-for-debugging-a-5-minute-quickstart-guide-to-pythons-logging-module/
    assert( len(log_file_path) > 1 )
    assert( type(log_file_path) == type("") )
    global logger
    # Make sure output dir exists
    log_file_folder =  os.path.dirname(log_file_path)
    if log_file_folder is not None:
        if not os.path.exists(log_file_folder):
            os.makedirs(log_file_folder)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logging.debug("Logging started.")
    return


def save_file(filenamein,data,force_save=False):
    assert_is_string(filenamein)
    counter = 0
    while counter <= 10:
        counter += 1
        try:
            if not force_save:
                if os.path.exists(filenamein):
                    logging.debug("file already exists! "+repr(filenamein))
                    return
            sanitizedpath = filenamein# sanitizepath(filenamein)
            foldername = os.path.dirname(sanitizedpath)
            if len(foldername) >= 1:
                if not os.path.isdir(foldername):
                    os.makedirs(foldername)
            file = open(sanitizedpath, "wb")
            file.write(data)
            file.close()
            return
        except IOError, err:
            logging.exception(err)
            logging.error(repr(locals()))
            continue
    logging.critical("Too many failed write attempts!")
    logging.critical(repr(locals()))
    raise(err)


def read_file(path):
    """grab the contents of a file"""
    assert_is_string(path)
    f = open(path, "r")
    data = f.read()
    f.close()
    return data


def add_http(url):
    """Ensure a url starts with http://..."""
    if "http://" in url:
        return url
    elif "https://" in url:
        return url
    else:
        #case //derpicdn.net/img/view/...
        first_two_chars = url[0:2]
        if first_two_chars == "//":
            output_url = "https:"+url
            return output_url
        else:
            logging.error(repr(locals()))
            raise ValueError


def deescape(html):
    # de-escape html
    # http://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1
    deescaped_string = HTMLParser.HTMLParser().unescape(html)
    return deescaped_string





##def get(url):
##    """Simpler url getter"""
##    assert_is_string(url)
##    deescaped_url = deescape(url)
##    url_with_protocol = add_http(deescaped_url)
##    response = urllib2.urlopen(url_with_protocol)
##    html = response.read()
##    return html




def get(url):
    #try to retreive a url. If unable to return None object
    #Example useage:
    #html = get("")
    #if html:
    assert_is_string(url)
    deescaped_url = deescape(url)
    url_with_protocol = add_http(deescaped_url)
    #logging.debug( "getting url ", locals())
    gettuple = getwithinfo(url_with_protocol)
    if gettuple:
        reply, info = gettuple
        return reply
    else:
        return


def getwithinfo(url):
    """Try to retreive a url. If unable to return None objects
    Example useage:
    html = get("")
        if html:
    """
    attemptcount = 0
    max_attempts = 10
    retry_delay = 10
    request_delay = 0
    while attemptcount < max_attempts:
        attemptcount = attemptcount + 1
        if attemptcount > 1:
            delay(retry_delay)
            logging.debug( "Attempt "+repr(attemptcount)+" for URL: "+repr(url) )
        try:
            save_file(os.path.join("debug","get_last_url.txt"), url, True)
            r = br.open(url, timeout=100)
            info = r.info()
            reply = r.read()
            delay(request_delay)
            # Save html responses for debugging
            #print info
            #print info["content-type"]
            if "html" in info["content-type"]:
                #print "saving debug html"
                save_file(os.path.join("debug","get_last_html.htm"), reply, True)
            else:
                save_file(os.path.join("debug","get_last_not_html.txt"), reply, True)
            # Retry if empty response and not last attempt
            if (len(reply) < 1) and (attemptcount < max_attempts):
                logging.error("Reply too short :"+repr(reply))
                continue
            return reply,info
        except urllib2.HTTPError, err:
            logging.debug(repr(err))
            if err.code == 404:
                logging.debug("404 error! "+repr(url))
                return
            elif err.code == 403:
                logging.debug("403 error, ACCESS DENIED! url: "+repr(url))
                return
            elif err.code == 410:
                logging.debug("410 error, GONE")
                return
            else:
                save_file(os.path.join("debug","HTTPError.htm"), err.fp.read(), True)
                continue
        except urllib2.URLError, err:
            logging.debug(repr(err))
            if "unknown url type:" in err.reason:
                return
            else:
                continue
        except httplib.BadStatusLine, err:
            logging.debug(repr(err))
            continue
        except httplib.IncompleteRead, err:
            logging.debug(repr(err))
            continue
        except mechanize.BrowserStateError, err:
            logging.debug(repr(err))
            continue
        except socket.timeout, err:
            logging.debug(repr( type(err) ) )
            logging.debug(repr(err))
            continue
    logging.critical("Too many repeated fails, exiting.")
    sys.exit()# [19:51] <@CloverTheClever> if it does it more than 10 times, quit/throw an exception upstream




def assert_is_string(object_to_test):
    """Make sure input is either a string or a unicode string"""
    if( (type(object_to_test) == type("")) or (type(object_to_test) == type(u"")) ):
        return
    logging.critical(repr(locals()))
    raise(ValueError)


def setup_browser(cj):
    #Initialize browser object to global variable "br" using cokie jar "cj"
    # Browser
    global br
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    # User-Agent (this is cheating, ok?)
    br.addheaders = [("User-agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1")]
    return


def delay(basetime,upperrandom=0):
    #replacement for using time.sleep, this adds a random delay to be sneaky
    sleeptime = basetime + random.randint(0,upperrandom)
    #logging.debug("pausing for "+repr(sleeptime)+" ...")
    time.sleep(sleeptime)


def append_list(lines,list_file_path="done_list.txt",initial_text="# List of completed items.\n"):
    # Append a string or list of strings to a file; If no file exists, create it and append to the new file.
    # Strings will be seperated by newlines.
    # Make sure we're saving a list of strings.
    if ((type(lines) is type(""))or (type(lines) is type(u""))):
        lines = [lines]
    # Ensure file exists.
    if not os.path.exists(list_file_path):
        list_file_segments = os.path.split(list_file_path)
        list_dir = list_file_segments[0]
        if list_dir:
            if not os.path.exists(list_dir):
                os.makedirs(list_dir)
        nf = open(list_file_path, "w")
        nf.write(initial_text)
        nf.close()
    # Write data to file.
    f = open(list_file_path, "a")
    for line in lines:
        outputline = line+"\n"
        f.write(outputline)
    f.close()
    return


def uniquify(seq, idfun=None):
    # List uniquifier from
    # http://www.peterbe.com/plog/uniqifiers-benchmark
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result





def main():
    pass

if __name__ == '__main__':
    main()
