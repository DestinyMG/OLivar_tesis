<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import { useRoute, useRouter } from 'vue-router';
import BaseAdmin from '../components/BaseAdmin.vue';

const route = useRoute();
const router = useRouter();
const incidenciaId = route.params.id;

const incidencia = ref(null);
const mensajes = ref([]);
const loading = ref(true);

const nuevoMensaje = ref('');
const nuevasImagenes = ref([]);
const previews = ref([]);

/* ----------------------------------
   DATOS DE SESIÓN
---------------------------------- */
const accessToken = localStorage.getItem('access_token');
const usuarioNombre = localStorage.getItem('usuario_nombre') || '';
const usuarioApellido = localStorage.getItem('usuario_apellido') || '';
const usuarioRol = localStorage.getItem('usuario_rol') || '';

/* ----------------------------------
   TEXTO SEGÚN ROL
---------------------------------- */
const generarPrefijoAutor = () => {
    if (usuarioRol === 'JEFE_SUB_PROGRAMA') {
        return `Prof. ${usuarioNombre} ${usuarioApellido} ha respondido`;
    }
    return `${usuarioNombre} ${usuarioApellido} ha respondido`;
};

/* ----------------------------------
   Cargar incidencia y mensajes
---------------------------------- */
const fetchIncidencia = async () => {
    loading.value = true;
    try {
        const response = await axios.get(
            `http://localhost:8000/api3/incidencias/${incidenciaId}/`,
            { headers: { Authorization: `Bearer ${accessToken}` } }
        );
        incidencia.value = response.data;
        mensajes.value = response.data.mensajes || [];
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            title: 'Error',
            text: 'No se pudo cargar.',
            icon: 'error',
            background: '#0a0a10',
            color: '#fff'
        });
        router.back();
    } finally {
        loading.value = false;
    }
};

/* ----------------------------------
   Manejar selección de archivos (Con Preview)
---------------------------------- */
const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    files.forEach(file => {
        nuevasImagenes.value.push(file);
        const reader = new FileReader();
        reader.onload = (e) => previews.value.push(e.target.result);
        reader.readAsDataURL(file);
    });
};

const removePreview = (index) => {
    nuevasImagenes.value.splice(index, 1);
    previews.value.splice(index, 1);
};

