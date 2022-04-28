<template>
    <div class="" style="width:90%; margin-left:5%;">
        <div style="margin-top: 15px; justify-content: space-between;" class="flex">
            <h1>Demandes</h1>

            <el-checkbox v-model="excludeInactive">Seulement non approuvée</el-checkbox>
            <el-input v-model="search" placeholder="Entrez quelque chose" class="input-with-select" style="width:500px">
                <el-select slot="prepend" v-model="searchField" placeholder="Choisir" style="width:150px">
                    <el-option label="TrucksBook" value="owner_trucksbook_username"></el-option>
                    <el-option label="Départ" value="from"></el-option>
                    <el-option label="Arrivée" value="to"></el-option>
                </el-select>
                <el-button slot="append" icon="el-icon-search"></el-button>
            </el-input>
        </div>
        <div class="accueil flex">
            <el-table
                ref="singleTable"
                :default-sort="{ prop: 'created', order: 'ascending' }"
                :data="tableData"
                highlight-current-row
                style="width: 100%"
            >
                <el-table-column prop="owner_trucksbook_username" label="Trucksbook" sortable width="250" />
                <el-table-column prop="from" label="Départ" sortable width="250"> </el-table-column>
                <el-table-column prop="to" label="Arrivée" sortable width="250"> </el-table-column>
                <el-table-column prop="estimated_km" label="KM (estimé)" sortable width="180"> </el-table-column>
                <el-table-column prop="created" label="Créer" sortable width="180"> </el-table-column>
                <el-table-column align="right" label="Opérations">
                    <template slot-scope="scope">
                        <div v-if="!scope.row.approved && !scope.row.cancelled">
                            <el-button
                                @click="updateField('approved', scope.row.id, !scope.row.approved)"
                                :type="'success'"
                                size="mini"
                                >Approuver
                            </el-button>

                            <el-button
                                @click="updateField('cancelled', scope.row.id, !scope.row.cancelled)"
                                :type="'danger'"
                                size="mini"
                                >Annuler
                            </el-button>
                        </div>
                        <div v-if="scope.row.approved">Approuvé le {{ scope.row.approved_time }}</div>
                        <div v-if="scope.row.cancelled">Annuler le {{ scope.row.modified }}</div>
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
            requests: [],
            search: '',
            searchField: 'owner_trucksbook_username',
            excludeInactive: true,
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
            let searchResults = this.requests.filter(
                request => !this.search || request[this.searchField].toLowerCase().includes(this.search.toLowerCase()),
            );

            if (this.excludeInactive) {
                searchResults = searchResults.filter(request => !request.approved && !request.cancelled);
            }
            return searchResults;
        },
    },
    mounted() {
        this.get_requests();
    },
    methods: {
        get_requests() {
            const scope = this;
            this.$firebase.requests.orderBy('created').onSnapshot(snapshot => {
                const postsArray = [];
                snapshot.forEach(data => {
                    const post = data.data();
                    post.id = data.id;
                    post.modified = this.processDate(post.modified);
                    post.created = this.processDate(post.created);
                    post.approved_time = this.processDate(post.approved_time);
                    postsArray.push(post);
                });
                scope.requests = postsArray;
            });
        },
        updateField(field, id, data) {
            const update = {};
            update[field] = data;
            if (field === 'approved') {
                update.approved_time = this.$firebase.firestore.Timestamp.now();
                update.approved_by = this.$firebase.auth.currentUser.uid;
            }
            this.$firebase.requests.doc(id).update({
                ...update,
                modified: this.$firebase.firestore.Timestamp.now(),
            });
        },
        processDate(field) {
            try {
                if (field === '' || field === undefined) {
                    return '';
                }
                return field
                    .toDate()
                    .toISOString()
                    .replace('T', ' ')
                    .substring(0, 19);
            } catch (e) {
                console.error(e, field);
                return '';
            }
        },
    },
};
</script>

<style lang="scss" scoped></style>
