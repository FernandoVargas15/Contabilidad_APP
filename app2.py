import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

empresa = "LufTech S.A. de C.V."
fecha_actual = datetime.now().strftime("%d de %B de %Y")


# VALORES ORIGINALES
activo_circulante_original = {
    "Caja": 50000, "Bancos": 2000000, "Inventarios": 6000000,
    "IVA Acreditable": 0, "IVA x Acreditar": 0, "Clientes": 0
}

activo_no_circulante_original = {
    "Terrenos": 2500000, "Edificios": 4000000, "Mobiliario y equipo": 300000, 
    "Equipo de computo": 650000, "Equipo de entrega y reparto": 0, "Equipo de transporte": 500000,
    "Gastos de constitucion": 100000, "Gastos de instalacion": 350000,
    "Papeleria y utiles": 8000, "Rentas pagadas por anticipado": 30000,
}

pasivo_original = {
    "Proveedores": 0, "Anticipo clientes": 0, 
    "IVA Trasladado": 0, "IVA x Trasladar": 0
}

capital_original = {
    "Capital Social": 16488000, "Utilidad": 0, "Perdida": 0
}

activo_circulante = activo_circulante_original.copy()
activo_no_circulante = activo_no_circulante_original.copy()
pasivo = pasivo_original.copy()
capital = capital_original.copy()

historial = []


# VARIABLES GLOBALES
libro_diario = []
asiento_borrador = []

datos_depreciacion = [
    {"cuenta": "Edificios", "inversion": 4000000, "tasa": 0.05},
    {"cuenta": "Mobiliario y equipo", "inversion": 600000, "tasa": 0.10},
    {"cuenta": "Equipo de Computo", "inversion": 1150000, "tasa": 0.30},
    {"cuenta": "Equipo de transporte", "inversion": 500000, "tasa": 0.25},
    {"cuenta": "Gastos de instalacion", "inversion": 350000, "tasa": 0.10}
]

CUENTAS_EXTRAS = [
    "Ventas", "Compras", "Gastos de compra", "Devoluciones sobre venta", "Descuentos sobre Venta",
    "Devoluciones sobre compra", "Descuentos sobre compra", "Gastos de venta", "Gastos de administracion",
    "Dep A. de M", "Depreciación acumulada de edificios", "Depreciación acumulada de equipo de computo",
    "Depreciación acumulada de equipo de transporte", "Amortizacion acumulada de gastos de instalacion",
    "Luz", "Agua", "Internet", "Sueldos" 
]

TODAS_LAS_CUENTAS = list(activo_circulante.keys()) + list(activo_no_circulante.keys()) + \
                    list(pasivo.keys()) + list(capital.keys()) + CUENTAS_EXTRAS
TODAS_LAS_CUENTAS = sorted(list(set(TODAS_LAS_CUENTAS))) 


# FUNCIONES BASICAS
def registrar(texto):
    historial.append(texto)
    historial_text.insert(tk.END, texto + "\n")
    historial_text.see(tk.END)

def obtener_monto():
    try: return float(entry_monto.get())
    except: return None

def obtener_porcentaje():
    try: return float(entry_porcentaje.get()) / 100
    except: return None

def registrar_en_diario_automatico(concepto, movimientos):
    asiento = {
        "id": len(libro_diario) + 1, "fecha": datetime.now().strftime("%Y-%m-%d"),
        "concepto": concepto, "movimientos": movimientos 
    }
    libro_diario.append(asiento)
    actualizar_todas_las_vistas()

def sincronizar_manual_con_balance(cuenta, debe, haber):
    if cuenta in activo_circulante: activo_circulante[cuenta] += (debe - haber)
    elif cuenta in activo_no_circulante: activo_no_circulante[cuenta] += (debe - haber)
    elif cuenta in pasivo: pasivo[cuenta] += (haber - debe)
    elif cuenta in capital: capital[cuenta] += (haber - debe)

def revertir_manual_con_balance(cuenta, debe, haber):
    if cuenta in activo_circulante: activo_circulante[cuenta] -= (debe - haber)
    elif cuenta in activo_no_circulante: activo_no_circulante[cuenta] -= (debe - haber)
    elif cuenta in pasivo: pasivo[cuenta] -= (haber - debe)
    elif cuenta in capital: capital[cuenta] -= (haber - debe)


# BOTONES ORIGINALES Pestaña 1
def compra_efectivo():
    monto = obtener_monto(); cuenta = combo_cuenta.get()
    if monto is None or cuenta == "": return
    iva = monto * 0.16; total = monto + iva
    activo_no_circulante[cuenta] += monto; activo_circulante["IVA Acreditable"] += iva; activo_circulante["Bancos"] -= total
    registrar(f"Efectivo: {cuenta} ${monto:,.2f}")
    registrar_en_diario_automatico(f"Compra de {cuenta} a contado", [
        (cuenta, 0, monto, 0), ("IVA Acreditable", 0, iva, 0), ("Bancos", 0, 0, total)
    ])

def compra_credito():
    monto = obtener_monto(); cuenta = combo_cuenta.get()
    if monto is None or cuenta == "": return
    iva = monto * 0.16; total = monto + iva
    activo_no_circulante[cuenta] += monto; activo_circulante["IVA x Acreditar"] += iva; pasivo["Proveedores"] += total
    registrar(f"Crédito: {cuenta} ${monto:,.2f}")
    registrar_en_diario_automatico(f"Compra de {cuenta} a crédito", [
        (cuenta, 0, monto, 0), ("IVA x Acreditar", 0, iva, 0), ("Proveedores", 0, 0, total)
    ])

