# Trustoo crawler

My entry to Trustoo's hiring challenge.

## Case 1

### Context

Trustoo has a long succesrate of selling leads to lawyers in NL. The category is live for over 4 years now.

### Objective

During the last 4 years new lawyer businesses likely have started. Next, businesses that failed to meet our quality standards 4 years ago probably now do fit our requirements. Our base of the best possible lawyers might be incomplete.

### Assignment

One of the websites we use a lot in the Netherlands to find candidate businesses is the Yellow Pages: [Gouden Gids](https://www.goudengids.nl/). Create a Python scraper to extract as much useful information as possible to help us adding more Lawyers on our platform. Include comments in your code to explain your choices and setup.

### Solution

...

## Case 2

### Context

Trustoo is expanding into Spain in Q4 2024 through our website trustlocal.es. Our team is responsible for providing the sales and marketing departments with as many potential business contacts as possible.

### Objective

The first category we will launch is Lawyers. Our team’s goal is to not only provide a large number of businesses but also ensure they are of high quality, so our website visitors are satisfied with the available options.

### Assignment

**Regular**
As the scraping specialist for launching the Lawyers category in Spain, identify at least three websites you would scrape to gather information on law firms.

**Bonus**
One of the websites we will use is the Spanish Yellow Pages: [Páginas Amarillas](https://www.paginasamarillas.es/). Create a Python scraper to extract as much useful information as possible to help us build the Lawyers category on our site. Include comments in your code to explain your choices and setup.

### Solution

#### Regular

##### [Yelp](https://www.yelp.es)

**ToS**:

- 4.B: You may not access or use the Service if you are a competitor of Yelp
- 7.B.ix: Use the Service to Modify, adapt, appropriate, reproduce, distribute, translate, create derivative works of the Service or the Service Content or adaptations thereof, and publicly display, sell, trade or exploit in any way the Service or the Service Content (other than Your Content), except as expressly authorized by Yelp; 
- 7.B.x: Use any robot, spider, Service search/retrieval application, or other automated device, process or means to access, copy, retrieve or index any portion of the Service or any content on the Service, unless expressly authorized by Yelp
- 7.B.xix: Use any device, software or routine that interferes with the proper working of the Service or attempts to do so in any way 
- 7.B.xxi: Remove, circumvent, disable, damage or interfere with security features of the Service, features that prevent or restrict use or copying of Service Content, or features that enforce limitations on the use of the Service. 

**robots.txt**:

A non-spoofed user agent would not be allowed anything (`Disallow: /`). Most details about a business are disallowed for any user agent.

##### [Hotfrog](https://www.hotfrog.es/)

##### [Opendi](https://www.opendi.es/)

##### [Yalwa](http://www.yalwa.es/)

##### [Enroll Business](http://es.enrollbusiness.com/)

*Sources*

- https://www.brainito.com/top-spain-business-directories-citations-for-local-seo