/* ----------------------------------
   Enviar mensaje + imágenes
---------------------------------- */
const enviarMensaje = async () => {
    if (!nuevoMensaje.value && nuevasImagenes.value.length === 0) {
        Swal.fire({
            title: 'Vacio',
            text: 'Escribe algo o adjunta una imagen.',
            icon: 'warning',
            background: '#0a0a10',
            color: '#fff'
        });
        return;
    }

    try {
        // 1️⃣ Crear mensaje
        const formDataMensaje = new FormData();
        formDataMensaje.append('incidencia', incidenciaId);
        formDataMensaje.append('texto', `${generarPrefijoAutor()}\n\n${nuevoMensaje.value}`);

        const responseMensaje = await axios.post(
            'http://localhost:8000/api3/mensajes/',
            formDataMensaje,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${accessToken}`
                }
            }
        );

        const mensajeCreado = responseMensaje.data;

        // 2️⃣ Subir imágenes asociadas al mensaje
        for (const file of nuevasImagenes.value) {
            const formDataImagen = new FormData();
            formDataImagen.append('mensaje', mensajeCreado.id);
            formDataImagen.append('imagen', file);

            await axios.post(
                'http://localhost:8000/api3/mensaje-imagenes/',
                formDataImagen,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                        Authorization: `Bearer ${accessToken}`
                    }
                }
            );
        }

        // 3️⃣ Actualizar UI
        nuevoMensaje.value = '';
        nuevasImagenes.value = [];
        previews.value = [];

        await fetchIncidencia(); // recarga mensajes y sus imágenes

    } catch (error) {
        console.error(error);
        Swal.fire({
            title: 'Error',
            text: 'Fallo al enviar el mensaje o las imágenes.',
            icon: 'error',
            background: '#0a0a10',
            color: '#fff'
        });
    }
};

onMounted(fetchIncidencia);
</script>


<template>
    <BaseAdmin>
        <div class="relative min-h-[calc(100vh-80px)] flex flex-col">
            <!-- LOADING -->
            <div v-if="loading" class="flex-1 flex items-center justify-center text-rose-500 font-black animate-pulse">
                CARGANDO EXPEDIENTE...
            </div>

            <div v-else class="flex-1 w-full max-w-4xl mx-auto p-6 pb-40">
                <!-- INFORMACIÓN DE INCIDENCIA -->
                <div class="bg-[#0a0a10] border border-white/10 p-10 rounded-[2.5rem] mb-10 shadow-2xl relative">
                    <h2
                        class="text-white text-3xl font-black mb-8 uppercase italic tracking-tighter text-center border-b border-white/5 pb-6">
                        {{ incidencia.tipo_incidencia?.replace(/_/g, ' ') || 'DETALLE DE SOLICITUD' }}
                    </h2>

                    <div
                        class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10 bg-white/[0.02] p-8 rounded-3xl border border-white/5 text-[11px] font-bold uppercase tracking-widest">
                        <div class="space-y-3">
                            <p><span class="text-rose-500">Nombre:</span> <span class="text-white">{{
                                incidencia.persona?.nombre }}</span></p>
                            <p><span class="text-rose-500">Apellido:</span> <span class="text-white">{{
                                incidencia.persona?.apellido }}</span></p>
                        </div>
                        <div class="space-y-3 text-right md:text-left">
                            <p><span class="text-rose-500">C.I:</span> <span class="text-white">{{
                                incidencia.persona?.ci }}</span></p>
                            <p><span class="text-rose-500">Programa:</span> <span class="text-white">{{
                                incidencia.persona?.sub_programa?.nombre }}</span></p>
                        </div>
                    </div>

                    <div class="mb-10 text-center">
                        <p class="text-[10px] text-rose-500 font-black uppercase tracking-widest mb-4">Descripción del
                            Hecho:</p>
                        <p
                            class="text-gray-300 italic text-sm whitespace-pre-wrap leading-relaxed bg-white/5 p-6 rounded-2xl border border-white/5">
                            {{ incidencia.descripcion }}
                        </p>
                    </div>

                    <div v-if="incidencia.imagenes?.length > 0" class="space-y-8 flex flex-col items-center">
                        <img v-for="img in incidencia.imagenes" :key="img.id" :src="img.imagen"
                            class="w-full h-auto object-contain rounded-2xl border border-white/10 shadow-2xl" />
                    </div>
                </div>

                <!-- MENSAJES -->
                <div class="space-y-8">
                    <div v-for="msg in mensajes" :key="msg.id"
                        class="bg-[#050505] border border-white/5 p-8 rounded-[2.5rem] shadow-lg">
                        <p class="text-gray-200 text-sm whitespace-pre-wrap leading-relaxed mb-6">{{ msg.texto }}</p>
                        <div v-if="msg.imagenes?.length > 0" class="flex flex-col items-center gap-8 my-6">
                            <img v-for="img in msg.imagenes" :key="img.id" :src="img.imagen"
                                class="w-full h-auto object-contain rounded-2xl border border-white/10 shadow-xl" />
                        </div>
                        <p class="text-gray-600 text-[9px] font-black uppercase mt-4 text-right tracking-[0.2em]">
                            {{ new Date(msg.fecha).toLocaleString('es-ES') }}
                        </p>
                    </div>
                </div>
            </div>

            <!-- INPUT MENSAJE -->
            <div class="sticky bottom-6 w-full max-w-4xl mx-auto px-4 mt-auto">
                <div
                    class="bg-[#111118]/95 backdrop-blur-2xl border border-white/15 p-4 rounded-[3rem] shadow-[0_0_50px_rgba(0,0,0,0.8)]">
                    <div v-if="previews.length" class="flex gap-4 p-4 overflow-x-auto mb-2 custom-scrollbar">
                        <div v-for="(p, idx) in previews" :key="idx" class="relative flex-shrink-0">
                            <img :src="p" class="w-20 h-20 object-cover rounded-xl border border-rose-500/50" />
                            <button @click="removePreview(idx)"
                                class="absolute -top-2 -right-2 bg-rose-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs shadow-lg">✕</button>
                        </div>
                    </div>

                    <div class="flex items-center gap-4 px-2">
                        <label class="cursor-pointer group flex-shrink-0">
                            <div
                                class="w-12 h-12 flex items-center justify-center bg-white/5 hover:bg-rose-600/20 rounded-full border border-white/10 group-hover:border-rose-500/50 transition-all">
                                <span class="text-xl">📎</span>
                            </div>
                            <input type="file" multiple accept="image/*" class="hidden" @change="handleFileChange">
                        </label>

                        <textarea v-model="nuevoMensaje" placeholder="Escribir respuesta oficial..."
                            class="flex-1 bg-transparent border-none text-white text-sm py-3 outline-none resize-none max-h-32 min-h-[48px] custom-scrollbar"></textarea>

                        <button @click="enviarMensaje"
                            class="w-12 h-12 bg-rose-600 hover:bg-rose-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all active:scale-90 flex-shrink-0 shadow-[0_0_15px_rgba(225,29,72,0.4)]">
                            🚀
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </BaseAdmin>
</template>

<style scoped>
/* Scrollbar para que no rompa el diseño */
::-webkit-scrollbar {
    width: 4px;
    height: 4px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(225, 29, 72, 0.4);
    border-radius: 10px;
}

textarea::-webkit-scrollbar {
    width: 0px;
}
</style>