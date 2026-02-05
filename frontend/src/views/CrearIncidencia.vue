<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import BaseAdmin from '../components/BaseAdmin.vue';

// --- Formulario de Incidencia ---
const form = ref({
    persona_id: null, // Ajustado para que coincida con el Serializer (source='persona')
    tipo_incidencia: '',
    descripcion: '',
    estado: 'CREADA'
});

const imagenesSeleccionadas = ref([]);
const previews = ref([]);
const enviando = ref(false);

// Opciones de tipo de incidencia
const TIPO_INCIDENCIA_CHOICES = [
    { value: 'INSCRIPCION_TEMPORAL', label: 'Inscripción Temporal' },
    { value: 'REINGRESO', label: 'Reingreso' },
    { value: 'CARGA_NOTAS_TEMPORAL', label: 'Carga de Notas Temporal' },
    { value: 'AUTO_ESTUDIO', label: 'Auto Estudio' },
    { value: 'PRUEBA_GLOBAL', label: 'Prueba Global' },
    { value: 'DENUNCIA', label: 'Denuncia' },
    { value: 'INTERSEMESTRAL', label: 'Solicitud de Intersemestral' },
];

// --- Al montar el componente, cargamos el ID ---
onMounted(() => {
    const usuarioId = localStorage.getItem('usuario_id');
    if (usuarioId) {
        form.value.persona_id = usuarioId;
    } else {
        console.error("⚠️ No se encontró usuario_id en localStorage");
    }
});

// --- Manejo de selección de imágenes ---
const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    files.forEach(file => {
        imagenesSeleccionadas.value.push(file);
        const reader = new FileReader();
        reader.onload = (e) => previews.value.push(e.target.result);
        reader.readAsDataURL(file);
    });
};

const removeImage = (index) => {
    imagenesSeleccionadas.value.splice(index, 1);
    previews.value.splice(index, 1);
};

// --- Confirmación y Envío ---
const crearIncidencia = async () => {
    if (!form.value.persona_id) {
        Swal.fire({
            title: 'Error de Sesión',
            text: 'No se puede identificar al autor. Por favor, inicie sesión nuevamente.',
            icon: 'error',
            background: '#0a0a10',
            color: '#fff'
        });
        return;
    }

    const result = await Swal.fire({
        title: '¿ESTÁ SEGURO?',
        html: `
            <div class="text-left text-xs p-2">
                <p class="mb-4 text-gray-300">¿Desea formalizar este reporte en el sistema?</p>
                <div class="bg-rose-500/10 border-l-4 border-rose-500 p-4">
                    <p class="text-rose-500 font-black uppercase tracking-widest mb-1">Advertencia:</p>
                    <p class="text-white italic">Reportar información falsa puede acarrear sanciones disciplinarias.</p>
                </div>
            </div>
        `,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'SÍ, ENVIAR',
        cancelButtonText: 'CANCELAR',
        background: '#0a0a10',
        color: '#fff',
        reverseButtons: true
    });

    if (result.isConfirmed) {
        procesarEnvio();
    }
};

