# md-link

This script gets all of the Markdown files in a directory (and its subdirs), and fixes link paths to targets that are within the directory. These are all internal links between a set of help topics.

The script writes out a set of fixed Markdown files, and also writes a set of the fixed Markdown files converted into HTML as a convenience for writers, reviewers, and paranoid link testers.

It can also (with a little editing) report on the existence of other kinds of links, such as links to external targets and bad links. All of the Markdown source files can safely be assumed to have unique names.
