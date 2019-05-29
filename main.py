import os

import kakuyomu
import syosetu
import test


def main():
    choice = input('[s]yousetu.com or [k]akuyomu.jp?: ').lower()
    if choice == 'k':
        ky = True
    elif choice == 's':
        ky = False
    else:
        raise ValueError('Choice has to be "s" or "k".')

    output_path = input('Output Path: ')
    if not output_path:
        output_path = os.path.dirname(__file__).replace('/', '\\')
    if output_path[-1] != '\\':
        output_path += '\\'

    if ky:
        kakuyomu.main(output_path)
    else:
        syosetu.main(output_path)

    print('FINISH')


main()
