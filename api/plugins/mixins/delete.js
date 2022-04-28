import UpdateMixin from './update';

export default class CRUDMixin extends UpdateMixin {
    async delete(id = null) {
        const response = await this.axios.delete(this.route + 'items/' + id);
        if (response.status === 201 || response.status === 200) {
            return response.status;
        } else {
            return { error: response.data };
        }
    }
}
