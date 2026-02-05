import { createRouter, createWebHistory } from 'vue-router';
import HelloWorld from '../components/HelloWorld.vue';
import Login from '../views/Login.vue';
import BaseAdmin from '../components/BaseAdmin.vue';
import Preregistros from '../views/Preregistros.vue';
import Usuarios from '../views/Usuarios.vue';
import CrearIncidencia from '../views/CrearIncidencia.vue';
import ListaIncidencias from '../views/ListaIncidencias.vue';
import ChatIncidencia from '../views/ChatIncidencia.vue';
import Perfil from '../views/Perfil.vue';

const routes = [
    {
        path: '/',
        name: 'home',
        component: HelloWorld,
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'login',
        component: Login,
        meta: { guestOnly: true } // Solo accesible si NO estás logueado
    },
    {
        path: '/admin',
        name: 'admin',
        component: BaseAdmin,
        meta: { requiresAuth: true }
    },
    {
        path: '/preregistros',
        name: 'preregistros',
        component: Preregistros,
        meta: { requiresAuth: true, role: 'JEFE_SUB_PROGRAMA' }
    },
    {
        path: '/usuarios',
        name: 'usuarios',
        component: Usuarios,
        meta: { requiresAuth: true, role: 'JEFE_SUB_PROGRAMA' }
    },
    {
        path: '/crear',
        name: 'crear',
        component: CrearIncidencia,
        meta: { requiresAuth: true, role: 'ESTUDIANTE' }
    },
    {
        path: '/incidencias',
        name: 'incidencias',
        component: ListaIncidencias,
        meta: { requiresAuth: true }
    },
    {
        path: '/chat/:id',
        name: 'chat',
        component: ChatIncidencia,
        meta: { requiresAuth: true }
    },
    {
        path: '/perfil',
        name: 'perfil',
        component: Perfil,
        meta: { requiresAuth: true }
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
});

/* ----------------------------------
   GUARDIA DE NAVEGACIÓN (SEGURIDAD)
---------------------------------- */
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token');
    const rol = localStorage.getItem('usuario_rol');

    // 1. Si la ruta requiere autenticación y no hay token
    if (to.meta.requiresAuth && !token) {
        return next({ name: 'login' });
    }

    // 2. Si el usuario ya está logueado e intenta ir al login
    if (to.meta.guestOnly && token) {
        return next({ name: 'incidencias' });
    }

    // 3. Verificación de Roles
    if (to.meta.role) {
        if (rol !== to.meta.role) {
            console.warn("Acceso denegado: No tienes el rol necesario");
            return next({ name: 'incidencias' }); // Redirigir a una ruta segura
        }
    }

    next(); // Permitir el acceso
});

export default router;