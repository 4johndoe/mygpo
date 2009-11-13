# -*- coding: utf-8 -*-
#
#
#
#  based on: gPodder's opml.py (2007-08-19)
#            libopmlreader.py (2006-06-13)
#            libopmlwriter.py (2005-12-08)
#

"""OPML import and export functionality

This module contains helper classes to import subscriptions 
from OPML files on the web and to export a list of channel 
objects to valid OPML 1.1 files.
"""

from mygpo.api import util

import xml.dom.minidom

import urllib
import urllib2
import os.path
import os
import platform
import shutil

from email.Utils import formatdate


class Importer(object):
    """
    Helper class to import an OPML feed from protocols
    supported by urllib2 (e.g. HTTP) and return a GTK 
    ListStore that can be displayed in the GUI.

    This class should support standard OPML feeds and
    contains workarounds to support odeo.com feeds.
    """

    VALID_TYPES = ( 'rss', 'link' )
    USER_AGENT = 'my.gpodder.org'

    def read_url( self, url):
        request = urllib2.Request( url, headers = {'User-agent': self.USER_AGENT})
        return urllib2.urlopen( request).read()

    def __init__( self, url='', content=''):
        """
        Parses the OPML feed from the given URL into 
        a local data structure containing channel metadata.
        """
        self.items = []
        try:
            if content != '':
                doc = xml.dom.minidom.parseString(content)
            elif os.path.exists(url):
                doc = xml.dom.minidom.parse(url)
            else:
                doc = xml.dom.minidom.parseString(self.read_url(url))

            for outline in doc.getElementsByTagName('outline'):
                if outline.getAttribute('type') in self.VALID_TYPES and outline.getAttribute('xmlUrl') or outline.getAttribute('url'):
                    channel = {
                        'url': outline.getAttribute('xmlUrl') or outline.getAttribute('url'),
                        'title': outline.getAttribute('title') or outline.getAttribute('text') or outline.getAttribute('xmlUrl') or outline.getAttribute('url'),
                        'description': outline.getAttribute('text') or outline.getAttribute('xmlUrl') or outline.getAttribute('url'),
                    }

                    if channel['description'] == channel['title']:
                        channel['description'] = channel['url']

                    for attr in ( 'url', 'title', 'description' ):
                        channel[attr] = channel[attr].strip()

                    self.items.append( channel)
                else:
                    print 'wrong type'
            if not len(self.items):
                #log( 'OPML import finished, but no items found: %s', url, sender = self)
                print 'OPML import finished, but no items found: %s' % url
                pass
        except Exception, e:
            #log( 'Cannot import OPML from URL: %s', url, traceback=True, sender = self)
            print 'Cannot import OPML from URL: %s: %s' % (url, e)
            pass

class Exporter(object):
    """
    Helper class to export a list of channel objects
    to a local file in OPML 1.1 format.

    See www.opml.org for the OPML specification.
    """

    FEED_TYPE = 'rss'

    def __init__( self, filename=''):
        if filename.endswith( '.opml') or filename.endswith( '.xml'):
            self.filename = filename
        else:
            self.filename = '%s.opml' % ( filename, )

    def create_node( self, doc, name, content):
        """
        Creates a simple XML Element node in a document 
        with tag name "name" and text content "content", 
        as in <name>content</name> and returns the element.
        """
        node = doc.createElement( name)
        node.appendChild( doc.createTextNode( content))
        return node

    def create_outline( self, doc, channel):
        """
        Creates a OPML outline as XML Element node in a
        document for the supplied channel.
        """
        outline = doc.createElement( 'outline')
        outline.setAttribute( 'title', channel.title)
        outline.setAttribute( 'text', channel.description if channel.description != None else '')
        outline.setAttribute( 'xmlUrl', channel.url)
        outline.setAttribute( 'type', self.FEED_TYPE)
        return outline

    def generate( self, channels):
        """
        Creates a XML document containing metadata for each 
        channel object in the "channels" parameter, which 
        should be a list of channel objects.
        """
        doc = xml.dom.minidom.Document()

        opml = doc.createElement('opml')
        opml.setAttribute('version', '2.0')
        doc.appendChild(opml)

        head = doc.createElement( 'head')
        head.appendChild( self.create_node( doc, 'title', 'my.gpodder.org Subscriptions'))
        head.appendChild( self.create_node( doc, 'dateCreated', formatdate(localtime=True)))
        opml.appendChild( head)

        body = doc.createElement( 'body')
        for channel in channels:
            body.appendChild( self.create_outline( doc, channel))
        opml.appendChild( body)
        return doc.toprettyxml(encoding='utf-8', indent='    ', newl=os.linesep)

    def write( self, channels):
        """
        Creates a XML document containing metadata for each 
        channel object in the "channels" parameter, which 
        should be a list of channel objects.

        OPML 2.0 specification: http://www.opml.org/spec2

        Returns True on success or False when there was an 
        error writing the file.
        """
        data = self.generate( self, channels)

        try:
            # We want to have at least 512 KiB free disk space after
            # saving the opml data, if this is not possible, don't 
            # try to save the new file, but keep the old one so we
            # don't end up with a clobbed, empty opml file.
            FREE_DISK_SPACE_AFTER = 1024*512
            available = util.get_free_disk_space(os.path.dirname(self.filename))
            if available < 2*len(data)+FREE_DISK_SPACE_AFTER:
                # FIXME: get_free_disk_space still unimplemented for win32
                #log('Not enough free disk space to save channel list to %s', self.filename, sender = self)
                return False
            fp = open(self.filename+'.tmp', 'w')
            fp.write(data)
            fp.close()
            os.rename(self.filename+'.tmp', self.filename)
        except:
            #log('Could not open file for writing: %s', self.filename, sender=self, traceback=True)
            return False

        return True

