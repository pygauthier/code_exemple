<template>
    <div>
        <div v-for="request in requests" :key="request.id" class="link-card">
            <div class="docu-recent-title">
                ({{ request.cargo }}) {{ request.from }} - {{ request.to }} (~{{ request.estimated_km }}km)
            </div>
            <div class="unpin-bookmark">
                {{ request.created }}
                <fa
                    v-if="showTimes === true"
                    @click="timesClick(request)"
                    :icon="fas.faTimesCircle"
                    class="c-pointer ml-15"
                />
            </div>
        </div>
    </div>
</template>

<script>
import { far } from '@fortawesome/free-regular-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';

export default {
    name: 'RequestsCard',
    props: {
        requests: {
            type: Array,
            default: () => {
                return [];
            },
        },
        showTimes: {
            type: Boolean,
            default: () => {
                return true;
            },
        },
    },
    data() {
        return {};
    },
    computed: {
        fas() {
            return fas;
        },
        far() {
            return far;
        },
    },
    methods: {
        timesClick(id) {
            this.$emit('timesClick', id);
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
