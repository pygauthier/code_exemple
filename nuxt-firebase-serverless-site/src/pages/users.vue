<template>
    <div class="" style="width:90%; margin-left:5%;">
        <div style="margin-top: 15px; justify-content: space-between;" class="flex">
            <h1>Utilisateurs</h1>

            <el-checkbox v-model="excludeInactive">exclure inactif</el-checkbox>
            <el-input v-model="search" placeholder="Entrez quelque chose" class="input-with-select" style="width:500px">
                <el-select slot="prepend" v-model="searchField" placeholder="Choisir" style="width:150px">
                    <el-option label="Email" value="email"></el-option>
                    <el-option label="Discord" value="discord"></el-option>
                    <el-option label="TrucksBook" value="trucksbook"></el-option>
                </el-select>
                <el-button slot="append" icon="el-icon-search"></el-button>
            </el-input>
        </div>
        <div class="accueil flex">
            <el-table
                ref="singleTable"
                :default-sort="{ prop: 'discord', order: 'descending' }"
                :data="tableData"
                highlight-current-row
                style="width: 100%"
            >
                <el-table-column prop="email" label="Couriel" sortable width="200"> </el-table-column>
                <el-table-column prop="discord" label="Discord" sortable width="180"></el-table-column>
                <el-table-column prop="trucksbook" label="Trucksbook" sortable width="180"> </el-table-column>
                <el-table-column prop="created" label="Créer" sortable width="180"> </el-table-column>
                <el-table-column prop="modified" label="Modification" sortable width="180"> </el-table-column>
                <el-table-column label="Status">
                    <template slot-scope="scope">
                        <el-button
                            @click="updateField('is_admin', scope.row.id, !scope.row.is_admin)"
                            :type="scope.row.is_admin_color"
                            size="mini"
                            >Admin
                        </el-button>
                        <el-button
                            @click="updateField('is_dispatcher', scope.row.id, !scope.row.is_dispatcher)"
                            :type="scope.row.is_dispatcher_color"
                            size="mini"
                            >Dispatcher</el-button
                        >
                        <el-button
                            @click="updateField('is_active', scope.row.id, !scope.row.is_active)"
                            :type="scope.row.is_active_color"
                            size="mini"
                            >Active</el-button
                        >
                    </template>
                </el-table-column>
                <el-table-column label="Opérations">
                    <template slot-scope="scope">
                        <el-button @click="openUser(scope.$index, scope.row)" size="mini">Editer</el-button>
                        <el-button @click="deleteUser(scope.$index, scope.row)" size="mini" type="danger"
                            >Supprimer</el-button
                        >
                    </template>
                </el-table-column>
            </el-table>
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
            users: [],
            search: '',
            searchField: 'discord',
            excludeInactive: false,
        };
    },
    computed: {
        fas() {
            return fas;
        },
        far() {
            return far;
        },
        tableData() {
            let searchResults = this.users.filter(
                user => !this.search || user[this.searchField].toLowerCase().includes(this.search.toLowerCase()),
            );

            if (this.excludeInactive) {
                searchResults = searchResults.filter(user => user.is_active);
            }
            return searchResults;
        },
    },
    mounted() {
        this.get_users();
    },
    methods: {
        get_users() {
            const scope = this;
            this.$firebase.users.orderBy('discord').onSnapshot(snapshot => {
                const postsArray = [];
                snapshot.forEach(data => {
                    const post = data.data();
                    post.id = data.id;
                    post.modified = this.processDate(post.modified);
                    post.created = this.processDate(post.created);
                    post.is_admin_color = post.is_admin ? 'success' : 'danger';
                    post.is_dispatcher_color = post.is_dispatcher ? 'success' : 'danger';
                    post.is_active_color = post.is_active ? 'success' : 'danger';
                    postsArray.push(post);
                });
                scope.users = postsArray;
            });
        },
        async openUser(index, row) {
            await this.$nuxt.$firebase.users.doc(row.id).update({
                modified: this.$firebase.firestore.Timestamp.now(),
            });
        },
        updateField(field, id, data) {
            const update = {};
            update[field] = data;
            this.$nuxt.$firebase.users.doc(id).update({
                ...update,
                modified: this.$firebase.firestore.Timestamp.now(),
            });
        },
        processDate(field) {
            return field
                .toDate()
                .toISOString()
                .replace('T', ' ')
                .substring(0, 19);
        },
    },
};
</script>

<style lang="scss" scoped></style>
