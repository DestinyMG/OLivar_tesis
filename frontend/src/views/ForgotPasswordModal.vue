<script setup>
import { ref } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';

const props = defineProps(['show']);
const emit = defineEmits(['close']);

const step = ref(1);
const loading = ref(false);
const tokenTemporal = ref('');

const recoveryForm = ref({
    username: '',
    email: '',
    codigo: '',
    password: ''
});

const solicitarCodigo = async () => {
    loading.value = true;
    try {
        const res = await axios.post('http://localhost:8000/api4/notificaciones/solicitar-codigo/', {
            username: recoveryForm.value.username,
            email: recoveryForm.value.email
        });
        tokenTemporal.value = res.data.token_temporal;
        step.value = 2;
        Swal.fire({
            icon: 'success', title: 'CÓDIGO GENERADO',
            text: 'Revisa tu bandeja de entrada.',
            background: '#0a0a12', color: '#00ffff', confirmButtonColor: '#00ffff'
        });
    } catch (error) {
        Swal.fire({
            icon: 'error', title: 'DATOS INVÁLIDOS',
            text: error.response?.data?.error || 'No hay coincidencia en el sistema.',
            background: '#0a0a12', color: '#ff0055', confirmButtonColor: '#ff0055'
        });
    } finally {
        loading.value = false;
    }
};

const confirmarCambio = async () => {
    loading.value = true;
    try {
        await axios.post('http://localhost:8000/api4/notificaciones/confirmar-cambio/', {
            token_temporal: tokenTemporal.value,
            codigo: recoveryForm.value.codigo,
            password: recoveryForm.value.password
        });
        Swal.fire({
            icon: 'success', title: 'ACCESO RESTAURADO',
            text: 'Ya puedes iniciar sesión con tu nueva clave.',
            background: '#0a0a12', color: '#00ffff', confirmButtonColor: '#00ffff'
        });
        cerrarModal();
    } catch (error) {
        Swal.fire({
            icon: 'error', title: 'ERROR DE NODO',
            text: 'Código expirado o incorrecto.',
            background: '#0a0a12', color: '#ff0055', confirmButtonColor: '#ff0055'
        });
    } finally {
        loading.value = false;
    }
};

const cerrarModal = () => {
    step.value = 1;
    recoveryForm.value = { username: '', email: '', codigo: '', password: '' };
    emit('close');
};
</script>

<template>
    <Transition name="fade">
        <div v-if="show"
            class="fixed inset-0 z-[150] flex items-center justify-center p-4 backdrop-blur-md bg-black/60">

            <div class="relative max-w-md w-full animate-slide-up">

                <div
                    class="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-fuchsia-600 rounded-[30px] blur opacity-20">
                </div>

                <div
                    class="relative bg-[#0d0d16] border border-white/10 p-8 rounded-[30px] shadow-2xl overflow-hidden text-left">

                    <div
                        class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent">
                    </div>

                    <button @click="cerrarModal"
                        class="absolute top-5 right-5 text-gray-500 hover:text-cyan-400 transition-all z-10 cursor-pointer">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>

                    <div class="mb-8">
                        <h3 class="text-3xl font-black text-white uppercase italic tracking-tighter leading-none">
                            {{ step === 1 ? 'System' : 'Identity' }}
                            <span class="text-cyan-500 block">Recovery</span>
                        </h3>
                        <div class="w-12 h-1 bg-fuchsia-600 mt-2"></div>
                    </div>

                    <form v-if="step === 1" @submit.prevent="solicitarCodigo" class="space-y-6">
                        <div class="space-y-2 text-left">
                            <label
                                class="text-[10px] font-black text-cyan-400 uppercase tracking-widest">Username</label>
                            <input v-model="recoveryForm.username" type="text"
                                class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-white text-sm font-bold outline-none focus:border-cyan-500/50 transition-all placeholder:text-white/20"
                                required placeholder="IDENTIFIER_01">
                        </div>
                        <div class="space-y-2 text-left">
                            <label class="text-[10px] font-black text-cyan-400 uppercase tracking-widest">Email
                                Address</label>
                            <input v-model="recoveryForm.email" type="email"
                                class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-white text-sm font-bold outline-none focus:border-cyan-500/50 transition-all placeholder:text-white/20"
                                required placeholder="user@network.com">
                        </div>
                        <button type="submit" :disabled="loading" class="cyber-btn w-full mt-4">
                            <span class="btn-content">{{ loading ? 'PROCESSING...' : 'REQUEST CODE' }}</span>
                        </button>
                    </form>

                    <form v-else @submit.prevent="confirmarCambio" class="space-y-6">
                        <div class="bg-cyan-500/5 border border-cyan-500/20 p-4 rounded-xl mb-4">
                            <p class="text-[11px] text-cyan-200 text-center leading-relaxed font-bold">
                                Introduce el código de 6 dígitos enviado a tu correo.
                            </p>
                        </div>

                        <div class="space-y-2">
                            <label
                                class="text-[10px] font-black text-fuchsia-500 uppercase tracking-widest text-center block">Security
                                Code</label>
                            <input v-model="recoveryForm.codigo" type="text" maxlength="6"
                                class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-fuchsia-400 text-2xl tracking-[0.5em] font-black outline-none focus:border-fuchsia-500/50 transition-all text-center"
                                required>
                        </div>

                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-cyan-400 uppercase tracking-widest">New
                                Password</label>
                            <input v-model="recoveryForm.password" type="password"
                                class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-white text-sm font-bold outline-none focus:border-cyan-500/50 transition-all placeholder:text-white/20"
                                required placeholder="••••••••">
                        </div>

                        <button type="submit" :disabled="loading" class="cyber-btn fuchsia w-full mt-4">
                            <span class="btn-content">{{ loading ? 'OVERWRITING...' : 'RESTORE ACCESS' }}</span>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </Transition>
</template>

<style scoped>
/* Estilos personalizados que no se pueden hacer solo con clases básicas de TW */
.cyber-btn {
    position: relative;
    padding: 1px;
    background: linear-gradient(90deg, #00ffff, #0066ff);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.cyber-btn.fuchsia {
    background: linear-gradient(90deg, #ff00ff, #7000ff);
}

.btn-content {
    display: block;
    background: #0d0d16;
    color: white;
    padding: 15px;
    border-radius: 11px;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.2em;
    text-align: center;
    transition: all 0.3s ease;
}

.cyber-btn:hover {
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    transform: translateY(-2px);
}

.cyber-btn:hover .btn-content {
    background: transparent;
    color: white;
}

.animate-slide-up {
    animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>