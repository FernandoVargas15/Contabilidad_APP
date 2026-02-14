import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

empresa = "LufTech, S.A de C.V."
fecha_actual = datetime.now().strftime("%d de %B de %Y")


# VALORES ORIGINALES
activo_circulante_original = {
    "Caja": 50000,
    "Bancos": 2000000,
    "Inventarios": 6000000,
    "IVA Acreditable": 0,
    "IVA x Acreditar": 0,
}

activo_no_circulante_original = {
    "Terrenos": 2500000,
    "Edificios": 4000000,
    "Mobiliaria y equipo": 300000,
    "Equipo de computo electronico": 650000,
    "Equipo de entrega y reparto": 0,
    "Equipo de transporte": 500000,
    "Gastos de constitucion": 100000,
    "Gastos de instalacion": 350000,
    "Papeleria y utiles": 8000,
    "Rentas pagadas por anticipado": 30000,
}

pasivo_original = {
    "Proveedores": 0,
    "Anticipo de clientes": 0,
    "IVA Trasladado": 0,
}

capital_original = {
    "Capital Social": 16488000,
    "Utilidad": 0,
    "Perdida": 0
}

activo_circulante = activo_circulante_original.copy()
activo_no_circulante = activo_no_circulante_original.copy()
pasivo = pasivo_original.copy()
capital = capital_original.copy()

historial = []


# FUNCIONES
def registrar(texto):
    historial.append(texto)
    historial_text.insert(tk.END, texto + "\n")

def obtener_monto():
    try:
        return float(entry_monto.get())
    except:
        messagebox.showerror("Error", "Ingrese monto válido")
        return None

def obtener_porcentaje():
    try:
        return float(entry_porcentaje.get()) / 100
    except:
        messagebox.showerror("Error", "Ingrese porcentaje válido")
        return None

def actualizar_tabla():

    text_activo.delete(1.0, tk.END)
    text_pasivo.delete(1.0, tk.END)

    total_ac = sum(activo_circulante.values())
    total_anc = sum(activo_no_circulante.values())
    total_activo = total_ac + total_anc
    total_pasivo = sum(pasivo.values())
    total_capital = sum(capital.values())

    # ACTIVO
    text_activo.insert(tk.END, "ACTIVO CIRCULANTE\n\n")
    for c,v in activo_circulante.items():
        text_activo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")

    text_activo.insert(tk.END, f"\nSuma Activo Circulante: ${total_ac:,.2f}\n\n")

    text_activo.insert(tk.END, "ACTIVO NO CIRCULANTE\n\n")
    for c,v in activo_no_circulante.items():
        text_activo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")

    text_activo.insert(tk.END, f"\nSuma Activo No Circulante: ${total_anc:,.2f}\n")
    text_activo.insert(tk.END, f"\nTOTAL ACTIVO: ${total_activo:,.2f}\n\n")

    # PIE
    text_activo.insert(tk.END, "Autorizado por:                          Elaborado por:\n")
    text_activo.insert(tk.END, "_________________________         _________________________\n")
    text_activo.insert(tk.END, "Nuria Gonzalez Zuñiga               Luis Fernando Vargas Ocaña\n")
    text_activo.insert(tk.END, "Supervisor                           Propietario\n")

    # PASIVO
    text_pasivo.insert(tk.END, "PASIVO\n\n")
    for c,v in pasivo.items():
        text_pasivo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")

    text_pasivo.insert(tk.END, f"\nTotal Pasivo: ${total_pasivo:,.2f}\n\n")

    text_pasivo.insert(tk.END, "CAPITAL CONTABLE\n\n")
    for c,v in capital.items():
        text_pasivo.insert(tk.END, f"{c:<35} ${v:>15,.2f}\n")

    text_pasivo.insert(tk.END, f"\nTotal Capital: ${total_capital:,.2f}")
    text_pasivo.insert(tk.END, f"\n\nPASIVO + CAPITAL: ${total_pasivo + total_capital:,.2f}")


# OPERACIONES
def compra_efectivo():
    monto = obtener_monto()
    cuenta = combo_cuenta.get()
    if monto is None or cuenta == "":
        return

    iva = monto * 0.16
    total = monto + iva

    activo_no_circulante[cuenta] += monto
    activo_circulante["IVA Acreditable"] += iva
    activo_circulante["Bancos"] -= total

    registrar(f"Efectivo: {cuenta} ${monto:,.2f}")
    actualizar_tabla()

