# OCCUR
Occur is the OPeNDAP Citatation Creator. 
OCCUR is a service to create data citations from OPeNDAP resources. 


## Requirements
OCCUR is built on django and uses citeproc-py for citation formatting

* django
* citeproc-py

Installing citeproc:

  pip3 install citeproc-py
  

Installing CSL Styles:

    wget https://github.com/citation-style-language/styles/archive/master.zip
    unzip master.zip 
    rm masters.zip
    STYLES_DIR=~/styles-master
    sudo ln -s $STYLES_DIR/[a-l]* /usr/lib/python3/dist-packages/citeproc/data/styles
    sudo ln -s $STYLES_DIR/[m-z]* /usr/lib/python3/dist-packages/citeproc/data/styles


