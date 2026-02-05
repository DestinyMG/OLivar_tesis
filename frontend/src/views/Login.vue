<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2';

const router = useRouter();
const isLogin = ref(true);
const showPassword = ref(false);

// Estado para los subprogramas
const subprogramas = ref([]);
const loadingSubprogramas = ref(false);

const form = ref({
    nombre: '',
    apellido: '',
    ci: '',
    user: '',
    password: '',
    subprograma_id: ''
});

// Cargar subprogramas desde la API
const fetchSubprogramas = async () => {
    loadingSubprogramas.value = true;
    try {
        const response = await axios.get('http://localhost:8000/api1/sub-programas/');
        subprogramas.value = response.data;
    } catch (error) {
        console.error("Error cargando subprogramas:", error);
    } finally {
        loadingSubprogramas.value = false;
    }
};

// Cambiar entre login y registro
const toggleAuth = () => {
    isLogin.value = !isLogin.value;
    showPassword.value = false;
    if (!isLogin.value && subprogramas.value.length === 0) fetchSubprogramas();
};

// --- Función de Submit ---
const handleSubmit = async () => {
    try {
        if (isLogin.value) {
            // --- Login ---
            const loginData = {
                username: form.value.user,
                password: form.value.password
            };

            // --- SweetAlert de carga ---
            Swal.fire({
                title: 'Iniciando sesión...',
                html: '<div class="loader"></div><p class="mt-3">Por favor espere</p>',
                showConfirmButton: false,
                allowOutsideClick: false,
                background: '#1a1a2e',
                color: '#fff',
                didOpen: () => Swal.showLoading()
            });

            const response = await axios.post('http://localhost:8000/api1/auth/token/', loginData);
            Swal.close();

            // ✅ Guardar token y todos los datos del usuario
            const usuario = response.data.usuario;
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('usuario_id', usuario.id);
            localStorage.setItem('usuario_nombre', usuario.nombre);
            localStorage.setItem('usuario_apellido', usuario.apellido);
            localStorage.setItem('usuario_ci', usuario.ci);
            localStorage.setItem('usuario_rol', usuario.rol);
            localStorage.setItem('usuario_sub_programa', usuario.sub_programa || '');


            // Redirigir al panel de incidencias
            window.location.href = 'http://localhost:5173/incidencias';

        } else {
            // --- Preregistro ---
            const subSelected = subprogramas.value.find(s => s.id == form.value.subprograma_id);

            const dataToRegister = {
                nombre: form.value.nombre,
                apellido: form.value.apellido,
                ci: form.value.ci,
                username: form.value.user,
                password: form.value.password,
                sub_programa: subSelected ? subSelected.nombre : '',
                sub_programa_id: form.value.subprograma_id,
                rol: "ESTUDIANTE",
                imagen: null
            };

            Swal.fire({
                title: 'Enviando preregistro...',
                html: '<div class="loader"></div><p class="mt-3">Por favor espere</p>',
                showConfirmButton: false,
                allowOutsideClick: false,
                background: '#1a1a2e',
                color: '#fff',
                didOpen: () => Swal.showLoading()
            });

            await axios.post('http://localhost:8000/api2/preregistros/', dataToRegister);
            Swal.close();

            Swal.fire({
                title: '¡Solicitud Enviada!',
                text: 'Tu preregistro se ha realizado con éxito. Por favor, espera la confirmación del administrador.',
                icon: 'success',
                background: '#1a1a2e',
                color: '#fff',
                confirmButtonColor: '#00ffff',
                confirmButtonText: 'Entendido'
            });

            isLogin.value = true;
            form.value = { nombre: '', apellido: '', ci: '', user: '', password: '', subprograma_id: '' };
        }
    } catch (error) {
        Swal.close();
        console.error("Error:", error.response?.data);

        if (isLogin.value) {
            Swal.fire({
                title: 'Login Fallido',
                text: 'Usuario o contraseña incorrecta',
                icon: 'error',
                background: '#1a1a2e',
                color: '#fff',
                confirmButtonColor: '#ff00ff'
            });
        } else {
            let errorDetail = "No se pudo procesar la solicitud.";
            if (error.response?.data) {
                errorDetail = Object.entries(error.response.data)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join('\n');
            }
            Swal.fire({
                title: 'Fallo de Validación',
                text: errorDetail,
                icon: 'error',
                background: '#1a1a2e',
                color: '#fff',
                confirmButtonColor: '#ff00ff'
            });
        }
    }
};

