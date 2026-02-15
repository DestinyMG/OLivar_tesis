// src/services/ReporteInstitucional.js
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

export class ReporteInstitucional {
    constructor(config) {
        this.doc = new jsPDF('l', 'mm', 'a4');
        this.subprograma = config.subprograma;
        this.periodo = config.periodo;
        this.logoUrl = "/logo_universidad.png"; // Asegúrate de tenerlo en public/
    }

    // Dibujar el encabezado de la Universidad
    dibujarMembrete() {
        // --- Rectángulo Decorativo Superior ---
        this.doc.setFillColor(225, 29, 72); // Tu color Rose-500
        this.doc.rect(0, 0, 297, 3, 'F');

        // --- Títulos Institucionales ---
        this.doc.setFont("helvetica", "bold");
        this.doc.setFontSize(14);
        this.doc.setTextColor(40, 40, 40);
        this.doc.text("REPÚBLICA BOLIVARIANA DE VENEZUELA", 148.5, 15, { align: "center" });
        this.doc.text("UNIVERSIDAD NACIONAL EXPERIMENTAL DE LOS LLANOS", 148.5, 22, { align: "center" });
        this.doc.setFontSize(12);
        this.doc.text("VICERRECTORADO DE PRODUCCIÓN AGRÍCOLA", 148.5, 29, { align: "center" });

        // --- Línea Divisoria ---
        this.doc.setDrawColor(200, 200, 200);
        this.doc.line(14, 35, 283, 35);
    }

    dibujarFooter() {
        const pageCount = this.doc.internal.getNumberOfPages();
        const width = this.doc.internal.pageSize.width;
        const height = this.doc.internal.pageSize.height;

        for (let i = 1; i <= pageCount; i++) {
            this.doc.setPage(i);

            // Línea superior del footer
            this.doc.setDrawColor(225, 29, 72);
            this.doc.line(14, height - 20, width - 14, height - 20);

            this.doc.setFontSize(8);
            this.doc.setTextColor(100);
            this.doc.setFont("helvetica", "normal");
            this.doc.text(`Reporte generado por el Sistema de Incidencias - Subprograma ${this.subprograma}`, 14, height - 15);
            this.doc.text(`Página ${i} de ${pageCount}`, width - 30, height - 15);

            // Sello de validación (opcional)
            this.doc.setFontSize(7);
            this.doc.text("ESTE DOCUMENTO ES UNA COPIA ELECTRÓNICA VÁLIDA", width / 2, height - 10, { align: "center" });
        }
    }

    generar(data) {
        this.dibujarMembrete();

        // Título del Reporte
        this.doc.setFontSize(16);
        this.doc.setTextColor(225, 29, 72);
        this.doc.text(`REPORTE DE INCIDENCIAS: ${this.subprograma}`, 14, 45);

        this.doc.setFontSize(9);
        this.doc.setTextColor(80);
        this.doc.text(`PERIODO AUDITADO: ${this.periodo.inicio} AL ${this.periodo.fin}`, 14, 51);

        // Tabla de datos
        autoTable(this.doc, {
            startY: 55,
            head: [['ID', 'TIPO DE INCIDENCIA', 'ESTADO', 'SOLICITANTE', 'CÉDULA', 'FECHA REGISTRO']],
            body: data.map(inc => [
                `#${inc.id}`,
                inc.tipo_incidencia.replace(/_/g, ' '),
                inc.estado,
                `${inc.persona.nombre} ${inc.persona.apellido}`,
                inc.persona.ci,
                new Date(inc.fecha_creacion).toLocaleDateString('es-ES')
            ]),
            theme: 'grid',
            headStyles: { fillColor: [30, 30, 30], textColor: [255, 255, 255], fontStyle: 'bold' },
            styles: { fontSize: 8, font: "helvetica" },
            columnStyles: {
                2: { fontStyle: 'bold' }, // Columna de Estado en Negrita
            },
            didParseCell: function (data) {
                // Colorear el texto según el estado
                if (data.section === 'body' && data.column.index === 2) {
                    if (data.cell.raw === 'RESUELTA') data.cell.styles.textColor = [22, 163, 74];
                    if (data.cell.raw === 'RECHAZADA') data.cell.styles.textColor = [220, 38, 38];
                    if (data.cell.raw === 'ABIERTA') data.cell.styles.textColor = [202, 138, 4];
                }
            }
        });

        this.dibujarFooter();
        this.doc.save(`REPORTE_${this.subprograma}_${Date.now()}.pdf`);
    }
}