def compra_combinada():
    monto = obtener_monto(); porcentaje = obtener_porcentaje(); cuenta = combo_cuenta.get()
    if monto is None or porcentaje is None or cuenta == "": return
    iva = monto * 0.16; total = monto + iva; contado = total * porcentaje; credito = total - contado
    activo_no_circulante[cuenta] += monto; activo_circulante["IVA Acreditable"] += iva * porcentaje; activo_circulante["IVA x Acreditar"] += iva * (1 - porcentaje)
    activo_circulante["Bancos"] -= contado; pasivo["Proveedores"] += credito
    registrar(f"Combinada: {cuenta} ${monto:,.2f}")
    registrar_en_diario_automatico(f"Compra Combinada: {cuenta}", [
        (cuenta, 0, monto, 0), ("IVA Acreditable", 0, iva * porcentaje, 0), 
        ("IVA x Acreditar", 0, iva * (1 - porcentaje), 0), ("Bancos", 0, 0, contado), ("Proveedores", 0, 0, credito)
    ])

def anticipo_clientes():
    monto = obtener_monto(); porcentaje = obtener_porcentaje()
    if monto is None or porcentaje is None: return
    anticipo = monto * porcentaje; iva = anticipo * 0.16
    activo_circulante["Bancos"] += anticipo + iva; pasivo["Anticipo clientes"] += anticipo; pasivo["IVA Trasladado"] += iva
    registrar(f"Anticipo: ${anticipo:,.2f}")
    registrar_en_diario_automatico("Anticipo de clientes", [
        ("Bancos", 0, anticipo + iva, 0), ("Anticipo clientes", 0, 0, anticipo), ("IVA Trasladado", 0, 0, iva)
    ])

def limpiar():
    global activo_circulante, activo_no_circulante, pasivo, capital
    activo_circulante = activo_circulante_original.copy()
    activo_no_circulante = activo_no_circulante_original.copy()
    pasivo = pasivo_original.copy()
    capital = capital_original.copy()
    historial.clear(); historial_text.delete(1.0, tk.END)
    libro_diario.clear()
    
    movs_apertura = []
    for c, v in activo_circulante.items(): 
        if v > 0: movs_apertura.append((c, 0, v, 0))
    for c, v in activo_no_circulante.items(): 
        if v > 0: movs_apertura.append((c, 0, v, 0))
    for c, v in pasivo.items(): 
        if v > 0: movs_apertura.append((c, 0, 0, v))
    for c, v in capital.items(): 
        if v > 0: movs_apertura.append((c, 0, 0, v))
    registrar_en_diario_automatico("Registro de situación financiera", movs_apertura)


# FUNCIONES CRUD (Pestaña 2)
def agregar_a_borrador():
    cuenta = combo_cuenta_diario.get()
    if not cuenta: return
    try: parcial = float(entry_parcial.get() or 0)
    except: parcial = 0.0
    try: debe = float(entry_debe.get() or 0)
    except: debe = 0.0
    try: haber = float(entry_haber.get() or 0)
    except: haber = 0.0
    if debe == 0 and haber == 0 and parcial == 0: return
        
    asiento_borrador.append((cuenta, parcial, debe, haber))
    tree_borrador.insert("", "end", values=(cuenta, f"${parcial:,.2f}" if parcial else "", f"${debe:,.2f}" if debe else "", f"${haber:,.2f}" if haber else ""))
    combo_cuenta_diario.set(""); entry_parcial.delete(0, tk.END); entry_debe.delete(0, tk.END); entry_haber.delete(0, tk.END)

def guardar_asiento_manual():
    concepto = entry_concepto.get(); fecha = entry_fecha.get()
    if not concepto or len(asiento_borrador) == 0: return
    t_debe = sum(m[2] for m in asiento_borrador); t_haber = sum(m[3] for m in asiento_borrador)
    
    if round(t_debe, 2) != round(t_haber, 2):
        return messagebox.showerror("Error", "El asiento no cuadra. Debe y Haber deben ser iguales.")
        
    asiento = {"id": len(libro_diario) + 1, "fecha": fecha, "concepto": concepto, "movimientos": list(asiento_borrador)}
    libro_diario.append(asiento)
    for mov in asiento_borrador: sincronizar_manual_con_balance(mov[0], mov[2], mov[3])
    asiento_borrador.clear(); [tree_borrador.delete(item) for item in tree_borrador.get_children()]; entry_concepto.delete(0, tk.END)
    actualizar_todas_las_vistas()

def eliminar_asiento():
    seleccion = tree_diario.selection()
    if not seleccion: return
    asiento_id = int(tree_diario.item(seleccion[0])['text'])
    if not messagebox.askyesno("Confirmar", f"¿Eliminar Asiento {asiento_id}?"): return

    asiento = next((a for a in libro_diario if a['id'] == asiento_id), None)
    if not asiento: return
    for mov in asiento['movimientos']: revertir_manual_con_balance(mov[0], mov[2], mov[3])
    libro_diario.remove(asiento)
    for i, a in enumerate(libro_diario): a['id'] = i + 1
    actualizar_todas_las_vistas()

