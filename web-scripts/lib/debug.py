def debug(title, message):
    print('[ ' + title + ' ]: ' + message)

def debug_error(soup, location, field, info='', return_type):
    if not isinstance(return_type, type):
        raise TypeError

    output = 0
    url = soup.find('link', {'rel': 'canonical'}).attrs['href']
    href = url.replace('https://www.basketball-reference.com', '')
    print('[ Error: ' + location + ' ]: Could not fill the ' + field + ' filed.')
    print("\tHREF: " + href)
    if info != '':
        print("\tCONTEXT: " + info)

    if return_type == int:
        output = 0
    elif return_type == str:
        output = ''

    return output

