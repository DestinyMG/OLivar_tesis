<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import BaseAdmin from '../components/BaseAdmin.vue';

const solicitudes = ref([]);
const loading = ref(true);

// 🔐 DATOS DEL USUARIO LOGUEADO
const rolUsuario = localStorage.getItem('usuario_rol');
const subProgramaJefe = localStorage.getItem('usuario_sub_programa');

// URLs
const API_PREREGISTROS = 'http://localhost:8000/api2/preregistros/';
const API_PERSONAS = 'http://localhost:8000/api1/personas/';

// 1️⃣ CARGAR PREREGISTROS
const fetchPreregistros = async () => {
    try {
        const response = await axios.get(API_PREREGISTROS);
        solicitudes.value = response.data;
    } catch (error) {
        console.error('Error cargando solicitudes:', error);
    } finally {
        loading.value = false;
    }
};

// 2️⃣ FILTRADO POR SUBPROGRAMA (SEGÚN ROL)
const solicitudesFiltradas = computed(() => {
    if (rolUsuario === 'ADMIN') return solicitudes.value;
    if (rolUsuario === 'JEFE_SUB_PROGRAMA') {
        return solicitudes.value.filter(item => item.sub_programa === subProgramaJefe);
    }
    return [];
});

// 3️⃣ CONFIRMAR Y MIGRAR
const confirmarUsuario = async (item) => {
    const result = await Swal.fire({
        title: '¿Confirmar Registro?',
        text: `Se creará el usuario oficial para ${item.nombre} ${item.apellido}.`,
        icon: 'question',
        showCancelButton: true,
        background: '#0a0a10',
        color: '#fff',
        confirmButtonColor: '#10b981',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'Sí, registrar',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    });

    if (!result.isConfirmed) return;

    try {
        // 🛠 MAPEADO CORRECTO DE CAMPOS (Incluyendo Email)
        const datosPersona = {
            nombre: item.nombre,
            apellido: item.apellido,
            ci: item.ci,
            email: item.email,        // <-- Agregado para la migración
            username: item.username,
            rol: 'ESTUDIANTE',
            imagen: null,
            password: item.password,
            sub_programa_id: item.sub_programa_id
        };

        console.log("Migrando datos con email:", datosPersona.email);

        // 1. Crear la persona oficial en la API 1
        await axios.post(API_PERSONAS, datosPersona);

        // 2. Si lo anterior funcionó, borrar el preregistro de la API 2
        await axios.delete(`${API_PREREGISTROS}${item.id}/`);

        solicitudes.value = solicitudes.value.filter(s => s.id !== item.id);

        Swal.fire({
            title: '¡Usuario Registrado!',
            text: 'El estudiante ya puede iniciar sesión con su correo o usuario.',
            icon: 'success',
            background: '#0a0a10',
            color: '#fff'
        });

    } catch (error) {
        console.error('Error detallado:', error.response?.data);
        const data = error.response?.data;
        let msg = "No se pudo procesar.";
        if (data) {
            msg = Object.entries(data).map(([k, v]) => `${k}: ${v}`).join('\n');
        }

        Swal.fire({
            title: 'Error de Servidor',
            text: msg,
            icon: 'error',
            background: '#0a0a10',
            color: '#fff'
        });
    }
};

// 4️⃣ RECHAZAR
const eliminarRegistro = async (id) => {
    const result = await Swal.fire({
        title: '¿Rechazar Solicitud?',
        text: 'Esta acción borrará el preregistro permanentemente.',
        icon: 'warning',
        showCancelButton: true,
        background: '#0a0a10',
        color: '#fff',
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    });

    if (!result.isConfirmed) return;

    try {
        await axios.delete(`${API_PREREGISTROS}${id}/`);
        solicitudes.value = solicitudes.value.filter(item => item.id !== id);

        Swal.fire({
            title: 'Eliminado',
            text: 'La solicitud fue rechazada.',
            icon: 'success',
            background: '#0a0a10',
            color: '#fff'
        });
    } catch (error) {
        console.error('Error al eliminar:', error);
    }
};

onMounted(fetchPreregistros);
</script>

<template>
    <BaseAdmin>
        <div class="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h1 class="text-3xl font-black italic tracking-tighter text-white uppercase">
                    Solicitudes de <span class="text-rose-500">Acceso</span>
                </h1>
                <p class="text-gray-500 text-xs font-bold uppercase tracking-[0.2em] mt-1">
                    Validación de Preregistros de Usuarios
                </p>
            </div>
            <div class="flex items-center gap-3 bg-white/5 border border-white/10 px-4 py-2 rounded-xl">
                <span class="text-rose-500 animate-pulse text-xl">●</span>
                <span class="text-[10px] font-black uppercase tracking-widest text-gray-300">
                    {{ solicitudesFiltradas.length }} Pendientes
                </span>
            </div>
        </div>

        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
            <div class="w-12 h-12 border-4 border-rose-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-rose-500 text-xs font-black uppercase tracking-[0.3em]">Sincronizando Base de Datos...</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div v-for="item in solicitudesFiltradas" :key="item.id"
                class="group relative bg-[#0a0a10] border border-white/5 rounded-2xl p-6 transition-all duration-500 hover:border-rose-500/40 hover:bg-[#0d0d15]">

                <div class="relative z-10 space-y-4">
                    <div class="flex justify-between items-start">
                        <div class="flex items-center gap-3">
                            <div
                                class="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-xl">
                                👤
                            </div>
                            <div>
                                <h3 class="text-white font-black uppercase tracking-tighter leading-tight text-sm">
                                    {{ item.nombre }} {{ item.apellido }}
                                </h3>
                                <p class="text-rose-500 text-[10px] font-bold uppercase italic">@{{ item.username }}</p>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 gap-3 py-4 border-y border-white/5">
                        <div class="flex justify-between items-center">
                            <span class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Cédula</span>
                            <span class="text-gray-200 text-xs font-bold tracking-tighter">{{ item.ci }}</span>
                        </div>
                        <div class="flex flex-col gap-1">
                            <span class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Correo
                                Electrónico</span>
                            <span class="text-rose-400 text-[11px] font-medium truncate">{{ item.email }}</span>
                        </div>
                        <div class="flex flex-col gap-1">
                            <span class="text-[9px] text-gray-500 uppercase font-black tracking-widest">Programa</span>
                            <span class="text-gray-200 text-[10px] font-bold">{{ item.sub_programa }}</span>
                        </div>
                    </div>

                    <div class="flex gap-3 pt-2">
                        <button @click="confirmarUsuario(item)"
                            class="flex-1 bg-emerald-500/10 hover:bg-emerald-500 text-emerald-500 hover:text-white border border-emerald-500/20 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-emerald-500/5">
                            Confirmar
                        </button>
                        <button @click="eliminarRegistro(item.id)"
                            class="flex-1 bg-rose-500/10 hover:bg-rose-600 text-rose-500 hover:text-white border border-rose-500/20 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-lg shadow-rose-500/5">
                            Rechazar
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="!loading && solicitudesFiltradas.length === 0"
            class="text-center py-32 bg-white/[0.02] border border-dashed border-white/10 rounded-3xl">
            <p class="text-gray-500 font-black uppercase tracking-[0.3em] text-xs">No hay solicitudes en espera</p>
        </div>
    </BaseAdmin>
</template>