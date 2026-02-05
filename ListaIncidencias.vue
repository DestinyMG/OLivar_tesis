<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import BaseAdmin from '../components/BaseAdmin.vue';

const incidencias = ref([]);
const loading = ref(true);
const search = ref('');
const incidenciaSeleccionada = ref(null);

/* ----------------------------------
   DATOS DEL USUARIO
---------------------------------- */
const usuarioRol = localStorage.getItem('usuario_rol') || '';
const usuarioSubPrograma = localStorage.getItem('usuario_sub_programa') || '';
const usuarioCI = localStorage.getItem('usuario_ci') || '';

/* ----------------------------------
   CARGAR INCIDENCIAS
---------------------------------- */
const fetchData = async () => {
    loading.value = true;
    try {
        const resInc = await axios.get('http://localhost:8000/api3/incidencias/');
        incidencias.value = resInc.data;
    } catch (error) {
        console.error("Error cargando incidencias:", error);
    } finally {
        loading.value = false;
    }
};

/* ----------------------------------
   LÓGICA DE BORRADO (6 HORAS)
---------------------------------- */
const puedeBorrar = (fechaCreacion) => {
    if (usuarioRol !== 'ESTUDIANTE') return false;

    const ahora = new Date();
    const creacion = new Date(fechaCreacion);
    const diferenciaMs = ahora - creacion;
    const seisHorasEnMs = 6 * 60 * 60 * 1000;

    return diferenciaMs < seisHorasEnMs;
};

const eliminarIncidencia = async (id) => {
    const result = await Swal.fire({
        title: '¿ELIMINAR INCIDENCIA?',
        text: "Esta acción no se puede deshacer.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'SÍ, ELIMINAR',
        background: '#0a0a10',
        color: '#fff'
    });

    if (result.isConfirmed) {
        try {
            await axios.delete(`http://localhost:8000/api3/incidencias/${id}/`);
            incidencias.value = incidencias.value.filter(i => i.id !== id);
            Swal.fire({
                title: 'Eliminado',
                icon: 'success',
                background: '#0a0a10',
                color: '#fff',
                timer: 1500,
                showConfirmButton: false
            });
        } catch (error) {
            Swal.fire('Error', 'No se pudo eliminar el ticket', 'error');
        }
    }
};

/* ----------------------------------
   OBTENER INFORMACIÓN DE LA PERSONA
---------------------------------- */
const getPersonaInfo = (personaObj) => {
    if (!personaObj) {
        return { nombre: 'N/A', apellido: '', ci: '---', sub_programa: { nombre: '---' }, imagen: null };
    }
    return personaObj;
};

const getAvatar = (p) => {
    return p.imagen ? p.imagen : `https://ui-avatars.com/api/?name=${p.nombre}+${p.apellido}&background=e11d48&color=fff&bold=true`;
};

/* ----------------------------------
   FILTRADO
---------------------------------- */
const incidenciasFiltradas = computed(() => {
    return incidencias.value.filter(i => {
        const persona = getPersonaInfo(i.persona);

        // 1. Filtrar por rol
        if (usuarioRol === 'JEFE_SUB_PROGRAMA') {
            if (persona.sub_programa.nombre !== usuarioSubPrograma) return false;
        } else if (usuarioRol === 'ESTUDIANTE') {
            if (persona.ci !== usuarioCI) return false;
        }

        // 2. Filtrar por búsqueda
        const term = search.value.toLowerCase();
        return i.id.toString().includes(term) ||
            i.tipo_incidencia.toLowerCase().includes(term) ||
            persona.ci.toLowerCase().includes(term);
    });
});

const formatTipo = (tipo) => tipo.replace(/_/g, ' ');
const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('es-ES', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
};

onMounted(fetchData);
</script>

