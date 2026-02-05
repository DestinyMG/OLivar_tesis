<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

defineProps(['isOpen'])
defineEmits(['close'])

const route = useRoute()
const totalPendientes = ref(0)

// ✅ LEER datos desde localStorage
const subProgramaJefe = ref(localStorage.getItem('usuario_sub_programa') || '')
const rolUsuario = ref(localStorage.getItem('usuario_rol') || '')

const isActive = (path) => route.path === path

const fetchCount = async () => {
    if (rolUsuario.value !== 'JEFE_SUB_PROGRAMA') return;

    try {
        const response = await axios.get('http://localhost:8000/api2/preregistros/')
        if (!subProgramaJefe.value) {
            totalPendientes.value = 0
            return
        }
        const jefeNormalizado = subProgramaJefe.value.trim().toLowerCase()
        const filtradas = response.data.filter(item => {
            if (!item.sub_programa) return false
            return item.sub_programa.trim().toLowerCase() === jefeNormalizado
        })
        totalPendientes.value = filtradas.length
    } catch (error) {
        console.error("Error al obtener conteo:", error)
    }
}

onMounted(() => {
    fetchCount()
    if (rolUsuario.value === 'JEFE_SUB_PROGRAMA') {
        setInterval(fetchCount, 30000)
    }
})
</script>

<template>
    <aside :class="[
        'fixed inset-y-0 left-0 z-[150] w-72 bg-[#050505] border-r border-white/5 p-6 transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 lg:flex lg:flex-col gap-8',
        isOpen ? 'translate-x-0 shadow-[20px_0_50px_rgba(0,0,0,0.9)]' : '-translate-x-full'
    ]">

        <button @click="$emit('close')"
            class="lg:hidden absolute top-5 right-5 w-8 h-8 flex items-center justify-center rounded-full bg-white/5 text-rose-500 border border-rose-500/20 hover:bg-rose-500 hover:text-white transition-colors">
            ✕
        </button>

        <div class="space-y-2 mt-10 lg:mt-0">
            <p
                class="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] mb-6 font-mono text-center lg:text-left italic">
                {{ rolUsuario === 'ESTUDIANTE' ? 'Student Interface' : 'Management Console' }}
            </p>

            <nav class="space-y-3">
                <template v-if="rolUsuario === 'JEFE_SUB_PROGRAMA'">
                    <router-link to="/preregistros"
                        :class="['group relative flex items-center gap-4 px-4 py-4 rounded-xl border transition-all duration-300', isActive('/preregistros') ? 'border-rose-500/30 text-rose-400 bg-rose-500/5 shadow-[0_10px_20px_rgba(225,29,72,0.1)]' : 'border-transparent text-gray-500 hover:text-white hover:bg-white/5']">
                        <span v-if="isActive('/preregistros')"
                            class="absolute left-0 top-0 w-1 h-full bg-rose-600 shadow-[0_0_15px_#e11d48]"></span>
                        <span class="text-xl">📋</span>
                        <div class="flex-1">
                            <span class="text-xs font-black uppercase tracking-widest block"
                                :class="isActive('/preregistros') ? 'text-white' : ''">Preregistros</span>
                        </div>
                        <div v-if="totalPendientes > 0"
                            class="relative flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-rose-600 rounded-lg shadow-[0_0_10px_#e11d48] animate-bounce">
                            <span class="text-[10px] font-black text-white leading-none">{{ totalPendientes }}</span>
                        </div>
                    </router-link>

                    <router-link to="/usuarios"
                        :class="['group relative flex items-center gap-4 px-4 py-4 rounded-xl border transition-all duration-300', isActive('/usuarios') ? 'border-rose-500/30 text-rose-400 bg-rose-500/5 shadow-[0_10px_20px_rgba(225,29,72,0.1)]' : 'border-transparent text-gray-500 hover:text-white hover:bg-white/5']">
                        <span v-if="isActive('/usuarios')"
                            class="absolute left-0 top-0 w-1 h-full bg-rose-600 shadow-[0_0_15px_#e11d48]"></span>
                        <span class="text-xl">👥</span>
                        <span class="text-xs font-black uppercase tracking-widest"
                            :class="isActive('/usuarios') ? 'text-white' : ''">Usuarios Base</span>
                    </router-link>
                </template>

                <router-link to="/incidencias"
                    :class="['group relative flex items-center gap-4 px-4 py-4 rounded-xl border transition-all duration-300', isActive('/incidencias') ? 'border-rose-500/30 text-rose-400 bg-rose-500/5 shadow-[0_10px_20px_rgba(225,29,72,0.1)]' : 'border-transparent text-gray-500 hover:text-white hover:bg-white/5']">
                    <span v-if="isActive('/incidencias')"
                        class="absolute left-0 top-0 w-1 h-full bg-rose-600 shadow-[0_0_15px_#e11d48]"></span>
                    <span class="text-xl">📊</span>
                    <span class="text-xs font-black uppercase tracking-widest"
                        :class="isActive('/incidencias') ? 'text-white' : ''">
                        {{ rolUsuario === 'ESTUDIANTE' ? 'Mis Incidencias' : 'Incidencias' }}
                    </span>
                </router-link>

                <router-link v-if="rolUsuario === 'ESTUDIANTE'" to="/crear"
                    :class="['group relative flex items-center gap-4 px-4 py-4 rounded-xl border transition-all duration-300', isActive('/crear-incidencia') ? 'border-rose-500/30 text-rose-400 bg-rose-500/5 shadow-[0_10px_20px_rgba(225,29,72,0.1)]' : 'border-transparent text-gray-500 hover:text-white hover:bg-white/5']">
                    <span v-if="isActive('/crear-incidencia')"
                        class="absolute left-0 top-0 w-1 h-full bg-rose-600 shadow-[0_0_15px_#e11d48]"></span>
                    <span class="text-xl">✍️</span>
                    <span class="text-xs font-black uppercase tracking-widest"
                        :class="isActive('/crear-incidencia') ? 'text-white' : ''">Crear Solicitud</span>
                </router-link>
            </nav>
        </div>

        <div v-if="rolUsuario === 'JEFE_SUB_PROGRAMA'"
            class="mt-auto p-5 rounded-2xl bg-[#0a0a0a] border border-white/5 relative overflow-hidden group">
            <div
                class="absolute -right-4 -top-4 w-16 h-16 bg-rose-600/10 blur-2xl rounded-full group-hover:bg-rose-600/20 transition-all">
            </div>
            <div class="relative z-10">
                <p class="text-[10px] font-black text-rose-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <span class="w-2 h-2 bg-rose-600 rounded-full animate-pulse shadow-[0_0_8px_#e11d48]"></span>
                    Status Operativo
                </p>
                <div class="space-y-3">
                    <div>
                        <div class="flex justify-between text-[9px] font-bold text-gray-400 uppercase mb-1">
                            <span>Pendientes</span>
                            <span class="text-white">{{ totalPendientes }}</span>
                        </div>
                        <div class="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                            <div :style="{ width: (totalPendientes > 0 ? '75%' : '0%') }"
                                class="h-full bg-gradient-to-r from-rose-600 to-orange-500 shadow-[0_0_10px_rgba(225,29,72,0.5)] transition-all duration-1000">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </aside>
</template>