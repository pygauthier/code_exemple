import { getMatchedComponents, normalizePath, routeOption } from '@/utils';

export default function({ app, route, store, redirect }) {
    if (routeOption(route, 'auth', false)) {
        return;
    }

    // Disable middleware if no route was matched to allow 404/error page
    const matches = [];
    const Components = getMatchedComponents(route, matches);
    if (!Components.length) {
        return;
    }

    // Redirect URL
    const login = app.localePath('login');
    const callback = app.localePath('login');
    const home = app.localePath('index');

    const pageIsInGuestMode = routeOption(route, 'auth', 'guest');
    const insidePage = page => normalizePath(route.path) === normalizePath(page);
    if (store.getters['auth/loggedIn']) {
        // -- Authorized --
        if (insidePage(login) || pageIsInGuestMode) {
            redirect(home);
        }
    } else if (!pageIsInGuestMode && !insidePage(callback)) {
        // -- Guest --
        // (Those passing `callback` at runtime need to mark their callback component
        // with `auth: false` to avoid an unnecessary redirect from callback to login)
        redirect(login);
    }
}