def compra_credito():
    monto = obtener_monto()
    cuenta = combo_cuenta.get()
    if monto is None or cuenta == "":
        return

    iva = monto * 0.16
    total = monto + iva

    activo_no_circulante[cuenta] += monto
    activo_circulante["IVA x Acreditar"] += iva
    pasivo["Proveedores"] += total

    registrar(f"Crédito: {cuenta} ${monto:,.2f}")
    actualizar_tabla()

def compra_combinada():
    monto = obtener_monto()
    porcentaje = obtener_porcentaje()
    cuenta = combo_cuenta.get()
    if monto is None or porcentaje is None or cuenta == "":
        return

    iva = monto * 0.16
    total = monto + iva

    contado = total * porcentaje
    credito = total - contado

    activo_no_circulante[cuenta] += monto
    activo_circulante["IVA Acreditable"] += iva * porcentaje
    activo_circulante["IVA x Acreditar"] += iva * (1 - porcentaje)

    activo_circulante["Bancos"] -= contado
    pasivo["Proveedores"] += credito

    registrar(f"Combinada: {cuenta} ${monto:,.2f}")
    actualizar_tabla()

def anticipo_clientes():
    monto = obtener_monto()
    porcentaje = obtener_porcentaje()
    if monto is None or porcentaje is None:
        return

    anticipo = monto * porcentaje
    iva = anticipo * 0.16

    activo_circulante["Bancos"] += anticipo + iva
    pasivo["Anticipo de clientes"] += anticipo
    pasivo["IVA Trasladado"] += iva

    registrar(f"Anticipo: ${anticipo:,.2f}")
    actualizar_tabla()

def limpiar():
    global activo_circulante, activo_no_circulante, pasivo, capital
    activo_circulante = activo_circulante_original.copy()
    activo_no_circulante = activo_no_circulante_original.copy()
    pasivo = pasivo_original.copy()
    capital = capital_original.copy()
    historial.clear()
    historial_text.delete(1.0, tk.END)
    actualizar_tabla()


# INTERFAZ
ventana = tk.Tk()
ventana.title("Sistema Contable Profesional")
ventana.geometry("1500x900")

tk.Label(ventana, text=empresa, font=("Arial",20,"bold")).pack()
tk.Label(ventana, text=f"Estado de situación financiera al {fecha_actual}").pack()

frame_input = tk.Frame(ventana)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Monto:").grid(row=0,column=0)
entry_monto = tk.Entry(frame_input)
entry_monto.grid(row=0,column=1)

tk.Label(frame_input, text="Cuenta a comprar:").grid(row=0,column=2)
combo_cuenta = ttk.Combobox(frame_input, values=list(activo_no_circulante.keys()))
combo_cuenta.grid(row=0,column=3)

tk.Label(frame_input, text="Porcentaje (%):").grid(row=0,column=4)
entry_porcentaje = tk.Entry(frame_input)
entry_porcentaje.grid(row=0,column=5)

frame_botones = tk.Frame(ventana)
frame_botones.pack()

tk.Button(frame_botones, text="Compra Efectivo", command=compra_efectivo).grid(row=0,column=0,padx=5)
tk.Button(frame_botones, text="Compra Crédito", command=compra_credito).grid(row=0,column=1,padx=5)
tk.Button(frame_botones, text="Compra Combinada", command=compra_combinada).grid(row=0,column=2,padx=5)
tk.Button(frame_botones, text="Anticipo Clientes", command=anticipo_clientes).grid(row=0,column=3,padx=5)
tk.Button(frame_botones, text="Limpiar", command=limpiar).grid(row=0,column=4,padx=5)

# TABLA + HISTORIAL
frame_principal = tk.Frame(ventana)
frame_principal.pack(pady=15)

text_activo = tk.Text(frame_principal, width=65, height=35, font=("Courier",11))
text_activo.grid(row=0,column=0)

text_pasivo = tk.Text(frame_principal, width=65, height=35, font=("Courier",11))
text_pasivo.grid(row=0,column=1)

# HISTORIAL
frame_historial = tk.Frame(frame_principal)
frame_historial.grid(row=0,column=2,padx=20)

tk.Label(frame_historial, text="Historial", font=("Arial",12,"bold")).pack()
historial_text = tk.Text(frame_historial, width=28, height=18)
historial_text.pack()

actualizar_tabla()
ventana.mainloop()