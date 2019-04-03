#!/usr/bin/env python3
import os
import xml.dom.minidom
import urllib.request
import argparse

def parseOpmlFile(path):
    try:
        root = xml.dom.minidom.parse(path)
    except (OSError, xml.parsers.expat.ExpatError) as e:
        raise e
    
    opml = root.childNodes[0]
    if opml.nodeName != 'opml':
        raise Exception("no opml node")
    
    repos = []
    for opmlChild in opml.childNodes:
        if opmlChild.nodeName != 'body':
            continue
        body = opmlChild
        for bodyChild in body.childNodes:
            if bodyChild.nodeName != 'outline':
                continue
            outline_list = bodyChild
            for outline in outline_list.childNodes:
                if outline.nodeName != 'outline':
                    continue
                repos.append(outline.getAttribute('title')[:-len('.git')])

    return repos

def writeManifest(repos):
    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, 'manifest', None)
    manifest = doc.documentElement

    # remote
    remote = doc.createElement('remote')
    remote.setAttribute('name', 'openwrt')
    remote.setAttribute('fetch', 'https://git.openwrt.org/')
    manifest.appendChild(remote)

    # default
    default = doc.createElement('default')
    default.setAttribute('revision', 'master')
    default.setAttribute('remote', 'openwrt')
    default.setAttribute('sync-j', '4')
    manifest.appendChild(default)

    # projects
    for r in repos:
        project = doc.createElement('project')
        project.setAttribute('name', r)
        manifest.appendChild(project)

    with open('default.xml', 'w') as xml_file:
        doc.writexml(xml_file, addindent=' ' * 2, newl='\n', encoding='UTF-8')

def downloadOpmlFile(path):
    URL = 'https://git.openwrt.org/?a=opml'
    resp = urllib.request.urlopen(URL)
    text = resp.read().decode('UTF-8')
    with open(path, 'w', encoding="UTF-8") as opml_file:
        opml_file.write(text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action='store_true', help="download opml repos from https://git.openwrt.org/")
    args = parser.parse_args()

    OPML_FILE = "./repos.opml"
    if args.update:
        downloadOpmlFile(OPML_FILE)
    repos = parseOpmlFile(OPML_FILE)
    writeManifest(repos)