def editar_asiento():
    seleccion = tree_diario.selection()
    if not seleccion: return
    asiento_id = int(tree_diario.item(seleccion[0])['text'])
    if len(asiento_borrador) > 0 and not messagebox.askyesno("Borrador Ocupado", "¿Sobreescribir borrador?"): return

    asiento = next((a for a in libro_diario if a['id'] == asiento_id), None)
    if not asiento: return
    for mov in asiento['movimientos']: revertir_manual_con_balance(mov[0], mov[2], mov[3])

    asiento_borrador.clear(); [tree_borrador.delete(item) for item in tree_borrador.get_children()]
    for mov in asiento['movimientos']:
        asiento_borrador.append(mov)
        tree_borrador.insert("", "end", values=(mov[0], f"${mov[1]:,.2f}" if mov[1] else "", f"${mov[2]:,.2f}" if mov[2] else "", f"${mov[3]:,.2f}" if mov[3] else ""))

    entry_concepto.delete(0, tk.END); entry_concepto.insert(0, asiento['concepto'])
    entry_fecha.delete(0, tk.END); entry_fecha.insert(0, asiento['fecha'])
    libro_diario.remove(asiento)
    for i, a in enumerate(libro_diario): a['id'] = i + 1
    actualizar_todas_las_vistas()

def agregar_datos_depreciacion():
    cuenta = combo_dep_cuenta.get()
    try: inv = float(entry_dep_inv.get())
    except: return messagebox.showerror("Error", "Inversión inválida")
    try: tasa = float(entry_dep_tasa.get()) / 100
    except: return messagebox.showerror("Error", "Porcentaje inválido")

    if not cuenta: return
    datos_depreciacion.append({"cuenta": cuenta, "inversion": inv, "tasa": tasa})
    combo_dep_cuenta.set(""); entry_dep_inv.delete(0, tk.END); entry_dep_tasa.delete(0, tk.END)
    actualizar_todas_las_vistas()


