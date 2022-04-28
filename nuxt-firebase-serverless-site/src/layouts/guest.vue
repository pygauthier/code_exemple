<template>
    <div class="guest-layout">
        <nuxt />
    </div>
</template>
<script>
export default {
    middleware: ['auth'],
    auth: 'guest',
};
</script>
<style lang="scss" scoped>
.guest-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: $--main-color-primary;
}
</style>
