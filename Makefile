# Makefile — Compilateur F++
# Usage depuis le dossier F++/:
#
#   make bonjour           → compile exemples/bonjour.fpp → bonjour
#   make fonctions         → compile exemples/fonctions.fpp → fonctions
#   make <nom>             → compile exemples/<nom>.fpp → <nom>
#   make run-bonjour       → compile et exécute bonjour
#   make voir-c-bonjour    → affiche le C généré de bonjour
#   make clean             → supprime les binaires générés

FPPC = python3 fppc.py
EXEMPLES_DIR = exemples

# Cible générique : make <nom> → compile exemples/<nom>.fpp
%: $(EXEMPLES_DIR)/%.fpp
	$(FPPC) $< -o $@

# Exécution rapide : make run-<nom>
run-%: %
	./$*

# Afficher le C : make voir-c-<nom>
voir-c-%:
	$(FPPC) $(EXEMPLES_DIR)/$*.fpp -S

clean:
	rm -f bonjour fonctions
	find . -maxdepth 1 -type f -executable ! -name "*.py" -delete

.PHONY: clean