# ACTUALIZACIÓN DE TODAS LAS VISTAS
def actualizar_todas_las_vistas():
    # --- PESTAÑA 1: PANEL ORIGINAL ---
    text_activo.delete(1.0, tk.END); text_pasivo.delete(1.0, tk.END)
    tot_ac = sum(activo_circulante.values()); tot_anc = sum(activo_no_circulante.values())
    tot_pasivo = sum(pasivo.values()); tot_capital = sum(capital.values())

    text_activo.insert(tk.END, "ACTIVO CIRCULANTE\n\n")
    for c,v in activo_circulante.items(): text_activo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")
    text_activo.insert(tk.END, f"\nSuma Activo Circulante: ${tot_ac:,.2f}\n\nACTIVO NO CIRCULANTE\n\n")
    for c,v in activo_no_circulante.items(): text_activo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")
    text_activo.insert(tk.END, f"\nSuma Activo No Circulante: ${tot_anc:,.2f}\n\nTOTAL ACTIVO: ${tot_ac+tot_anc:,.2f}\n\n")

    text_pasivo.insert(tk.END, "PASIVO\n\n")
    for c,v in pasivo.items(): text_pasivo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")
    text_pasivo.insert(tk.END, f"\nTotal Pasivo: ${tot_pasivo:,.2f}\n\nCAPITAL CONTABLE\n\n")
    for c,v in capital.items(): text_pasivo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")
    text_pasivo.insert(tk.END, f"\nTotal Capital: ${tot_capital:,.2f}\n\nPASIVO + CAPITAL: ${tot_pasivo+tot_capital:,.2f}")

    # --- PESTAÑA 2: LIBRO DIARIO ---
    [tree_diario.delete(item) for item in tree_diario.get_children()]
    tot_d, tot_h = 0, 0
    for asiento in libro_diario:
        str_id = str(asiento['id']) 
        tree_diario.insert("", "end", text=str_id, values=("", f"Asiento {asiento['id']}", "", "", ""), tags=("asiento",))
        primero = True
        for mov in asiento["movimientos"]:
            tree_diario.insert("", "end", text=str_id, values=(
                asiento["fecha"] if primero else "", 
                f"    {mov[0]}" if mov[3] > 0 else mov[0],
                f"${mov[1]:,.2f}" if mov[1] else "", f"${mov[2]:,.2f}" if mov[2] else "", f"${mov[3]:,.2f}" if mov[3] else ""
            ))
            primero = False
            tot_d += mov[2]; tot_h += mov[3]
        tree_diario.insert("", "end", text=str_id, values=("", asiento["concepto"], "", "", ""), tags=("concepto",))
        tree_diario.insert("", "end", text=str_id, values=("", "", "", "", ""))
    if libro_diario: tree_diario.insert("", "end", values=("", "SUMAS TOTALES", "", f"${tot_d:,.2f}", f"${tot_h:,.2f}"), tags=("totales",))

    # --- PESTAÑA 3 y 4: LIBRO MAYOR Y BALANZA DE COMPROBACIÓN ---
    [widget.destroy() for widget in scrollable_mayor.winfo_children()]
    [tree_balanza.delete(item) for item in tree_balanza.get_children()]

    datos_mayor = {}
    for asiento in libro_diario:
        for mov in asiento['movimientos']:
            c, d, h = mov[0], mov[2], mov[3]
            if c not in datos_mayor: datos_mayor[c] = {'debe': [], 'haber': [], 'md': 0, 'ma': 0}
            if d > 0: datos_mayor[c]['debe'].append((asiento['id'], d)); datos_mayor[c]['md'] += d
            if h > 0: datos_mayor[c]['haber'].append((asiento['id'], h)); datos_mayor[c]['ma'] += h

    row, col = 0, 0
    t_md, t_ma, t_sd, t_sa = 0, 0, 0, 0
    cuentas_usadas = sorted(list(datos_mayor.keys()))
    
    for cuenta in cuentas_usadas:
        data = datos_mayor[cuenta]
        # Dibujar Cuenta T
        frame_t = tk.Frame(scrollable_mayor, bd=2, relief="groove", bg="white")
        frame_t.grid(row=row, column=col, padx=15, pady=15, sticky="n")
        tk.Label(frame_t, text=cuenta, font=("Arial", 10, "bold"), bg="white", fg="#004085").pack(fill=tk.X, pady=2)
        tree_t = ttk.Treeview(frame_t, columns=("D", "H"), show="headings", height=max(len(data['debe']), len(data['haber']), 1) + 3)
        tree_t.heading("D", text="Debe"); tree_t.heading("H", text="Haber")
        tree_t.column("D", width=110, anchor="e"); tree_t.column("H", width=110, anchor="e"); tree_t.pack(padx=2, pady=2)

        for i in range(max(len(data['debe']), len(data['haber']))):
            str_d = f"{data['debe'][i][0]}) ${data['debe'][i][1]:,.2f}" if i < len(data['debe']) else ""
            str_h = f"${data['haber'][i][1]:,.2f} ({data['haber'][i][0]}" if i < len(data['haber']) else ""
            tree_t.insert("", "end", values=(str_d, str_h))

        md, ma = data['md'], data['ma']
        tree_t.insert("", "end", values=("-"*15, "-"*15)); tree_t.insert("", "end", values=(f"MD ${md:,.2f}", f"MA ${ma:,.2f}"), tags=("bold",))

        sd = md - ma if md > ma else 0
        sa = ma - md if ma > md else 0
        
        if sd > 0: tree_t.insert("", "end", values=(f"SD ${sd:,.2f}", ""), tags=("saldo",))
        elif sa > 0: tree_t.insert("", "end", values=("", f"SA ${sa:,.2f}"), tags=("saldo",))
        else: tree_t.insert("", "end", values=("CUENTA", "SALDADA"), tags=("saldada",))

        tree_t.tag_configure("bold", font=("Arial", 9, "bold"))
        tree_t.tag_configure("saldo", font=("Arial", 10, "bold"), background="#dff0d8")
        tree_t.tag_configure("saldada", foreground="gray")
        col += 1
        if col > 3: col = 0; row += 1

        # Llenar Balanza
        t_md += md; t_ma += ma; t_sd += sd; t_sa += sa
        tree_balanza.insert("", "end", values=(cuenta, f"${md:,.2f}", f"${ma:,.2f}", f"${sd:,.2f}", f"${sa:,.2f}"))

    tree_balanza.insert("", "end", values=("", "", "", "", ""))
    tree_balanza.insert("", "end", values=("SUMAS IGUALES", f"${t_md:,.2f}", f"${t_ma:,.2f}", f"${t_sd:,.2f}", f"${t_sa:,.2f}"), tags=("totales",))
    tree_balanza.tag_configure("totales", font=("Arial", 11, "bold"), background="#dff0d8")

    scrollable_mayor.update_idletasks()
    canvas_mayor.configure(scrollregion=canvas_mayor.bbox("all"))

    # --- PESTAÑA 5: ANÁLISIS DE DEPRECIACIÓN ---
    [tree_depreciacion.delete(item) for item in tree_depreciacion.get_children()]
    for d in datos_depreciacion:
        anual = d["inversion"] * d["tasa"]; mensual = anual / 12
        tree_depreciacion.insert("", "end", values=(d["cuenta"], f"${d['inversion']:,.2f}", f"{d['tasa']*100:.2f}%", f"${anual:,.2f}", f"${mensual:,.2f}"))

  
    # LÓGICA PARA RESULTADOS Y BALANCE FINAL
    # Cálculos para el Estado de Resultados
    ventas_totales = datos_mayor.get("Ventas", {}).get("ma", 0) - datos_mayor.get("Ventas", {}).get("md", 0)
    desc_ventas = datos_mayor.get("Descuentos sobre Venta", {}).get("md", 0) - datos_mayor.get("Descuentos sobre Venta", {}).get("ma", 0)
    dev_ventas = datos_mayor.get("Devoluciones sobre venta", {}).get("md", 0) - datos_mayor.get("Devoluciones sobre venta", {}).get("ma", 0)
    ventas_netas = ventas_totales - desc_ventas - dev_ventas

    inv_inicial = activo_circulante_original["Inventarios"]
    compras = datos_mayor.get("Compras", {}).get("md", 0) - datos_mayor.get("Compras", {}).get("ma", 0)
    gastos_compra = datos_mayor.get("Gastos de compra", {}).get("md", 0) - datos_mayor.get("Gastos de compra", {}).get("ma", 0)
    compras_tot = compras + gastos_compra
    
    dev_compra = datos_mayor.get("Devoluciones sobre compra", {}).get("ma", 0) - datos_mayor.get("Devoluciones sobre compra", {}).get("md", 0)
    desc_compra = datos_mayor.get("Descuentos sobre compra", {}).get("ma", 0) - datos_mayor.get("Descuentos sobre compra", {}).get("md", 0)
    compras_netas = compras_tot - dev_compra - desc_compra

    merc_disp = inv_inicial + compras_netas
    
    # Inventario final fijado al 10% del inicial
    inv_final = inv_inicial * 0.10  
    
    costo_ventas = merc_disp - inv_final
    utilidad_bruta = ventas_netas - costo_ventas

    gastos_venta = datos_mayor.get("Gastos de venta", {}).get("md", 0) - datos_mayor.get("Gastos de venta", {}).get("ma", 0)
    gastos_admin = datos_mayor.get("Gastos de administracion", {}).get("md", 0) - datos_mayor.get("Gastos de administracion", {}).get("ma", 0)
    tot_gastos_operacion = gastos_venta + gastos_admin

    utilidad_operacion = utilidad_bruta - tot_gastos_operacion

    # --- PESTAÑA 6: ESTADO DE RESULTADOS ---
    [tree_resultados.delete(item) for item in tree_resultados.get_children()]
    
    def insertar_res(concepto, col1="", col2="", col3="", col4="", tag=""):
        tree_resultados.insert("", "end", values=(concepto, col1, col2, col3, col4), tags=(tag,))

    insertar_res("Ventas Totales", "", "", f"${ventas_totales:,.2f}")
    insertar_res("Descuentos sobre Ventas", "", f"${desc_ventas:,.2f}")
    insertar_res("Devoluciones sobre Ventas", "", f"${dev_ventas:,.2f}", f"${desc_ventas+dev_ventas:,.2f}")
    insertar_res("Ventas Netas", "", "", "", f"${ventas_netas:,.2f}", "negrita")
    
    insertar_res("Inventario Inicial", "", "", f"${inv_inicial:,.2f}")
    insertar_res("Compras", f"${compras:,.2f}")
    insertar_res("Gastos de Compra", f"${gastos_compra:,.2f}")
    insertar_res("Compras Totales", "", f"${compras_tot:,.2f}")
    insertar_res("Devoluciones sobre Compra", f"${dev_compra:,.2f}")
    insertar_res("Descuentos sobre Compra", f"${desc_compra:,.2f}", f"${dev_compra+desc_compra:,.2f}")
    insertar_res("Compras Netas", "", "", f"${compras_netas:,.2f}")
    insertar_res("Mercancías Disponibles", "", "", f"${merc_disp:,.2f}")
    insertar_res("Inventario Final", "", "", f"${inv_final:,.2f}")
    insertar_res("Costo de Ventas", "", "", "", f"${costo_ventas:,.2f}", "negrita")
    
    tag_bruta = "perdida" if utilidad_bruta < 0 else "utilidad"
    texto_bruta = "Pérdida Bruta" if utilidad_bruta < 0 else "Utilidad Bruta"
    insertar_res(texto_bruta, "", "", "", f"${utilidad_bruta:,.2f}", tag_bruta)

    insertar_res("Gastos de Operación")
    insertar_res("Gastos de Venta", "", "", f"${gastos_venta:,.2f}")
    insertar_res("Gastos de Administración", "", "", f"${gastos_admin:,.2f}", f"${tot_gastos_operacion:,.2f}")
    
    tag_op = "perdida" if utilidad_operacion < 0 else "utilidad"
    texto_op = "Pérdida de Operación" if utilidad_operacion < 0 else "Utilidad de Operación"
    insertar_res(texto_op, "", "", "", f"${utilidad_operacion:,.2f}", tag_op)

    tree_resultados.tag_configure("negrita", font=("Arial", 10, "bold"))
    tree_resultados.tag_configure("utilidad", font=("Arial", 11, "bold"), background="#dff0d8")
    tree_resultados.tag_configure("perdida", font=("Arial", 11, "bold"), background="#f2dede")

    # --- PESTAÑA 7: BALANCE GENERAL UNIFICADO ---
    [tree_balance_unico.delete(item) for item in tree_balance_unico.get_children()]

    filas_activo = []
    filas_pasivo = []

    # lado Izquierdo (Activos)
    tot_ac = 0
    filas_activo.append(["ACTIVO CIRCULANTE", "", "", "", ""])
    for c in list(activo_circulante_original.keys()):
        sd = datos_mayor.get(c, {}).get("md", 0) - datos_mayor.get(c, {}).get("ma", 0)
        if sd != 0:
            filas_activo.append([c, "", f"${sd:,.2f}", "", ""])
            tot_ac += sd
    filas_activo.append(["Suma Activo Circulante", "", "", f"${tot_ac:,.2f}", ""])
    filas_activo.append(["", "", "", "", ""])

    tot_anc = 0
    filas_activo.append(["ACTIVO NO CIRCULANTE", "", "", "", ""])
    for c in list(activo_no_circulante_original.keys()):
        sd = datos_mayor.get(c, {}).get("md", 0) - datos_mayor.get(c, {}).get("ma", 0)
        if sd != 0:
            filas_activo.append([c, "", f"${sd:,.2f}", "", ""])
            tot_anc += sd
    
    # Restar depreciaciones
    for c in CUENTAS_EXTRAS:
        if "Depreciación" in c or "Amortizacion" in c or "Dep A" in c:
            sa = datos_mayor.get(c, {}).get("ma", 0) - datos_mayor.get(c, {}).get("md", 0)
            if sa != 0:
                filas_activo.append([c, "", f"-${sa:,.2f}", "", ""])
                tot_anc -= sa

    filas_activo.append(["Suma Activo No Circulante", "", "", f"${tot_anc:,.2f}", ""])
    filas_activo.append(["", "", "", "", ""])
    filas_activo.append(["TOTAL ACTIVO", "", "", "", f"${tot_ac + tot_anc:,.2f}"])

    # lado Derecho (Pasivo y Capital)
    tot_pas = 0
    filas_pasivo.append(["PASIVO", "", "", "", ""])
    filas_pasivo.append(["Corto Plazo", "", "", "", ""])
    for c in list(pasivo_original.keys()):
        sa = datos_mayor.get(c, {}).get("ma", 0) - datos_mayor.get(c, {}).get("md", 0)
        if sa != 0:
            filas_pasivo.append([c, "", f"${sa:,.2f}", "", ""])
            tot_pas += sa
    filas_pasivo.append(["Total Pasivo", "", "", f"${tot_pas:,.2f}", ""])
    filas_pasivo.append(["", "", "", "", ""])

    filas_pasivo.append(["CAPITAL CONTABLE", "", "", "", ""])
    filas_pasivo.append(["Contribuido", "", "", "", ""])
    cap_soc = datos_mayor.get("Capital Social", {}).get("ma", 0)
    filas_pasivo.append(["Capital Social", "", "", f"${cap_soc:,.2f}", ""])
    filas_pasivo.append(["", "", "", "", ""])
    
    filas_pasivo.append(["Ganado", "", "", "", ""])
    if utilidad_operacion < 0:
        filas_pasivo.append(["Pérdida del Ejercicio", "", "", f"-${abs(utilidad_operacion):,.2f}", ""])
    else:
        filas_pasivo.append(["Utilidad del Ejercicio", "", "", f"${utilidad_operacion:,.2f}", ""])

    tot_cap = cap_soc + utilidad_operacion
    filas_pasivo.append(["", "", "", "", ""])
    filas_pasivo.append(["Total Contable", "", "", "", f"${tot_cap:,.2f}"])
    filas_pasivo.append(["", "", "", "", ""])
    filas_pasivo.append(["TOTAL PASIVO + CAPITAL", "", "", "", f"${tot_pas + tot_cap:,.2f}"])

    # Fusionar ambas listas
    max_len = max(len(filas_activo), len(filas_pasivo))
    
    while len(filas_activo) < max_len: filas_activo.append(["", "", "", "", ""])
    while len(filas_pasivo) < max_len: filas_pasivo.append(["", "", "", "", ""])

    for i in range(max_len):
        fila_combinada = tuple(filas_activo[i] + filas_pasivo[i])
        tree_balance_unico.insert("", "end", values=fila_combinada)


