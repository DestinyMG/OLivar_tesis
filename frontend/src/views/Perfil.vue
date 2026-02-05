<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import BaseAdmin from '../components/BaseAdmin.vue';

// URL base de tu API1
const API_URL = 'http://localhost:8000/api1/personas/';

const usuario = ref({
    id: null,
    nombre: '',
    apellido: '',
    ci: '',
    username: '',
    rol: '',
    imagen: null,
    sub_programa: { nombre: '' }
});

// Campos para edición
const passwordActual = ref('');
const passwordNuevo = ref('');
const nuevaImagen = ref(null);
const previewUrl = ref(null);
const cargando = ref(false);

// 1. Cargar datos del perfil
onMounted(async () => {
    const id = localStorage.getItem('usuario_id');
    try {
        const res = await axios.get(`${API_URL}${id}/`);
        usuario.value = res.data;
        previewUrl.value = res.data.imagen;
    } catch (error) {
        console.error("Error al cargar perfil:", error);
    }
});

// 2. Previsualizar imagen
const onFileSelected = (e) => {
    const file = e.target.files[0];
    if (file) {
        nuevaImagen.value = file;
        previewUrl.value = URL.createObjectURL(file);
    }
};

// 3. Guardar cambios (PATCH)
const actualizarPerfil = async () => {
    cargando.value = true;
    const formData = new FormData();

    // Solo mandamos lo que el Serializer permite escribir
    formData.append('nombre', usuario.value.nombre);
    formData.append('apellido', usuario.value.apellido);

    if (nuevaImagen.value) {
        formData.append('imagen', nuevaImagen.value);
    }

    // 🔐 GESTIÓN DE CONTRASEÑA:
    // Solo la incluimos si el usuario escribió algo en el campo nuevo
    if (passwordNuevo.value) {
        formData.append('password', passwordNuevo.value);
    }

    try {
        const res = await axios.patch(`${API_URL}${usuario.value.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });

        usuario.value = res.data;
        passwordNuevo.value = ''; // Limpiar campo

        Swal.fire({
            title: '¡PERFIL ACTUALIZADO!',
            text: 'Los cambios se guardaron correctamente.',
            icon: 'success',
            background: '#0a0a10',
            color: '#fff',
            confirmButtonColor: '#e11d48'
        });
    } catch (error) {
        console.error("Error backend:", error.response?.data);
        Swal.fire('Error', 'No se pudo actualizar el perfil. Revisa los datos.', 'error');
    } finally {
        cargando.value = false;
    }
};
</script>

<template>
    <BaseAdmin>
        <div class="max-w-5xl mx-auto space-y-8">
            <div class="border-l-4 border-rose-600 pl-6 mb-10">
                <h1 class="text-4xl font-black text-white uppercase italic tracking-tighter">
                    Mi <span class="text-rose-600">Perfil</span>
                </h1>
                <p class="text-gray-500 text-[10px] font-black uppercase tracking-[0.4em]">Configuración de cuenta</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

                <div class="space-y-6">
                    <div
                        class="bg-[#0a0a10]/80 border border-white/5 p-8 rounded-[40px] text-center backdrop-blur-xl relative overflow-hidden">
                        <div class="absolute top-0 right-0 p-4">
                            <span class="text-[8px] font-black text-rose-500/40 uppercase tracking-widest">ID: #{{
                                usuario.id }}</span>
                        </div>

                        <div class="relative w-44 h-44 mx-auto mb-6 group">
                            <img :src="previewUrl || '/default-avatar.png'"
                                class="w-full h-full object-cover rounded-full border-4 border-rose-600/20 shadow-[0_0_30px_rgba(225,29,72,0.2)] group-hover:scale-105 transition-transform duration-500">

                            <label
                                class="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-all cursor-pointer rounded-full border-2 border-rose-500 border-dashed">
                                <span class="text-[9px] font-black text-white uppercase italic">Subir Foto</span>
                                <input type="file" class="hidden" @change="onFileSelected" accept="image/*">
                            </label>
                        </div>

                        <h3 class="text-xl font-black text-white uppercase tracking-tighter">{{ usuario.username }}</h3>
                        <p class="text-rose-500 text-[10px] font-black uppercase tracking-[0.2em] mb-4">{{ usuario.rol
                            }}</p>

                        <div class="bg-white/5 rounded-2xl p-4 text-left space-y-3">
                            <div>
                                <p class="text-[8px] text-gray-500 font-black uppercase">Sub-Programa</p>
                                <p class="text-xs text-white font-bold">{{ usuario.sub_programa?.nombre || 'General' }}
                                </p>
                            </div>
                            <div>
                                <p class="text-[8px] text-gray-500 font-black uppercase">Documento</p>
                                <p class="text-xs text-white font-bold">{{ usuario.ci }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="lg:col-span-2 space-y-6">
                    <div class="bg-[#0a0a10]/40 border border-white/5 p-10 rounded-[40px] shadow-2xl">
                        <form @submit.prevent="actualizarPerfil" class="space-y-8">

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div class="space-y-2">
                                    <label
                                        class="text-[10px] font-black text-rose-500 uppercase tracking-widest">Nombre</label>
                                    <input v-model="usuario.nombre" type="text"
                                        class="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white text-xs font-bold outline-none focus:border-rose-500/50 transition-all">
                                </div>
                                <div class="space-y-2">
                                    <label
                                        class="text-[10px] font-black text-rose-500 uppercase tracking-widest">Apellido</label>
                                    <input v-model="usuario.apellido" type="text"
                                        class="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white text-xs font-bold outline-none focus:border-rose-500/50 transition-all">
                                </div>
                            </div>

                            <div class="p-8 bg-rose-600/5 border border-rose-600/10 rounded-3xl space-y-6">
                                <h4
                                    class="text-[10px] font-black text-rose-500 uppercase tracking-widest flex items-center gap-2">
                                    <span class="w-1.5 h-1.5 bg-rose-500 rounded-full shadow-[0_0_10px_#e11d48]"></span>
                                    Cambiar Contraseña
                                </h4>
                                <div class="grid grid-cols-1 gap-4">
                                    <input v-model="passwordNuevo" type="password"
                                        placeholder="Nueva contraseña (dejar vacío para no cambiar)"
                                        class="w-full bg-black/40 border border-white/10 rounded-2xl px-5 py-4 text-white text-xs font-bold outline-none focus:border-rose-500/50 transition-all">
                                    <p class="text-[8px] text-gray-600 italic px-2">Nota: Al actualizar la contraseña,
                                        el sistema la encriptará automáticamente.</p>
                                </div>
                            </div>

                            <button type="submit" :disabled="cargando"
                                class="w-full py-5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-black uppercase tracking-[0.3em] rounded-2xl transition-all shadow-[0_10px_20px_rgba(225,29,72,0.2)] active:scale-95 disabled:bg-gray-800">
                                {{ cargando ? 'GUARDANDO CAMBIOS...' : 'ACTUALIZAR PERFIL' }}
                            </button>
                        </form>
                    </div>
                </div>

            </div>
        </div>
    </BaseAdmin>
</template>