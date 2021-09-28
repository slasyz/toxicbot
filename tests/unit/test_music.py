from toxic.handlers.music import search_links


def test_search_links():
    src = '''
https://yandex.ru/ASDF
message
https://youtu.be/asdff
https://www.youtube.com/FDSA
something more
https://fakeyoutube.com/FFFF    
'''
    expected = ['https://youtu.be/asdff', 'https://www.youtube.com/FDSA']
    assert search_links(src) == expected
