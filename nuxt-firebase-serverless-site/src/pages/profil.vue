<template>
    <div class="accueil flex">
        <div class="login">
            <el-form ref="form" :model="user" @submit.native.prevent="save" label-position="top">
                <el-form-item>
                    <label>Discord Username</label>
                    <el-input v-model="user.discord"></el-input>
                </el-form-item>

                <el-form-item>
                    <label>Trucksbook Username</label>
                    <el-input v-model="user.trucksbook"></el-input>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" native-type="submit">Enregistrer</el-button>
                </el-form-item>
            </el-form>
        </div>
    </div>
</template>

<script>
import { far } from '@fortawesome/free-regular-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';
// import { mapActions } from 'vuex';

export default {
    components: {},
    data() {
        return {
            fb_user: {},
            user: {},
        };
    },
    computed: {
        fas() {
            return fas;
        },
        far() {
            return far;
        },
    },
    async mounted() {
        await this.get_user();
    },
    methods: {
        async get_user() {
            const user = await this.$firebase.users.doc(this.$firebase.auth.currentUser.uid);
            this.fb_user = user;
            user.get().then(_user => {
                this.user = _user.data();
            });
        },
        save() {
            this.fb_user.update({
                discord: this.user.discord,
                trucksbook: this.user.trucksbook,
                modified: this.$firebase.firestore.Timestamp.now(),
            });
        },
    },
};
</script>

<style lang="scss" scoped>
.login {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