onMounted(() => {
    if (!isLogin.value) fetchSubprogramas();
});
</script>


<template>
    <div class="neon-bg-container">
        <div class="stars-overlay"></div>
        <div class="blur-circle circle-1"></div>
        <div class="blur-circle circle-2"></div>
        <div class="floating-cube cube-1"></div>
        <div class="floating-cube cube-2"></div>

        <div class="glass-card-wrapper">
            <div :class="['glass-card', isLogin ? 'active-login' : 'active-register']">

                <div class="text-center mb-6">
                    <h2 class="text-4xl font-black uppercase tracking-widest text-white italic drop-shadow-neon">
                        {{ isLogin ? 'Login' : 'Register' }}
                    </h2>
                    <p class="text-cyan-400 text-[10px] font-bold mt-2 tracking-[0.2em] uppercase opacity-80">
                        {{ isLogin ? 'System Access' : 'New Identity Core' }}
                    </p>
                </div>

                <form @submit.prevent="handleSubmit" class="space-y-4">

                    <div v-if="!isLogin" class="animate-fade-in space-y-4">
                        <div class="grid grid-cols-2 gap-3">
                            <div class="input-container">
                                <label>Nombre</label>
                                <input v-model="form.nombre" type="text" placeholder="John" class="neon-input"
                                    required />
                            </div>
                            <div class="input-container">
                                <label>Apellido</label>
                                <input v-model="form.apellido" type="text" placeholder="Doe" class="neon-input"
                                    required />
                            </div>
                        </div>

                        <div class="input-container">
                            <label>Cédula (CI)</label>
                            <input v-model="form.ci" type="text" placeholder="V-000000" class="neon-input" required />
                        </div>

                        <div class="input-container">
                            <label>Subprograma</label>
                            <div class="relative">
                                <select v-model="form.subprograma_id" class="neon-input appearance-none cursor-pointer"
                                    required>
                                    <option value="" disabled selected>Selecciona Programa</option>
                                    <option v-for="sub in subprogramas" :key="sub.id" :value="sub.id"
                                        class="bg-[#1a1a2e]">
                                        {{ sub.nombre }}
                                    </option>
                                </select>
                                <div
                                    class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-cyan-400">
                                    ▼</div>
                            </div>
                        </div>
                    </div>

                    <div class="input-container">
                        <label>Username</label>
                        <input v-model="form.user" type="text" placeholder="User_ID" class="neon-input" required />
                    </div>

                    <div class="input-container">
                        <label>Password</label>
                        <div class="relative">
                            <input v-model="form.password" :type="showPassword ? 'text' : 'password'"
                                placeholder="••••••••" class="neon-input pr-12" required />
                            <button type="button" @click="showPassword = !showPassword"
                                class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-cyan-400 transition-colors cursor-pointer">
                                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                                    viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                    <circle cx="12" cy="12" r="3"></circle>
                                </svg>
                                <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                                    viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path
                                        d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24">
                                    </path>
                                    <line x1="1" y1="1" x2="23" y2="23"></line>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <button type="submit" class="submit-btn">
                        {{ isLogin ? 'Execute Login' : 'Initialize Core' }}
                    </button>
                </form>

                <div class="mt-6 text-center">
                    <button @click="toggleAuth" class="toggle-link">
                        {{ isLogin ? ">> Create New Access Code" : ">> Return to Login" }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.neon-bg-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle at center, #0a0a1a 0%, #050505 100%);
    position: relative;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
}

