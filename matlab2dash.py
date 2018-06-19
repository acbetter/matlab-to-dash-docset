# -*- coding: utf-8 -*-
import os
import shutil
import getpass
import sqlite3
import plistlib

from bs4 import BeautifulSoup


def get_matlab_docset_path():
    """Get the path of Matlab like: /Applications/MATLAB_R2017a.app/"""
    matlab_version = [x for x in os.listdir('/Applications/') if 'MATLAB' in x]
    # 180618 add new feature: Muti-version MATLAB select.
    if len(matlab_version) > 1:
        print('We find {} possible packages:'.format(len(matlab_version)))
        print('\n'.join([str(x) + ' - ' + y for x, y in zip(list(range(1, len(matlab_version) + 1)), matlab_version)]))
        while True:
            input_number = int(input('Please choose one: '))
            if 1 <= input_number <= len(matlab_version):
                matlab_version = matlab_version[input_number - 1]
                print('You choose matlab is {}'.format(matlab_version))
                break
            else:
                print('Please input the right number between 1 to {}'.format(len(matlab_version)))
    else:
        matlab_version = matlab_version[0]
        print('Auto-script find only one matlab: {}'.format(matlab_version))
    print('\nBuilding index... It may take a long time... Please wait for a minute...\n')

    docs_src_path = os.path.join('/Applications', matlab_version, 'help')
    download_path = os.path.join('/Users', getpass.getuser(), 'Downloads')
    docs_out_path = os.path.join(download_path, 'matlab.docset/Contents/Resources/Documents')
    try:
        os.makedirs(docs_out_path)
        os.rmdir(docs_out_path)
        # Way 1 symlink
        # os.symlink(docs_src_path, docs_out_path, target_is_directory=True)
        # Way 2 ln -s
        # subprocess.call('mkdir {}'.format(docs_out_path), shell=True)
        # subprocess.call('ln -s {}/* {}'.format(docs_src_path, docs_out_path), shell=True)
        # Way 3 copy
        shutil.copytree(docs_src_path, docs_out_path, symlinks=True)
        info_plist = dict(
            CFBundleIdentifier='matlab',
            CFBundleName=matlab_version.replace('.app', '').replace('_', ' '),
            DocSetPlatformFamily='matlab',
            isDashDocset=True,
            dashIndexFilePath='matlab/index.html',
            isJavaScriptEnabled=True
        )
        with open(os.path.join(download_path, 'matlab.docset', 'Contents', 'Info.plist'), 'wb') as file:
            plistlib.dump(info_plist, file)
    except FileExistsError:
        pass

    return download_path


file_path = get_matlab_docset_path()
docs_path = 'matlab.docset/Contents/Resources/Documents'


def select_products():
    """Select which products you need"""
    page = open(os.path.join(file_path, docs_path, 'documentation-center.html')).read()
    soup = BeautifulSoup(page, 'lxml')
    i = [x.find('a') for x in soup.find_all('li', class_='product-link') if x.find('a')]
    return [(x.get_text(), 'Package', os.path.join(x['href'].replace('../', ''))) for x in i]


def get_guides(packages: list):
    """Guide"""
    for p in packages:
        package = p[2].replace('/index.html', '')
        page = open(os.path.join(file_path, docs_path, p[2])).read()
        soup = BeautifulSoup(page, 'lxml')
        i = soup.find_all('a', class_='corrected_url')
        for x in i:
            yield (x.get_text(), 'Guide', os.path.join(package, x['href'].replace('../', '')))


def get_examples(packages: list):
    """Examples"""
    for p in packages:
        package = p[2].replace('/index.html', '')
        try:
            page = open(os.path.join(file_path, docs_path, package, 'examples.html')).read()
            soup = BeautifulSoup(page, 'lxml')
            i = [x.find('a') for x in soup.find_all('li', class_='an-example ex12345') if x.find('a')]
            for x in i:
                yield (x.get_text(), 'Sample', os.path.join(x['href'].replace('../', '')))
        except FileNotFoundError:
            pass


def get_functions(packages: list):
    """Functions"""
    for p in packages:
        package = p[2].replace('/index.html', '')
        try:
            page = open(os.path.join(file_path, docs_path, package, 'functionlist.html')).read()
            soup = BeautifulSoup(page, 'lxml')
            i = [x.find('a') for x in soup.find_all('td', class_='term notranslate') if x.find('a')]
            for x in i:
                try:
                    yield (x.find('code').get_text(), 'Function', os.path.join(x['href'].replace('../', '')))
                except AttributeError:
                    pass
        except FileNotFoundError:
            pass


def get_classes(packages: list):
    """Functions"""
    for p in packages:
        package = p[2].replace('/index.html', '')
        try:
            page = open(os.path.join(file_path, docs_path, package, 'classeslist.html')).read()
            soup = BeautifulSoup(page, 'lxml')
            i = [x.find('a') for x in soup.find_all('td', class_='term notranslate') if x.find('a')]
            for x in i:
                try:
                    yield (x.find('code').get_text(), 'Class', os.path.join(x['href'].replace('../', '')))
                except AttributeError:
                    pass
        except FileNotFoundError:
            pass


def write_to_sqlite(doc_set: list):
    print('Writing to sqlite.... It may take 5 minutes... Please wait...')
    conn = sqlite3.connect(os.path.join(file_path, 'matlab.docset/Contents/Resources/docSet.dsidx'))
    cur = conn.cursor()
    try:
        cur.execute('DROP TABLE searchIndex;')
    except sqlite3.OperationalError:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    for item in doc_set:
        cur.executemany('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', [item])
        print(item, end='\n')

    conn.commit()
    conn.close()


products = select_products()
docs = []
docs.extend(get_guides(products))
docs.extend(get_classes(products))
docs.extend(get_examples(products))
docs.extend(get_functions(products))
write_to_sqlite(docs)
print('Okay! Done! Have fun coding')