# INTERFAZ GRÁFICA PRINCIPAL
ventana = tk.Tk()
ventana.title("Sistema Contable Profesional - LufTech S.A. de C.V.")
ventana.geometry("1500x900")

tk.Label(ventana, text=empresa, font=("Arial",20,"bold")).pack()
tk.Label(ventana, text=f"Sistema de contabilidad al 11 de Abril de 2026", font=("Arial",12)).pack()

notebook = ttk.Notebook(ventana)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tab_original = tk.Frame(notebook); notebook.add(tab_original, text="1. Panel Operativo")
tab_diario = tk.Frame(notebook); notebook.add(tab_diario, text="2. Libro Diario")
tab_mayor = tk.Frame(notebook); notebook.add(tab_mayor, text="3. Libro Mayor (T)")
tab_balanza = tk.Frame(notebook); notebook.add(tab_balanza, text="4. Balanza Comprob.")
tab_depreciacion = tk.Frame(notebook); notebook.add(tab_depreciacion, text="5. Depreciación")
tab_resultados = tk.Frame(notebook); notebook.add(tab_resultados, text="6. Edo. Resultados")
tab_balance = tk.Frame(notebook); notebook.add(tab_balance, text="7. Balance Final")

# --------- PESTAÑA 1: PANEL OPERATIVO ---------
frame_input = tk.Frame(tab_original); frame_input.pack(pady=10)
tk.Label(frame_input, text="Monto:").grid(row=0,column=0); entry_monto = tk.Entry(frame_input); entry_monto.grid(row=0,column=1)
tk.Label(frame_input, text="Cuenta a comprar:").grid(row=0,column=2); combo_cuenta = ttk.Combobox(frame_input, values=list(activo_no_circulante.keys())); combo_cuenta.grid(row=0,column=3)
tk.Label(frame_input, text="Porcentaje (%):").grid(row=0,column=4); entry_porcentaje = tk.Entry(frame_input); entry_porcentaje.grid(row=0,column=5)

