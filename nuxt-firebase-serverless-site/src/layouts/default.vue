<template>
    <div class="default-layout">
        <Header />
        <nuxt />
    </div>
</template>
<script>
import { mapActions } from 'vuex';

import Header from '~/components/Header.vue';

export default {
    components: {
        Header,
    },
    middleware: ['auth'],
    data() {
        return {
            loggedIn: false,
            isHidden: false,
            warningBandClass: '',
            warningBandMessage: '',
        };
    },
    mounted() {
        this.isLogged();
    },
    methods: {
        ...mapActions('auth', ['isLogged']),
    },
};
</script>
<style lang="scss" scoped>
.default-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
</style>
