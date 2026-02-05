<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import BaseAdmin from '../components/BaseAdmin.vue';

const usuarios = ref([]);
const loading = ref(true);
const search = ref('');

const API_URL = 'http://localhost:8000/api1/personas/';

// 🔐 DATOS DEL USUARIO LOGUEADO
const rolUsuario = localStorage.getItem('usuario_rol');
const subProgramaJefe = localStorage.getItem('usuario_sub_programa');

// 1️⃣ CARGAR USUARIOS
const fetchUsuarios = async () => {
    try {
        const response = await axios.get(API_URL);
        usuarios.value = response.data;
    } catch (error) {
        console.error('Error cargando usuarios:', error);
    } finally {
        loading.value = false;
    }
};

// 2️⃣ FILTRADO POR ROL + SUBPROGRAMA + BUSQUEDA
const estudiantesFiltrados = computed(() => {
    return usuarios.value.filter(user => {

        // 👉 Solo estudiantes
        if (user.rol !== 'ESTUDIANTE') return false;

        // 👉 Si es JEFE_SUB_PROGRAMA, filtrar por su subprograma
        if (rolUsuario === 'JEFE_SUB_PROGRAMA') {
            if (!user.sub_programa) return false;
            if (user.sub_programa.nombre !== subProgramaJefe) return false;
        }

        // 👉 Búsqueda
        const texto = search.value.toLowerCase();
        return (
            user.nombre.toLowerCase().includes(texto) ||
            user.apellido.toLowerCase().includes(texto) ||
            user.username.toLowerCase().includes(texto) ||
            user.ci.includes(search.value)
        );
    });
});

// 3️⃣ ELIMINAR USUARIO
const eliminarUsuario = async (user) => {
    const result = await Swal.fire({
        title: '¿ELIMINAR ESTUDIANTE?',
        text: `Esta acción borrará a ${user.nombre} ${user.apellido} permanentemente del sistema.`,
        icon: 'warning',
        showCancelButton: true,
        background: '#0a0a10',
        color: '#fff',
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'SÍ, ELIMINAR',
        cancelButtonText: 'CANCELAR',
        reverseButtons: true
    });

    if (!result.isConfirmed) return;

    try {
        await axios.delete(`${API_URL}${user.id}/`);
        usuarios.value = usuarios.value.filter(u => u.id !== user.id);

        await Swal.fire({
            title: 'ELIMINADO',
            text: 'El estudiante ha sido removido con éxito.',
            icon: 'success',
            background: '#0a0a10',
            color: '#fff',
            confirmButtonColor: '#e11d48'
        });
    } catch (error) {
        console.error('Error al eliminar:', error);
        Swal.fire({
            title: 'ERROR',
            text: 'No se pudo completar la operación.',
            icon: 'error',
            background: '#0a0a10',
            color: '#fff'
        });
    }
};

// 4️⃣ AVATAR
const getAvatar = (user) => {
    if (user.imagen) return user.imagen;
    return `https://ui-avatars.com/api/?name=${user.nombre}+${user.apellido}&background=e11d48&color=fff&bold=true`;
};

onMounted(fetchUsuarios);
</script>

<template>
    <BaseAdmin>
        <div class="mb-10 flex flex-col xl:flex-row xl:items-center justify-between gap-6">
            <div>
                <h1 class="text-3xl font-black italic tracking-tighter text-white uppercase">
                    Base de <span class="text-rose-500">Estudiantes</span>
                </h1>
                <p class="text-gray-500 text-xs font-bold uppercase tracking-[0.2em] mt-1">
                    Control de identidades registradas
                </p>
            </div>

            <div class="relative group max-w-md w-full">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-rose-500">🔍</span>
                <input v-model="search" type="text" placeholder="BUSCAR ESTUDIANTE..."
                    class="w-full bg-[#0a0a10] border border-white/10 rounded-2xl py-3 pl-12 pr-4 text-[10px] font-black text-white uppercase tracking-widest focus:outline-none focus:border-rose-500/50 transition-all shadow-2xl" />
            </div>
        </div>

        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
            <div class="w-10 h-10 border-2 border-rose-500/20 border-t-rose-500 rounded-full animate-spin"></div>
        </div>

        <div v-else-if="estudiantesFiltrados.length > 0"
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-4">
            <div v-for="user in estudiantesFiltrados" :key="user.id"
                class="bg-[#050505] border border-white/5 rounded-2xl p-4 hover:border-rose-500/30 transition-all duration-300 group relative">

                <button @click="eliminarUsuario(user)"
                    class="absolute top-3 right-3 w-8 h-8 rounded-lg bg-rose-500/10 text-rose-500 flex items-center justify-center opacity-0 group-hover:opacity-100 hover:bg-rose-500 hover:text-white transition-all duration-300 z-20"
                    title="Eliminar Registro">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 6h18m-2 0v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                    </svg>
                </button>

                <div class="flex items-center gap-4 relative z-10">
                    <div class="relative shrink-0">
                        <img :src="getAvatar(user)"
                            class="w-14 h-14 rounded-xl object-cover border border-white/10 group-hover:border-rose-500/40 transition-colors shadow-lg" />
                        <div
                            class="absolute -bottom-1 -right-1 w-4 h-4 bg-[#050505] rounded-full flex items-center justify-center">
                            <div class="w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_5px_#10b981]"></div>
                        </div>
                    </div>

                    <div class="overflow-hidden">
                        <h3 class="text-white font-black uppercase tracking-tighter text-sm truncate">
                            {{ user.nombre }} {{ user.apellido }}
                        </h3>
                        <p class="text-rose-500 text-[10px] font-bold uppercase italic tracking-tighter">@{{
                            user.username }}</p>
                    </div>
                </div>

                <div class="mt-4 pt-4 border-t border-white/5 space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[8px] text-gray-500 uppercase font-black tracking-[0.2em]">Cédula</span>
                        <span class="text-gray-300 text-[10px] font-bold">{{ user.ci }}</span>
                    </div>
                    <div class="flex flex-col gap-1">
                        <span class="text-[8px] text-gray-500 uppercase font-black tracking-[0.2em]">Sub-Programa</span>
                        <span
                            class="text-white text-[10px] font-bold leading-tight bg-white/5 p-2 rounded-lg border border-white/5">
                            {{ user.sub_programa.nombre }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="text-center py-24 bg-[#0a0a10] rounded-3xl border border-dashed border-white/5">
            <div class="text-4xl mb-4">🛡️</div>
            <p class="text-gray-500 text-xs font-black uppercase tracking-[0.3em]">No hay estudiantes registrados</p>
        </div>
    </BaseAdmin>
</template>