frame_botones = tk.Frame(tab_original); frame_botones.pack()
tk.Button(frame_botones, text="Compra Efectivo", command=compra_efectivo).grid(row=0,column=0,padx=5)
tk.Button(frame_botones, text="Compra Crédito", command=compra_credito).grid(row=0,column=1,padx=5)
tk.Button(frame_botones, text="Compra Combinada", command=compra_combinada).grid(row=0,column=2,padx=5)
tk.Button(frame_botones, text="Anticipo Clientes", command=anticipo_clientes).grid(row=0,column=3,padx=5)
tk.Button(frame_botones, text="Limpiar", command=limpiar).grid(row=0,column=4,padx=5)

frame_principal = tk.Frame(tab_original); frame_principal.pack(pady=15)
text_activo = tk.Text(frame_principal, width=65, height=35, font=("Courier",11)); text_activo.grid(row=0,column=0)
text_pasivo = tk.Text(frame_principal, width=65, height=35, font=("Courier",11)); text_pasivo.grid(row=0,column=1)

frame_historial = tk.Frame(frame_principal); frame_historial.grid(row=0,column=2,padx=20)
tk.Label(frame_historial, text="Historial", font=("Arial",12,"bold")).pack(); historial_text = tk.Text(frame_historial, width=28, height=18); historial_text.pack()

# --------- PESTAÑA 2: LIBRO DIARIO ---------
frame_izq = tk.Frame(tab_diario, width=400, padx=10, pady=10); frame_izq.pack(side=tk.LEFT, fill=tk.Y)
tk.Label(frame_izq, text="CAPTURA MANUAL DE ASIENTOS", font=("Arial",12,"bold")).pack(pady=5)

f_dat = tk.LabelFrame(frame_izq, text="Paso 1: Datos"); f_dat.pack(fill=tk.X, pady=5)
tk.Label(f_dat, text="Fecha:").grid(row=0, column=0); entry_fecha = tk.Entry(f_dat); entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d")); entry_fecha.grid(row=0, column=1)
tk.Label(f_dat, text="Concepto:").grid(row=1, column=0); entry_concepto = tk.Entry(f_dat, width=25); entry_concepto.grid(row=1, column=1)

