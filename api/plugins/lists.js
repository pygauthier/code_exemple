import CRUDMixin from './mixins/delete';

export default function({ $axios, $api }) {
    class Lists extends CRUDMixin {
        axios = $axios;
        route = 'api/lists/';
    }
    const lists = new Lists();
    $api.lists = lists;
}
