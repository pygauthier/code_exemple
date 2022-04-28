import CRUDMixin from './mixins/delete';

export default function({ $axios, $api }) {
    class Categories extends CRUDMixin {
        axios = $axios;
        route = 'api/categories/';
    }
    const categories = new Categories();
    $api.categories = categories;
}
