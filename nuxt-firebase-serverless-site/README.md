# Trucksbook Queue Manager Serverless

##### Documentation

- [Vue](https://vuejs.org/)
- [VueX](https://vuex.vuejs.org/)
- [Nuxt](https://nuxtjs.org/)
- [Firebase](https://console.firebase.google.com/)
- [element-ui](https://element.eleme.io/#/en-US/component/)
- [git-flow](https://github.com/petervanderdoes/gitflow-avh)

##### Modules

- [axios-module](https://axios.nuxtjs.org/)
- [router-module](https://github.com/nuxt-community/router-module)
- [dotenv-module](https://github.com/nuxt-community/dotenv-module)
- [nuxt-i18n](https://github.com/nuxt-community/nuxt-i18n)
- [cookie-universal-nuxt](https://github.com/microcipcip/cookie-universal/tree/master/packages/cookie-universal-nuxt#readme)
- [vue-svg-inline-loader](https://github.com/oliverfindl/vue-svg-inline-loader#readme)
- [firebase](https://console.firebase.google.com/)

## Utilisation

Ce projet gère ses dépendances avec [`yarn`](https://yarnpkg.com/)

#### Mode développement

```sh
# install dependencies
yarn
# serve with hot-reload
yarn dev
```

#### Mode production

```sh
# install dependencies
yarn
# build
yarn build
#serve
yarn start
```

#### Lint

**Note:** Éxécuter automatiquement en mode dev

```sh
yarn lint:js
yarn lint:scss
```

#### Deploiement

```sh
# Deploy develop on dev
dep deploy dev
# Deploy specific branch on dev
dep deploy dev --branch=feature/1234_myfeature
```


## Arborescence

#### Répertoires racine

##### deploy

Le répertoire `deploy` contient les fichiers de configuration pour `deployer`, l'outil de déploiment.

##### src

Le répertoire `src` contient les fichiers source de l'application Nuxt.

##### dist

Le répertoire `dist` contient les fichiers compilé pour la distribution. Ce répertoire ne devrait pas être dans le Git.

#### Répertoire src

##### assets

Le répertoire `assets` contient vos ressources qui seront compilées et bundler par Webpack tels que les fichiers SASS global et les SVG.

##### components

Le répertoire `components` contient vos composants Vue.js. Vous ne pouvez pas utiliser les méthodes `asyncData` ou `fetch` sur ces composants.

##### i18n

Le répertoire `i18n` contient les fichiers de traductions global au format JSON. Vous pouvez aussi traduire directement dans les composants.

##### layout

Le répertoire `layouts` contient les mises en page de votre application. Les mises en page sont utilisées pour changer l'aspect de votre page.

##### middleware

Le répertoire `middleware` contient vos middlewares. Un middleware vous permet de définir une fonction qui sera exécutée avant de faire le rendu d'une mise en page ou d'un groupe de mises en page.

##### pages

Le répertoire `pages` contient vos vues et routes de l'application.

##### plugins

Le répertoire `plugins` contient les plugins JavaScript que vous désirez exécuter avant d'instancier l'application. C'est le bon endroit pour enregistrer des composants globaux.

##### static

Le répertoire `static` est directement servi par le serveur ([/static/robots.txt]() est accessible à l'adresse http://localhost:3000/robots.txt).

##### store

Le répertoire `store` contient vos fichiers de store Vuex. Chaque fichier représente un module de store ou un dossier représente un modules découper en fichiers (`state.js`, `getters.js`, `mutation.js`, `actions.js`)

## Plugins

##### element-ui.js

Le plugin `element-ui` contient les import et la définition des components global de element-ui.

##### nuxtClientInit.js

Le plugin `nuxtClientInit` ajoute une actions dans le store vuex qui est appelé lors du premier chargement de la page.

##### firebase.js

Le plugin `firebase` contient la définition du client javascript qui exécute les appels d'API.

## Utilisation

##### svg

Les SVG sont utilisé pour les icônes. Si le SVG contient des couleurs, elle seront supprimées lorsque la balise sera remplacer par le code SVG de l'icône. Une fois le SVG inline, il est possible de controller sa couleur en CSS ce qui permet de lui appliquer les effets de hover.

Avant la compilation:
```html
<img inline src="@/assets/svg/test-logo.svg" width="150" height="25" />
```

Après la compilation:
```html
<svg
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    inline=""
    role="presentation"
    focusable="false"
    tabindex="-1"
>
    <use xlink:href="#sprite-2433fa800e839a4b93f4bace9d713aed" href="#sprite-2433fa800e839a4b93f4bace9d713aed"></use>
</svg>

<!-- Sprite symbol -->
<svg xmlns="http://www.w3.org/2000/svg" style="display: none !important;">
    <symbol
        id="sprite-2433fa800e839a4b93f4bace9d713aed"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="xMidYMid"
        viewBox="0 0 514 86"
    >
        <path
            d="M468.512 86.037c-24.032-.114-45.217-17.563-45.098-43.227.122-25.659 21.47-42.911 45.502-42.802 24.036.113 45.212 17.563 45.094 43.223-.122 25.659-21.462 42.915-45.498 42.806zm.306-65.088c-12.332-.057-23.29 8.799-23.351 21.966-.061 13.167 10.811 22.125 23.143 22.181 12.332.057 23.285-8.799 23.351-21.966.061-13.168-10.811-22.125-23.143-22.181zM310.588 2.342h77.02v19.223h-77.02V2.342zm59.564 49.247h-38.335v12.799h55.791v19.446h-77.02V32.802h59.564v18.787zM244.596 83.614H188.56V2.284h51.846c14.441 0 24.983 8.824 24.983 22.504 0 5.143-1.877 10.145-5.63 12.796 6.931 4.112 10.974 10.145 10.974 20.439 0 14.266-11.553 25.591-26.137 25.591zm-5.043-61.973h-30.045v10.993h30.776c2.19 0 4.377-2.82 4.377-5.494 0-2.081-1.314-5.499-5.108-5.499zm3.913 29.703H209.48v12.772l34.569.004c3.357 0 5.981-2.384 5.981-6.242 0-3.713-2.77-6.534-6.564-6.534zM118.034 2.285h22.16v81.33h-22.16V2.285zM-.001 2.281h21.234v61.884h54.305v19.446H-.001V2.281z"
            fill-rule="evenodd"
            class="libeo-logo_svg__cls-2"
        ></path>
    </symbol>
</svg>
```


##### media query

Breakpoints:

- xs: <768px
- sm: ≥768px
- md: ≥992px
- lg: ≥1200px
- xl: ≥1920px

```scss
@include res('xs') {
    background: $--main-color-primary;
}
```
