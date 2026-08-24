from app.engineering.extrator_dxf import extrair_dxf

p = r"U:\I1 PC PRODUZIDAS\I1044\I1044996.DXF"

r = extrair_dxf(p)

principal = r["contorno_principal"]

print("=== AREAS DOS CONTORNOS ===")
print(f"AREA BRUTA   : {principal['area_mm2']:.6f} mm2")
print(f"CONTORNOS    : {len(r['contornos'])}")

for i, c in enumerate(r["contornos"][1:], 1):
    print(
        f"CONTOUR {i}: "
        f"area={c['area_mm2']:.6f} mm2 | "
        f"{c['largura_mm']:.3f} x {c['altura_mm']:.3f} | "
        f"tipos={c['entidades_origem']['tipos']}"
    )

area_furos = sum(
    c["area_mm2"]
    for c in r["contornos"][1:]
)

area_liquida = (
    principal["area_mm2"]
    - area_furos
)

print(f"AREA FUROS   : {area_furos:.6f} mm2")
print(f"AREA LIQUIDA : {area_liquida:.6f} mm2")
