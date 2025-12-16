import os
import sys
import configparser
import argparse

from scrapperlib import syosetu, kakuyomu, gui

legal_settings = ('output_folder',)


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


def set_output_folder(settings):
    output_folder = ''
    valid = False

    while not valid:
        valid = True
        output_folder = input('Enter an output path. No Path uses current working directory: ')

        # Empty input
        if not output_folder:
            output_folder = os.path.dirname(__file__).replace('/', '\\')
        if output_folder[-1] != '\\':
            output_folder += '\\'

        # check if path is valid
        if not os.path.isdir(output_folder):
            print("ERROR: This is not a directory: '%s'" % output_folder, file=sys.stderr)
            valid = False

    settings['main']['output_folder'] = output_folder


def get_settings(**user_settings):
    settings = read_settings()
    for s in legal_settings:
        if s in user_settings:
            settings['main'][s] = str(user_settings[s])

    output_folder = settings['main']['output_folder']

    # Get a correct output path if not in settings
    if not output_folder or not os.path.isdir(output_folder):
        print('No valid output path was given or saved.')
        set_output_folder(settings)

    return settings


def ask_about_settings(settings):
    # Functions to change a setting with user input
    changed = False
    change = {'p': set_output_folder}
    user_in = True
    while user_in:
        print('Should the following settings be used?')
        print('[P] Output Path: \t\t\t\t\t%s' % settings['main']['output_folder'])
        print('[C] Number of Chapters per book: \t%s' % settings['main']['chapters_per_book'])
        user_in = input('To change a setting type its letter. Otherwise just press Enter: ').lower().strip()
        if user_in:
            try:
                # call function to change the specified setting
                change[user_in](settings)
                changed = True
            except KeyError:
                print("ERROR: Did not recognize the setting of '%s'" % user_in, file=sys.stderr)

    if changed and 'y' == input("Save settings? (y/n): "):
        save_settings(settings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('code', nargs='*',
                        help='The novel code from either syosetu.com or kakuyomu.jp')
    parser.add_argument('-r', '--range', dest='range',
                        help='Only downloads chapters in the given range. Format: <start>:<end>\n'
                             'If start is omitted, start from first chapter.\n'
                             'If end is omitted, read all chapters from start until there are no more found.')
    parser.add_argument('-f', dest='fast', action='store_true',
                        help='Do not ask for input, use saved settings.')
    parser.add_argument('-o', dest='output',
                        help='Creates novel files in the specified output folder.')
    parser.add_argument('-s', dest='website', choices=('kakuyomu', 'syosetu'),
                        help='Look up novel on this site instead of guessing - "kakuyomu" or "syosetu".')
    parser.add_argument('-q', dest='quiet', action='store_true',
                        help='In quiet mode there will be no console output while downloading.')
    parser.add_argument('--nogui', dest='nogui', action='store_true',
                        help='Do not start the gui, only work with console arguments.')

    args = parser.parse_args()
    user_args = dict()
    if args.output:
        if args.output[-1] != '\\':
            args.output += '\\'
        user_args['output_folder'] = args.output

    if args.nogui:
        # Do not start up gui
        if not args.code:
            raise ValueError("Provide a code to run without gui")

        first_chapter = 0
        last_chapter = float('inf')
        if args.range:
            try:
                s, e = args.range.split(':')
                if s:
                    first_chapter = int(s)-1
                if e:
                    last_chapter = int(e)
            except Exception:
                print("The range was not correctly formatted. Use integers. Format: <start>:<end>", file=sys.stderr)
                return

        settings = get_settings(**user_args)

        if not args.fast:
            ask_about_settings(settings)

        book = None

        if not args.website:
            # Differences between codes (as fas as I can see):
            # Syosetu code begins with 'n'
            # Kakuyomu code is just numerical
            if args.code[0] == 'n':
                book = syosetu.SyosetuScrapper(code=args.code)
            else:
                book = kakuyomu.KakuyomuScrapper(code=args.code)

        elif args.website == 'syosetu':
            book = syosetu.SyosetuScrapper(code=args.code)
        elif args.website == 'kakuyomu':
            book = kakuyomu.KakuyomuScrapper(code=args.code)

        if not book:
            raise AssertionError("Book has not been initialized")

        try:
            overview = book.get_novel_overview()
        except AssertionError as e:
            print("Getting Overview: " + str(e), file=sys.stderr)
            return

        book.scrap(overview=overview,
                   output_folder=settings['main']['output_folder'])

    else:
        # Start up gui
        settings = read_settings()
        old_path = settings['main']['output_folder']
        last_path = gui.main(old_path)
        # If a valid path was entered and used, save it for next time
        if os.path.isdir(last_path):
            settings['main']['output_folder'] = last_path
            save_settings(settings)


if __name__ == '__main__':
    main()
