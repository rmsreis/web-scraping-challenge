### Dependencies and Setup
from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import datetime as dt
from time import sleep

##############################
### Defining Main scrapper ###
##############################

def scrape():

    # FOR Mac Users: 
    # !which chromedriver
    # # executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    # browser = Browser('chrome', **executable_path, headless=True)

    # For Windows user (like myself) otherwise uncomment lines above
    
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)
    
    title_news, paragraph_news = mars_news(browser)
    
    # to store results into a dictionary
    mars_data = {
        "news_title": title_news,
        "news_paragraph": paragraph_news,
        "featured_image": featured_image(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere(browser),
        "last_modified": dt.datetime.now()
    }

    # Quit the browser and return the scraped results
    browser.quit()

    return mars_data 

####################################
###           MARS NEWS          ###
####################################

def mars_news():

    # Visit NASA Mars News Site
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)    
    html = browser.html

    # Parse Results HTML (BeautifulSoup)
    news_soup = BeautifulSoup(html, "html.parser")
    slide_element = news_soup.select_one("ul.item_list li.slide")
    slide_element.find("div", class_="content_title")

    # Scrape the Latest News Title
    # Find First <a> tag
    title_news = slide_element.find("div", class_="content_title").get_text()
    paragraph_news = slide_element.find("div", class_="article_teaser_body").get_text()

    return title_news, paragraph_news

#######################################################################
###                         Featured Mars Import                    ###
###         NASA JPL (Jet Propulsion Laboratory) Site Web Scraper   ###
#######################################################################

def featured_image():

    # Visit the NASA JPL (Jet Propulsion Laboratory) Site
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)    

    #Go to 'FULL IMAGE', then to 'more info'
    #full_image_button = browser.find_by_id("FULL IMAGE")

    browser.click_link_by_partial_text('FULL IMAGE')
    
    sleep(1)

    #full_image_button.click()
    browser.click_link_by_partial_text('more info')


    # Find "More Info" Button and Click It
    #browser.is_element_present_by_text("more info", wait_time=1)
    #more_info_element = browser.find_link_by_partial_text("more info")
    #more_info_element.click()

    # Parse Results HTML with BeautifulSoup
    html = browser.html
    image_soup = BeautifulSoup(html, "html.parser")

    img_url = image_soup.find('figure', class_='lede').a['href']

    #img_url = img.get("src")

    #Create Absolute URL
    img_url = f"https://www.jpl.nasa.gov{img_url}"
    
    return img_url

#####################################################
#####               Mars Weather                #####
##### Mars Weather Twitter Account Web Scraper  #####
#####################################################

def twitter_weather():
    
    # Visit the Mars Weather Twitter Account
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    # Parse Results HTML with BeautifulSoup
    html = browser.html
    weather_soup = BeatifulSOup(html, "html.parser")
    
    # Find a Tweet with the data-name "Mars Weather"
    mars_weather_tweet = weather_soup.find("div", 
                                            attrs={
                                            "class": "tweet", 
                                            "data-name": "Mars Weather"
                                        })

   # Search for <p> Tag Containing tweet Text
    mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()
   
    return mars_weather

###########################################
###             Mars Facts              ###
###     Mars Facts Web Scraper          ###
###########################################

def mars_facts():
    # Visit the Mars Facts Site Using Pandas to Read
    df = pd.read_html("https://space-facts.com/mars/")[0]

    df.columns=["Description", "Value"]
    
     # Set index to property in preparation for import into MongoDB
    df.set_index("Description", inplace=True)

#Convert to HTML table string and return
    return df.to_html(classes="table table-striped")


#############################################
###             Mars Hemispheres          ###
###     Mars Hemispheres Web Scraper      ###
#############################################


def hemisphere(browser):
    
    # Visit the USGS Astrogeology Science Center Site
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
        
        
    # Initialize hemisphere_image_urls list
    hemisphere_image_urls = []

    # Get a List of all the Hemisphere
    links = browser.find_by_css("a.product-item h3")

    for item in range(len(links)):
        hemisphere = {}
        
        # Find Element on Each Loop to Avoid a Stale Element Exception
        browser.find_by_css("a.product-item h3")[item].click()
        
        # Find Sample Image Anchor Tag & Extract <href>
        sample_element = browser.find_link_by_text("Sample").first
        hemisphere["img_url"] = sample_element["href"]
        
        # Get Hemisphere Title
        hemisphere["title"] = browser.find_by_css("h2.title").text
        
        # Append Hemisphere Object to List
        hemisphere_image_urls.append(hemisphere)
        
        # Navigate Backwards
        browser.back()

    return hemisphere_image_urls

### Finalizing!!! wohooooo!!!

if __name__ == "__main__":
    print(scrape())
