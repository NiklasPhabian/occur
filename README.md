# Requirements

    sudo apt install texlive-bibtex-extra texlive-science texlive-latex-extra biber
    
# Build
    
    biber occur
    makeglossaries occur.glo
    pdflatex occur.tex
    
    
# tex > md

    pandoc
    
## Replace latex citations with md citations

    %s/\\cite{\([^}]*\)}/[@\1]/g 
    

## Replace images

    %s/<img src="\([^"]*\)".*alt="\([^"]*\)" \/>/![\2](\1)/g 


## Slash FU

    %s/\\\([\[\]]\)/\1/g 