<template>
    <BaseAdmin>
        <div class="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
                <h1 class="text-3xl font-black italic tracking-tighter text-white uppercase">
                    Central de <span class="text-rose-500">Tickets</span>
                </h1>
                <p class="text-gray-500 text-[10px] font-black uppercase tracking-[0.3em] mt-1">Sincronizado con
                    Incidencias</p>
            </div>

            <div class="relative max-w-md w-full">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-rose-500">🔍</span>
                <input v-model="search" type="text" placeholder="BUSCAR POR ID, TIPO O C.I..."
                    class="w-full bg-[#0a0a10] border border-white/10 rounded-2xl py-3 pl-12 pr-4 text-[10px] font-black text-white uppercase tracking-widest focus:border-rose-500/50 outline-none transition-all" />
            </div>
        </div>

        <div v-if="loading" class="flex justify-center py-20">
            <div class="w-10 h-10 border-2 border-rose-500/20 border-t-rose-500 rounded-full animate-spin"></div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <div v-for="inc in incidenciasFiltradas" :key="inc.id"
                class="bg-[#050505] border border-white/5 rounded-3xl p-6 hover:border-rose-500/30 transition-all group relative overflow-hidden">

                <div class="flex justify-between items-start mb-6">
                    <span
                        class="text-[9px] font-black bg-white/5 text-gray-400 px-3 py-1 rounded-lg border border-white/5">
                        #ID-{{ inc.id }}
                    </span>

                    <div class="flex items-center gap-2">
                        <button v-if="puedeBorrar(inc.fecha_creacion)" @click="eliminarIncidencia(inc.id)"
                            class="w-6 h-6 flex items-center justify-center rounded-lg bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white transition-all text-xs"
                            title="Eliminar (Plazo 6h)">
                            ✕
                        </button>

                        <span :class="[
                            'text-[8px] font-black px-2 py-1 rounded-md uppercase tracking-widest',
                            inc.estado === 'CREADA' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'
                        ]">
                            {{ inc.estado }}
                        </span>
                    </div>
                </div>

                <div class="space-y-4">
                    <div>
                        <h3
                            class="text-white font-black text-xs uppercase tracking-widest leading-tight h-10 line-clamp-2 italic">
                            {{ formatTipo(inc.tipo_incidencia) }}
                        </h3>
                        <p class="text-gray-500 text-[9px] font-bold mt-2 uppercase tracking-tighter">
                            <span class="text-rose-500">FECHA:</span> {{ formatDate(inc.fecha_creacion) }}
                        </p>
                    </div>

                    <div class="pt-4 border-t border-white/5 flex gap-2">
                        <button @click="incidenciaSeleccionada = inc"
                            class="flex-1 py-3 bg-white/5 hover:bg-white/10 text-white text-[9px] font-black uppercase tracking-widest rounded-xl border border-white/5 transition-all">
                            Visualizar
                        </button>
                        <button @click="$router.push(`/chat/${inc.id}`)"
                            class="flex-1 py-3 bg-rose-600 hover:bg-rose-700 text-white text-[9px] font-black uppercase tracking-widest rounded-xl transition-all shadow-[0_5px_15px_rgba(225,29,72,0.2)]">
                            Chat
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="incidenciaSeleccionada"
            class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
            <div
                class="bg-[#0a0a10] border border-white/10 w-full max-w-2xl rounded-[2.5rem] overflow-hidden shadow-2xl">
                <div
                    class="p-8 border-b border-white/5 bg-gradient-to-r from-white/[0.02] to-transparent flex items-center justify-between">
                    <div class="flex items-center gap-5">
                        <img :src="getAvatar(getPersonaInfo(incidenciaSeleccionada.persona))"
                            class="w-16 h-16 rounded-2xl object-cover border-2 border-rose-500/30" />
                        <div>
                            <h2 class="text-white text-xl font-black uppercase italic tracking-tighter">
                                {{ getPersonaInfo(incidenciaSeleccionada.persona).nombre }} {{
                                    getPersonaInfo(incidenciaSeleccionada.persona).apellido }}
                            </h2>
                            <p
                                class="text-rose-500 text-[10px] font-black uppercase tracking-widest mt-2 flex items-center gap-2">
                                <span class="bg-rose-500 w-1 h-1 rounded-full animate-pulse"></span>
                                {{ getPersonaInfo(incidenciaSeleccionada.persona).sub_programa.nombre }}
                            </p>
                        </div>
                    </div>
                    <button @click="incidenciaSeleccionada = null"
                        class="text-gray-500 hover:text-rose-500 transition-colors text-xl">✕</button>
                </div>

                <div class="p-8 space-y-6">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                            <p class="text-[8px] text-gray-500 font-black uppercase mb-1 tracking-widest">CI Usuario</p>
                            <p class="text-white text-xs font-black">{{
                                getPersonaInfo(incidenciaSeleccionada.persona).ci }}</p>
                        </div>
                        <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                            <p class="text-[8px] text-gray-500 font-black uppercase mb-1 tracking-widest">Reportado el
                            </p>
                            <p class="text-white text-xs font-bold">{{ formatDate(incidenciaSeleccionada.fecha_creacion)
                                }}</p>
                        </div>
                    </div>
                    <div>
                        <p class="text-[8px] text-gray-500 font-black uppercase mb-2 tracking-widest">Tipo de Incidencia
                        </p>
                        <h3 class="text-rose-400 font-black text-sm uppercase italic">
                            {{ formatTipo(incidenciaSeleccionada.tipo_incidencia) }}
                        </h3>
                    </div>
                </div>

                <div class="p-6 border-t border-white/5 text-center">
                    <button @click="incidenciaSeleccionada = null"
                        class="px-14 py-4 bg-white/5 hover:bg-white/10 text-white text-[10px] font-black uppercase tracking-widest rounded-2xl border border-white/10 transition-all">
                        Cerrar Detalle
                    </button>
                </div>
            </div>
        </div>

        <div v-if="!loading && incidenciasFiltradas.length === 0" class="text-center py-20 opacity-30 italic">
            No se encontraron incidencias activas.
        </div>
    </BaseAdmin>
</template>

<style scoped>
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(225, 29, 72, 0.2);
    border-radius: 10px;
}
</style>
