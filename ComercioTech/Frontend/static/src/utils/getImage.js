import imgAlmacenamiento from '../assets/almacenamiento.png';
import imgAudifonos from '../assets/audifonos.webp';
import imgComputador from '../assets/computador_sobremesa.webp';
import imgCpu from '../assets/cpu.webp';
import imgEnchufe from '../assets/enchufe_inteligente.jpg';
import imgEscritorio from '../assets/escritorio.jpg';
import imgGpu from '../assets/gpu.webp';
import imgMonitor from '../assets/monitor.webp';
import imgMouse from '../assets/mouse.webp';
import imgNotebook from '../assets/notebook.webp';
import imgPilas from '../assets/pilas recargables.webp';
import imgPowerbank from '../assets/powerbank.webp';
import imgRam from '../assets/ram.jpg';
import imgSilla from '../assets/silla.webp';
import imgSoftware from '../assets/software.png';
import imgSwitch from '../assets/switch.webp';
import imgTeclado from '../assets/teclado.png';

export function getProductImage(item) {
    if (!item) return "/placeholder.png";

    const sku = (item.sku || "").toUpperCase();
    const tipo = (item.atributos?.tipo_producto || "").toLowerCase();
    const nombre = (item.nombre || "").toLowerCase();
    const categoria = (item.categoria || "").toLowerCase();

    // 1. Mapeo por prefijo de SKU
    if (sku.startsWith("DESK")) return imgComputador;
    if (sku.startsWith("LAP")) return imgNotebook;
    if (sku.startsWith("MOB")) return imgNotebook;
    if (sku.startsWith("PROC")) return imgCpu;
    if (sku.startsWith("GPU")) return imgGpu;
    if (sku.startsWith("RAM")) return imgRam;
    if (sku.startsWith("STO")) return imgAlmacenamiento;
    if (sku.startsWith("ESC")) return imgEscritorio;
    if (sku.startsWith("SIL")) return imgSilla;
    if (sku.startsWith("NET")) return imgSwitch; 
    if (sku.startsWith("SWI")) return imgSwitch; 
    if (sku.startsWith("PWR")) return imgPilas; 
    if (sku.startsWith("PBK")) return imgPowerbank;
    if (sku.startsWith("SMT")) return imgEnchufe; 
    if (sku.startsWith("MON")) return imgMonitor;
    if (sku.startsWith("MOU")) return imgMouse;
    if (sku.startsWith("AUD")) return imgAudifonos;
    if (sku.startsWith("SOFT")) return imgSoftware;

    // 2. Mapeo por Categoría Principal (fuerte)
    if (categoria.includes("sobremesa") || categoria.includes("computador")) return imgComputador;
    if (categoria.includes("laptop") || categoria.includes("notebook")) return imgNotebook;
    if (categoria.includes("software")) return imgSoftware;
    if (categoria.includes("teclado")) return imgTeclado;
    if (categoria.includes("escritorio")) return imgEscritorio;
    if (categoria.includes("silla")) return imgSilla;

    // 3. Mapeo por Tipo de Producto
    if (tipo.includes("procesador")) return imgCpu;
    if (tipo.includes("gráfica")) return imgGpu;
    if (tipo.includes("ram")) return imgRam;
    if (tipo.includes("almacenamiento")) return imgAlmacenamiento;
    if (tipo.includes("escritorio")) return imgEscritorio;
    if (tipo.includes("silla")) return imgSilla;
    if (tipo.includes("red") || tipo.includes("switch")) return imgSwitch;
    if (tipo.includes("pila") || tipo.includes("batería")) return imgPilas;
    if (tipo.includes("powerbank")) return imgPowerbank;
    if (tipo.includes("enchufe")) return imgEnchufe;
    if (tipo.includes("monitor")) return imgMonitor;
    if (tipo.includes("teclado")) return imgTeclado;
    if (tipo.includes("mouse")) return imgMouse;
    if (tipo.includes("ear") || tipo.includes("audífono") || tipo.includes("auricular")) return imgAudifonos;

    // 4. Mapeo por Nombre (débil, prioridades ordenadas)
    if (nombre.includes("computador") || nombre.includes("pc ") || nombre.includes("desktop")) return imgComputador;
    if (nombre.includes("notebook") || nombre.includes("laptop") || nombre.includes("macbook")) return imgNotebook;
    if (nombre.includes("procesador") || nombre.includes("ryzen") || nombre.includes("intel core")) return imgCpu;
    if (nombre.includes("rtx") || nombre.includes("rx ") || nombre.includes("radeon") || nombre.includes("geforce")) return imgGpu;
    if (nombre.includes("ram ") || nombre.includes("ddr")) return imgRam;
    if (nombre.includes("ssd") || nombre.includes("hdd") || nombre.includes("nvme")) return imgAlmacenamiento;
    if (nombre.includes("escritorio") || nombre.includes("desk")) return imgEscritorio; // 'desktop' ya fue atrapado arriba
    if (nombre.includes("silla") || nombre.includes("chair")) return imgSilla;
    if (nombre.includes("router")) return imgSwitch;
    if (nombre.includes("pila")) return imgPilas;
    if (nombre.includes("powerbank") || nombre.includes("power bank")) return imgPowerbank;
    if (nombre.includes("enchufe") || nombre.includes("smart plug")) return imgEnchufe;
    if (nombre.includes("monitor")) return imgMonitor;
    if (nombre.includes("teclado") || nombre.includes("keyboard")) return imgTeclado;
    if (nombre.includes("mouse") || nombre.includes("ratón")) return imgMouse;
    if (nombre.includes("audífono") || nombre.includes("auricular") || nombre.includes("headset")) return imgAudifonos;
    if (nombre.includes("software") || nombre.includes("windows") || nombre.includes("office") || nombre.includes("antivirus")) return imgSoftware;
    
    return "/placeholder.png";
}
