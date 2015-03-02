#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     02/03/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------



from utils import *


def fix_project_page_links(unfixed_links):
    """Turn '/projects/openofficeorg.mirror/' into 'http://sourceforge.net/projects/openofficeorg.mirror/'
    """
    fixed_links = []
    for unfixed_link in unfixed_links:
        fixed_links.append("http://sourceforge.net"+unfixed_link)
    return fixed_links



def extract_project_pages(html):
    """Scan through a HTML page and extract links to sourceforge projects.
    """
    # <a href="/projects/openofficeorg.mirror/?source=directory-featured" itemprop="url" title="Find out more about Apache OpenOffice"><span itemprop="name">Apache OpenOffice</span></a>
    # /projects/openofficeorg.mirror/
    extract_project_page_links_regex = """(/projects/[^/{]+/)"""
    short_project_page_links = re.findall(extract_project_page_links_regex, html, re.IGNORECASE)
    # Add 'http://sourceforge.net' to links
    project_page_links = fix_project_page_links(short_project_page_links)
    return uniquify(project_page_links)




def search_for_string(search_term,max_search_pages=100):
    logging.info("Searching for "+repr(search_term))
    all_project_page_links = []
    last_page_links = []
    page_number = 0
    while page_number <= max_search_pages:
        page_number += 1
        # Load search page
        search_url = "http://sourceforge.net/directory/?q="+search_term+"&sort=update&page="+str(page_number)
        logging.debug("Loading "+search_url)
        html = get(search_url)
        # Extract project links
        project_page_links = extract_project_pages(html)
        logging.debug("project_page_links: "+repr(project_page_links))
        # Append to results list
        all_project_page_links += project_page_links
        append_list(project_page_links,list_file_path="found_projects_list.txt",initial_text="# List of found projects.\n")
        #logging.debug("all_project_page_links: "+repr(all_project_page_links))
        # Stop if 2 pages match
        if project_page_links == last_page_links:
            logging.debug("Last two pages were the same, stopping scan.")
            logging.debug("project_page_links:"+repr(project_page_links))
            logging.debug("last_page_links:"+repr(last_page_links))
            break
        last_page_links = project_page_links[:]
        continue
    return all_project_page_links




def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","sourceforge_project_lister_log.txt"))
        # Setup browser
        global cj
        cj = cookielib.LWPCookieJar()
        setup_browser(cj)
        # Run main code
        project_page_links = search_for_string(search_term="as",max_search_pages=100)

        logging.info("Finished, exiting.")

    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return

if __name__ == '__main__':
    main()
