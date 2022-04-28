import * as firebase from 'firebase/app';

export const state = () => ({
    user: {},
    token: '',
    loading: false,
    alert: {},
});

export const mutations = {
    SET_TOKEN(state, payload) {
        state.token = payload;
        if (payload) {
            this.$cookies.set('token', payload, {
                path: '/',
                maxAge: 60 * 60 * 24 * 7,
            });
        } else {
            this.$cookies.remove('token');
        }
    },
    SET_USER(state, payload) {
        state.user = payload;
    },
    SET_LOADING(state, payload) {
        state.loading = payload;
    },
    SET_ALERT(state, payload) {
        state.alert = payload;
    },
};

export const getters = {
    loggedIn(state) {
        return !!state.token;
    },
};

export const actions = {
    getAlert({ state }) {
        return state.alert;
    },
    currentUser({ state }) {
        return state.user;
    },
    login({ commit, dispatch }, user) {
        try {
            firebase
                .auth()
                .currentUser.getIdToken()
                .then(token => {
                    commit('SET_TOKEN', token);
                    dispatch('fetchUserProfile', this.$firebase.auth.currentUser);
                });
        } catch (e) {
            const status = e.response && e.response.status;
            if (status >= 400 && status < 500) {
                this.$notify({
                    title: "Informations d'identification invalides",
                    message: "Le nom d'utilisateur ou le mot de passe n'est pas valide",
                    type: 'error',
                });
            } else {
                this.$notify({
                    title: "Erreur de connexion à l'API",
                    message: 'Veuillez réessayer plus tard',
                    type: 'error',
                });
            }
        }
    },
    async signup({ dispatch }, form) {
        const { user } = await firebase.auth().createUserWithEmailAndPassword(form.email, form.password);

        // create user profile object in userCollections
        await this.$firebase.users.doc(user.uid).set({
            email: form.email,
            discord: form.discord,
            trucksbook: form.trucksbook,
            is_admin: false,
            is_dispatcher: false,
            is_active: true,
            created: this.$firebase.firestore.Timestamp.now(),
            modified: this.$firebase.firestore.Timestamp.now(),
        });

        // fetch user profile and set in state
        dispatch('login', user);
    },
    async fetchUserProfile({ dispatch, commit }, user) {
        // fetch user profile
        const userProfile = await this.$firebase.users.doc(user.uid).get();

        // set user profile in state
        const profil = { ...userProfile.data(), uid: user.uid };
        if (profil.is_active) {
            commit('SET_USER', profil);

            // change route to dashboard
            this.$router.push(this.app.localePath('index'));
        } else {
            commit('SET_ALERT', {
                title: "Le compte n'est plus actif",
                message: 'Veuillez réessayer plus tard',
                type: 'error',
            });
            dispatch('logout');
        }
    },
    logout({ commit }) {
        commit('SET_TOKEN', null);
        this.$firebase.auth.signOut().then(() => {
            this.$router.go({ path: 'login' });
        });
    },
    isLogged() {
        this.$firebase.isLogged();
    },
};
