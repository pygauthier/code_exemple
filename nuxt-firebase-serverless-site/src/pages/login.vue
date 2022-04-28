<template>
    <div v-loading="loading">
        <div id="main-login" class="flex">
            <div class="flex-column">
                <div class="flex-center mb-25">
                    <medaillon />
                </div>
                <el-button @click="dialogVisible = true" href="#" native-type="button" class="text-doyon">{{
                    $t('login.login')
                }}</el-button>
            </div>
        </div>

        <el-dialog :close-on-click-modal="false" :visible.sync="dialogVisible" width="400px">
            <div class="login">
                <el-form ref="form" :model="form" @submit.native.prevent="onLogin" label-position="top">
                    <el-form-item>
                        <label>{{ $t('login.username') }}</label>
                        <el-input v-model="form.email"></el-input>
                    </el-form-item>

                    <div class="flex">
                        <label>{{ $t('login.pass') }}</label>
                        <el-link class="ml-auto" href="#">{{ $t('login.forgot') }}</el-link>
                    </div>

                    <el-form-item>
                        <el-input v-model="form.password" type="password"></el-input>
                    </el-form-item>

                    <div class="flex" style="justify-content: space-between;">
                        <el-form-item>
                            <el-button type="primary" native-type="submit">{{ $t('login.loginButton') }}</el-button>
                        </el-form-item>

                        <el-form-item>
                            <el-button
                                @click="
                                    dialogVisible = false;
                                    dialogSignUpVisible = true;
                                "
                                href="#"
                                native-type="button"
                                class="text-doyon"
                            >
                                Créer un compte
                            </el-button>
                        </el-form-item>
                    </div>
                </el-form>
            </div>
        </el-dialog>

        <el-dialog :close-on-click-modal="false" :visible.sync="dialogSignUpVisible" width="400px">
            <div class="login">
                <el-form ref="form" :model="signUpForm" @submit.native.prevent="onSignUp" label-position="top">
                    <el-form-item>
                        <label>{{ $t('login.username') }}</label>
                        <el-input v-model="signUpForm.email"></el-input>
                    </el-form-item>

                    <el-form-item>
                        <label>{{ $t('login.pass') }}</label>
                        <el-input v-model="signUpForm.password" type="password"></el-input>
                    </el-form-item>

                    <el-form-item>
                        <label>Discord Username</label>
                        <el-input v-model="signUpForm.discord"></el-input>
                    </el-form-item>

                    <el-form-item>
                        <label>Trucksbook Username</label>
                        <el-input v-model="signUpForm.trucksbook"></el-input>
                    </el-form-item>

                    <el-form-item>
                        <el-button type="primary" native-type="submit">Créer</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </el-dialog>
    </div>
</template>
<script>
import * as firebase from 'firebase/app';
import { mapActions } from 'vuex';
import medaillon from '~/assets/img/logos/truck.svg';

export default {
    layout: 'guest',
    components: {
        medaillon,
    },
    data() {
        return {
            loading: false,
            form: {
                email: '',
                password: '',
            },
            signUpForm: {
                email: '',
                password: '',
                discord: '',
                trucksbook: '',
            },
            dialogVisible: false,
            dialogSignUpVisible: false,
        };
    },
    mounted() {
        this.$firebase.init();
        this.checkAlert();
    },
    methods: {
        ...mapActions('auth', ['login', 'signup', 'getAlert']),
        checkAlert() {
            this.getAlert().then(_alert => {
                if (_alert.type !== undefined) {
                    this.$notify(_alert);
                }
            });
        },
        onLogin() {
            this.loading = true;
            this.dialogVisible = false;
            firebase
                .auth()
                .signInWithEmailAndPassword(this.form.email, this.form.password)
                .then(data => {
                    this.login(data);
                })
                .catch(error => {
                    this.error = error;
                    this.loading = false;
                    this.$notify({
                        title: "Informations d'identification invalides",
                        message: "Le nom d'utilisateur ou le mot de passe n'est pas valide",
                        type: 'error',
                    });
                });
        },
        async onSignUp() {
            await this.signup(this.signUpForm);
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
.login-form {
    width: 290px;
}
.el-card {
    display: flex;
    width: 340px;
    justify-content: center;
}
.flex {
    display: flex;
}
.django-login {
    position: absolute;
    right: 0;
    bottom: 0;
    margin: 5px;
    color: white;
    cursor: pointer;
}
#main-login {
    height: 100vh;
    background-color: $--main-color-primary;
    align-items: center;
    justify-content: center;
}
</style>
