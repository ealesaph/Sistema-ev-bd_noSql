from faker import Faker
from pymongo import MongoClient
from bson import ObjectId
from datetime import timezone
import random

fake = Faker('es_CL')

#RECUERDA VER AL FINAL LA BASE DE DATOS Y CEOLECCION A LA QUE VA DIRIGIDA LOS ARCHIVOS

# ─── Datos de dominio ────────────────────────────────────────────────────────

CATEGORIAS = {

    # ── Computación ──────────────────────────────────────────────────────────
    "laptops": {
        "etiqueta": "computadores",
        "prefijo_sku": "LAP",
        "marcas": ["Dell", "HP", "Lenovo", "Apple", "Asus", "MSI", "Acer"],
        "modelos": ["XPS 15", "Pavilion 14", "ThinkPad X1", "MacBook Pro", "ZenBook Pro", "Raider GE78", "Swift X14"],
        "atributos": lambda: {
            "ram_gb": random.choice([8, 16, 32, 64]),
            "procesador": random.choice(["Intel i5-13500H", "Intel i7-13700H", "AMD Ryzen 7 7745HX", "Apple M3", "Intel i9-13900H"]),
            "almacenamiento_gb": random.choice([256, 512, 1024, 2048]),
            "tipo_pantalla": random.choice(["IPS 14 pulgadas", "OLED 15.6 pulgadas", "Retina 16 pulgadas", "Mini-LED 16 pulgadas"]),
            "tipo_switch": None, "tipo_licencia": None,
            "tarjeta_grafica": random.choice(["RTX 4060", "RTX 4070", "RX 7600M", "Intel Iris Xe", "Apple M3 GPU"]),
            "peso_kg": round(random.uniform(1.2, 2.8), 1),
            "tipo_producto": None, "material": None, "capacidad_mah": None,
            "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "computadores_sobremesa": {
        "etiqueta": "computadores",
        "prefijo_sku": "DES",
        "marcas": ["Dell", "HP", "Lenovo", "Apple", "Asus", "MSI", "Custom Build"],
        "modelos": ["OptiPlex 7000", "EliteDesk 800", "ThinkCentre M90", "Mac Mini M3", "ProArt PA90", "MEG Trident X2", "ROG Strix GT"],
        "atributos": lambda: {
            "ram_gb": random.choice([8, 16, 32, 64, 128]),
            "procesador": random.choice(["Intel i5-14600K", "Intel i7-14700K", "Intel i9-14900K", "AMD Ryzen 5 7600X", "AMD Ryzen 9 7950X", "Apple M3 Pro"]),
            "almacenamiento_gb": random.choice([512, 1024, 2048, 4096]),
            "tipo_pantalla": None,
            "tipo_switch": None, "tipo_licencia": None,
            "tarjeta_grafica": random.choice(["RTX 4070 Ti", "RTX 4090", "RX 7900 XTX", "Intel Arc A770", "Apple M3 GPU"]),
            "peso_kg": round(random.uniform(3.5, 12.0), 1),
            "tipo_producto": None, "material": None, "capacidad_mah": None,
            "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "teclados": {
        "etiqueta": "perifericos",
        "prefijo_sku": "TEC",
        "marcas": ["Logitech", "Corsair", "Razer", "HyperX", "Keychron", "Ducky"],
        "modelos": ["K95 RGB", "BlackWidow V3", "Alloy Origins", "K8 Pro", "G Pro X", "One 3 Mini"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tarjeta_grafica": None, "peso_kg": round(random.uniform(0.4, 1.2), 1),
            "tipo_switch": random.choice(["Cherry MX Red", "Cherry MX Blue", "Gateron Yellow", "Optical Red", "Topre 45g"]),
            "tipo_licencia": None, "tipo_producto": None, "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "software": {
        "etiqueta": "software",
        "prefijo_sku": "SOF",
        "marcas": ["Microsoft", "Adobe", "Autodesk", "JetBrains", "Bitdefender", "Corel"],
        "modelos": ["Office 365", "Creative Cloud", "AutoCAD 2026", "IntelliJ IDEA", "Total Security", "CorelDRAW"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tarjeta_grafica": None,
            "tipo_licencia": random.choice(["Anual", "Perpetua", "Mensual", "Por usuario/mes"]),
            "peso_kg": None, "tipo_producto": None, "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    # ── Componentes ──────────────────────────────────────────────────────────
    "procesadores": {
        "etiqueta": "componentes",
        "prefijo_sku": "CPU",
        "marcas": ["Intel", "AMD"],
        "modelos": ["Core i5-14600K", "Core i7-14700K", "Core i9-14900K", "Ryzen 5 7600X", "Ryzen 7 7700X", "Ryzen 9 7950X"],
        "atributos": lambda: {
            "ram_gb": None, "almacenamiento_gb": None, "tipo_pantalla": None,
            "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "procesador": random.choice(["LGA1700", "AM5"]),  # socket
            "nucleos": random.choice([6, 8, 12, 16, 24]),
            "frecuencia_ghz": round(random.uniform(3.0, 5.8), 1),
            "tdp_w": random.choice([65, 105, 125, 170]),
            "peso_kg": round(random.uniform(0.05, 0.15), 2),
            "tipo_producto": "Procesador", "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "tarjetas_graficas": {
        "etiqueta": "componentes",
        "prefijo_sku": "GPU",
        "marcas": ["Nvidia", "AMD", "Intel"],
        "modelos": ["RTX 4060", "RTX 4070 Ti", "RTX 4090", "RX 7600", "RX 7900 XTX", "Arc A770"],
        "atributos": lambda: {
            "ram_gb": random.choice([8, 12, 16, 24]),  # VRAM
            "procesador": None, "almacenamiento_gb": None, "tipo_pantalla": None,
            "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tdp_w": random.choice([115, 160, 200, 285, 450]),
            "memoria_tipo": random.choice(["GDDR6", "GDDR6X"]),
            "peso_kg": round(random.uniform(0.6, 2.2), 1),
            "tipo_producto": "Tarjeta Gráfica", "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "memorias_ram": {
        "etiqueta": "componentes",
        "prefijo_sku": "RAM",
        "marcas": ["Corsair", "Kingston", "G.Skill", "Crucial", "TeamGroup"],
        "modelos": ["Vengeance DDR5", "Fury Beast DDR5", "Trident Z5 RGB", "Pro DDR5", "T-Force Delta"],
        "atributos": lambda: {
            "ram_gb": random.choice([8, 16, 32, 64]),
            "procesador": None, "almacenamiento_gb": None, "tipo_pantalla": None,
            "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "velocidad_mhz": random.choice([4800, 5200, 5600, 6000, 6400]),
            "tipo_memoria": random.choice(["DDR4", "DDR5"]),
            "cantidad_modulos": random.choice([1, 2]),
            "peso_kg": round(random.uniform(0.03, 0.1), 2),
            "tipo_producto": "Memoria RAM", "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "almacenamiento": {
        "etiqueta": "componentes",
        "prefijo_sku": "STO",
        "marcas": ["Samsung", "WD", "Seagate", "Kingston", "Crucial", "Sabrent"],
        "modelos": ["990 Pro NVMe", "Black SN850X", "Barracuda HDD", "NV2 SSD", "MX500 SSD", "Rocket 4 Plus"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None,
            "almacenamiento_gb": random.choice([500, 1000, 2000, 4000, 8000]),
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tipo_almacenamiento": random.choice(["NVMe PCIe 4.0", "NVMe PCIe 5.0", "SATA SSD", "HDD 7200RPM"]),
            "velocidad_lectura_mbs": random.choice([550, 3500, 5000, 7000]),
            "peso_kg": round(random.uniform(0.04, 0.7), 2),
            "tipo_producto": "Almacenamiento", "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    # ── Mobiliario ───────────────────────────────────────────────────────────
    "escritorios": {
        "etiqueta": "hogarOficina",
        "prefijo_sku": "ESC",
        "marcas": ["Flexispot", "Autonomous", "Ergotron", "Ikea", "Brateck", "MotionGrey"],
        "modelos": ["EG8 Standing Desk", "SmartDesk Pro", "LX Desk", "UPPSPEL", "BD-T01", "Standing Desk Pro"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "material": random.choice(["MDF", "Bambú", "Madera maciza", "Vidrio templado", "MDF con recubrimiento"]),
            "ancho_cm": random.choice([120, 140, 160, 180, 200]),
            "profundidad_cm": random.choice([60, 70, 80]),
            "altura_regulable": fake.boolean(chance_of_getting_true=50),
            "peso_kg": round(random.uniform(20.0, 65.0), 1),
            "tipo_producto": "Escritorio", "capacidad_mah": None,
            "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "sillas_oficina": {
        "etiqueta": "hogarOficina",
        "prefijo_sku": "SIL",
        "marcas": ["Herman Miller", "Secretlab", "DXRacer", "Autonomous", "Haworth", "Steelcase"],
        "modelos": ["Aeron", "Titan Evo", "OH/C588", "ErgoChair Pro", "Fern", "Leap V2"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "material": random.choice(["Malla transpirable", "Cuero PU", "Cuero genuino", "Tela premium", "Nylon"]),
            "reclinable": fake.boolean(chance_of_getting_true=80),
            "reposabrazos": random.choice(["4D", "3D", "2D", "Fijo"]),
            "peso_maximo_kg": random.choice([100, 120, 135, 150]),
            "peso_kg": round(random.uniform(10.0, 25.0), 1),
            "tipo_producto": "Silla", "capacidad_mah": None,
            "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    # ── Redes y conectividad ─────────────────────────────────────────────────
    "routers_y_redes": {
        "etiqueta": "conectividadRedes",
        "prefijo_sku": "NET",
        "marcas": ["TP-Link", "Asus", "Netgear", "Ubiquiti", "Mikrotik", "D-Link"],
        "modelos": ["Archer AX90", "RT-AX88U", "Orbi RBK863S", "UniFi Dream Machine", "hEX S", "DIR-X5460"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "velocidad_mbps": random.choice([300, 600, 1200, 2400, 4800, 9600]),
            "estandar_wifi": random.choice(["Wi-Fi 5 (802.11ac)", "Wi-Fi 6 (802.11ax)", "Wi-Fi 6E", "Wi-Fi 7"]),
            "puertos": random.choice(["4x GbE LAN + 1x WAN", "8x GbE + 2x SFP+", "4x 2.5GbE + 1x 10GbE WAN"]),
            "peso_kg": round(random.uniform(0.2, 1.5), 1),
            "tipo_producto": "Red", "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None,
        },
    },

    "switches_red": {
        "etiqueta": "conectividadRedes",
        "prefijo_sku": "SWT",
        "marcas": ["TP-Link", "Cisco", "Netgear", "Ubiquiti", "D-Link"],
        "modelos": ["TL-SG108E", "Catalyst 1000", "GS308E", "USW-Lite-8-PoE", "DGS-1210-10P"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "velocidad_mbps": random.choice([1000, 2500, 10000]),
            "puertos": random.choice(["8x GbE", "16x GbE", "24x GbE + 4x SFP", "48x GbE + 4x SFP+"]),
            "poe": fake.boolean(chance_of_getting_true=40),
            "administrable": fake.boolean(chance_of_getting_true=60),
            "peso_kg": round(random.uniform(0.4, 3.5), 1),
            "tipo_producto": "Switch", "material": None,
            "capacidad_mah": None, "velocidad_carga_w": None,
            "estandar_wifi": None,
        },
    },

    # ── Electrónica ──────────────────────────────────────────────────────────
    "baterias_y_pilas": {
        "etiqueta": "electronica",
        "prefijo_sku": "BAT",
        "marcas": ["Duracell", "Energizer", "Panasonic", "Varta", "GP Batteries"],
        "modelos": ["Optimum AA", "Ultimate Lithium", "Eneloop Pro", "Longlife Power", "ReCyko+"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tipo_producto": random.choice(["Pila AA", "Pila AAA", "Pila 9V", "Batería 18650", "Batería CR2032"]),
            "recargable": fake.boolean(chance_of_getting_true=40),
            "capacidad_mah": random.choice([800, 1000, 1500, 2000, 2500, 3000]),
            "cantidad_unidades": random.choice([2, 4, 8, 12, 16]),
            "peso_kg": round(random.uniform(0.05, 0.5), 2),
            "material": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "powerbanks": {
        "etiqueta": "electronica",
        "prefijo_sku": "PWB",
        "marcas": ["Anker", "Baseus", "Xiaomi", "RavPower", "Belkin", "Mophie"],
        "modelos": ["PowerCore 26800", "Blade 10000", "Mi Power Bank 3", "PD Pioneer 20000", "BPZ-004", "Powerstation XXL"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tipo_producto": "Powerbank",
            "capacidad_mah": random.choice([5000, 10000, 15000, 20000, 26800, 30000]),
            "velocidad_carga_w": random.choice([18, 22.5, 30, 45, 65, 100, 140]),
            "puertos": random.choice(["1x USB-A + 1x USB-C", "2x USB-A + 1x USB-C", "1x USB-C PD + 1x USB-A", "2x USB-C + 2x USB-A"]),
            "carga_inalambrica": fake.boolean(chance_of_getting_true=30),
            "peso_kg": round(random.uniform(0.18, 0.85), 2),
            "material": None, "velocidad_mbps": None,
        },
    },

    "enchufes_inteligentes": {
        "etiqueta": "electronica",
        "prefijo_sku": "SMT",
        "marcas": ["TP-Link", "Sonoff", "Meross", "Eve", "Shelly", "Amazon"],
        "modelos": ["Kasa EP25", "S40 Lite", "MSS310", "Eve Energy", "Plug S", "Smart Plug Mini"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tipo_producto": "Enchufe Inteligente",
            "potencia_maxima_w": random.choice([1100, 1800, 2300, 3680]),
            "protocolo": random.choice(["Wi-Fi 2.4GHz", "Zigbee", "Z-Wave", "Thread/Matter", "Bluetooth"]),
            "monitoreo_energia": fake.boolean(chance_of_getting_true=60),
            "compatible_voz": random.choice(["Alexa, Google Home", "Alexa, Google Home, Siri", "Google Home", "Alexa"]),
            "peso_kg": round(random.uniform(0.05, 0.25), 2),
            "material": None, "capacidad_mah": None,
            "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "pantallas": {
        "etiqueta": "perifericos",
        "prefijo_sku": "MON",
        "marcas": ["Samsung", "LG", "Dell", "BenQ", "Asus", "AOC", "MSI"],
        "modelos": ["Odyssey G7", "UltraGear 27", "U2723QE", "MOBIUZ EX2710Q", "ROG Swift PG279QM", "Q27G2S", "MAG 274QRFDE"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tipo_producto": "Monitor",
            "tipo_pantalla": random.choice([
                "IPS 24 pulgadas", "IPS 27 pulgadas", "VA 32 pulgadas",
                "OLED 27 pulgadas", "Mini-LED 32 pulgadas", "IPS 34 pulgadas ultrawide"
            ]),
            "resolucion": random.choice(["1920x1080", "2560x1440", "3840x2160", "3440x1440", "1920x1200"]),
            "frecuencia_hz": random.choice([60, 75, 144, 165, 240, 360]),
            "tiempo_respuesta_ms": random.choice([1, 2, 4, 5]),
            "hdr": random.choice(["HDR400", "HDR600", "HDR1000", "Sin HDR"]),
            "puertos": random.choice([
                "2x HDMI 2.0 + 1x DP 1.4",
                "1x HDMI 2.1 + 2x DP 1.4 + 4x USB-A",
                "2x HDMI 2.1 + 1x DP 2.0 + 1x USB-C 90W",
                "1x HDMI 1.4 + 1x VGA + 1x DP 1.2",
            ]),
            "ajuste_altura": fake.boolean(chance_of_getting_true=65),
            "peso_kg": round(random.uniform(3.5, 10.0), 1),
            "material": None, "capacidad_mah": None,
            "velocidad_carga_w": None, "velocidad_mbps": None,
        },
    },

    "mouses": {
        "etiqueta": "perifericos",
        "prefijo_sku": "MOU",
        "marcas": ["Logitech", "Razer", "SteelSeries", "Zowie", "HyperX", "Corsair", "Glorious"],
        "modelos": ["G Pro X Superlight 2", "DeathAdder V3", "Rival 650", "EC2-CW", "Pulsefire Haste 2", "Dark Core RGB Pro", "Model O Pro"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tipo_producto": "Mouse",
            "dpi_maximo": random.choice([6400, 8000, 12000, 16000, 25000, 30000]),
            "conexion": random.choice(["USB con cable", "Inalámbrico 2.4GHz", "Bluetooth", "Inalámbrico 2.4GHz + Bluetooth"]),
            "botones": random.choice([5, 6, 7, 8, 11]),
            "bateria_mah": random.choice([None, 400, 500, 800, 1000]),  # None si es con cable
            "autonomia_horas": random.choice([None, 40, 60, 70, 100, 140]),
            "sensor": random.choice(["HERO 25K", "Focus Pro 30K", "TrueMove Air", "PMW3370", "Optical XY"]),
            "peso_g": random.choice([55, 61, 68, 75, 82, 95, 110]),
            "peso_kg": round(random.uniform(0.05, 0.15), 2),
            "material": None, "capacidad_mah": None,
            "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },

    "audifonos": {
        "etiqueta": "perifericos",
        "prefijo_sku": "AUD",
        "marcas": ["Sony", "Bose", "Apple", "Samsung", "Jabra", "Sennheiser", "HyperX", "SteelSeries"],
        "modelos": ["WH-1000XM5", "QuietComfort 45", "AirPods Max", "Galaxy Buds3 Pro", "Evolve2 85", "Momentum 4", "Cloud Alpha S", "Arctis Nova Pro"],
        "atributos": lambda: {
            "ram_gb": None, "procesador": None, "almacenamiento_gb": None,
            "tipo_pantalla": None, "tipo_switch": None, "tipo_licencia": None, "tarjeta_grafica": None,
            "tipo_producto": random.choice(["Over-ear", "On-ear", "In-ear / TWS"]),
            "conexion": random.choice([
                "Bluetooth 5.3", "Bluetooth 5.2 + cable 3.5mm",
                "USB-C + Bluetooth 5.0", "Inalámbrico 2.4GHz + Bluetooth"
            ]),
            "cancelacion_ruido": fake.boolean(chance_of_getting_true=60),
            "microfono": fake.boolean(chance_of_getting_true=75),
            "capacidad_mah": random.choice([300, 500, 570, 800, 1000, 1500]),
            "autonomia_horas": random.choice([6, 8, 20, 30, 35, 40, 60]),
            "resistencia_agua": random.choice(["IPX4", "IPX5", "IP55", "Sin certificación"]),
            "respuesta_frecuencia_hz": random.choice(["20Hz-20kHz", "6Hz-22kHz", "4Hz-40kHz"]),
            "peso_kg": round(random.uniform(0.02, 0.38), 2),
            "material": None, "velocidad_carga_w": None, "velocidad_mbps": None, "puertos": None,
        },
    },
}

COLORES = ["Negro", "Blanco", "Plata", "Gris", "Azul", "Rojo", "Verde"]
VOLTAJES = ["110V", "220V", "Dual voltage", "N/A"]


# ─── Funciones generadoras ───────────────────────────────────────────────────

def generar_sku(prefijo, marca, modelo, indice):
    marca_slug  = marca.upper().replace(" ", "")[:4]
    modelo_slug = modelo.upper().replace(" ", "")[:6]
    return f"{prefijo}-{marca_slug}-{modelo_slug}-{indice:03d}"


def generar_variantes(sku_base, categoria):
    # Mobiliario y software no tienen variantes de color/voltaje relevantes
    sin_variantes = {"software", "escritorios", "sillas_oficina"}
    if categoria in sin_variantes:
        return []

    colores_elegidos = random.sample(COLORES, k=random.randint(1, 3))
    return [
        {
            "color": color,
            "voltaje": random.choice(VOLTAJES),
            "sku_variante": f"{sku_base}-{color[:2].upper()}",
            "stock": random.randint(0, 50),
        }
        for color in colores_elegidos
    ]


def generar_producto(indice, activo=False):
    categoria = random.choice(list(CATEGORIAS.keys()))
    cfg = CATEGORIAS[categoria]

    marca   = random.choice(cfg["marcas"])
    modelo  = random.choice(cfg["modelos"])
    sku     = generar_sku(cfg["prefijo_sku"], marca, modelo, indice)

    variantes   = generar_variantes(sku, categoria)
    stock_total = sum(v["stock"] for v in variantes) if variantes else random.randint(1, 100)

    fecha_creacion      = fake.date_time_between(start_date="-2y", end_date="-6M", tzinfo=timezone.utc)
    fecha_actualizacion = fake.date_time_between(start_date=fecha_creacion, end_date="now", tzinfo=timezone.utc)

    atributos_generados = cfg["atributos"]()  # <-- se llama UNA sola vez (ver nota abajo)

    return {
        "_id": ObjectId(),
        "sku": sku,
        "id_proveedor_sql": random.randint(100, 999),
        "nombre": f"{marca} {modelo}",
        "categoria": categoria,
        "etiqueta": cfg["etiqueta"],
        "descripcion": fake.sentence(nb_words=14),
        "precio_actual": random.choice(range(3990, 5000001, 1000)),
        "moneda": "CLP",
        "stock_disponible": stock_total,
        "activo": activo,  
        "atributos": atributos_generados,
        "variantes": variantes,
        "especificaciones_fabricante": {
            "garantia_meses": random.choice([3, 6, 12, 24, 36]),
            "peso_kg": atributos_generados.get("peso_kg") or round(random.uniform(0.1, 5.0), 1),
            "fabricante": marca,
        },
        "rating_promedio": round(random.uniform(1.0, 5.0), 1),
        "total_resenas": random.randint(0, 800),
        "fecha_creacion": fecha_creacion,
        "fecha_actualizacion": fecha_actualizacion,
    }

# ─── Inserción ───────────────────────────────────────────────────────────────

def seed(n=1_200_000, n_activos=250, tamano_lote=5000):
    client = MongoClient("mongodb://localhost:27017/")
    col = client["comerciotech"]["productos"]
    col.drop()

    # Elegimos al azar (sin reemplazo) qué 250 índices del total serán los activos
    indices_activos = set(random.sample(range(1, n + 1), n_activos))

    total_insertados = 0
    lote = []

    for i in range(1, n + 1):
        es_activo = i in indices_activos
        lote.append(generar_producto(i, activo=es_activo))

        if len(lote) >= tamano_lote:
            col.insert_many(lote, ordered=False)
            total_insertados += len(lote)
            print(f"  → {total_insertados:,} / {n:,} insertados...")
            lote = []

    if lote:  # insertar lo que quede en el último lote incompleto
        col.insert_many(lote, ordered=False)
        total_insertados += len(lote)

    print(f"  {total_insertados:,} productos insertados en 'comerciotech.productos'")
    print(f"  Activos: {col.count_documents({'activo': True}):,}")
    print(f"  Inactivos: {col.count_documents({'activo': False}):,}")

    # Índices útiles (se crean al final, después de insertar todo: es más rápido)
    col.create_index("sku",       unique=True)
    col.create_index("categoria")
    col.create_index("etiqueta")
    col.create_index("activo")
    print("Índices creados: sku, categoria, etiqueta, activo")

    client.close()


if __name__ == "__main__":
    seed(n=1_200_000, n_activos=250)