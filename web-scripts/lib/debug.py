def debug(title, message):
    print('[ ' + title + ' ]: ' + message)

def debug_error(soup, location, field, info=''):
    url = soup.find('link', {'rel': 'canonical'}).attrs['href']
    href = url.replace('https://www.basketball-reference.com', '')
    print('[ Error: ' + location + ' ]: Could not fill the ' + field + ' filed.')
    print("\tHREF: " + href)
    if info != '':
        print("\tCONTEXT: " + info)
