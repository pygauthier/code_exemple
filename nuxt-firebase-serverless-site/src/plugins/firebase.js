import 'firebase/auth';
import 'firebase/firestore';
import * as firebase from 'firebase/app';
import Cookies from 'js-cookie';

// const firebaseConfig = process.env.firebaseConfig;
export default ({ store, app, redirect, $axios }, inject) => {
    const _firebase = {
        collestionsList: ['users', 'requests'],
        async init() {
            // Your web app's Firebase configuration
            const firebaseConfig = {
                apiKey: 'env_key',
                authDomain: 'firebase_auth',
                databaseURL: 'firebase_url',
                projectId: 'firebase_projects',
                storageBucket: 'firebase_bucket',
                messagingSenderId: '86271491834',
                appId: 'app_id',
            };
            // Initialize Firebase
            if (!firebase.apps.length) {
                await firebase.initializeApp(firebaseConfig);
            }

            // inject modules
            this.auth = firebase.auth();
            this.db = firebase.firestore();
            this.fire = firebase;
            this.firestore = firebase.firestore;
            const scope = this;
            this.collestionsList.forEach(collection => {
                scope[collection] = this.db.collection(collection);
            });
        },
        isLogged() {
            this.init();
            let loggedIn = false;
            firebase.auth().onAuthStateChanged(user => {
                if (user) {
                    loggedIn = true;
                    firebase
                        .auth()
                        .currentUser.getIdToken()
                        .then(token => {
                            Cookies.set('access_token', token);
                        });
                } else {
                    loggedIn = false;
                    Cookies.remove('access_token');
                }
            });
            return loggedIn;
        },
    };
    inject('firebase', _firebase);
};
