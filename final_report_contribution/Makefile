default:
	pdflatex -shell-escape -interaction=nostopmode "\input" main.tex
	bibtex main
	pdflatex -shell-escape -interaction=nostopmode "\input" main.tex
	pdflatex -shell-escape -interaction=nostopmode "\input" main.tex
