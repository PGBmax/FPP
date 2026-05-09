# ============================================================
#  Makefile — Compilateur / runtime F++
# ============================================================
#
#  Cibles principales
#  ------------------
#  all          Compile tous les exemples dans build/
#  re           fclean + all
#  clean        Supprime les .c intermédiaires
#  fclean       clean + supprime les binaires et build/
#
#  Cibles utilitaires
#  ------------------
#  run-<nom>    Compile (si besoin) et exécute l'exemple <nom>
#  voir-c-<nom> Affiche le C généré pour l'exemple <nom>
#  liste        Liste les exemples disponibles
#
#  Variables surchargeables
#  ------------------------
#  EXEMPLES_DIR  Dossier des sources .fpp     (défaut: exemples)
#  BUILD_DIR     Dossier de sortie des binaires (défaut: build)
#  FPPC          Chemin vers le compilateur    (défaut: python3 fppc.py)
# ============================================================

FPPC        = python3 fppc.py
EXEMPLES_DIR = exemples
BUILD_DIR   = build

# ── Sources & cibles ──────────────────────────────────────────
SRCS   = $(wildcard $(EXEMPLES_DIR)/*.fpp)
NAMES  = $(basename $(notdir $(SRCS)))
BINS   = $(addprefix $(BUILD_DIR)/, $(NAMES))
CSRCS  = $(addsuffix .c, $(basename $(SRCS)))

# ── Règles principales ────────────────────────────────────────
.DEFAULT_GOAL := all

all: $(BUILD_DIR) $(BINS)

re: fclean all

# Création du dossier de sortie
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Règle générique : chaque binaire dépend de son .fpp
$(BUILD_DIR)/%: $(EXEMPLES_DIR)/%.fpp | $(BUILD_DIR)
	$(FPPC) $< -o $@

# ── Nettoyage ─────────────────────────────────────────────────
clean:
	rm -f $(CSRCS)

fclean: clean
	rm -f $(BINS)
	rmdir $(BUILD_DIR) 2>/dev/null || true

# ── Utilitaires ───────────────────────────────────────────────

# make run-bonjour  → compile si besoin, puis exécute
run-%: $(BUILD_DIR)/%
	$<

# make voir-c-bonjour  → affiche le C généré (sans compiler)
voir-c-%:
	$(FPPC) $(EXEMPLES_DIR)/$*.fpp -S

# Liste les exemples disponibles
liste:
	@echo "Exemples disponibles :"
	@$(foreach n, $(NAMES), echo "  $(n)";)

.PHONY: all re clean fclean liste
