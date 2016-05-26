#!/bin/bash
for D in `find /tmp -type d`
do
  echo "grrr"
  echo ${D}
  for F in `find /tmp -type d`
  do
    echo ${F}
    sed -ie '/# Author :: Alex Ethier <aethier@mitre.org>/ i\
# Author :: Turdy McTurd Face <turdy@example.com> \
' ${F}
  done
done
echo "done"
