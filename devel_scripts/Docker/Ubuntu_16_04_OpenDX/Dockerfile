###############################################################################
#                                                                             #
# Copyright (C) 2017 Troels Schwarz-Linnet                                    #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
#                                                                             #
###############################################################################

# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y \
        dx

RUN useradd -ms /bin/bash developer
# -m : Create the home directory if it does not exist.
# -s : User's login shell, which defaults to /bin/bash

USER developer
RUN mkdir -p $HOME/work
WORKDIR /home/developer/work

# Run command
CMD /usr/bin/dx
