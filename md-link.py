# This script gets all of the Markdown files in a directory (and its subdirs),
# and fixes link paths to targets that are within the directory. These are
# all internal links between a set of help topics.
#
# The script writes out a set of fixed Markdown files, and also writes a
# set of the fixed Markdown files converted into HTML as a convenience 
# for writers, reviewers, and paranoid link testers.
#
# It can also (with a little editing) report on the existence of 
# other kinds of links, such as links to external targets and bad links. 
# All of the Markdown source files can safely be assumed to have unique names.
import mistune # this is a Markdown renderer
from lxml import etree
import glob
import re
import os
import sys
import shutil
from pathlib import Path

# make a dictionary of all the Markdown files in the folder to be fixed
# link_dict keys are filenames; link_dict values are paths
# filenames can safely be assumed to be unique, no need to complain about dupes
link_dict = {}
for filename in glob.iglob('**/*.md', recursive=True):
    head, tail = os.path.split(filename)
    link_dict[tail] = head.replace('\\', '/')

pwd = os.getcwd() 
# make some folders for the converted files 
# fixeddir contains the .md files with fized links
fixeddir = str(Path(pwd).parent.joinpath(os.path.basename(pwd) + 'fixed'))
shutil.rmtree(fixeddir, ignore_errors=True)   
shutil.copytree(pwd, fixeddir)
# and save html versions too for convenience 
htmldir = str(Path(pwd).parent.joinpath(os.path.basename(pwd) + 'html'))
shutil.rmtree(htmldir, ignore_errors=True)   
shutil.copytree(pwd, htmldir)   


def wrap(s):
    # take a fragment of html and return a minimally valid html doc
    c = os.path.dirname(os.path.realpath(sys.argv[0]))
    # style.txt is a file containing some boilerplate CSS
    style = os.path.join(c, 'style.txt')
    with open(style, encoding='utf-8') as f:
        style = f.read()
    # html doc needs these tags
    a = '<html>' + style + '<body>'
    b = '</body></html>'
    return a + s + b

def rellink(source_file, link):
    # given a link in a source_file, return the link with the correct path
    opd =  os.path.dirname(source_file) 
    if opd == '': opd = './'
    # link_dict keys are target filenames; link_dict values are paths to the target
    # what we really want is the relative path to the link
    newpath = os.path.relpath(opd, link_dict[link])
    # this script assumes Windows paths; make them into ur paths
    newlink = newpath.replace('\\', '/') + '/' + link 
    return newlink  

def fixlinks(source_file):
    # this is presumably 
    print(source_file) # print filename so we can see progress
    with open(source_file, encoding='utf-8') as f:
        filetext = f.read()
        # convert the Markdown file to HTML
        md = mistune.markdown(filetext, use_xhtml=True) 
        # wrap the html fragment into an html doc to parse
        doc = etree.fromstring(wrap(md))
        for link in doc.xpath('//a'): # links are in <a> tags
            lt = link.get('href')     # link target is <a href="foo">
            # TODO: make these tests emit in verbose mode
            if '(' in lt:
                # probably a version number that wasn't stripped
                # print('   parens:   ' + lt)
                pass 
            elif lt.startswith('assetId'):
                # whoops, old style msdn link wasn't fixed
                # print('   assetId:  ' + lt)
                pass 
            elif lt.startswith('http'):
                # external link
                # print('   http:     ' + lt)
                pass 
            elif lt.startswith('#'):
                # intra-topic link
                # print('   internal: ' + lt)
                pass 
            else:
                linkpath, _, linkfname = lt.rpartition('/') 
                if linkfname not in link_dict: # the link target doesn't exist in this batch of files
                    print('  BORKEN:    ' + lt)
                else:
                    print('   fixed:    ' + rellink(source_file, linkfname))
                    filetext = filetext.replace(lt, rellink(source_file, linkfname))
        # save the fixed Markdown file in a directory of fixed files
        with open(os.path.join(fixeddir, source_file), 'wt', encoding='utf-8') as fout:
            fout.write(filetext)
        # change link targets to ".html", assuming ".md)" is a link
        filetext = filetext.replace('.md)', '.html)')
        # convert Markdown to HTML
        htmltext = mistune.markdown(filetext, use_xhtml=True)
        # wrap the html fragment in some tags and add some CSS
        htmltext = wrap(htmltext)
        # save the HTML file in a dir with its new hTML friends
        with open(os.path.join(htmldir, source_file[:-3] + '.html'), 'wt', encoding='utf-8') as fout:
            fout.write(htmltext)

# for all the Markdown files in the pwd, make link urls have correct paths
for file in glob.iglob('**/*.md', recursive=True):
    fixlinks(file)
