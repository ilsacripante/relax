###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing generic fns for creation and parsing of XML representations of python objects."""

# Python module imports.
from re import search


def fill_object_contents(doc, elem, object=None, blacklist=None):
    """Place all simple python objects into the XML element namespace.

    @param doc:         The XML document object.
    @type doc:          xml.dom.minidom.Document instance
    @param elem:        The element to add all python objects to.
    @type elem:         XML element object
    @param object:      The python class instance containing the objects to add.
    @type object:       instance
    @param blacklist:   A list of object names to exclude.
    @type blacklist:    list of str
    """

    # Loop over the elements of the object.
    for name in dir(object):
        # Skip blacklisted objects.
        if name in blacklist:
            continue

        # Skip special objects.
        if search("^_", name):
            continue

        # Only pack objects in the __mod_attr__ list, if that list exists.
        if hasattr(object, '__mod_attr__') and name not in object.__mod_attr__:
            continue

        # Create a new element for this object, and add it to the main element.
        sub_elem = doc.createElement(name)
        elem.appendChild(sub_elem)

        # Add the text value to the sub element.
        text_val = doc.createTextNode(`getattr(object, name)`)
        sub_elem.appendChild(text_val)
