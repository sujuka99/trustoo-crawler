# Trustoo crawler

My entry to Trustoo's hiring challenge. Find its description [here](case_junior_developer_webscraping.pdf).

## Case 1

### QuickStart

### Features

##### Present

##### Planned

### Roadmap

### Developer Guide

## Case 2

The items below are ordered from most to least preferable to scrape in terms of data quality.

#### [Enroll Business](http://es.enrollbusiness.com/)

###### [Link to lawyers (In Barcelona)](https://es.enrollbusiness.com/sbp?ign=Servicios%2520Legales&cti=0&sti=632)

Enroll Business is one of the leading business directories in Spain. It enables browsing of local businesses with ease. Useful customer reviews help customers identify the best services.

###### ToS

Could not find anything that would apply to scraping.

###### robots.txt

Trustoo would likely be allowed to scrape useful data.

###### Content

- Address
- Telephone
- Work hours
- Website
- Description
- Reviews (Mostly missing)
- Photos (Often missing)

###### General information

- Free
- Domain authority 74 (Excellent)
- Must choose area when searching
- Provides a "change language" option which would allow a person who doesn't speak Spanish to explore more easily.

#### [Opendi](https://www.opendi.es/)

###### [Link to lawyers (in Madrid)](https://www.opendi.es/madrid/A/23.html)

###### ToS

Could not find them

###### robots.txt

Trustoo would not be allowed to scrape useful information.

###### Content

- Address
- Telephone
- Work hours
- Website
- Email
- Description
- Specifics about areas of work
- Reviews (Mostly missing)
- Photos (Often missing)

###### General information

Not as big as some of the other websites listed here.

- Free
- Domain authority 30 (Below average)
- Must choose area when searching

#### [Yelp](https://www.yelp.es)

Yelp is a popular business directory in Spain. Yelp is a great platform to connect with local businesses by making it easier for consumers to make a purchase, reservation, or an appointment. It has detailed information and review content, and all necessary business information.

###### [Link to lawyers](https://www.yelp.es/search?find_desc=abogado&find_loc=Madrid)

###### ToS

- 4.B: You may not access or use the Service if you are a competitor of Yelp
- 7.B.ix: Use the Service to Modify, adapt, appropriate, reproduce, distribute, translate, create derivative works of the Service or the Service Content or adaptations thereof, and publicly display, sell, trade or exploit in any way the Service or the Service Content (other than Your Content), except as expressly authorized by Yelp;
- 7.B.x: Use any robot, spider, Service search/retrieval application, or other automated device, process or means to access, copy, retrieve or index any portion of the Service or any content on the Service, unless expressly authorized by Yelp
- 7.B.xix: Use any device, software or routine that interferes with the proper working of the Service or attempts to do so in any way
- 7.B.xxi: Remove, circumvent, disable, damage or interfere with security features of the Service, features that prevent or restrict use or copying of Service Content, or features that enforce limitations on the use of the Service.

###### robots.txt

A non-spoofed user agent would not be allowed anything (`Disallow: /`). Most details about a business are disallowed for any user agent.

###### Content

- Address
- Telephone
- Work hours
- Website
- Description
- Specifics about areas of work
- Reviews (Mostly missing)
- Photos (Often missing)

###### General information

- It is not possible to get all lawyers in spain from a single search, city always has to be specified.
- A lot of the entries are of low quality
- Free
- Domain authority 59 (Good)

#### [Hotfrog](https://www.hotfrog.es/)

It is quite simple to find a local business with Hotfrog. It is a famous business directory in Spain, helping millions of small businesses gain maximum customers.

###### [Link to lawyers](https://www.hotfrog.es/search/es/abogado)

###### ToS

Fair use by users

All Content made available on or via the Services is provided for informational purposes only. The Content may only be used and reproduced for personal and non-commercial use. The following are examples of unacceptable use: (a) Content framing; (b) Content scaping; \(c\) Content data-mining; (d) Content extraction; (e) Content re-distribution; (f) mirroring of material; or (g) using this website in any way which would interfere with its operation for other parties.

###### Content

- Address
- Telephone
- Website
- Description
- Specifics about areas of work
- Reviews (Mostly missing)
- Socials
- Photos (Often missing)

###### robots.txt

No restrictions are specified for the information that would be useful to Trustoo.

###### General information

- Free
- Domain authority 42 (Average)

#### [Yalwa](http://www.yalwa.es/)

###### [Link to lawyers (in Madrid)](https://madrid.yalwa.es/Abogados-Servicios-legales/406/)

###### ToS

- Inflict an excessive load on our infrastructure or otherwise
- Interfere with the proper functioning of Yalwa through:
- Copying, modifying, distributing content from other users' ads
- Copying other people's information, including email addresses, without their consent
- Circumvention of measures intended to prevent or restrict access to Yalwa

###### robots.txt

Trustoo would not be allowed to scrape useful information. Interestingly, a number of older Mozilla user agents are severely restricted along with scraping-associated user agents such as "EmailSiphon".

###### Content

- Address
- Telephone (Says click to reveal, but doesn't get revealed. Didn't easily find it in the source)
- Website
- Description
- Photos (Often missing)

###### General information

- Free
- Domain authority 40
- Must choose area when searching

#### [e-justice](https://e-justice.europa.eu/fal/index.html) [Not part of the ranking]

The European e-Justice Portal allows you to easily find a lawyer throughout the EU. This service is provided by the European Commission in collaboration with the currently participating national bar registers.

Could be useful, especially if there is an easy way to access the data. I did not manage to find it, but perhaps there is an API?

#### [Paginas Amarillas](https://www.paginasamarillas.es/) [Not part of the ranking]

Spanish yellow pages, blocked when visiting from abroad.

### sources

- [brainito](https://www.brainito.com/top-spain-business-directories-citations-for-local-seo): Aided discovery of websites and their descriptions
- [Moz](https://moz.com/domain-analysis): Check domain authority
- [ahrefs](https://ahrefs.com/website-authority-checker/): Check domain authority
- [Google](google.com): Various searches
