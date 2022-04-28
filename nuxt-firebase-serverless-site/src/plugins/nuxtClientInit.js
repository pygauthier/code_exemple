export default async function(ctx, inject) {
    const { store } = ctx;
    await store.dispatch('nuxtClientInit', ctx);
}
