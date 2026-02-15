<script setup>
import { ref } from 'vue';
import Navbar from './Navbar.vue';
import Sidebar from './Sidebar.vue';

const isSidebarOpen = ref(false);
</script>

<template>
    <div class="h-screen flex flex-col bg-[#030303] text-white font-sans selection:bg-rose-500/30 overflow-hidden">

        <div class="fixed inset-0 z-0 pointer-events-none">
            <div class="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-rose-600/5 blur-[120px] rounded-full">
            </div>
            <div
                class="absolute bottom-[-10%] right-[-5%] w-[400px] h-[400px] bg-orange-600/5 blur-[100px] rounded-full">
            </div>
        </div>

        <Navbar class="flex-shrink-0 z-[160]" @toggle-menu="isSidebarOpen = !isSidebarOpen" />

        <div class="flex flex-1 overflow-hidden relative z-10">
            <Sidebar :isOpen="isSidebarOpen" @close="isSidebarOpen = false" class="flex-shrink-0" />

            <transition enter-active-class="transition-opacity duration-300"
                leave-active-class="transition-opacity duration-200">
                <div v-if="isSidebarOpen" @click="isSidebarOpen = false"
                    class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[140] lg:hidden"></div>
            </transition>

            <main class="flex-1 overflow-y-auto custom-scrollbar relative">
                <div class="max-w-7xl mx-auto p-4 md:p-8 lg:p-10 animate-[fade-up_0.6s_ease-out]">
                    <slot />
                </div>
            </main>
        </div>
    </div>
</template>

<style>
/* Animación de entrada */
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

/* Scrollbar global para que no se vea el de Windows feo */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #030303;
}

::-webkit-scrollbar-thumb {
    background: #1f1f1f;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #e11d48;
}
</style>