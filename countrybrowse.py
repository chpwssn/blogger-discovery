import gzip
import re
import requests
import string
import sys
import time
import random

DEFAULT_HEADERS = {'User-Agent': 'ChipATDev'}


class FetchError(Exception):
    '''Custom error class when fetching does not meet our expectation.'''


def main():
    # Take the program arguments given to this script
    # Normal programs use 'argparse' but this keeps things simple
    start_num = int(sys.argv[1])
    end_num = int(sys.argv[2])
    country_code = sys.argv[3]
    output_filename = sys.argv[4]  # this should be something like myfile.txt.gz
    
    assert start_num <= end_num
    
    print('Starting', start_num, end_num)
    
    gzip_file = gzip.GzipFile(output_filename, 'wb')
    
    for shortcode in check_range(country_code,start_num, end_num):
        # Write the valid result one per line to the file
        line = '{0}\n'.format(shortcode)
        gzip_file.write(line.encode('ascii'))
    
    gzip_file.close()

print('Done')


def check_range(country_code,start_num, end_num):
    for num in range(start_num, end_num + 1,10):
        shortcode = num
        url = 'https://www.blogger.com/profile-find.g?t=l&loc0={0}&start={1}'.format(country_code,shortcode)
        counter = 0
        
        while True:
            # Try 20 times before giving up
            if counter > 20:
                # This will stop the script with an error
                raise Exception('Giving up!')
            
            try:
                text = fetch(url)
            except FetchError:
                # The server may be overloaded so wait a bit
                print('Sleeping... If you see this')
                time.sleep(10)
            else:
                if text:
                    yield 'country_code:{0} start:{1}'.format(country_code,shortcode)
                    previous_profile = ""
                    for profile in extract_profiles(text):
                        profile_number = (profile.split("/")[4:])[0]
                        if not profile_number == previous_profile:
                            yield 'profile:{0}'.format(profile_number)
                            previous_profile = profile_number
                break  # stop the while loop
            counter += 1


def fetch(url):
    '''Fetch the URL and check if it returns OK.
        
        Returns True, returns the response text. Otherwise, returns None
        '''
    time.sleep(random.randint(10,25))
    print('Fetch', url)
    response = requests.get(url, headers=DEFAULT_HEADERS)
    
    # response doesn't have a reason attribute all the time??
    print('Got', response.status_code, getattr(response, 'reason'))
    
    if response.status_code == 200:
        # The item exists
        if not response.text:
            # If HTML is empty maybe server broke
            raise FetchError()
        
        return response.text
    elif response.status_code == 404:
        # Does not exist
        return
    else:
        # Problem
        raise FetchError()



def extract_profiles(text):
    '''Return a list of tags from the text.'''
    # Search for "http://www.blogger.com/profile/07965966522135022399"
    return re.findall(r'"https?://www.blogger.com/profile/[0-9]+', text)

if __name__ == '__main__':
    main()
