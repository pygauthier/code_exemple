import CRUDMixin from './mixins/delete';
import ReadOnlyMixin from './mixins/read';

export default function({ $axios, $api }) {
    class Items extends CRUDMixin {
        axios = $axios;
        route = 'api/items/items/';
    }
    class Versions extends ReadOnlyMixin {
        axios = $axios;
        route = 'api/items/versions/';
    }
    const items = new Items();
    items.versions = new Versions();
    $api.items = items;
}
