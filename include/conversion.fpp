# ══════════════════════════════════════════════════════════════
#  F++ — Bibliothèque de conversions d'unités
#  inclure "include/conversion.fpp"
# ══════════════════════════════════════════════════════════════

# ── Températures ──────────────────────────────────────────────

fonction celsius_vers_fahrenheit(c) faire
    retourner c * 9 / 5 + 32
fin

fonction fahrenheit_vers_celsius(f) faire
    retourner (f - 32) * 5 / 9
fin

fonction celsius_vers_kelvin(c) faire
    retourner c + 273.15
fin

fonction kelvin_vers_celsius(k) faire
    retourner k - 273.15
fin

fonction fahrenheit_vers_kelvin(f) faire
    retourner celsius_vers_kelvin(fahrenheit_vers_celsius(f))
fin

fonction kelvin_vers_fahrenheit(k) faire
    retourner celsius_vers_fahrenheit(kelvin_vers_celsius(k))
fin

# ── Distances ─────────────────────────────────────────────────

fonction km_vers_miles(km) faire
    retourner km * 0.621371
fin

fonction miles_vers_km(mi) faire
    retourner mi * 1.609344
fin

fonction m_vers_pieds(m) faire
    retourner m * 3.28084
fin

fonction pieds_vers_m(ft) faire
    retourner ft * 0.3048
fin

fonction m_vers_pouces(m) faire
    retourner m * 39.3701
fin

fonction pouces_vers_m(po) faire
    retourner po * 0.0254
fin

fonction cm_vers_pouces(cm) faire
    retourner cm * 0.393701
fin

fonction pouces_vers_cm(po) faire
    retourner po * 2.54
fin

fonction km_vers_nautiques(km) faire
    retourner km * 0.539957
fin

fonction nautiques_vers_km(nm) faire
    retourner nm * 1.852
fin

# ── Masses ────────────────────────────────────────────────────

fonction kg_vers_livres(kg) faire
    retourner kg * 2.20462
fin

fonction livres_vers_kg(lb) faire
    retourner lb * 0.453592
fin

fonction kg_vers_onces(kg) faire
    retourner kg * 35.274
fin

fonction onces_vers_kg(oz) faire
    retourner oz * 0.0283495
fin

fonction tonnes_vers_kg(t) faire
    retourner t * 1000
fin

fonction kg_vers_tonnes(kg) faire
    retourner kg / 1000
fin

# ── Volumes ───────────────────────────────────────────────────

fonction litres_vers_gallons(l) faire
    retourner l * 0.264172
fin

fonction gallons_vers_litres(gal) faire
    retourner gal * 3.78541
fin

fonction litres_vers_pintes(l) faire
    retourner l * 2.11338
fin

fonction pintes_vers_litres(pt) faire
    retourner pt * 0.473176
fin

fonction ml_vers_cuilleres(ml) faire
    retourner ml * 0.202884
fin

fonction cl_vers_ml(cl) faire
    retourner cl * 10
fin

# ── Surfaces ──────────────────────────────────────────────────

fonction m2_vers_pieds2(m2) faire
    retourner m2 * 10.7639
fin

fonction pieds2_vers_m2(ft2) faire
    retourner ft2 * 0.092903
fin

fonction km2_vers_hectares(km2) faire
    retourner km2 * 100
fin

fonction hectares_vers_km2(ha) faire
    retourner ha / 100
fin

fonction hectares_vers_acres(ha) faire
    retourner ha * 2.47105
fin

fonction acres_vers_hectares(ac) faire
    retourner ac * 0.404686
fin

# ── Vitesses ──────────────────────────────────────────────────

fonction kmh_vers_ms(kmh) faire
    retourner kmh / 3.6
fin

fonction ms_vers_kmh(ms) faire
    retourner ms * 3.6
fin

fonction kmh_vers_mph(kmh) faire
    retourner kmh * 0.621371
fin

fonction mph_vers_kmh(mph) faire
    retourner mph * 1.609344
fin

fonction kmh_vers_noeuds(kmh) faire
    retourner kmh * 0.539957
fin

fonction noeuds_vers_kmh(kn) faire
    retourner kn * 1.852
fin

# ── Énergie ───────────────────────────────────────────────────

fonction joules_vers_calories(j) faire
    retourner j * 0.239006
fin

fonction calories_vers_joules(cal) faire
    retourner cal * 4.18400
fin

fonction kwh_vers_joules(kwh) faire
    retourner kwh * 3600000
fin

fonction joules_vers_kwh(j) faire
    retourner j / 3600000
fin

# ── Pression ──────────────────────────────────────────────────

fonction bars_vers_psi(bar) faire
    retourner bar * 14.5038
fin

fonction psi_vers_bars(psi) faire
    retourner psi * 0.0689476
fin

fonction pa_vers_bars(pa) faire
    retourner pa / 100000
fin

fonction bars_vers_pa(bar) faire
    retourner bar * 100000
fin

fonction atm_vers_bars(atm) faire
    retourner atm * 1.01325
fin

fonction bars_vers_atm(bar) faire
    retourner bar / 1.01325
fin

# ── Temps ─────────────────────────────────────────────────────

fonction secondes_vers_minutes(s) faire
    retourner s / 60
fin

fonction minutes_vers_secondes(m) faire
    retourner m * 60
fin

fonction heures_vers_secondes(h) faire
    retourner h * 3600
fin

fonction secondes_vers_heures(s) faire
    retourner s / 3600
fin

fonction jours_vers_secondes(j) faire
    retourner j * 86400
fin

fonction secondes_vers_jours(s) faire
    retourner s / 86400
fin

fonction heures_vers_jours(h) faire
    retourner h / 24
fin

fonction semaines_vers_jours(s) faire
    retourner s * 7
fin

# ── Données numériques ────────────────────────────────────────

fonction octets_vers_ko(o) faire
    retourner o / 1024
fin

fonction ko_vers_mo(ko) faire
    retourner ko / 1024
fin

fonction mo_vers_go(mo) faire
    retourner mo / 1024
fin

fonction go_vers_to(go) faire
    retourner go / 1024
fin

fonction octets_vers_mo(o) faire
    retourner o / (1024 * 1024)
fin

fonction octets_vers_go(o) faire
    retourner o / (1024 * 1024 * 1024)
fin

# ── Angles ────────────────────────────────────────────────────

fonction deg_vers_rad(deg) faire
    retourner deg * pi / 180
fin

fonction rad_vers_deg(rad) faire
    retourner rad * 180 / pi
fin

fonction deg_vers_grades(deg) faire
    retourner deg * 10 / 9
fin

fonction grades_vers_deg(gr) faire
    retourner gr * 9 / 10
fin
