<template>
    <div class="login">
        <el-form ref="form" :model="form" @submit.native.prevent="onNewRequest" label-position="top">
            <el-switch
                v-model="game"
                active-text="ETS2"
                inactive-text="ATS"
                active-value="ets"
                inactive-value="ats"
                class="mb-20"
            />
            <br />
            <span>Départ</span>
            <el-form-item class="mt-10 mb-30">
                <el-select v-model="form.from" @change="calcDist" filterable placeholder="Départ" style="width:100%">
                    <el-option-group v-for="city in $cities[game]" :key="city.name" :label="city.name">
                        <el-option
                            v-for="item in city.Placemark.sort((a, b) => a.name > b.name)"
                            :key="item.name"
                            :label="item.name"
                            :value="item.name"
                        >
                        </el-option>
                    </el-option-group>
                </el-select>
            </el-form-item>

            <span>Arrivée</span>
            <el-form-item class="mt-10">
                <el-select v-model="form.to" @change="calcDist" filterable placeholder="Arrivée" style="width:100%">
                    <el-option-group v-for="city in $cities[game]" :key="city.name" :label="city.name">
                        <el-option
                            v-for="item in city.Placemark.sort((a, b) => a.name > b.name)"
                            :key="item.name"
                            :label="item.name"
                            :value="item.name"
                        >
                        </el-option>
                    </el-option-group>
                </el-select>
            </el-form-item>

            <el-form-item>
                <label>Cargo</label>
                <el-input v-model="form.cargo" />
            </el-form-item>

            <el-form-item>
                <label>Commentaire</label>
                <el-input v-model="form.comments" :rows="2" type="textarea" />
            </el-form-item>

            <div class="flex" style="justify-content: space-between;">
                <el-form-item>
                    <el-button type="primary" native-type="submit">Créer</el-button>
                </el-form-item>
                <span class="mt-15">{{ estimated_km }} Km à vol d'oiseau</span>
            </div>
        </el-form>
    </div>
</template>

<script>
import { far } from '@fortawesome/free-regular-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { mapActions } from 'vuex';

export default {
    name: 'NewRequestForm',
    data() {
        return {
            game: 'ets',
            user: {},
            form: {},
            value: '',
            estimated_km: 0,
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
        this.user = await this.currentUser();
    },
    methods: {
        ...mapActions('auth', ['logout', 'currentUser']),
        onNewRequest() {
            this.form.created = this.$firebase.firestore.Timestamp.now();
            this.form.modified = this.$firebase.firestore.Timestamp.now();
            this.form.owner = this.$firebase.auth.currentUser.uid;
            this.form.owner_trucksbook_username = this.user.trucksbook;
            this.form.approved = false;
            this.form.cancelled = false;
            this.form.approved_time = '';
            this.form.estimated_km = this.estimated_km;
            this.$firebase.requests.doc().set(this.form);
            this.dialogNewRequest = false;
            this.$emit('after', true);
        },

        calcDist(input) {
            if (this.form.from && this.form.to) {
                const allCity = [];
                this.$cities[this.game].forEach(dlc => {
                    dlc.Placemark.forEach(city => {
                        allCity.push(city);
                    });
                });
                const from = allCity.find(city => city.name === this.form.from);
                const to = allCity.find(city => city.name === this.form.to);

                this.estimated_km = this.calcCrow(
                    parseFloat(from.Point.coordinates.split(', ')[0]),
                    parseFloat(from.Point.coordinates.split(', ')[1]),
                    parseFloat(to.Point.coordinates.split(', ')[0]),
                    parseFloat(to.Point.coordinates.split(', ')[1]),
                ).toFixed(2);
            }
        },
        calcCrow(lat1, lon1, lat2, lon2) {
            const R = 6371; // km
            const dLat = this.toRad(lat2 - lat1);
            const dLon = this.toRad(lon2 - lon1);
            lat1 = this.toRad(lat1);
            lat2 = this.toRad(lat2);

            const a =
                Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            const d = R * c;
            return d;
        },

        // Converts numeric degrees to radians
        toRad(Value) {
            return (Value * Math.PI) / 180;
        },
    },
};
</script>
<style lang="scss" scoped>
.unpin-bookmark {
    margin-left: auto;
}
.link-card {
    display: flex;
    height: 50px;
    margin: 0 0 5px 5px;
    padding: 0 15px 0 15px;
    border-radius: 8px;
    background-color: $--color-main-grey;
    align-items: center;
}
.fa-times-circle {
    font-size: 20px;
}
</style>
