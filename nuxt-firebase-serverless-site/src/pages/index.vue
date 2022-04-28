<template>
    <div class="accueil flex">
        <div class="flex flex-grow">
            <div id="sect-docu-recents">
                <div id="docu-recents">
                    <div class="container">
                        <h4>Mes demandes actives</h4>
                        <div class="cards-overflow">
                            <requestsCard :requests="requestsPending" @timesClick="deleteRequests" />
                        </div>
                    </div>
                </div>
            </div>

            <div id="sect-pinned">
                <div id="docu-pinned">
                    <div class="container">
                        <h4 class="mb-15">Mes demandes acceptées</h4>
                        <div class="cards-overflow">
                            <requestsCard :requests="requestsAccepted" :showTimes="false" />
                        </div>
                    </div>
                </div>
            </div>

            <div id="sect-liens-utile">
                <div id="liens-utile">
                    <div class="container">
                        <h4 class="mb-15">Mes demandes annulée</h4>
                        <div class="cards-overflow">
                            <requestsCard :requests="requestsCancelled" :showTimes="false" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { far } from '@fortawesome/free-regular-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { mapActions } from 'vuex';
import requestsCard from '~/components/homeRequestsCard';

export default {
    components: {
        requestsCard,
    },
    data() {
        return {
            requestsPending: [],
            requestsAccepted: [],
            requestsCancelled: [],
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
    mounted() {
        // this.updateClientUserNameInNotification();
        this.get_requests();
    },
    methods: {
        ...mapActions('auth', ['currentUser']),
        get_requests() {
            const scope = this;
            this.$firebase.requests
                .orderBy('created')
                .where('owner', '==', this.$firebase.auth.currentUser.uid)
                .onSnapshot(snapshot => {
                    this.requestsPending = [];
                    this.requestsAccepted = [];
                    this.requestsCancelled = [];
                    snapshot.forEach(data => {
                        const post = data.data();
                        post.id = data.id;
                        post.modified = this.processDate(post.modified);
                        post.created = this.processDate(post.created);
                        if (!post.approved && !post.cancelled) {
                            scope.requestsPending.push(post);
                        }

                        if (post.cancelled) {
                            scope.requestsCancelled.push(post);
                        }

                        if (post.approved) {
                            scope.requestsAccepted.push(post);
                        }
                    });
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

        deleteRequests(value) {
            value.cancelled = true;
            this.$firebase.requests.doc(value.id).update({
                cancelled: true,
                modified: this.$firebase.firestore.Timestamp.now(),
            });
        },
        /* updateClientUserNameInNotification() {
            const user = this.currentUser();
            user.then(response => {
                this.$OneSignal.push(() => {
                    this.$OneSignal.isPushNotificationsEnabled(isEnabled => {
                        if (isEnabled) {
                            const usersCollection = firebase.firestore().collection('users');
                            usersCollection.doc(user.uid).update({
                                player_ids: firebase.firestore.FieldValue.arrayUnion(this.$OneSignal.getUserId()),
                            });
                            if (user.uid !== '' || user.uid !== 'undefined') {
                                console.log(
                                    this.$OneSignal.push(() => {
                                        this.$OneSignal.setExternalUserId(user.uid);
                                    }),
                                );
                            }
                        } else {
                            console.log('Push notifications are not enabled yet.');
                        }
                    });
                });
            });
        }, */
    },
};
</script>

<style lang="scss" scoped>
#sect-docu-recents {
    display: flex;
    width: 33.33%;
    background-color: #e4e4e4;
    #docu-recents {
        width: 100%;
        padding: 50px 0 50px 0;
        h4 {
            margin-bottom: 15px;
        }
    }
}
#sect-pinned {
    display: flex;
    position: relative;
    width: 33.33%;
    padding: 50px 0 50px 0;
    background-color: #e4e4e4;
}
#docu-pinned {
    width: 100%;
}
#sect-liens-utile {
    width: 33.33%;
    background-color: #e4e4e4;
}
.accueil {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}
.cards-overflow {
    overflow-y: scroll;
    max-height: 650px;
}
</style>