f_mov = tk.LabelFrame(frame_izq, text="Paso 2: Movimiento"); f_mov.pack(fill=tk.X, pady=5)
tk.Label(f_mov, text="Cuenta:").grid(row=0, column=0); combo_cuenta_diario = ttk.Combobox(f_mov, values=TODAS_LAS_CUENTAS, width=22); combo_cuenta_diario.grid(row=0, column=1)
tk.Label(f_mov, text="Parcial:").grid(row=1, column=0); entry_parcial = tk.Entry(f_mov, width=15); entry_parcial.grid(row=1, column=1)
tk.Label(f_mov, text="Debe:").grid(row=2, column=0); entry_debe = tk.Entry(f_mov, width=15); entry_debe.grid(row=2, column=1)
tk.Label(f_mov, text="Haber:").grid(row=3, column=0); entry_haber = tk.Entry(f_mov, width=15); entry_haber.grid(row=3, column=1)
tk.Button(f_mov, text="➕ Agregar al Borrador", bg="#d9edf7", command=agregar_a_borrador).grid(row=4, column=0, columnspan=2, pady=10)

f_borr = tk.LabelFrame(frame_izq, text="Paso 3: Borrador"); f_borr.pack(fill=tk.BOTH, expand=True, pady=5)
tree_borrador = ttk.Treeview(f_borr, columns=("C", "P", "D", "H"), show="headings", height=5)
tree_borrador.heading("C", text="Cuenta"); tree_borrador.heading("P", text="Parcial"); tree_borrador.heading("D", text="Debe"); tree_borrador.heading("H", text="Haber")
tree_borrador.column("C", width=120); tree_borrador.column("P", width=60); tree_borrador.column("D", width=60); tree_borrador.column("H", width=60)
tree_borrador.pack(fill=tk.BOTH, expand=True)
tk.Button(f_borr, text="💾 Guardar Asiento", bg="#dff0d8", font=("Arial",10,"bold"), command=guardar_asiento_manual).pack(fill=tk.X, pady=5)

f_der = tk.Frame(tab_diario, padx=10, pady=10); f_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tk.Label(f_der, text="LufTech, S.A de C.V.", font=("Arial",14,"bold")).pack()
tk.Label(f_der, text=f"Libro diario del 23 de Enero al 13 de Abril de 2026", font=("Arial",12)).pack(pady=2)

tree_diario = ttk.Treeview(f_der, columns=("F", "C", "P", "D", "H"), show="headings")
tree_diario.heading("F", text="Fecha"); tree_diario.heading("C", text="Cuentas"); tree_diario.heading("P", text="Parcial"); tree_diario.heading("D", text="Debe"); tree_diario.heading("H", text="Haber")
tree_diario.column("F", width=100, anchor="center"); tree_diario.column("C", width=300); tree_diario.column("P", width=100, anchor="e"); tree_diario.column("D", width=100, anchor="e"); tree_diario.column("H", width=100, anchor="e")
s_dia = ttk.Scrollbar(f_der, orient="vertical", command=tree_diario.yview); tree_diario.configure(yscrollcommand=s_dia.set)
s_dia.pack(side=tk.RIGHT, fill=tk.Y); tree_diario.pack(fill=tk.BOTH, expand=True)

f_crud = tk.Frame(f_der); f_crud.pack(fill=tk.X, pady=5)
tk.Button(f_crud, text="✏️ Editar Asiento", bg="#fcf8e3", command=editar_asiento).pack(side=tk.LEFT, padx=5)
tk.Button(f_crud, text="🗑️ Eliminar Asiento", bg="#f2dede", command=eliminar_asiento).pack(side=tk.LEFT, padx=5)

# --------- PESTAÑA 3: MAYOR ---------
tk.Label(tab_mayor, text=empresa, font=("Arial", 16, "bold")).pack(pady=5)
tk.Label(tab_mayor, text="Libro mayor del 23 de Enero al 20 de Marzo de 2026", font=("Arial", 12, "bold")).pack(pady=5)

canvas_mayor = tk.Canvas(tab_mayor, bg="#f4f4f4"); scrollbar_mayor = ttk.Scrollbar(tab_mayor, orient="vertical", command=canvas_mayor.yview)
scrollable_mayor = tk.Frame(canvas_mayor, bg="#f4f4f4")
scrollable_mayor.bind("<Configure>", lambda e: canvas_mayor.configure(scrollregion=canvas_mayor.bbox("all")))
canvas_mayor.create_window((0, 0), window=scrollable_mayor, anchor="nw")
canvas_mayor.configure(yscrollcommand=scrollbar_mayor.set)
canvas_mayor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); scrollbar_mayor.pack(side=tk.RIGHT, fill=tk.Y)

# --------- PESTAÑA 4: BALANZA ---------
tk.Label(tab_balanza, text=empresa, font=("Arial", 16, "bold")).pack(pady=5)
tk.Label(tab_balanza, text="Balanza de comprobación al 20 de marzo de 2026", font=("Arial", 12)).pack(pady=5)
tree_balanza = ttk.Treeview(tab_balanza, columns=("C", "MD", "MA", "SD", "SA"), show="headings", height=25)
tree_balanza.heading("C", text="Cuentas"); tree_balanza.heading("MD", text="Movimiento Deudor"); tree_balanza.heading("MA", text="Movimiento Acreedor"); tree_balanza.heading("SD", text="Saldo Deudor"); tree_balanza.heading("SA", text="Saldo Acreedor")
tree_balanza.column("C", width=300)
for col in ("MD", "MA", "SD", "SA"): tree_balanza.column(col, width=150, anchor="e")
tree_balanza.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# --------- PESTAÑA 5: DEPRECIACIÓN ---------
tk.Label(tab_depreciacion, text=empresa, font=("Arial", 16, "bold")).pack(pady=5)
tk.Label(tab_depreciacion, text="Analisis de depreciacion al 04 de marzo de 2026", font=("Arial", 12, "bold")).pack(pady=5)

