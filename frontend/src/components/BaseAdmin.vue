<script setup>
import { ref } from 'vue';
import Navbar from './Navbar.vue';
import Sidebar from './Sidebar.vue';

const isSidebarOpen = ref(false); // Estado del menú controlado desde aquí
</script>

<template>
    <div class="min-h-screen flex flex-col bg-[#030303] text-white font-sans selection:bg-rose-500/30">

        <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden">
            <div class="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-rose-600/5 blur-[120px] rounded-full">
            </div>
            <div
                class="absolute bottom-[-10%] right-[-5%] w-[400px] h-[400px] bg-orange-600/5 blur-[100px] rounded-full">
            </div>
        </div>

        <Navbar @toggle-menu="isSidebarOpen = !isSidebarOpen" />

        <div class="flex flex-1 relative z-10 overflow-hidden">

            <Sidebar :isOpen="isSidebarOpen" @close="isSidebarOpen = false" />

            <transition enter-active-class="transition-opacity duration-300 ease-linear" enter-from-class="opacity-0"
                enter-to-class="opacity-100" leave-active-class="transition-opacity duration-200 ease-linear"
                leave-from-class="opacity-100" leave-to-class="opacity-0">
                <div v-if="isSidebarOpen" @click="isSidebarOpen = false"
                    class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[140] lg:hidden"></div>
            </transition>

            <main class="flex-1 overflow-y-auto p-4 md:p-8 lg:p-10 custom-scrollbar">
                <div class="max-w-7xl mx-auto animate-[fade-up_0.6s_cubic-bezier(0.16,1,0.3,1)]">
                    <slot />
                </div>
            </main>
        </div>
    </div>
</template>

<style>
/* Estilizamos el scroll de manera global pero sin usar @apply para evitar líos */
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #1f1f1f;
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #e11d48;
}

/* Definimos la animación clave de forma estándar de CSS */
@keyframes fade-up {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>