const procesarEnvio = async () => {
    enviando.value = true;

    // Mostramos loader de SweetAlert
    Swal.fire({
        title: 'Procesando...',
        text: 'Enviando reporte y archivos...',
        allowOutsideClick: false,
        background: '#0a0a10',
        color: '#fff',
        didOpen: () => Swal.showLoading()
    });

    const formData = new FormData();
    // 🚩 IMPORTANTE: 'persona_id' es el nombre que espera tu Serializer ahora
    formData.append('persona_id', form.value.persona_id);
    formData.append('tipo_incidencia', form.value.tipo_incidencia);
    formData.append('descripcion', form.value.descripcion);
    formData.append('estado', form.value.estado);

    // Adjuntar imágenes
    imagenesSeleccionadas.value.forEach(file => {
        formData.append('nuevas_imagenes', file);
    });

    try {
        await axios.post('http://localhost:8000/api3/incidencias/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });

        Swal.fire({
            title: '¡REPORTE GENERADO!',
            text: 'La incidencia ha sido registrada correctamente.',
            icon: 'success',
            background: '#0a0a10',
            color: '#fff',
            confirmButtonColor: '#10b981'
        });

        // Reiniciar campos
        form.value.tipo_incidencia = '';
        form.value.descripcion = '';
        imagenesSeleccionadas.value = [];
        previews.value = [];

    } catch (error) {
        console.error("Error backend:", error.response?.data);

        // Formatear mensaje de error para mostrar al usuario
        let errorMsg = "Ocurrió un error inesperado.";
        if (error.response?.data) {
            errorMsg = Object.entries(error.response.data)
                .map(([key, val]) => `${key.toUpperCase()}: ${val}`)
                .join('\n');
        }

        Swal.fire({
            title: 'Fallo al registrar',
            text: errorMsg,
            icon: 'error',
            background: '#0a0a10',
            color: '#fff'
        });
    } finally {
        enviando.value = false;
    }
};
</script>

<template>
    <BaseAdmin>
        <div class="max-w-5xl mx-auto">
            <div class="mb-10 border-l-4 border-rose-500 pl-6">
                <h1 class="text-4xl font-black italic tracking-tighter text-white uppercase">
                    Nueva <span class="text-rose-500">Solicitud</span>
                </h1>
                <p class="text-gray-500 text-[10px] font-black uppercase tracking-[0.4em] mt-1">
                    Módulo de Incidencias Administrativas
                </p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div class="lg:col-span-2 space-y-6">
                    <div class="bg-[#0a0a10]/60 backdrop-blur-xl border border-white/5 p-8 rounded-3xl shadow-2xl">
                        <form @submit.prevent="crearIncidencia" class="space-y-8">

                            <div class="space-y-3">
                                <label class="text-[10px] font-black text-rose-500 uppercase tracking-widest">
                                    Tipo de Incidencia
                                </label>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <div v-for="tipo in TIPO_INCIDENCIA_CHOICES" :key="tipo.value"
                                        @click="form.tipo_incidencia = tipo.value" :class="[
                                            'cursor-pointer p-4 rounded-xl border text-[9px] font-black uppercase tracking-widest transition-all text-center flex items-center justify-center min-h-[50px]',
                                            form.tipo_incidencia === tipo.value
                                                ? 'bg-rose-600 border-rose-500 text-white shadow-[0_0_15px_rgba(225,29,72,0.4)]'
                                                : 'bg-white/5 border-white/10 text-gray-500 hover:border-white/20'
                                        ]">
                                        {{ tipo.label }}
                                    </div>
                                </div>
                            </div>

                            <div class="space-y-3">
                                <label class="text-[10px] font-black text-rose-500 uppercase tracking-widest">
                                    Descripción Detallada
                                </label>
                                <textarea v-model="form.descripcion" required rows="6"
                                    placeholder="Explique detalladamente su situación..."
                                    class="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-5 text-white text-xs font-bold focus:border-rose-500/50 outline-none transition-all resize-none shadow-inner"></textarea>
                            </div>

                            <button type="submit" :disabled="enviando || !form.tipo_incidencia"
                                class="w-full py-5 bg-rose-600 hover:bg-rose-700 disabled:bg-gray-800 disabled:text-gray-500 text-white text-xs font-black uppercase tracking-[0.3em] rounded-2xl transition-all shadow-lg active:scale-95">
                                {{ enviando ? 'PROCESANDO ENVÍO...' : 'CONFIRMAR Y ENVIAR REPORTE' }}
                            </button>
                        </form>
                    </div>
                </div>

                <div class="space-y-6">
                    <div class="bg-[#0a0a10]/60 border border-white/5 p-6 rounded-3xl">
                        <h2
                            class="text-[10px] font-black text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <span class="w-2 h-2 bg-rose-500 rounded-full animate-pulse"></span>
                            Evidencia Digital
                        </h2>

                        <label class="group cursor-pointer block">
                            <div
                                class="border-2 border-dashed border-white/10 group-hover:border-rose-500/40 rounded-2xl p-10 transition-all text-center bg-white/[0.02]">
                                <div class="text-4xl mb-4 group-hover:scale-110 transition-transform">🖼️</div>
                                <span
                                    class="text-[9px] font-black text-gray-500 uppercase tracking-widest group-hover:text-rose-500">
                                    Adjuntar Imágenes
                                </span>
                            </div>
                            <input type="file" multiple accept="image/*" class="hidden" @change="handleFileChange">
                        </label>

                        <div class="mt-8 grid grid-cols-2 gap-4">
                            <div v-for="(img, index) in previews" :key="index" class="relative group aspect-square">
                                <img :src="img" class="w-full h-full object-cover rounded-2xl border border-white/10" />
                                <button @click="removeImage(index)"
                                    class="absolute -top-2 -right-2 w-7 h-7 bg-rose-600 text-white rounded-full text-[10px] flex items-center justify-center shadow-2xl opacity-0 group-hover:opacity-100 transition-all active:scale-90">
                                    ✕
                                </button>
                            </div>
                        </div>

                        <div v-if="previews.length === 0"
                            class="mt-6 text-center border border-dashed border-white/5 rounded-xl py-10">
                            <p class="text-[8px] text-gray-700 font-black uppercase tracking-widest italic">
                                Sin archivos seleccionados
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </BaseAdmin>
</template>