.stars-overlay {
    position: absolute;
    inset: 0;
    background-image: radial-gradient(2px 2px at 20px 30px, #eee, rgba(0, 0, 0, 0)),
        radial-gradient(2px 2px at 40px 70px, #fff, rgba(0, 0, 0, 0));
    background-repeat: repeat;
    background-size: 200px 200px;
    opacity: 0.1;
    animation: move-stars 100s linear infinite;
}

@keyframes move-stars {
    from {
        background-position: 0 0;
    }

    to {
        background-position: 1000px 1000px;
    }
}

.floating-cube {
    position: absolute;
    width: 60px;
    height: 60px;
    border: 1px solid rgba(0, 255, 255, 0.2);
    background: rgba(0, 255, 255, 0.05);
    animation: float 15s ease-in-out infinite;
}

.cube-1 {
    top: 15%;
    left: 10%;
    transform: rotate(45deg);
}

.cube-2 {
    bottom: 15%;
    right: 10%;
    border-color: rgba(255, 0, 255, 0.2);
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0) rotate(0);
    }

    50% {
        transform: translateY(-30px) rotate(180deg);
    }
}

.blur-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    z-index: 0;
}

.circle-1 {
    width: 500px;
    height: 500px;
    background: rgba(0, 255, 255, 0.1);
    top: -200px;
    left: -100px;
}

.circle-2 {
    width: 400px;
    height: 400px;
    background: rgba(255, 0, 255, 0.08);
    bottom: -100px;
    right: -50px;
}

.glass-card-wrapper {
    z-index: 10;
    width: 100%;
    max-width: 480px;
    padding: 20px;
}

.glass-card {
    background: rgba(10, 10, 26, 0.6);
    backdrop-filter: blur(40px);
    border-radius: 30px;
    padding: 2.5rem 2rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}

.active-login {
    box-shadow: 0 0 60px rgba(0, 255, 255, 0.15);
    border-color: rgba(0, 255, 255, 0.4);
}

.active-register {
    box-shadow: 0 0 60px rgba(255, 0, 255, 0.15);
    border-color: rgba(255, 0, 255, 0.4);
}

.input-container label {
    font-size: 0.65rem;
    font-weight: 900;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 5px;
    display: block;
}

.neon-input {
    width: 100%;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 10px 15px;
    color: #fff;
    font-size: 0.9rem;
    outline: none;
    transition: all 0.3s;
}

.active-login .neon-input:focus {
    border-color: #00ffff;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
}

.active-register .neon-input:focus {
    border-color: #ff00ff;
    box-shadow: 0 0 15px rgba(255, 0, 255, 0.3);
}

.submit-btn {
    width: 100%;
    padding: 14px;
    border-radius: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 3px;
    cursor: pointer;
    transition: all 0.4s;
    border: none;
    color: white;
}

.active-login .submit-btn {
    background: linear-gradient(90deg, #00ffff, #0066ff);
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
}

.active-register .submit-btn {
    background: linear-gradient(90deg, #ff00ff, #6600ff);
    box-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
}

.submit-btn:hover {
    transform: translateY(-3px);
    filter: brightness(1.2);
}

.toggle-link {
    background: none;
    border: none;
    color: #555;
    font-size: 0.7rem;
    font-weight: 700;
    cursor: pointer;
    transition: 0.3s;
}

.toggle-link:hover {
    color: #00ffff;
    text-shadow: 0 0 10px #00ffff;
}

.animate-fade-in {
    animation: fadeIn 0.5s ease forwards;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

.drop-shadow-neon {
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}


/* Loader para SweetAlert */
.loader {
    border: 5px solid #f3f3f3;
    border-top: 5px solid #00ffff;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    margin: 0 auto;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}
</style>