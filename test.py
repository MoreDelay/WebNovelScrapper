import os
import sys
import configparser
import argparse

import kakuyomu
import syosetu

legal_settings = ('output_path', 'chapters_per_book')


def save_settings(settings):
    with open('settings.ini', 'w') as file:
        settings.write(file)


def read_settings():
    settings = configparser.ConfigParser()
    settings.read('settings.ini')
    if 'main' not in settings:
        settings['main'] = dict()

    for s in legal_settings:
        if s not in settings['main']:
            settings['main'][s] = ''

    return settings


def set_output_path(settings):
    output_path = ''
    valid = False

    while not valid:
        valid = True
        output_path = input('Enter an output path. No Path uses current working directory: ')

        # Empty input
        if not output_path:
            output_path = os.path.dirname(__file__).replace('/', '\\')
        if output_path[-1] != '\\':
            output_path += '\\'

        # check if path is valid
        if not os.path.isdir(output_path):
            print("ERROR: This is not a directory: '%s'" % output_path, file=sys.stderr)
            valid = False

    settings['main']['output_path'] = output_path


def set_chapters_per_book(settings):
    book_size = ''
    valid = False

    while not valid:
        valid = True
        book_size = input('Enter a book size (number of chapters per book). No Value will create just one book: ')

        # Empty input
        if not book_size:
            book_size = '-1'
            break

        # Non empty input, check if integer
        try:
            int(book_size)
        except ValueError:
            print('ERROR: This is not an integer: %s' % book_size, file=sys.stderr)
            valid = False

    settings['main']['chapters_per_book'] = book_size


def get_settings(**user_settings):
    settings = read_settings()
    for s in legal_settings:
        if s in user_settings:
            settings['main'][s] = user_settings[s]

    output_path = settings['main']['output_path']
    book_size = settings['main']['chapters_per_book']

    # Get a correct output path if not in settings
    if not output_path or not os.path.isdir(output_path):
        print('No valid output path was given or saved.')
        set_output_path(settings)

    # Get a book size limit if not in settings
    try:
        int(book_size)
    # No entry or not integer
    except ValueError:
        print('No book size was given or saved.')
        set_chapters_per_book(settings)

    return settings


def ask_about_settings(settings):
    # Functions to change a setting with user input
    change = {'p': set_output_path, 'c': set_chapters_per_book}
    user_in = True
    while user_in:
        print('Should the following settings be used?')
        print('Output [P]ath: %s' % settings['main']['output_path'])
        print('Number of [C]hapters per book: %s' % settings['main']['chapters_per_book'])
        user_in = input('To change a setting type its letter. Otherwise just press Enter: ').lower().strip()
        try:
            # call function to change the specified setting
            change[user_in](settings)
        except KeyError:
            print("ERROR: Did not recognize the setting of '%s'" % user_in, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('code',
                        help='The novel code from either syosetu.com or kakuyomu.jp')
    parser.add_argument('-f', dest='fast', action='store_true',
                        help='Do not ask for input, use saved settings.')
    parser.add_argument('-o', dest='output',
                        help='Use the specified output path.')
    parser.add_argument('-c', dest='chapters', type=int,
                        help='Number of chapters that will be put in a single book.')
    parser.add_argument('-s', dest='website', choices=('kakuyomu', 'syosetu'),
                        help='Look up novel on this site instead of trying both - "kakuyomu" or "syosetu".')

    args = parser.parse_args()
    user_args = dict()
    if args.output:
        user_args['output_path'] = args.output
    if args.chapters:
        user_args['chapters_per_book'] = args.chapters

    settings = get_settings(**user_args)

    if not args.fast:
        ask_about_settings(settings)

    # TODO Create all functions to get a book in this file, including Threading
    # TODO Make a class in syosetu and kakuyomu which provide all specific methods for their sites
    #  (named the same, duck typing)
    # TODO To get a book, first get an object of the needed type by passing the class' code and use its methods

    return
    choice = input('[s]yousetu.com or [k]akuyomu.jp?: ').lower()
    if choice == 'k':
        ky = True
    elif choice == 's':
        ky = False
    else:
        raise ValueError('Choice has to be "s" or "k".')


    if ky:
        kakuyomu.main(output_path)
    else:
        syosetu.main(output_path)

    print('FINISH')


main()
