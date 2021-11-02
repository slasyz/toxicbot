from toxic.handlers.music import search_links


def test_search_links():
    src = '''
https://yandex.ru/ASDF
message
https://youtu.be/asdff
https://www.youtube.com/FDSA
something more
https://fakeyoutube.com/FFFF    
https://share.boom.ru/artist/66721/?share_auth=02b256a0b5e773bfad811a61816080
'''
    expected = ['https://youtu.be/asdff', 'https://www.youtube.com/FDSA', 'https://share.boom.ru/artist/66721/?share_auth=02b256a0b5e773bfad811a61816080']
    assert search_links(src) == expected
