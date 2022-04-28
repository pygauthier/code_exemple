const pkg = require('./package.json');
const lang = require('./src/i18n/translations.js');
require('dotenv').config();

const svgo = {
    plugins: [
        { prefixIds: true },
        { removeTitle: true },
        { removeDesc: true },
        { removeViewBox: false },
        { removeDimensions: true },
        {
            removeAttrs: {
                attrs: ['opacity'],
            },
        },
    ],
};

module.exports = {
    srcDir: 'src/',
    buildDir: 'functions/.nuxt',
    server: {
        port: process.env.PORT,
        host: process.env.HOST,
    },

    env: {
        API_URL: process.env.API_URL,
        firebaseConfig: {
            apiKey: process.env.apiKey,
            authDomain: process.env.authDomain,
            databaseURL: process.env.databaseURL,
            projectId: process.env.projectId,
            storageBucket: process.env.storageBucket,
            messagingSenderId: process.env.messagingSenderId,
            appId: process.env.appId,
        },
    },

    mode: 'universal',

    /*
     ** Headers of the page
     */
    head: {
        title: 'Trucksbook Queue Manager',
        meta: [
            { charset: 'utf-8' },
            {
                name: 'viewport',
                content: 'width=device-width, initial-scale=1',
            },
            { 'http-equiv': 'X-UA-Compatible', content: 'IE=edge' },
            { hid: 'format-detection', name: 'format-detection', content: 'telephone=no' },
            {
                hid: 'description',
                name: 'description',
                content: pkg.description,
            },
            {
                hid: 'og:image',
                property: 'og:image',
                content: '/medaillon.png',
            },
        ],
        link: [{ rel: 'icon', type: 'image/x-icon', href: '/medaillon.png' }],
    },

    /*
     ** Customize the progress-bar color
     */
    loading: { color: '#fff' },

    /*
     ** Global CSS
     */
    css: ['element-ui/packages/theme-chalk/src/index.scss', { src: '@/assets/scss/app.scss', lang: 'scss' }],

    /*
     ** Plugins to load before mounting the App
     */
    plugins: [
        '@/plugins/cities',
        '@/plugins/firebase',
        '@/plugins/element-ui',
        { src: '@/plugins/nuxtClientInit', mode: 'client' },
    ],

    /*
     ** Nuxt.js dev-modules
     */
    buildModules: ['@nuxtjs/eslint-module', '@nuxtjs/stylelint-module', '@nuxtjs/router'],

    /*
     ** Nuxt.js modules
     */
    modules: [
        'cookie-universal-nuxt',
        '@nuxtjs/axios',
        '@nuxtjs/svg',
        '@nuxtjs/dotenv',
        '@nuxtjs/sentry',
        '@nuxtjs/style-resources',
        'nuxt-svg-loader',
        // '@nuxtjs/onesignal',
        //'@nuxtjs/pwa',
        '@nuxtjs/firebase',
        [
            'nuxt-fontawesome',
            {
                component: 'fa',
                imports: [
                    // import whole set
                    {
                        set: '@fortawesome/free-solid-svg-icons',
                        icons: ['fas'],
                    },
                ],
            },
        ],
        ['@nuxtjs/moment', ['fr']],
        [
            'nuxt-i18n',
            {
                // Options
                // vueI18nLoader: false,
                locales: [
                    {
                        code: 'fr',
                        name: 'Français',
                        iso: 'fr-FR',
                    },
                    {
                        code: 'en',
                        name: 'English',
                        iso: 'en-US',
                    },
                ],
                parsePages: false,
                detectBrowserLanguage: {
                    useCookie: true,
                },
                defaultLocale: 'fr',

                vueI18n: {
                    messages: lang.translations,
                },
            },
        ],
    ],

    firebase: {
        lazy: false,
        config: {
            apiKey: '',
            authDomain: '',
            databaseURL: '',
            projectId: '',
            storageBucket: '',
            messagingSenderId: '',
            appId: '',
            measurementId: '',
            fcmPublicVapidKey: '',
        },
    },
    pwa: {
        icon: [
            {
                src: '/icons/android-icon-36x36.png',
                sizes: '36x36',
                type: 'image/png',
                density: '0.75',
            },
            {
                src: '/icons/android-icon-48x48.png',
                sizes: '48x48',
                type: 'image/png',
                density: '1.0',
            },
            {
                src: '/icons/android-icon-72x72.png',
                sizes: '72x72',
                type: 'image/png',
                density: '1.5',
            },
            {
                src: '/icons/android-icon-96x96.png',
                sizes: '96x96',
                type: 'image/png',
                density: '2.0',
            },
            {
                src: '/icons/android-icon-144x144.png',
                sizes: '144x144',
                type: 'image/png',
                density: '3.0',
            },
            {
                src: '/icons/android-icon-192x192.png',
                sizes: '192x192',
                type: 'image/png',
                density: '4.0',
            },
            {
                src: '/icons/app-icon-512x512.png',
                sizes: '512x512',
                type: 'image/png',
                density: '4.0',
            },
        ],
        manifest: {
            name: 'Trucksbook Queue Manager',
            short_name: 'TB QM',
            lang: 'fr',
            useWebmanifestExtension: false,
            background_color: '#212529',
            theme_color: '#e14eca',
            start_url: '/login',
            score: '/',
            display: 'fullscreen',
            icons: [
                {
                    src: '/icons/android-icon-36x36.png',
                    sizes: '36x36',
                    type: 'image/png',
                    density: '0.75',
                },
                {
                    src: '/icons/android-icon-48x48.png',
                    sizes: '48x48',
                    type: 'image/png',
                    density: '1.0',
                },
                {
                    src: '/icons/android-icon-72x72.png',
                    sizes: '72x72',
                    type: 'image/png',
                    density: '1.5',
                },
                {
                    src: '/icons/android-icon-96x96.png',
                    sizes: '96x96',
                    type: 'image/png',
                    density: '2.0',
                },
                {
                    src: '/icons/android-icon-144x144.png',
                    sizes: '144x144',
                    type: 'image/png',
                    density: '3.0',
                },
                {
                    src: '/icons/app-icon-512x512.png',
                    sizes: '512x512',
                    type: 'image/png',
                    density: '4.0',
                },
            ],
        },
        workbox: {
            runtimeCaching: [
                {
                    urlPattern: 'https://fonts.googleapis.com/.*',
                    handler: 'cacheFirst',
                    method: 'GET',
                    strategyOptions: { cacheableResponse: { statuses: [0, 200] } },
                },
                {
                    urlPattern: 'https://fonts.gstatic.com/.*',
                    handler: 'cacheFirst',
                    method: 'GET',
                    strategyOptions: { cacheableResponse: { statuses: [0, 200] } },
                },
            ],
        },
    },
    oneSignal: {
        cdn: true,
        OneSignalSDK: 'https://cdn.onesignal.com/sdks/OneSignalSDK.js',
        init: {
            appId: '',
            allowLocalhostAsSecureOrigin: true,
            welcomeNotification: {
                disable: false,
            },
        },
        importScripts: ['/sw.js'],
    },
    axios: {
        baseURL: process.env.BASE_URL,
    },

    sentry: {
        initialize: process.env.NODE_ENV !== 'development',
        dsn: process.env.SENTRY_DSN,
        config: {}, // Additional config
    },

    styleResources: {
        scss: ['@/assets/scss/settings/*', '@/assets/scss/base/_base.scss', '@/assets/scss/base/_extends.scss'],
    },

    svgLoader: {
        svgoConfig: {
            svgo,
        },
    },

    eslint: {
        fix: true,
    },

    stylelint: {
        fix: true,
    },

    /*
     ** Build configuration
     */
    build: {
        transpile: [/^element-ui/],
        extractCSS: true,
        /*
         ** You can extend webpack config here
         */
        extend(config, ctx) {
            const vueRule = config.module.rules.find(rule => rule.test.test('.vue'));
            vueRule.use = [
                {
                    loader: vueRule.loader,
                    options: vueRule.options,
                },
                {
                    loader: 'vue-svg-inline-loader',
                    options: {
                        inlineKeyword: 'inline',
                        inlineStrict: true,
                        spriteKeyword: 'sprite',
                        spriteStrict: false,
                        removeAttributes: ['alt', 'src'],
                        xhtml: false,
                        svgo,
                    },
                },
            ];
            delete vueRule.loader;
            delete vueRule.options;
        },
    },
};
