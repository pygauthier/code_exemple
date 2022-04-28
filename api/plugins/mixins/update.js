import ReadOnlyMixin from './read';

export default class UpdateMixin extends ReadOnlyMixin {
    async post(payload) {
        const response = await this.axios.post(this.route, payload);
        return this._defaultResponse(response);
    }
    async update(id = null, payload) {
        const response = await this.axios.patch(this.route + 'items/' + id, payload);
        return this._defaultResponse(response);
    }
}
