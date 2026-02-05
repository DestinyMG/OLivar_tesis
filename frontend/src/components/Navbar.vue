<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';

const router = useRouter();

// --- Estados del Usuario (Reactivos) ---
const nombreUsuario = ref('Cargando...');
const apellidoUsuario = ref('');
const rolUsuario = ref('');
const imagenUsuario = ref(null);
const isDropdownOpen = ref(false);

// Emisiones para el Sidebar
defineEmits(['toggle-menu']);

// --- Función para traer datos frescos del Servidor ---
const fetchUsuario = async () => {
    const id = localStorage.getItem('usuario_id');
    if (!id) return;

    try {
        const response = await axios.get(`http://localhost:8000/api1/personas/${id}/`);
        const data = response.data;

        // Actualizamos los refs con lo que diga la base de datos
        nombreUsuario.value = data.nombre;
        apellidoUsuario.value = data.apellido;
        rolUsuario.value = data.rol;
        imagenUsuario.value = data.imagen; // Aquí viene la URL de la imagen

        // Opcional: Sincronizamos localStorage por si otros componentes lo usan
        localStorage.setItem('usuario_nombre', data.nombre);
        localStorage.setItem('usuario_apellido', data.apellido);
        localStorage.setItem('usuario_rol', data.rol);
        if (data.imagen) localStorage.setItem('usuario_imagen', data.imagen);

    } catch (error) {
        console.error("Error al obtener datos del usuario:", error);
        // Si falla la API, intentamos usar lo que haya en localStorage como respaldo
        nombreUsuario.value = localStorage.getItem('usuario_nombre') || 'Usuario';
        rolUsuario.value = localStorage.getItem('usuario_rol') || 'Invitado';
    }
};

onMounted(() => {
    fetchUsuario();
});

// --- Lógica de Imagen (Prioriza API, luego Genérica) ---
const avatarSrc = computed(() => {
    if (imagenUsuario.value && imagenUsuario.value !== 'null') {
        return imagenUsuario.value;
    }
    // Si no hay imagen, generamos un avatar con DiceBear usando el nombre
    return `https://api.dicebear.com/7.x/bottts-neutral/svg?seed=${nombreUsuario.value}`;
});

const cerrarSesion = async () => {
    const result = await Swal.fire({
        title: '¿CERRAR SESIÓN?',
        text: "Tu sesión actual será finalizada.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'SÍ, SALIR',
        background: '#0a0a10',
        color: '#fff',
        reverseButtons: true
    });

    if (result.isConfirmed) {
        localStorage.clear();
        delete axios.defaults.headers.common['Authorization'];
        router.push('/login');
    }
};
</script>

<template>
    <nav
        class="h-20 flex items-center justify-between px-4 md:px-8 sticky top-0 z-[100] bg-[#050505]/80 backdrop-blur-xl border-b border-rose-500/20">

        <div class="flex items-center gap-4">
            <button @click="$emit('toggle-menu')"
                class="lg:hidden p-2 text-rose-500 hover:bg-rose-500/10 rounded-xl transition-colors outline-none">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
            </button>

            <div class="flex items-center gap-3">
                <div
                    class="w-10 h-10 md:w-11 md:h-11 bg-gradient-to-tr from-rose-600 to-orange-500 rounded-xl shadow-[0_0_20px_rgba(225,29,72,0.4)] flex items-center justify-center shrink-0">
                    <span class="text-white text-xl">⚠️</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-lg md:text-xl font-black tracking-tighter text-white leading-none uppercase">
                        HELP<span class="text-rose-500">DESK</span>
                    </span>
                    <span class="text-[8px] md:text-[9px] font-bold text-gray-500 uppercase tracking-[0.3em]">
                        Incidencias
                    </span>
                </div>
            </div>
        </div>

        <div class="relative">
            <button @click="isDropdownOpen = !isDropdownOpen"
                class="flex items-center gap-3 md:gap-4 p-1.5 md:p-2 md:pl-4 rounded-2xl bg-white/5 border border-white/10 hover:border-rose-400/50 transition-all outline-none">

                <div class="text-right hidden sm:block">
                    <p class="text-xs font-black uppercase text-white">
                        {{ nombreUsuario }} {{ apellidoUsuario }}
                    </p>
                    <p class="text-[10px] text-rose-500 font-bold uppercase tracking-widest">
                        {{ rolUsuario.replace('_', ' ') }}
                    </p>
                </div>

                <div class="relative shrink-0">
                    <img :src="avatarSrc"
                        class="w-9 h-9 md:w-10 md:h-10 rounded-xl bg-rose-900/20 border border-rose-500/30 object-cover" />
                    <div
                        class="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-[#050505] rounded-full shadow-[0_0_8px_#22c55e]">
                    </div>
                </div>
            </button>

            <transition enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-150 ease-in" leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0">

                <div v-if="isDropdownOpen"
                    class="absolute right-0 mt-4 w-56 bg-[#0a0a10]/95 border border-white/10 rounded-2xl p-2 shadow-2xl backdrop-blur-2xl overflow-hidden ring-1 ring-white/5">

                    <div class="px-4 py-2 mb-1">
                        <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Cuenta</p>
                    </div>

                    <router-link to="/perfil" @click="isDropdownOpen = false"
                        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold text-gray-300 hover:bg-rose-500/10 hover:text-white transition-all group no-underline">
                        <span class="text-gray-400 group-hover:text-rose-500">👤</span>
                        <span>Perfil</span>
                    </router-link>

                    <div class="h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent my-2"></div>

                    <button @click="cerrarSesion"
                        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold text-rose-500 hover:bg-rose-500/10 transition-all group">
                        <span class="group-hover:rotate-12 transition-transform">🔌</span>
                        <span>Cerrar Sesión</span>
                    </button>
                </div>
            </transition>
        </div>
    </nav>
</template>