f_add_dep = tk.LabelFrame(tab_depreciacion, text="Agregar Nuevo Activo a Depreciar", padx=10, pady=10)
f_add_dep.pack(fill=tk.X, padx=20, pady=10)
tk.Label(f_add_dep, text="Cuenta:").grid(row=0, column=0, padx=5); combo_dep_cuenta = ttk.Combobox(f_add_dep, values=list(activo_no_circulante.keys()), width=25); combo_dep_cuenta.grid(row=0, column=1, padx=5)
tk.Label(f_add_dep, text="Inversión Original ($):").grid(row=0, column=2, padx=5); entry_dep_inv = tk.Entry(f_add_dep); entry_dep_inv.grid(row=0, column=3, padx=5)
tk.Label(f_add_dep, text="% Anual:").grid(row=0, column=4, padx=5); entry_dep_tasa = tk.Entry(f_add_dep, width=10); entry_dep_tasa.grid(row=0, column=5, padx=5)
tk.Button(f_add_dep, text="Agregar Activo", bg="#d9edf7", command=agregar_datos_depreciacion).grid(row=0, column=6, padx=15)
tree_depreciacion = ttk.Treeview(tab_depreciacion, columns=("C", "I", "T", "DA", "DM"), show="headings", height=15)
tree_depreciacion.heading("C", text="Cuenta"); tree_depreciacion.heading("I", text="Inversión"); tree_depreciacion.heading("T", text="% Anual"); tree_depreciacion.heading("DA", text="Depreciación Anual"); tree_depreciacion.heading("DM", text="Depreciación Mensual")
tree_depreciacion.column("C", width=250)
for col in ("I", "T", "DA", "DM"): tree_depreciacion.column(col, width=150, anchor="e")
tree_depreciacion.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# --------- PESTAÑA 6: ESTADO DE RESULTADOS ---------
tk.Label(tab_resultados, text=empresa, font=("Arial", 16, "bold")).pack(pady=5)
tk.Label(tab_resultados, text="Estado de resultados al 20 de marzo de 2026", font=("Arial", 12)).pack(pady=5)

tree_resultados = ttk.Treeview(tab_resultados, columns=("C", "1", "2", "3", "4"), show="headings", height=25)
tree_resultados.heading("C", text="Concepto")
for i in range(1, 5): tree_resultados.heading(str(i), text=str(i)); tree_resultados.column(str(i), width=120, anchor="e")
tree_resultados.column("C", width=300)
tree_resultados.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)

# --------- PESTAÑA 7: BALANCE GENERAL FINAL ---------
tk.Label(tab_balance, text=empresa, font=("Arial", 16, "bold")).pack(pady=5)
tk.Label(tab_balance, text="Estado de Situación Financiera al 20 de marzo de 2026", font=("Arial", 12)).pack(pady=5)

tree_balance_unico = ttk.Treeview(tab_balance, columns=("CA", "A1", "A2", "A3", "A4", "CP", "P1", "P2", "P3", "P4"), show="headings", height=25)
tree_balance_unico.heading("CA", text="Cuenta de Activo")
tree_balance_unico.heading("A1", text="1")
tree_balance_unico.heading("A2", text="2")
tree_balance_unico.heading("A3", text="3")
tree_balance_unico.heading("A4", text="4")

tree_balance_unico.heading("CP", text="Cuenta de Pasivo / Capital")
tree_balance_unico.heading("P1", text="1")
tree_balance_unico.heading("P2", text="2")
tree_balance_unico.heading("P3", text="3")
tree_balance_unico.heading("P4", text="4")

tree_balance_unico.column("CA", width=250)
for col in ("A1", "A2", "A3", "A4"): tree_balance_unico.column(col, width=90, anchor="e")
tree_balance_unico.column("CP", width=250)
for col in ("P1", "P2", "P3", "P4"): tree_balance_unico.column(col, width=90, anchor="e")

tree_balance_unico.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

f_firmas = tk.Frame(tab_balance)
f_firmas.pack(fill=tk.X, padx=150, pady=20)

f_auth = tk.Frame(f_firmas)
f_auth.pack(side=tk.LEFT, expand=True)
tk.Label(f_auth, text="Autorizado por:", font=("Arial", 11, "bold")).pack()
tk.Label(f_auth, text="_______________________________________").pack(pady=(30, 5))
tk.Label(f_auth, text="Nuria Gonzalez Zuñiga", font=("Arial", 10)).pack()
tk.Label(f_auth, text="Supervisor", font=("Arial", 10)).pack()

f_elab = tk.Frame(f_firmas)
f_elab.pack(side=tk.RIGHT, expand=True)
tk.Label(f_elab, text="Elaborado por:", font=("Arial", 11, "bold")).pack()
tk.Label(f_elab, text="_______________________________________").pack(pady=(30, 5))
tk.Label(f_elab, text="Luis Fernando Vargas Ocaña", font=("Arial", 10)).pack()
tk.Label(f_elab, text="Propietario", font=("Arial", 10)).pack()

# EVENTOS
def _on_mousewheel(event):
    try:
        if notebook.index(notebook.select()) == 2:
            canvas_mayor.yview_scroll(int(-1*(event.delta/120)), "units")
    except: pass

ventana.bind_all("<MouseWheel>", _on_mousewheel)

limpiar()
ventana.mainloop()