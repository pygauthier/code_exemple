export const state = () => ({});

export const mutations = {};

export const actions = {
    async nuxtServerInit({ dispatch }) {
        await dispatch('setFirebaseClient');
    },
    async nuxtClientInit({ dispatch }) {
        await dispatch('setFirebaseClient');
    },
    async setFirebaseClient({ commit, dispatch }) {
        const token = this.$cookies.get('token');
        commit('auth/SET_TOKEN', token);
        if (token) {
            await this.$firebase.init();
        }
    },
};
