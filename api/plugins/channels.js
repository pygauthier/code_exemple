import CRUDMixin from './mixins/delete';

export default function({ $axios, $api }) {
    class Channels extends CRUDMixin {
        axios = $axios;
        route = 'api/channels/';
    }
    const channels = new Channels();
    $api.channels = channels;
}
