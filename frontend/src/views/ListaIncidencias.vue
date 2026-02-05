<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import BaseAdmin from '../components/BaseAdmin.vue';

const incidencias = ref([]);
const loading = ref(true);
const search = ref('');
const incidenciaSeleccionada = ref(null);
const mostrarHistorial = ref(false); // Control para mostrar historial

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
   LÓGICA DE ESTADOS (COLORES)
---------------------------------- */
const getEstadoClass = (estado) => {
    switch (estado) {
        case 'CREADA':
        case 'ABIERTA':
            return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
        case 'RECHAZADA':
            return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
        case 'RESUELTA':
            return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
        default:
            return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
};

/* ----------------------------------
   CAMBIAR ESTADO (CORRECCIÓN DE SELECT)
---------------------------------- */
const cambiarEstado = async (incidencia) => {
    const { value: nuevoEstado } = await Swal.fire({
        title: 'GESTIONAR ESTADO',
        input: 'select',
        inputOptions: {
            'CREADA': 'CREADA',
            'ABIERTA': 'ABIERTA',
            'RESUELTA': 'RESUELTA',
            'RECHAZADA': 'RECHAZADA'
        },
        inputValue: incidencia.estado,
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#1f2937',
        confirmButtonText: 'ACTUALIZAR',
        background: '#0a0a10',
        color: '#fff',
        customClass: {
            input: 'custom-swal-select'
        }
    });

    if (nuevoEstado) {
        try {
            await axios.patch(`http://localhost:8000/api3/incidencias/${incidencia.id}/`, {
                estado: nuevoEstado
            });
            incidencias.value = incidencias.value.map(i =>
                i.id === incidencia.id ? { ...i, estado: nuevoEstado } : i
            );
            Swal.fire({
                title: 'Estado Actualizado',
                icon: 'success',
                background: '#0a0a10',
                color: '#fff',
                timer: 1500,
                showConfirmButton: false
            });
        } catch (error) {
            Swal.fire('Error', 'No se pudo actualizar', 'error');
        }
    }
};

/* ----------------------------------
   LÓGICA DE BORRADO (6 HORAS)
---------------------------------- */
const puedeBorrar = (fechaCreacion) => {
    if (usuarioRol !== 'ESTUDIANTE') return false;
    const ahora = new Date();
    const creacion = new Date(fechaCreacion);
    return (ahora - creacion) < (6 * 60 * 60 * 1000);
};

const eliminarIncidencia = async (id) => {
    const result = await Swal.fire({
        title: '¿ELIMINAR?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        background: '#0a0a10',
        color: '#fff'
    });

    if (result.isConfirmed) {
        try {
            await axios.delete(`http://localhost:8000/api3/incidencias/${id}/`);
            incidencias.value = incidencias.value.filter(i => i.id !== id);
        } catch (error) {
            console.error(error);
        }
    }
};

/* ----------------------------------
   HELPERS
---------------------------------- */
const getPersonaInfo = (personaObj) => personaObj || { nombre: 'N/A', apellido: '', ci: '---', sub_programa: { nombre: '---' } };
const getAvatar = (p) => p.imagen ? p.imagen : `https://ui-avatars.com/api/?name=${p.nombre}+${p.apellido}&background=e11d48&color=fff&bold=true`;
const formatTipo = (tipo) => tipo.replace(/_/g, ' ');
const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

/* ----------------------------------
   FILTRADO DE INCIDENCIAS
---------------------------------- */
const incidenciasFiltradas = computed(() => {
    let filtradas = incidencias.value.filter(i => {
        const persona = getPersonaInfo(i.persona);

        // Filtro por rol
        if (usuarioRol === 'JEFE_SUB_PROGRAMA') {
            if (persona.sub_programa.nombre !== usuarioSubPrograma) return false;

            // Si NO está viendo el historial, excluir rechazadas/resueltas
            if (!mostrarHistorial.value && (i.estado === 'RECHAZADA' || i.estado === 'RESUELTA')) {
                return false;
            }

            // Si SÍ está viendo el historial, solo mostrar rechazadas/resueltas
            if (mostrarHistorial.value && i.estado !== 'RECHAZADA' && i.estado !== 'RESUELTA') {
                return false;
            }

        } else if (usuarioRol === 'ESTUDIANTE') {
            if (persona.ci !== usuarioCI) return false;
        }

        // Filtro de búsqueda
        const term = search.value.toLowerCase();
        return i.id.toString().includes(term) ||
            i.tipo_incidencia.toLowerCase().includes(term) ||
            persona.ci.toLowerCase().includes(term);
    });

    // Ordenar historial: primero resueltas, luego rechazadas
    if (mostrarHistorial.value) {
        filtradas.sort((a, b) => {
            if (a.estado === 'RESUELTA' && b.estado === 'RECHAZADA') return -1;
            if (a.estado === 'RECHAZADA' && b.estado === 'RESUELTA') return 1;
            return 0;
        });
    }

    return filtradas;
});

/* ----------------------------------
   CONTADORES PARA BOTONES
---------------------------------- */
const contarIncidenciasActivas = computed(() => {
    if (usuarioRol !== 'JEFE_SUB_PROGRAMA') return 0;

    return incidencias.value.filter(i => {
        const persona = getPersonaInfo(i.persona);
        return persona.sub_programa.nombre === usuarioSubPrograma &&
            (i.estado === 'CREADA' || i.estado === 'ABIERTA');
    }).length;
});

const contarIncidenciasHistorial = computed(() => {
    if (usuarioRol !== 'JEFE_SUB_PROGRAMA') return 0;

    return incidencias.value.filter(i => {
        const persona = getPersonaInfo(i.persona);
        return persona.sub_programa.nombre === usuarioSubPrograma &&
            (i.estado === 'RECHAZADA' || i.estado === 'RESUELTA');
    }).length;
});

onMounted(fetchData);
</script>

<template>
    <BaseAdmin>
        <div class="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
                <h1 class="text-3xl font-black italic tracking-tighter text-white uppercase leading-none">
                    Central de <span class="text-rose-500">Tickets</span>
                </h1>
                <p class="text-gray-500 text-[10px] font-black uppercase tracking-[0.3em] mt-1 italic">Gestión de
                    Incidencias Operativas</p>
            </div>

            <div class="flex flex-col md:flex-row gap-4 items-center">
                <!-- Botones de filtro para JEFE_SUB_PROGRAMA -->
                <div v-if="usuarioRol === 'JEFE_SUB_PROGRAMA'" class="flex gap-2">
                    <button @click="mostrarHistorial = false" :class="[
                        'px-4 py-2 rounded-xl text-[10px] font-black uppercase border transition-all',
                        !mostrarHistorial
                            ? 'bg-rose-600 text-white border-rose-600 shadow-[0_5px_15px_rgba(225,29,72,0.3)]'
                            : 'bg-white/5 text-gray-400 border-white/10 hover:border-rose-500/30'
                    ]">
                        Activas
                        <span v-if="contarIncidenciasActivas > 0"
                            class="ml-2 px-1.5 py-0.5 bg-white/10 rounded-md text-[8px]">
                            {{ contarIncidenciasActivas }}
                        </span>
                    </button>

                    <button @click="mostrarHistorial = true" :class="[
                        'px-4 py-2 rounded-xl text-[10px] font-black uppercase border transition-all',
                        mostrarHistorial
                            ? 'bg-rose-600 text-white border-rose-600 shadow-[0_5px_15px_rgba(225,29,72,0.3)]'
                            : 'bg-white/5 text-gray-400 border-white/10 hover:border-rose-500/30'
                    ]">
                        Historial
                        <span v-if="contarIncidenciasHistorial > 0"
                            class="ml-2 px-1.5 py-0.5 bg-white/10 rounded-md text-[8px]">
                            {{ contarIncidenciasHistorial }}
                        </span>
                    </button>
                </div>

                <!-- Barra de búsqueda -->
                <div class="relative max-w-md w-full">
                    <span class="absolute left-4 top-1/2 -translate-y-1/2 text-rose-500">🔍</span>
                    <input v-model="search" type="text" placeholder="BUSCAR POR ID, TIPO O C.I..."
                        class="w-full bg-[#0a0a10] border border-white/10 rounded-2xl py-3 pl-12 pr-4 text-[10px] font-black text-white uppercase focus:border-rose-500/50 outline-none transition-all" />
                </div>
            </div>
        </div>

        <!-- Indicador de vista actual -->
        <div v-if="usuarioRol === 'JEFE_SUB_PROGRAMA'" class="mb-6">
            <div class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
                <span class="text-[10px] font-black uppercase text-gray-400">
                    Mostrando:
                </span>
                <span class="text-[10px] font-black uppercase text-rose-500">
                    {{ mostrarHistorial ? 'Historial (Resueltas/Rechazadas)' : 'Incidencias Activas (Creadas/Abiertas)'
                    }}
                </span>
                <span v-if="incidenciasFiltradas.length === 0"
                    class="text-[8px] text-gray-500 font-black uppercase ml-4">
                    No hay {{ mostrarHistorial ? 'incidencias en historial' : 'incidencias activas' }}
                </span>
            </div>
        </div>

        <div v-if="loading" class="flex justify-center py-20">
            <div class="w-10 h-10 border-2 border-rose-500/20 border-t-rose-500 rounded-full animate-spin"></div>
        </div>

        <div v-else-if="incidenciasFiltradas.length > 0"
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <div v-for="inc in incidenciasFiltradas" :key="inc.id"
                class="bg-[#050505] border border-white/5 rounded-3xl p-6 hover:border-rose-500/30 transition-all group relative overflow-hidden">

                <div class="flex justify-between items-start mb-6">
                    <span
                        class="text-[9px] font-black bg-white/5 text-gray-400 px-3 py-1 rounded-lg border border-white/5">
                        #ID-{{ inc.id }}
                    </span>

                    <div class="flex items-center gap-2">
                        <button v-if="usuarioRol === 'JEFE_SUB_PROGRAMA' && !mostrarHistorial"
                            @click="cambiarEstado(inc)"
                            class="w-6 h-6 flex items-center justify-center rounded-lg bg-white/5 text-gray-400 hover:bg-rose-500 hover:text-white transition-all text-[10px]"
                            title="Cambiar Estado">
                            📝
                        </button>

                        <button v-if="puedeBorrar(inc.fecha_creacion)" @click="eliminarIncidencia(inc.id)"
                            class="w-6 h-6 flex items-center justify-center rounded-lg bg-rose-500/10 text-rose-500 hover:bg-rose-500 transition-all text-xs">
                            ✕
                        </button>

                        <span
                            :class="['text-[8px] font-black px-2 py-1 rounded-md uppercase tracking-widest border', getEstadoClass(inc.estado)]">
                            {{ inc.estado }}
                        </span>
                    </div>
                </div>

                <div class="space-y-4">
                    <h3
                        class="text-white font-black text-xs uppercase tracking-widest leading-tight h-10 line-clamp-2 italic">
                        {{ formatTipo(inc.tipo_incidencia) }}
                    </h3>
                    <p class="text-gray-500 text-[9px] font-bold mt-2 uppercase tracking-tighter">
                        <span class="text-rose-500">FECHA:</span> {{ formatDate(inc.fecha_creacion) }}
                    </p>

                    <div class="pt-4 border-t border-white/5 flex gap-2">
                        <button @click="incidenciaSeleccionada = inc"
                            class="flex-1 py-3 bg-white/5 hover:bg-white/10 text-white text-[9px] font-black uppercase rounded-xl border border-white/5 transition-all">Visualizar</button>
                        <button @click="$router.push(`/chat/${inc.id}`)"
                            class="flex-1 py-3 bg-rose-600 hover:bg-rose-700 text-white text-[9px] font-black uppercase rounded-xl transition-all shadow-[0_5px_15px_rgba(225,29,72,0.2)]">Chat</button>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="text-center py-20">
            <div class="inline-flex flex-col items-center gap-4 p-8 rounded-3xl bg-white/5 border border-white/10">
                <span class="text-6xl text-gray-700">📭</span>
                <h3 class="text-white font-black text-sm uppercase italic">No hay incidencias disponibles</h3>
                <p class="text-gray-500 text-[10px] font-bold uppercase max-w-md">
                    {{ usuarioRol === 'JEFE_SUB_PROGRAMA'
                        ? (mostrarHistorial
                            ? 'No hay incidencias resueltas o rechazadas en tu subprograma'
                            : 'No hay incidencias activas en tu subprograma. ¡Todo está bajo control!')
                        : 'No se encontraron incidencias con los filtros actuales'
                    }}
                </p>
            </div>
        </div>

        <!-- Modal de detalle -->
        <div v-if="incidenciaSeleccionada"
            class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
            <div
                class="bg-[#0a0a10] border border-white/10 w-full max-w-2xl rounded-[2.5rem] overflow-hidden shadow-2xl">
                <div class="p-8 border-b border-white/5 flex items-center justify-between">
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
                        class="text-gray-500 hover:text-rose-500 text-xl">✕</button>
                </div>

                <div class="p-8 space-y-6">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                            <p class="text-[8px] text-gray-500 font-black uppercase mb-1 tracking-widest">CI Usuario</p>
                            <p class="text-white text-xs font-black">{{
                                getPersonaInfo(incidenciaSeleccionada.persona).ci }}</p>
                        </div>
                        <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                            <p class="text-[8px] text-gray-500 font-black uppercase mb-1 tracking-widest">Estado Actual
                            </p>
                            <p
                                :class="['text-xs font-black uppercase', getEstadoClass(incidenciaSeleccionada.estado).split(' ')[1]]">
                                {{ incidenciaSeleccionada.estado }}
                            </p>
                        </div>
                    </div>
                    <h3 class="text-rose-400 font-black text-sm uppercase italic">{{
                        formatTipo(incidenciaSeleccionada.tipo_incidencia) }}</h3>
                </div>

                <div class="p-6 border-t border-white/5 text-center">
                    <button @click="incidenciaSeleccionada = null"
                        class="px-14 py-4 bg-white/5 hover:bg-white/10 text-white text-[10px] font-black uppercase rounded-2xl border border-white/10 transition-all">Cerrar
                        Detalle</button>
                </div>
            </div>
        </div>
    </BaseAdmin>
</template>

<style>
/** IMPORTANTE: No usar 'scoped' para que afecte al modal de SweetAlert2 **/

.custom-swal-select {
    background-color: #0a0a10 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    height: 50px !important;
}

/* Forzar el color de fondo y texto de las opciones del select */
.swal2-select option {
    background-color: #0a0a10 !important;
    color: white !important;
}

/* Evitar que el sistema cambie el color al pasar el mouse */
.swal2-select:focus {
    border-color: #e11d48 !important;
    box-shadow: 0 0 0 2px rgba(225, 29, 72, 0.2) !important;
}

.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>