export default class ReadOnlyMixin {
    route = '';
    filters = {};
    axios = null;
    clear() {
        this.filters = {};
    }
    _defaultResponse(response) {
        let returnPayload;
        if (response.status === 201 || response.status === 200) {
            returnPayload = response.data;
        } else {
            returnPayload = { error: response.data };
        }
        this.clear();
        return returnPayload;
    }
    async get(id = null) {
        let route = this.route;
        if (id) {
            route = route + id;
        }
        const response = await this.axios.get(route, { params: this.filters });
        return this._defaultResponse(response);
    }
}
