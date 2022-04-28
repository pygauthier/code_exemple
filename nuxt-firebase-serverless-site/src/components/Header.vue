<template>
    <header>
        <div class="header-container">
            <div id="header-logo">
                <nuxt-link to="/"><logo /></nuxt-link>
            </div>

            <div id="header-links" v-if="!isHidden">
                <span @click="dialogNewRequest = true" class="no-style-link c-pointer">Nouvelle demande</span>
                <nuxt-link
                    v-if="user.is_admin || user.is_dispatcher"
                    class="header-links-space no-style-link"
                    to="/queue"
                    >Queue</nuxt-link
                >
                <nuxt-link v-if="user.is_admin" class="no-style-link" to="/users">Utilisateurs</nuxt-link>
            </div>

            <div id="header-options">
                <nuxt-link class="no-style-link" to="/profil"><fa :icon="fas.faUser" class="c-pointer"/></nuxt-link>
                <el-tooltip class="item" effect="dark" content="Déconnexion" placement="bottom">
                    <fa @click.prevent="logout" :icon="fas.faSignOutAlt" class="c-pointer" />
                </el-tooltip>
            </div>
        </div>
        <div :class="warningBandClass">{{ warningBandMessage }}</div>

        <el-dialog :close-on-click-modal="false" :visible.sync="dialogNewRequest" width="400px">
            <newRequestForm @after="dialogNewRequest = false" />
        </el-dialog>
    </header>
</template>

<script>
import { far } from '@fortawesome/free-regular-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { mapActions } from 'vuex';
import logo from '~/assets/img/logos/logo-header.svg';
import newRequestForm from '~/components/newRequests';

export default {
    components: {
        logo,
        newRequestForm,
    },
    data() {
        return {
            isHidden: false,
            warningBandClass: '',
            warningBandMessage: '',
            user: {},
            dialogNewRequest: false,
            form: {},
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
        if (this.$firebase.auth.currentUser === null) {
            await this.login();
        }
        this.$nuxt.$on('warningBand', message => {
            this.warningBandMessage = message;
            this.warningBandClass = message ? 'warningBand' : '';
        });
        this.user = await this.currentUser();
    },
    methods: {
        ...mapActions('auth', ['login', 'logout', 'currentUser']),
        onNewRequest() {
            this.form.created = this.$firebase.firestore.Timestamp.now();
            this.form.modified = this.$firebase.firestore.Timestamp.now();
            this.form.owner = this.$firebase.auth.currentUser.uid;
            this.form.owner_trucksbook_username = this.user.trucksbook;
            this.form.approved = false;
            this.form.cancelled = false;
            this.form.approved_time = '';
            this.$firebase.requests.doc().set(this.form);
            this.dialogNewRequest = false;
        },
    },
};
</script>

<style lang="scss" scoped>
header {
    background-color: $--main-color-primary;
}
#header-incognito,
#header-user,
#header-dropdown {
    height: 100%;
}
#header-mode-client {
    flex-direction: column;
    width: 100%;
    min-height: 100px;
    color: #999999;
    background-color: $--color-main-grey;
    @extend .flex-ultimate-center;
}
#header-dropdown-content {
    @extend .flex-column-center;
    width: 190px;
    min-width: 190px;
}
#header-incognito {
    display: flex;
    width: 40px;
    border-top-left-radius: 50px;
    border-bottom-left-radius: 50px;
    background-color: white;
    justify-content: center;
    align-items: center;
    .fa-user-secret {
        margin-left: 3px;
        color: $--main-color-primary;
    }
}
#header-user {
    display: flex;
    box-sizing: border-box;
    width: 35px;
    margin: 0 1px 0 1px;
    border: 2px solid white;
    justify-content: center;
    align-items: center;
}
#header-dropdown {
    display: flex;
    width: 15px;
    border-top-right-radius: 50px;
    border-bottom-right-radius: 50px;
    background-color: white;
    justify-content: space-between;
    align-items: center;
    .fa-caret-down {
        margin-left: 3px;
        color: $--main-color-primary;
    }
}
#header-logo {
    width: 200px;
}
#header-options {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    width: 200px;
    height: 32px;
}
#header-links {
    display: flex;
    height: 32px;
    font-weight: 700;
    align-items: center;
}
#header-search-bar {
    width: 70%;
}
.el-autocomplete {
    width: 100% !important;
}
.el-dropdown-menu {
    padding: 0 !important;
}
.header-dropdown-b-botom {
    width: 85%;
    border-bottom: 1px solid #e4e4e4;
}
.header-container {
    @extend .container;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 80px;
}
.header-links-space {
    margin: 0 110px 0 110px;
}
.no-style-link {
    text-decoration: none;
    color: white;
}
.fa-user,
.fa-bell,
.fa-times-circle {
    margin-right: 24px;
}
.fa-user,
.fa-sign-out-alt {
    font-size: 25px;
}
.fa-search,
.fa-bell,
.fa-user,
.fa-times-circle,
.fa-sign-out-alt {
    color: white;
}
.warningBand {
    width: 100%;
    padding: 20px;
    text-align: center;
    background-color: yellow;
}
/*
.slide-search-enter-active {
    transition: transform 0.3s ease;
    transform: rotateX(90deg);
}
.slide-search-leave-active {
    transition: transform 0s ease;
}
.slide-search-leave-to {
    transition: transform 0s ease;
}*/
.desktop-hidden {
    display: none;
}
@media screen and (max-width: 414px) {
    /*Header*/
    #header-links,
    #header-options {
        display: none;
    }
    .desktop-hidden {
        display: block;
    }
}
@media print {
    header {
        display: none;
    }
}
</style>
